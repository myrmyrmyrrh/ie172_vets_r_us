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
        html.Div( # This div shall contain all dcc.Store objects
            [
                dcc.Store(id='doctorprof_toload', storage_type='memory', data=0),
            ]
        ),
        html.H2("Vet Details"),
        html.Hr(),
        dbc.Row(
            [
                dbc.Label("Name", width=2),
                dbc.Col(
                    dbc.Input(
                        type="text", id="doctorprof_name", placeholder="Enter name"
                    ),
                    width=6,
                ),
            ],
            className="mb-3",
        ),
        dbc.Row(
            [
                dbc.Label("Specialty", width=2),
                dbc.Col(
                    dbc.Input(
                        type="text", id="doctorprof_specialty", placeholder="Enter specialty"
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
                                id='doctorprof_removerecord',
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
            id = 'doctorprof_removerecord_div'
        ),
        html.Hr(),
        dbc.Button('Submit', color="success", id='doctorprof_submitbtn'),
        dbc.Modal(
        [
            dbc.ModalHeader(dbc.ModalTitle("Saving Progress")),
            dbc.ModalBody("tempmessage", id='doctorprof_feedback_message'),
            dbc.ModalFooter(
                dbc.Button(
                    "Okay", id="doctorprof_closebtn", className="ms-auto", n_clicks=0
                ),
            ),
        ],
        id="doctorprof_modal",
        is_open=False,
        ),
    ],
)

@app.callback(
    [
        Output('doctorprof_toload', 'data'),
        Output('doctorprof_removerecord_div', 'style'),
    ],
    [
        Input('url', 'pathname')
    ],
    [
        State('url', 'search')
    ]
)

def doctorprof_loaddropdown(pathname, search):

    if pathname == '/doctors/doctor_profile':
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
        Output('doctorprof_modal', 'is_open'),
        Output('doctorprof_feedback_message', 'children'),
        Output('doctorprof_closebtn', 'href'),
    ],
    [
        Input('doctorprof_submitbtn', 'n_clicks'),
        Input('doctorprof_closebtn', 'n_clicks'),
    ],
    [
        State('doctorprof_name', 'value'),
        State('doctorprof_specialty', 'value'),
        State('url', 'search'),
        State('doctorprof_removerecord', 'value')
    ]
)
def doctorprof_submitprocess(submitbtn, closebtn, name, specialty, search, removerecord):
    ctx = dash.callback_context
    if ctx.triggered:
        # eventid = name of the element that caused the trigger
        eventid = ctx.triggered[0]['prop_id'].split('.')[0]
        openmodal = False
        feedbackmessage = ''
        okay_href = None
    else:
        raise PreventUpdate

    if eventid == 'doctorprof_submitbtn' and submitbtn:
        openmodal = True

        # check if you have inputs
        inputs = [name, specialty]
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
                sqlcode = """INSERT INTO doctors(
                    doctor_name,
                    doctor_specialty,
                    doctor_delete_ind
                )
                VALUES(%s, %s, %s)
                """
                values = [name, specialty, False]
                db.modifydatabase(sqlcode, values)
                feedbackmessage = "Doctor has been added."
                okay_href = '/doctors'
            
            elif mode == 'edit':
                parsed = urlparse(search)
                doctorid = parse_qs(parsed.query)['id'][0]

                # 2. we need to update the db
                sqlcode = """UPDATE doctors
                SET
                    doctor_name = %s,
                    doctor_specialty = %s,
                    doctor_delete_ind = %s
                WHERE doctor_id = %s
                """
                to_delete = bool(removerecord)

                values = [name, specialty, to_delete, doctorid]
                db.modifydatabase(sqlcode, values)
                feedbackmessage = "Doctor has been updated."
                okay_href = '/doctors'

            else:
                raise PreventUpdate            

    elif eventid == 'doctorprof_closebtn' and closebtn:
        pass

    else:
        raise PreventUpdate

    return [openmodal, feedbackmessage, okay_href]

@app.callback(
    [
        # Our goal is to update values of these fields
        Output('doctorprof_name', 'value'),
        Output('doctorprof_specialty', 'value'),
    ],
    [
        # Our trigger is if the dcc.Store object changes its value
        # This is how you check a change in value for a dcc.Store
        Input('doctorprof_toload', 'modified_timestamp')
    ],
    [
        # We need the following to proceed
        # Note that the value of the dcc.Store object is in
        # the ‘data’ property, and not in the ‘modified_timestamp’ property
        State('doctorprof_toload', 'data'),
        State('url', 'search'),
    ]
)

def movieprofile_loadprofile(timestamp, toload, search):
    if toload: # check if toload = 1
    
        # Get movieid value from the search parameters
        parsed = urlparse(search)
        doctor_id = parse_qs(parsed.query)['id'][0]
        # Query from db
        sql = """
            SELECT doctor_name, doctor_specialty
            FROM doctors
            WHERE doctor_id = %s
        """
        values = [doctor_id]
        col = ['name', 'specialty']
        df = db.querydatafromdatabase(sql, values, col)
        name = df['name'][0]
        # Our dropdown list has the genreids as values then it will
        # display the correspoinding labels
        specialty = df['specialty'][0]
        return [name, specialty]
 
    else:
        raise 