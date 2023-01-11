from dash import dcc
from dash import html
import dash_bootstrap_components as dbc
import dash
from dash.exceptions import PreventUpdate
from dash.dependencies import Input, Output, State
import pandas as pd

from app import app

from apps import dbconnect as db

layout = html.Div(
    [
        html.H2("Transactions"),
        html.Hr(),
        dbc.Card(
            [
                dbc.CardHeader(html.H4("Transaction List")),
                dbc.CardBody(
                    [
                        dbc.Button("New Transaction", color="primary", href = '/transactions/trans_new?mode=add'),
                        html.Hr(),
                        html.Div(
                            [
                                html.H6("Find Transaction",style={'fontweight':'bold'}),
                                html.Hr(),
                                dbc.Row(
                                    [
                                        dbc.Label("Search Transaction Date", width=2),
                                        dbc.Col(
                                            dbc.Input(
                                                type="date", id="trans_date_filter", placeholder="Enter date"
                                            ),
                                            width=6,
                                        ),
                                    ],
                                className='mb-3',
                                ),
                                html.Div(
                                    "This will contain the table for transactions",
                                    id="transactions_translist"
                                )
                            ]
                        )
                    ]
                )
            ]
        )
    ]
)
@app.callback(
    [
        Output('transactions_translist', 'children')
    ],
    [
        Input('url', 'pathname'),
        Input('trans_date_filter', 'value'),
    ]
 )
def updatetranslist(pathname, searchterm):
    if pathname == '/transactions':
        sql = """SELECT trans_date, p.pet_name, d.doctor_name, s.service_name, i.inv_name, inv_qty_used, trans_paid, trans_status, trans_id
            from transactions t
            inner join pets p on t.pet_id = p.pet_id
            inner join doctors d on t.doctor_id = d.doctor_id
            inner join services s on t.service_id = s.service_id
            inner join inventory i on t.inv_id = i.inv_id
            where not t.trans_delete_ind
        """
        val = []
        colnames = ['Date', 'Pet', 'Doctor-In-Charge','Service Availed','Inventory Used','Inventory Quantity Used','Amount Paid','Status', 'ID']
        if searchterm:
            sql += "AND CAST(trans_date AS text) ILIKE %s"
            val += [f"%{searchterm}%"]
        
        transactions = db.querydatafromdatabase(sql, val, colnames)
        if transactions.shape[0]:
            buttons = []
            for transid in transactions['ID']:
                buttons += [
                    html.Div(
                        dbc.Button('Edit/Delete', href=f"/transactions/trans_new?mode=edit&id={transid}",
                                    size='sm', color='warning'),
                        style={'text-align': 'center'}
                    )
                ]
            transactions['Edit/Delete Record'] = buttons

            transactions.drop('ID', axis=1, inplace=True)

            table = dbc.Table.from_dataframe(transactions, striped = True, bordered = True, hover = True, size = 'sm')
            return [table]

        else:
            return ["There are no records that match the search term."]
    
    else:
        raise PreventUpdate