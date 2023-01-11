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
            dcc.Store(id='petprof_toload', storage_type='memory', data=0),
            ]
        ),
        html.H2("Pet Details"),
        html.Hr(),
        dbc.Row(
            [
                dbc.Label("Name", width=2),
                dbc.Col(
                    dbc.Input(
                        type="text", id="petprof_name", placeholder="Enter pet name"
                    ),
                    width=6,
                ),
            ],
            className="mb-3",
        ),
        dbc.Row(
            [
                dbc.Label("Owner", width=2),
                dbc.Col(
                    html.Div(
                        dcc.Dropdown(
                            id='petprof_owner',
                            clearable=True,
                            searchable=True,
                        ),
                        className="dash-bootstrap"
                    ),
                    width=6,
                ),
            ],
            className="mb-3",
        ),
        dbc.Row(
            [
                dbc.Label("Type", width=2),
                dbc.Col(
                    dbc.Input(
                        type="text", id="petprof_type", placeholder="Enter pet type"
                    ),
                    width=6,
                ),
            ],
            className="mb-3",
        ),
        dbc.Row(
            [
                dbc.Label("Date of Birth", width=2),
                dbc.Col(     
                    html.Div(
                        dcc.DatePickerSingle(
                            id='petprof_dob',
                        ),
                        className="dash-bootstrap"
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
                            id='petprof_removerecord',
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
            id = 'petprof_removerecord_div'
        ),
        html.Hr(),
        dbc.Button('Submit', color="success", id='petprof_submitbtn', n_clicks=0),
        dbc.Modal(
            [
                dbc.ModalHeader("Saving Progress"),
                dbc.ModalBody("tempmessage", id='petprof_feedback_message'),
                dbc.ModalFooter(
                    dbc.Button(
                        "Okay", id="petprof_closebtn", className="ms-auto", n_clicks=0
                    )
                ),
            ],
            id="petprof_modal",
            is_open=False
        ),
    ],
)


@app.callback(
    [
        Output('petprof_owner', 'options'),
        Output('petprof_toload', 'data'),
        Output('petprof_removerecord_div', 'style')
    ],
    [
        Input('url', 'pathname'),
    ],
    [
        State('url', 'search')
    ]
)

def petprof_loaddropdown(pathname, search):
    if pathname == '/pets/pets_profile':
        sql = """
            SELECT owner_name as label, owner_id as value
                FROM owners
                WHERE owner_delete_ind = False
        """
        values = []
        cols = ['label', 'value']
        df = db.querydatafromdatabase(sql, values, cols)
        owner_opts = df.to_dict('records')

        parsed = urlparse(search)
        mode = parse_qs(parsed.query)['mode'][0]
        to_load = 1 if mode == 'edit' else 0

        removerecord_div = None if to_load else {'display': 'none'}

    else:
        raise PreventUpdate
    
    return [owner_opts, to_load, removerecord_div]

@app.callback(
    [
        Output('petprof_modal', 'is_open'),
        Output('petprof_feedback_message', 'children'),
        Output('petprof_closebtn', 'href')
    ],
    [
        Input('petprof_submitbtn', 'n_clicks'),
        Input('petprof_closebtn', 'n_clicks')
    ],
    [
        State('petprof_name','value'),
        State('petprof_owner', 'value'),
        State('petprof_type', 'value'),
        State('petprof_dob', 'date'),
        State('url', 'search'),
        State('petprof_removerecord', 'value')
    ]
)

def petprof_submitprocess(submitbtn, closebtn,
                            name, owner, type, dob,
                            search, removerecord):
    ctx = dash.callback_context
    if ctx.triggered:
        eventid = ctx.triggered[0]['prop_id'].split('.')[0]
        openmodal = False
        feedbackmessage = ''
        okay_href = None
        if eventid == "petprof_submitbtn" and submitbtn:
            openmodal = True
            inputs = [
                name,
                owner,
                type,
                dob,
            ]
            if not all(inputs):
                feedbackmessage = "Please supply all inputs."
            elif len(name)>256:
                feedbackmessage = "Title is too long (length=256)."

            else:
                parsed = urlparse(search)
                mode = parse_qs(parsed.query)['mode'][0]
                if mode == 'add': 
                    sqlcode = """ INSERT INTO pets(
                        pet_name,
                        owner_id,
                        pet_type,
                        pet_dob,
                        pet_delete_ind
                    )
                    VALUES (%s, %s, %s, %s, %s)
                    """
                    values = [name, owner, type, dob, False]
                    db.modifydatabase(sqlcode, values)
                    feedbackmessage = "Pet has been saved."
                    okay_href = '/pets'

                elif mode == 'edit':
                    parsed = urlparse(search)
                    petid = parse_qs(parsed.query)['id'][0]
                    sqlcode = """UPDATE pets
                    SET
                        pet_name = %s,
                        owner_id = %s,
                        pet_type = %s,
                        pet_dob = %s,
                        pet_delete_ind = %s
                    WHERE
                        pet_id = %s
                    """

                    to_delete = bool(removerecord)

                    values = [name, owner, type, dob, to_delete, petid]
                    db.modifydatabase(sqlcode, values)
                    feedbackmessage = "Pet has been updated."
                    okay_href = '/pets'

                else:
                    raise PreventUpdate

        elif eventid == 'petprof_closebtn' and closebtn:
            pass

        else:
            raise PreventUpdate

        return [openmodal, feedbackmessage, okay_href]


@app.callback(
    [
        Output('petprof_name', 'value'),
        Output('petprof_owner', 'value'),
        Output('petprof_type', 'value'),
        Output('petprof_dob', 'date'),
    ],
    [
        Input('petprof_toload', 'modified_timestamp')
    ],
    [
        State('petprof_toload', 'data'),
        State('url', 'search')
    ]
)

def loadpetdetails(timestamp, to_load, search):
    if to_load == 1:
        sql = """SELECT pet_name, owner_id, pet_type, pet_dob
        FROM pets
        WHERE pet_id = %s
        """

        parsed = urlparse(search)
        petid = parse_qs(parsed.query)['id'][0]

        val = [petid]
        colnames = ['name', 'owner', 'type','dob']

        df = db.querydatafromdatabase(sql, val, colnames)

        name = df['name'][0]
        owner = df['owner'][0]
        type = df['type'][0]
        dob = df['dob'][0]

        return [name, owner, type, dob]

    else:
        raise PreventUpdate