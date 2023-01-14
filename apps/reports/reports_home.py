from dash import dcc
from dash import html
import dash_bootstrap_components as dbc
import dash
from dash.exceptions import PreventUpdate
import plotly.express as px
import pandas as pd
from dash.dependencies import Input, Output, State

from apps import dbconnect as db
from app import app


layout = html.Div(
    [
        html.H2("Monthly Sales"),
        dcc.Graph(
            id='sales_graph',
        ),

    ]
)

@app.callback(
    [
        Output('sales_graph', 'figure'),
    ],
    [
        Input('url', 'pathname'),
    ]
 )
def home_loadreports(pathname):
    if pathname == '/reports':
        sql = """select extract(month from trans_date), to_char(trans_date, 'Mon'), count(to_char(trans_date, 'Mon')) as "sales"
        from transactions
        where trans_status = 'Paid'
        group by extract(month from trans_date), to_char(trans_date, 'Mon')
        order by extract(month from trans_date) ASC
        """
        values = []
        colnames = ["MM", "Month", "Transactions"]

        sales = db.querydatafromdatabase(sql,values,colnames)

        sales_figure = px.bar(sales, x="Month", y="Transactions", color="Month", barmode="group",color_discrete_sequence=["#900C3F", "#900C3F", "#900C3F", "#900C3F", "#900C3F", "#900C3F", "#900C3F", "#900C3F", "#900C3F", "#900C3F","#900C3F", "#900C3F"] )

        return [sales_figure]

    else:
        raise PreventUpdate
