from dash import dcc
from dash import html
import dash_bootstrap_components as dbc
import dash
from dash.exceptions import PreventUpdate
from dash.dependencies import Input, Output, State
import pandas as pd
from datetime import datetime
from urllib.parse import urlparse, parse_qs

from app import app
from apps import dbconnect as db

layout = html.Div(
    [ 
        html.Div( 
            [
                dcc.Store(id='invprof_toload', storage_type='memory', data=0),
            ]
        ),
        html.H2("Inventory Details"),
        html.Hr(),
        dbc.Row(
            [
                dbc.Label("Inventory Name", width=2),
                dbc.Col(
                    dbc.Input(
                        type="text", id="invprof_name", placeholder="Enter name"
                    ),
                    width=6,
                ),
            ],
            className="mb-3",
        ),
        dbc.Row(
            [
                dbc.Label("Quantity", width=2),
                dbc.Col(
                    dbc.Input(
                        type="number", id="invprof_quantity", placeholder="Enter Quantity"
                    ),
                    width=6,
                ),
            ],
            className="mb-3",
        ),
        html.Div(
            dbc.Row(
                [
                    dbc.Label("Wish to Delete?", width=2),
                    dbc.Col(
                            dbc.Checklist(
                                id='invprof_removerecord',
                                options=[
                                    {
                                        'label': "Mark for Deletion",
                                        'value': 1
                                    }
                                ],
                                # I want the label to be bold
                                style={'fontWeight':'bold'},
                        ),
                        width=6,
                    ),
                ],
                className="mb-3",
            ),
            id = 'invprof_removerecord_div'
        ),
        html.Hr(),
        dbc.Button('Submit', color="success", id='invprof_submitbtn'),
        dbc.Modal(
        [
            dbc.ModalHeader(dbc.ModalTitle("Saving Progress")),
            dbc.ModalBody("tempmessage", id='invprof_feedback_message'),
            dbc.ModalFooter(
                dbc.Button(
                    "Okay", id="invprof_closebtn", className="ms-auto", n_clicks=0
                ),
            ),
        ],
        id="invprof_modal",
        is_open=False,
        ),
    ],
)

@app.callback(
    [
        Output('invprof_toload', 'data'),
        Output('invprof_removerecord_div', 'style'),
    ],
    [
        Input('url', 'pathname')
    ],
    [
        State('url', 'search')
    ]
)

def invprof_loaddropdown(pathname, search):

    if pathname == '/inventory/inventory_profile':
        sql = """
        """
        parsed = urlparse(search)
        create_mode = parse_qs(parsed.query)['mode'][0]
        to_load = 1 if create_mode == 'edit' else 0

        removediv_style = {'display': 'none'} if not to_load else None

        # if style = none, we get default value

    else: 
        raise PreventUpdate

    return [to_load, removediv_style]

@app.callback(
    [
        Output('invprof_modal', 'is_open'),
        Output('invprof_feedback_message', 'children'),
        Output('invprof_closebtn', 'href'),
    ],
    [
        Input('invprof_submitbtn', 'n_clicks'),
        Input('invprof_closebtn', 'n_clicks'),
    ],
    [
        State('invprof_name', 'value'),
        State('invprof_quantity', 'value'),
        State('url', 'search'),
        State('invprof_removerecord', 'value')
    ]
)
def invprof_submitprocess(submitbtn, closebtn, name, quantity, search, removerecord):
    ctx = dash.callback_context
    if ctx.triggered:
        # eventid = name of the element that caused the trigger
        eventid = ctx.triggered[0]['prop_id'].split('.')[0]
        openmodal = False
        feedbackmessage = ''
        okay_href = None
    else:
        raise PreventUpdate

    if eventid == 'invprof_submitbtn' and submitbtn:
        openmodal = True

        # check if you have inputs
        inputs = [name, quantity]
        #if errroneous, raise prompt
        if not all(inputs):
            feedbackmessage = "Please supply all inputs"
        elif len(name)>256:
            feedbackmessage = "Name is too long (length>256)."
        else:
            parsed = urlparse(search)
            mode = parse_qs(parsed.query)['mode'][0]

            if mode == 'add':
            
            #save to db
                sqlcode = """INSERT INTO inventory(
                    inv_name,
                    inv_qty,
                    inv_delete_ind
                )
                VALUES(%s, %s, %s)
                """
                values = [name, quantity, False]
                db.modifydatabase(sqlcode, values)
                feedbackmessage = "Inventory has been added."
                okay_href = '/inventory'
            
            elif mode == 'edit':
                parsed = urlparse(search)
                invid = parse_qs(parsed.query)['id'][0]

                # 2. we need to update the db
                sqlcode = """UPDATE inventory
                SET
                    inv_name = %s,
                    inv_qty = %s,
                    inv_delete_ind = %s
                WHERE inv_id = %s
                """
                to_delete = bool(removerecord)

                values = [name, quantity, to_delete, invid]
                db.modifydatabase(sqlcode, values)
                feedbackmessage = "Inventory has been updated."
                okay_href = '/inventory'

            else:
                raise PreventUpdate            

    elif eventid == 'invprof_closebtn' and closebtn:
        pass

    else:
        raise PreventUpdate

    return [openmodal, feedbackmessage, okay_href]

@app.callback(
    [
        # Our goal is to update values of these fields
        Output('invprof_name', 'value'),
        Output('invprof_quantity', 'value'),
    ],
    [
        # Our trigger is if the dcc.Store object changes its value
        # This is how you check a change in value for a dcc.Store
        Input('invprof_toload', 'modified_timestamp')
    ],
    [
        # We need the following to proceed
        # Note that the value of the dcc.Store object is in
        # the ‘data’ property, and not in the ‘modified_timestamp’ property
        State('invprof_toload', 'data'),
        State('url', 'search'),
    ]
)

def invprofile_loadprofile(timestamp, toload, search):
    if toload: # check if toload = 1
    
        # Get movieid value from the search parameters
        parsed = urlparse(search)
        inv_id = parse_qs(parsed.query)['id'][0]
        # Query from db
        sql = """
            SELECT inv_name, inv_qty
            FROM inventory
            WHERE inv_id = %s
        """
        values = [inv_id]
        col = ['name', 'quantity']
        df = db.querydatafromdatabase(sql, values, col)
        name = df['name'][0]
        # Our dropdown list has the genreids as values then it will
        # display the correspoinding labels
        quantity = df['quantity'][0]
        return [name, quantity]
 
    else:
        raise PreventUpdate