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
            dcc.Store(id='transnew_toload', storage_type='memory', data=0),
            ]
        ),
        html.H2("Transaction Details"),
        html.Hr(),
        dbc.Row(
            [
                dbc.Label("Transaction Date", width=2),
                dbc.Col(
                    dbc.Input(
                        type="date", id="transnew_date", placeholder="Enter date"
                    ),
                    width=6,
                ),
            ],
            className="mb-3",
        ),
       dbc.Row(
            [
                dbc.Label("Pet", width=2),
                dbc.Col(
                    html.Div(
                        dcc.Dropdown(
                            id='transnew_pet',
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
                dbc.Label("Doctor-In-Charge", width=2),
                dbc.Col(
                    html.Div(
                        dcc.Dropdown(
                            id='transnew_doctor',
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
                dbc.Label("Service Offered", width=2),
                dbc.Col(
                    html.Div(
                        dcc.Dropdown(
                            id='transnew_service',
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
                dbc.Label("Inventory Used", width=2),
                dbc.Col(
                    html.Div(
                        dcc.Dropdown(
                            id='transnew_inv',
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
                dbc.Label("Quantity Used", width=2),
                dbc.Col(
                    dbc.Input(
                        type="number", id="transnew_qtyused", placeholder="", min=1
                    ),
                    width=2,
                ),
            ],
            className="mb-3",
        ),
        dbc.Row(
            [
                dbc.Label("Service Price", width=2),
                dbc.Col(
                    id='transnew_paid',
                    width=6,
                ),
            ],
            className="mb-3",
        ),
        dbc.Row(
            [
                dbc.Label("Payment Status", width=2),
                dbc.Col(
                    html.Div(
                        dcc.Dropdown(
                            id='transnew_status',
                            options=['Paid', 'Not Paid'],
                            value=False,
                            clearable=False,
                            searchable=False,
                        ),
                        className="dash-bootstrap"
                    ),
                    width=3,
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
                            id='transnew_removerecord',
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
            id = 'transnew_removerecord_div'
        ),
        html.Hr(),
        dbc.Button('Submit', color="success", id='transnew_submitbtn', n_clicks=0),
        dbc.Modal(
            [
                dbc.ModalHeader("Saving Progress"),
                dbc.ModalBody("tempmessage", id='transnew_feedback_message'),
                dbc.ModalFooter(
                    dbc.Button(
                        "Okay", id="transnew_closebtn", className="ms-auto", n_clicks=0
                    )
                ),
            ],
            id="transnew_modal",
            is_open=False
        ),
    ],
)

@app.callback(
    [
        Output('transnew_pet','options')
    ],
    [
        Input('url','pathname')
    ]
)
def transpetdropdown(pathname):
    if pathname=='/transactions/trans_new':
        sql = """
        SELECT pet_name as label, pet_id as value
        FROM pets
        WHERE pet_delete_ind = False
        """
        values = []
        cols = ['label', 'value']
        df = db.querydatafromdatabase(sql, values, cols)
     
        pet_options = df.to_dict('records')
        return [pet_options]

    else:
        raise PreventUpdate

    
@app.callback(
    [
        Output('transnew_doctor','options')
    ],
    [
        Input('url','pathname')
    ]
)
def transdoctordropdown(pathname):
    if pathname=='/transactions/trans_new':
        sql = """
        SELECT doctor_name as label, doctor_id as value
        FROM doctors
        WHERE doctor_delete_ind = False
        """
        values = []
        cols = ['label', 'value']
        df = db.querydatafromdatabase(sql, values, cols)
     
        doctor_options = df.to_dict('records')
        return [doctor_options]

    else:
        raise PreventUpdate


@app.callback(
    [
        Output('transnew_service','options'),
    ],
    [
        Input('url','pathname')
    ]
)
def transservicedropdown(pathname):
    if pathname=='/transactions/trans_new':
        sql = """
        SELECT service_name as label, service_id as value
        FROM services
        WHERE service_delete_ind = False
        """
        values = []
        cols = ['label', 'value']
        df = db.querydatafromdatabase(sql, values, cols)
     
        service_options = df.to_dict('records')
        return [service_options]

    else:
        raise PreventUpdate

@app.callback(
    [
        Output('transnew_paid','children'),
    ],
    [
        Input('transnew_service','value')
    ]
)
def transserviceprice(serviceid):
    if serviceid:
        sql = """
        SELECT service_price as price
        FROM services
        WHERE service_id = %s
        """
        values = [serviceid]
        cols = ['price']
        df = db.querydatafromdatabase(sql, values, cols)

        price = df['price'][0]

        return [price]

    else:
        raise PreventUpdate

@app.callback(
    [
        Output('transnew_inv','options')
    ],
    [
        Input('url','pathname')
    ]
)
def transinventorydropdown(pathname):
    if pathname=='/transactions/trans_new':
        sql = """
        SELECT inv_name as label, inv_id as value
        FROM inventory
        WHERE inv_delete_ind = False AND inv_qty > 0
        """
        values = []
        cols = ['label', 'value']
        df = db.querydatafromdatabase(sql, values, cols)
     
        inv_options = df.to_dict('records')
        return [inv_options]

    else:
        raise PreventUpdate

@app.callback(
    [
        Output('transnew_toload', 'data'),
        Output('transnew_removerecord_div', 'style')
    ],
    [
        Input('url', 'pathname'),
    ],
    [
        State('url', 'search')
    ]
)

def transnew_editprocess(pathname, search):
    if pathname == '/transactions/trans_new':
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
        Output('transnew_modal', 'is_open'),
        Output('transnew_feedback_message', 'children'),
        Output('transnew_closebtn', 'href')
    ],
    [
        Input('transnew_submitbtn', 'n_clicks'),
        Input('transnew_closebtn', 'n_clicks')
    ],
    [
        State('transnew_date','value'),
        State('transnew_pet', 'value'),
        State('transnew_doctor', 'value'),
        State('transnew_service', 'value'),
        State('transnew_inv', 'value'),
        State('transnew_qtyused', 'value'),
        State('transnew_paid', 'children'),
        State('transnew_status', 'value'),
        State('url', 'search'),
        State('transnew_removerecord', 'value')
    ]
)

def transnew_submitprocess(
            submitbtn, closebtn,date, pet, doctor, service, inv, qty, paid, status, search, removerecord
                        ):
    ctx = dash.callback_context
    if ctx.triggered:
        eventid = ctx.triggered[0]['prop_id'].split('.')[0]
        openmodal = False
        feedbackmessage = ''
        okay_href = None
        if eventid == "transnew_submitbtn" and submitbtn:
            openmodal = True
            inputs = [
                date,
                pet,
                doctor,
                service,
                inv,
                qty,
                paid,
                status
            ]
            if not date:
                feedbackmessage = "Please supply date."
            elif not pet:
                feedbackmessage = "Please supply pet."
            elif not doctor:
                feedbackmessage = "Please supply doctor."
            elif not service:
                feedbackmessage = "Please supply service."
            elif not inv:
                feedbackmessage = "Please supply inv item."
            elif not qty:
                feedbackmessage = "Please supply inv qty."
            # elif not paid:
            #     feedbackmessage = "Please supply amount paid."
            elif not status:
                feedbackmessage = "Please supply payment status."
            else:
                parsed = urlparse(search)
                mode = parse_qs(parsed.query)['mode'][0]
                if mode == 'add': 
                    sqlcode = """ INSERT INTO transactions(
                        trans_date,
                        pet_id,
                        doctor_id,
                        service_id,
                        inv_id,
                        inv_qty_used,
                        trans_paid,
                        trans_status,
                        trans_delete_ind
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s);

                    UPDATE inventory
                    SET
                        inv_qty = inv_qty - %s
                    WHERE
                        inventory.inv_id = %s;
                    """
                    values =[
                        date,pet,doctor,service,inv,qty,paid,status,False,
                        qty,inv
                    ]
                    db.modifydatabase(sqlcode, values)
                
                    feedbackmessage = "Transaction has been saved."
                    okay_href = '/transactions'

                elif mode == 'edit':
                    parsed = urlparse(search)
                    transid = parse_qs(parsed.query)['id'][0]

                    to_delete = bool(removerecord)
                    if(to_delete):
                        qty = 0

                    sqlcode = """
                    UPDATE inventory
                    SET 
                        inv_qty = inv_qty - (%s - inv_qty_used)
                    FROM transactions
                    WHERE trans_id=%s and inventory.inv_id=%s;

                    UPDATE transactions
                    SET
                        trans_date = %s,
                        pet_id = %s,
                        doctor_id = %s,
                        service_id = %s,
                        inv_id = %s,
                        inv_qty_used = %s,
                        trans_paid = %s,
                        trans_status = %s,
                        trans_delete_ind = %s
                    WHERE
                        trans_id = %s;                
                    """

                    values = [
                        qty,transid,inv,
                        date,pet,doctor,service,inv,qty,paid,status, to_delete, transid
                        ]
                    db.modifydatabase(sqlcode, values)
                    feedbackmessage = "Transaction has been updated."
                    okay_href = '/transactions'

                else:
                    raise PreventUpdate

        elif eventid == 'transnew_closebtn' and closebtn:
            pass

        else:
            raise PreventUpdate

        return [openmodal, feedbackmessage, okay_href]

    else:
        raise PreventUpdate   
        

@app.callback(
    [
        Output('transnew_date','value'),
        Output('transnew_pet', 'value'),
        Output('transnew_doctor', 'value'),
        Output('transnew_service', 'value'),
        Output('transnew_inv', 'value'),
        Output('transnew_qtyused', 'value'),
        Output('transnew_paid', 'value'),
        Output('transnew_status', 'value'),
    ],
    [
        Input('transnew_toload', 'modified_timestamp')
    ],
    [
        State('transnew_toload', 'data'),
        State('url', 'search')
    ]
)

def loadtransdetails(timestamp, to_load, search):
    if to_load == 1:
        sql = """SELECT trans_date,
                        pet_id,
                        doctor_id,
                        service_id,
                        inv_id,
                        inv_qty_used,
                        trans_paid,
                        trans_status
        FROM transactions
        WHERE trans_id = %s
        """

        parsed = urlparse(search)
        transid = parse_qs(parsed.query)['id'][0]

        val = [transid]
        colnames = ['Date', 'Pet', 'Doctor-In-Charge','Service Availed','Inventory Used','Inventory Quantity Used','Amount Paid','Status']

        df = db.querydatafromdatabase(sql, val, colnames)

        date = df['Date'][0]
        pet = df['Pet'][0]
        doctor = df['Doctor-In-Charge'][0]
        service = df['Service Availed'][0]
        inv = df['Inventory Used'][0]
        qty = df['Inventory Quantity Used'][0]
        paid = df['Amount Paid'][0]
        status = df['Status'][0]

        return [date,pet,doctor,service,inv,qty,paid,status]

    else:
        raise PreventUpdate