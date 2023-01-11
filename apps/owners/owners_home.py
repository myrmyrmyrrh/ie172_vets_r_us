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
        html.H2("Pet Owners"),
        html.Hr(),
        dbc.Card(
            [
                dbc.CardHeader(html.H4("Owner Records")),
                dbc.CardBody(
                    [
                        dbc.Button("Add Owner", color="primary", href = '/owners/owners_profile?mode=add'),
                        html.Hr(),
                        html.Div(
                            [
                                html.H6("Find Owner",style={'fontweight':'bold'}),
                                html.Hr(),
                                dbc.Row(
                                    [
                                        dbc.Label("Search Owner", width=2),
                                        dbc.Col(
                                            dbc.Input(
                                                type='text',
                                                id='owner_name_filter',
                                                placeholder='Enter Owner Name'
                                            ),
                                            width=6,
                                        ),
                                    ],
                                className='mb-3',
                                ),
                                html.Div(
                                    "This will contain the table for pet owner records",
                                    id="owner_ownerlist"
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
        Output('owner_ownerlist', 'children')
    ],
    [
        Input('url', 'pathname'),
        Input('owner_name_filter', 'value'),
    ]
 )
def updateownerlist(pathname, searchterm):
    if pathname == '/owners':
        sql = """select owner_name, owner_contact, owner_id
            from owners o 
            where not owner_delete_ind
        """
        val = []
        colnames = ['Owner', 'Contact Number', 'ID']
        if searchterm:
            sql += "AND owner_name ILIKE %s"
            val += [f"%{searchterm}%"]
        
        owners = db.querydatafromdatabase(sql, val, colnames)
        if owners.shape[0]:
            buttons = []
            for ownersid in owners['ID']:
                buttons += [
                    html.Div(
                        dbc.Button('Edit/Delete', href=f"/owners/owners_profile?mode=edit&id={ownersid}",
                                    size='sm', color='warning'),
                        style={'text-align': 'center'}
                    )
                ]
            owners['Edit/Delete Record'] = buttons

            owners.drop('ID', axis=1, inplace=True)

            table = dbc.Table.from_dataframe(owners, striped = True, bordered = True, hover = True, size = 'sm')
            return [table]

        else:
            return ["There are no records that match the search term."]
    
    else:
        raise PreventUpdate
                            