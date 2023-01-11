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
        html.H2("Inventory"),
        html.Hr(),
        dbc.Card(
            [
                dbc.CardHeader(html.H4("Inventory Catalog")),
                dbc.CardBody(
                    [ 
                        dbc.Button("Add Inventory Items", color="primary", href = '/inventory/inventory_profile?mode=add'),
                        html.Hr(),
                        html.Div(
                            [
                                html.H6("Find Inventory Item",style={'fontweight':'bold'}),
                                html.Hr(),
                                dbc.Row(
                                    [
                                        dbc.Label("Search Inventory", width=2),
                                        dbc.Col(
                                            dbc.Input(
                                                type='text',
                                                id='inv_name_filter',
                                                placeholder='Enter Inventory Name'
                                            ),
                                            width=6,
                                        ),
                                    ],
                                className='mb-3',
                                ),
                                html.Div(
                                    "This will contain the table for inventory catalog",
                                    id="inv_inventorylist"
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
        Output('inv_inventorylist', 'children')
    ],
    [
        Input('url', 'pathname'),
        Input('inv_name_filter', 'value'),
    ]
 )
def invhome_loadinventorylist(pathname, searchterm):
    if pathname == '/inventory':
        sql = """select inv_name, inv_qty, inv_id
            from inventory
            where not inv_delete_ind
        """
        values = []
        colnames = ['Inventory Name', 'Quantity', 'ID']

        if searchterm:
            sql += " AND inv_name ILIKE %s"
            values += [f"%{searchterm}%"]

        inv=db.querydatafromdatabase(sql,values,colnames)
        inv.loc[inv['Quantity'] == 0, 'Quantity'] = "Out of stock"
        
        if inv.shape:
            buttons = []
            for inv_id in inv['ID']:
                buttons += [
                html.Div(
                    dbc.Button('Edit/Delete',
                    href=f'inventory/inventory_profile?mode=edit&id={inv_id}',
                        size='sm', color='warning'),
                        style={'text-align': 'center'}
                )   
            ]

            inv['Action'] = buttons


            inv.drop('ID', axis=1, inplace=True)
            table = dbc.Table.from_dataframe(inv, striped=True, bordered=True,
            hover=True, size='sm')

            return [table]
        else:
            return ["No records to display"]
    
    else:
        raise PreventUpdate