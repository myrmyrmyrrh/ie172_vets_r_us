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
            dcc.Store(id='serviceprof_toload', storage_type='memory', data=0),
            ]
        ),
        html.H2("Service Details"),
        html.Hr(),
        dbc.Row(
            [
                dbc.Label("Name", width=2),
                dbc.Col(
                    dbc.Input(
                        type="text", id="serviceprof_name", placeholder="Enter service name"
                    ),
                    width=6,
                ),
            ],
            className="mb-3",
        ),
        dbc.Row(
            [
                dbc.Label("Service Description", width=2),
                dbc.Col(
                    dbc.Input(
                        type="text", id="serviceprof_desc", placeholder="Enter service description"
                    ),
                    width=8,
                ),
            ],
            className="mb-3",
        ),
        dbc.Row(
            [
                dbc.Label("Service Price", width=2),
                dbc.Col(
                    dbc.Input(
                        type="number", id="serviceprof_price", placeholder="Enter service price"
                    ),
                    width=2,
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
                            id='serviceprof_removerecord',
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
            id = 'serviceprof_removerecord_div'
        ),
        html.Hr(),
        dbc.Button('Submit', color="success", id='serviceprof_submitbtn', n_clicks=0),
        dbc.Modal(
            [
                dbc.ModalHeader("Saving Progress"),
                dbc.ModalBody("tempmessage", id='serviceprof_feedback_message'),
                dbc.ModalFooter(
                    dbc.Button(
                        "Okay", id="serviceprof_closebtn", className="ms-auto", n_clicks=0
                    )
                ),
            ],
            id="serviceprof_modal",
            is_open=False
        ),
    ],
)
@app.callback(
    [
        Output('serviceprof_toload', 'data'),
        Output('serviceprof_removerecord_div', 'style')
    ],
    [
        Input('url', 'pathname'),
    ],
    [
        State('url', 'search')
    ]
)

def serviceprof_editprocess(pathname, search):
    if pathname == '/services/services_profile':
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
        Output('serviceprof_modal', 'is_open'),
        Output('serviceprof_feedback_message', 'children'),
        Output('serviceprof_closebtn', 'href')
    ],
    [
        Input('serviceprof_submitbtn', 'n_clicks'),
        Input('serviceprof_closebtn', 'n_clicks')
    ],
    [
        State('serviceprof_name','value'),
        State('serviceprof_desc', 'value'),
        State('serviceprof_price', 'value'),
        State('url', 'search'),
        State('serviceprof_removerecord', 'value')
    ]
)

def serviceprof_submitprocess(submitbtn, closebtn,
                                name, desc, price,
                                search, removerecord):
    ctx = dash.callback_context
    if ctx.triggered:
        eventid = ctx.triggered[0]['prop_id'].split('.')[0]
        openmodal = False
        feedbackmessage = ''
        okay_href = None
        if eventid == "serviceprof_submitbtn" and submitbtn:
            openmodal = True
            inputs = [
                name,
                desc,
                price
            ]
            if not all(inputs):
                feedbackmessage = "Please supply all inputs."
            elif len(name)>256:
                feedbackmessage = "Title is too long (length=256)."

            else:
                parsed = urlparse(search)
                mode = parse_qs(parsed.query)['mode'][0]
                if mode == 'add': 
                    sqlcode = """ INSERT INTO services(
                        service_name,
                        service_desc,
                        service_price,
                        service_delete_ind
                    )
                    VALUES (%s, %s, %s, %s)
                    """
                    values = [name, desc, price, False]
                    db.modifydatabase(sqlcode, values)
                    feedbackmessage = "Service has been saved."
                    okay_href = '/services'

                elif mode == 'edit':
                    parsed = urlparse(search)
                    serviceid = parse_qs(parsed.query)['id'][0]
                    sqlcode = """UPDATE services
                    SET
                        service_name = %s,
                        service_desc = %s,
                        service_price = %s,
                        service_delete_ind = %s
                    WHERE
                        service_id = %s
                    """

                    to_delete = bool(removerecord)

                    values = [name,desc, price, to_delete, serviceid]
                    db.modifydatabase(sqlcode, values)
                    feedbackmessage = "service has been updated."
                    okay_href = '/services'

                else:
                    raise PreventUpdate

        elif eventid == 'serviceprof_closebtn' and closebtn:
            pass

        else:
            raise PreventUpdate

        return [openmodal, feedbackmessage, okay_href]


@app.callback(
    [
        Output('serviceprof_name', 'value'),
        Output('serviceprof_desc', 'value'),
        Output('serviceprof_price', 'value'),

    ],
    [
        Input('serviceprof_toload', 'modified_timestamp')
    ],
    [
        State('serviceprof_toload', 'data'),
        State('url', 'search')
    ]
)

def loadservicedetails(timestamp, to_load, search):
    if to_load == 1:
        sql = """SELECT service_name, service_desc, service_price
        FROM services
        WHERE service_id = %s
        """

        parsed = urlparse(search)
        serviceid = parse_qs(parsed.query)['id'][0]

        val = [serviceid]
        colnames = ['name','desc', 'price']

        df = db.querydatafromdatabase(sql, val, colnames)

        name = df['name'][0]
        desc = df['desc'][0]
        price = df['price'][0]

        return [name, desc, price]

    else:
        raise PreventUpdate

        