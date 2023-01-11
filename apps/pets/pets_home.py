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
        html.H2("Pets"),
        html.Hr(),
        dbc.Card(
            [
                dbc.CardHeader(html.H4("Pet Records")),
                dbc.CardBody(
                    [
                        dbc.Button("Add Pet", color="primary", href = '/pets/pets_profile?mode=add'),
                        html.Hr(),
                        html.Div(
                            [
                                html.H6("Find Pet",style={'fontweight':'bold'}),
                                html.Hr(),
                                dbc.Row(
                                    [
                                        dbc.Label("Search Pet", width=2),
                                        dbc.Col(
                                            dbc.Input(
                                                type='text',
                                                id='pet_name_filter',
                                                placeholder='Enter Pet Name'
                                            ),
                                            width=6,
                                        ),
                                    ],
                                className='mb-3',
                                ),
                                html.Div(
                                    "This will contain the table for pet records",
                                    id="pet_petlist"
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
        Output('pet_petlist', 'children')
    ],
    [
        Input('url', 'pathname'),
        Input('pet_name_filter', 'value'),
    ]
 )
def updatepetlist(pathname, searchterm):
    if pathname == '/pets':
        sql = """select pet_name, owner_name, pet_type, pet_dob, pet_id
            from pets p 
                inner join owners o on p.owner_id = o.owner_id
            where not pet_delete_ind
        """
        val = []
        colnames = ['Pet Name', 'Owner', 'Type', 'Date of Birth', 'ID']
        if searchterm:
            sql += "AND pet_name ILIKE %s"
            val += [f"%{searchterm}%"]
        
        pets = db.querydatafromdatabase(sql, val, colnames)
        if pets.shape[0]:
            buttons = []
            for petsid in pets['ID']:
                buttons += [
                    html.Div(
                        dbc.Button('Edit/Delete', href=f"/pets/pets_profile?mode=edit&id={petsid}",
                                    size='sm', color='warning'),
                        style={'text-align': 'center'}
                    )
                ]
            pets['Edit/Delete Record'] = buttons

            pets.drop('ID', axis=1, inplace=True)

            table = dbc.Table.from_dataframe(pets, striped = True, bordered = True, hover = True, size = 'sm')
            return [table]

        else:
            return ["There are no records that match the search term."]
    
    else:
        raise PreventUpdate
                            