from dash import dcc
from dash import html
import dash_bootstrap_components as dbc
import dash
from dash.exceptions import PreventUpdate
import pandas as pd
from dash.dependencies import Input, Output, State

from app import app

from apps import dbconnect as db

layout = html.Div(
    [
        html.H2('Veterinary Database Management System'),
        html.Hr(),
        html.Div(
            [
                html.Span("Quick Dashboard"),
                html.Br(),
                html.Br(),
                html.Span("Contact support if you need assistance!",
                style={'font-style':'italic'}),
            ]
        ),
        html.Hr(),
        dbc.Card(
            [
                dbc.CardHeader(html.H4("Top 5 Services")),
                dbc.CardBody(
                    [
                        html.Div(
                            "This will contain the table for the top services",
                            id="services_toplist"
                        )            
                    ]
                )
            ]
        ),
        html.Hr(),
        dbc.Card(
            [
                dbc.CardHeader(html.H4("Most Popular Doctor")),
                dbc.CardBody(
                    [
                        html.Div(
                            "This will contain the table for the most popular doctor",
                            id="doctors_toplist"
                        )            
                    ]
                )
            ]
        ),
        html.Hr(),
        dbc.Card(
            [
                dbc.CardHeader(html.H4("Clients with Payment Due")),
                dbc.CardBody(
                    [
                        html.Div(
                            "This will contain the table for unpaid customers",
                            id="transactions_unpaidlist"
                        )            
                    ]
                )
            ]
        )
    ]
)

@app.callback(
    [
        Output('services_toplist', 'children'),
        Output('doctors_toplist', 'children'),
        Output('transactions_unpaidlist', 'children'),
    ],
    [
        Input('url', 'pathname'),
    ]
 )
def home_loadreports(pathname):
    if pathname == '/home':
        sql = """select service_name, COUNT(s.service_id) AS customers_served
            from transactions t 
            inner join services s on t.service_id = s.service_id
            where trans_status = 'Paid'
            group by s.service_id
            order by customers_served DESC
            limit 5
        """
        values = []
        colnames = ['Service Name', 'Customers Served']

        topservices=db.querydatafromdatabase(sql,values,colnames)

        sql = """select doctor_name, COUNT(d.doctor_id) AS customers_served
            from transactions t 
            inner join doctors d on t.doctor_id = d.doctor_id
            where trans_status = 'Paid'
            group by d.doctor_id
            order by customers_served DESC
            limit 1
        """
        values = []
        colnames = ['Doctor Name', 'Customers Served']

        topdoctor=db.querydatafromdatabase(sql,values,colnames)
        
        sql = """select owner_name, owner_contact, service_name, service_price
            from transactions t 
            inner join services s on t.service_id = s.service_id
            inner join pets p on t.pet_id = p.pet_id
            inner join owners o on p.owner_id = o.owner_id
            where trans_status ='Not Paid' and trans_delete_ind = 'false'
        """
        values = []
        colnames = ['Customer Name', 'Contact Number', 'Service', 'Unpaid Amount']
        
        unpaid=db.querydatafromdatabase(sql,values,colnames)
    
        if topservices.shape:
            table1 = dbc.Table.from_dataframe(topservices, striped=True, bordered=True,
            hover=True, size='sm', style = {'textAlign': 'center'})

        if topdoctor.shape:
            table2 = dbc.Table.from_dataframe(topdoctor, striped=True, bordered=True,
            hover=True, size='sm', style = {'textAlign': 'center'})

        if unpaid.shape:
            table3 = dbc.Table.from_dataframe(unpaid, striped=True, bordered=True,
            hover=True, size='sm', style = {'textAlign': 'center'})
            
            return [table1, table2, table3]
        else:
            return ["No records to display"]
    
    else:
        raise PreventUpdate
