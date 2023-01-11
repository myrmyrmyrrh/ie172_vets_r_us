from dash import dcc
from dash import html
import dash_bootstrap_components as dbc
import dash
from dash.exceptions import PreventUpdate
import pandas as pd

from app import app

navlink_style = {
    'color': '#fff',
    'margin-right': '1em'
}
navbar = dbc.Navbar(
    [
        html.A(
            dbc.NavbarBrand("VETS r US", className="ml-2", 
            style={'margin-right': '2em','margin-left': '1em', 'font-size':'3em'}),
            href="/home",
        ),
        dbc.NavLink("Home", href="/home", style=navlink_style),
        dbc.NavLink("Transactions", href="/transactions", style=navlink_style),
        dbc.NavLink("Owners", href="/owners", style=navlink_style),
        dbc.NavLink("Pets", href="/pets", style=navlink_style),
        dbc.NavLink("Doctors", href="/doctors", style=navlink_style),
        dbc.NavLink("Services", href="/services", style=navlink_style),
        dbc.NavLink("Inventory", href="/inventory", style=navlink_style),
        dbc.NavLink("Reports", href="/reports", style=navlink_style),
        dbc.NavLink("Logout", href="/logout", style=navlink_style),
    ],
    dark=True,
    color='blue'
)


    