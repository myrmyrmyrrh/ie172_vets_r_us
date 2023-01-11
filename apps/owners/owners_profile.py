from datetime import date
from sre_parse import State
from dash import dcc
from dash import html
import dash_bootstrap_components as dbc
import dash
from dash.exceptions import PreventUpdate
from dash.dependencies import Input, Output, State
import pandas as pd
from urllib.parse import urlparse, parse_qs

from app import app
from apps import dbconnect as db

layout = html.Div(
    [ 
        html.Div(
            [
            dcc.Store(id='ownerprof_toload', storage_type='memory', data=0),
            ]
        ),
        html.H2("Owner Details"),
        html.Hr(),
        dbc.Row(
            [
                dbc.Label("Name", width=2),
                dbc.Col(
                    dbc.Input(
                        type="text", id="ownerprof_name", placeholder="Enter owner name"
                    ),
                    width=6,
                ),
            ],
            className="mb-3",
        ),
        dbc.Row(
            [
                dbc.Label("Contact Number", width=2),
                dbc.Col(
                    dbc.Input(
                        type="text", id="ownerprof_contact", placeholder="Enter contact number"
                    ),
                    width=6,
                ),
            ],
            className="mb-3",
        ),
        html.Div(
                dbc.Row(
                [
                    dbc.Label("Wish to delete?", width=2),
                    dbc.Col(
                        dbc.Checklist(
                            id='ownerprof_removerecord',
                            options=[
                                {
                                'label': "Mark for Deletion",
                                'value': 1
                                }
                            ],
                            style={'fontWeight':'bold'},
                        ),
                        width=6,
                    ),
                ],
                className="mb-3",
            ),
            id = 'ownerprof_removerecord_div'
        ),
        html.Hr(),
        dbc.Button('Submit', color="success", id='ownerprof_submitbtn', n_clicks=0),
        dbc.Modal(
            [
                dbc.ModalHeader("Saving Progress"),
                dbc.ModalBody("tempmessage", id='ownerprof_feedback_message'),
                dbc.ModalFooter(
                    dbc.Button(
                        "Okay", id="ownerprof_closebtn", className="ms-auto", n_clicks=0
                    )
                ),
            ],
            id="ownerprof_modal",
            is_open=False
        ),
    ],
)
@app.callback(
    [
        Output('ownerprof_toload', 'data'),
        Output('ownerprof_removerecord_div', 'style')
    ],
    [
        Input('url', 'pathname'),
    ],
    [
        State('url', 'search')
    ]
)

def ownerprof_editprocess(pathname, search):
    if pathname == '/owners/owners_profile':
        sql = """
        """

        parsed = urlparse(search)
        mode = parse_qs(parsed.query)['mode'][0]
        to_load = 1 if mode == 'edit' else 0

        removerecord_div = None if to_load else {'display': 'none'}

    else:
        raise PreventUpdate
    
    return [to_load, removerecord_div]  

@app.callback(
    [
        Output('ownerprof_modal', 'is_open'),
        Output('ownerprof_feedback_message', 'children'),
        Output('ownerprof_closebtn', 'href')
    ],
    [
        Input('ownerprof_submitbtn', 'n_clicks'),
        Input('ownerprof_closebtn', 'n_clicks')
    ],
    [
        State('ownerprof_name','value'),
        State('ownerprof_contact', 'value'),
        State('url', 'search'),
        State('ownerprof_removerecord', 'value')
    ]
)

def ownerprof_submitprocess(submitbtn, closebtn,
                            name, contact,
                            search, removerecord):
    ctx = dash.callback_context
    if ctx.triggered:
        eventid = ctx.triggered[0]['prop_id'].split('.')[0]
        openmodal = False
        feedbackmessage = ''
        okay_href = None
        if eventid == "ownerprof_submitbtn" and submitbtn:
            openmodal = True
            inputs = [
                name,
                contact
            ]
            if not all(inputs):
                feedbackmessage = "Please supply all inputs."
            elif len(name)>256:
                feedbackmessage = "Title is too long (length=256)."

            else:
                parsed = urlparse(search)
                mode = parse_qs(parsed.query)['mode'][0]
                if mode == 'add': 
                    sqlcode = """ INSERT INTO owners(
                        owner_name,
                        owner_contact,
                        owner_delete_ind
                    )
                    VALUES (%s, %s, %s)
                    """
                    values = [name, contact, False]
                    db.modifydatabase(sqlcode, values)
                    feedbackmessage = "Owner has been saved."
                    okay_href = '/owners'

                elif mode == 'edit':
                    parsed = urlparse(search)
                    ownerid = parse_qs(parsed.query)['id'][0]
                    sqlcode = """UPDATE owners
                    SET
                        owner_name = %s,
                        owner_contact = %s,
                        owner_delete_ind = %s
                    WHERE
                        owner_id = %s
                    """

                    to_delete = bool(removerecord)

                    values = [name, contact, to_delete, ownerid]
                    db.modifydatabase(sqlcode, values)
                    feedbackmessage = "Owner has been updated."
                    okay_href = '/owners'

                else:
                    raise PreventUpdate

        elif eventid == 'ownerprof_closebtn' and closebtn:
            pass

        else:
            raise PreventUpdate

        return [openmodal, feedbackmessage, okay_href]


@app.callback(
    [
        Output('ownerprof_name', 'value'),
        Output('ownerprof_contact', 'value'),
    ],
    [
        Input('ownerprof_toload', 'modified_timestamp')
    ],
    [
        State('ownerprof_toload', 'data'),
        State('url', 'search')
    ]
)

def loadownerdetails(timestamp, to_load, search):
    if to_load == 1:
        sql = """SELECT owner_name, owner_contact
        FROM owners
        WHERE owner_id = %s
        """

        parsed = urlparse(search)
        ownerid = parse_qs(parsed.query)['id'][0]

        val = [ownerid]
        colnames = ['name','contact']

        df = db.querydatafromdatabase(sql, val, colnames)

        name = df['name'][0]
        contact = df['contact'][0]

        return [name, contact]

    else:
        raise PreventUpdate