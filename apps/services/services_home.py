from dash import dcc
from dash import html
import dash_bootstrap_components as dbc
import dash
from dash.exceptions import PreventUpdate
import pandas as pd
from dash.dependencies import Input, Output, State
from apps import dbconnect as db

from app import app

layout = html.Div(
    [
        html.H2("Services"),
        html.Hr(),
        dbc.Card(
            [
                dbc.CardHeader(html.H4("Services Available")),
                dbc.CardBody(
                    [
                        dbc.Button("Add Service", color="primary", href = '/services/services_profile?mode=add'),
                        html.Hr(),
                        html.Div(
                            [
                                html.H6("Find Service",style={'fontweight':'bold'}),
                                html.Hr(),
                                dbc.Row(
                                    [
                                        dbc.Label("Search Service", width=2),
                                        dbc.Col(
                                            dbc.Input(
                                                type='text',
                                                id='service_name_filter',
                                                placeholder='Enter Service Name'
                                            ),
                                            width=6,
                                        ),
                                    ],
                                className='mb-3',
                                ),
                                html.Div(
                                    "This will contain the table for services offered.",
                                    id="service_servicelist"
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
        Output('service_servicelist', 'children')
    ],
    [
        Input('url', 'pathname'),
        Input('service_name_filter', 'value'),
    ]
 )
def updateservicelist(pathname, searchterm):
    if pathname == '/services':
        sql = """select service_name, service_desc, service_price, service_id
            from services  
            where not service_delete_ind
        """
        val = []
        colnames = ['Service', 'Description', 'Price','ID']
        if searchterm:
            sql += "AND service_name ILIKE %s"
            val += [f"%{searchterm}%"]
        
        services = db.querydatafromdatabase(sql, val, colnames)
        if services.shape[0]:
            buttons = []
            for servicesid in services['ID']:
                buttons += [
                    html.Div(
                        dbc.Button('Edit/Delete', href=f"/services/services_profile?mode=edit&id={servicesid}",
                                    size='sm', color='warning'),
                        style={'text-align': 'center'}
                    )
                ]
            services['Edit/Delete Record'] = buttons

            services.drop('ID', axis=1, inplace=True)

            table = dbc.Table.from_dataframe(services, striped = True, bordered = True, hover = True, size = 'sm')
            return [table]

        else:
            return ["There are no records that match the search term."]
    
    else:
        raise PreventUpdate
                            