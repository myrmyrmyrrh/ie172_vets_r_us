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
        html.H2("Doctors"),
        html.Hr(),
        dbc.Card(
            [
                dbc.CardHeader(html.H4("Doctor Catalog")),
                dbc.CardBody(
                    [ 
                        dbc.Button("Add Veterinarian", color="primary", href = '/doctors/doctor_profile?mode=add'),
                        html.Hr(),
                        html.Div(
                            [
                                html.H6("Find Doctor",style={'fontweight':'bold'}),
                                html.Hr(),
                                dbc.Row(
                                    [
                                        dbc.Label("Search Doctor", width=2),
                                        dbc.Col(
                                            dbc.Input(
                                                type='text',
                                                id='doctor_name_filter',
                                                placeholder='Enter Doctor Name'
                                            ),
                                            width=6,
                                        ),
                                    ],
                                className='mb-3',
                                ),
                                html.Div(
                                    "This will contain the table for doctor catalog",
                                    id="doctors_doctorslist"
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
        Output('doctors_doctorslist', 'children')
    ],
    [
        Input('url', 'pathname'),
        Input('doctor_name_filter', 'value'),
    ]
 )
def doctorhome_loaddoctorlist(pathname, searchterm):
    if pathname == '/doctors':
        sql = """select doctor_name, doctor_specialty, doctor_id
            from doctors
            where not doctor_delete_ind
        """
        values = []
        colnames = ['Doctor Name', 'Specialty', 'ID']

        if searchterm:
            sql += " AND doctor_name ILIKE %s"
            values += [f"%{searchterm}%"]

        doctors=db.querydatafromdatabase(sql,values,colnames)
    
        if doctors.shape:
            buttons = []
            for doctor_id in doctors['ID']:
                buttons += [
                html.Div(
                    dbc.Button('Edit/Delete',
                    href=f'doctors/doctor_profile?mode=edit&id={doctor_id}',
                        size='sm', color='warning'),
                        style={'text-align': 'center'}
                )   
            ]

            doctors['Action'] = buttons

            # remove the column ID before turning into a table 

            doctors.drop('ID', axis=1, inplace=True)
            table = dbc.Table.from_dataframe(doctors, striped=True, bordered=True,
            hover=True, size='sm')

            return [table]
        else:
            return ["No records to display"]
    
    else:
        raise PreventUpdate