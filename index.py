from dash import dcc
from dash import html
import dash_bootstrap_components as dbc
import dash
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate

import webbrowser

from app import app
from apps import commonmodules as cm
from apps import home
from apps.pets import pets_home, pets_profile
from apps.owners import owners_home, owners_profile
from apps.transactions import trans_home, trans_new
from apps.services import services_home, services_profile
from apps.doctors import doctor_profile, doctors_home
from apps import login, signup
from apps.inventory import inventory_profile, inventory_home
from apps.reports import reports_home

CONTENT_STYLE = {
    "margin-left": "1em",
    "margin-right": "1em",
    "padding": "1em 1em",
}

server = app.server

app.layout = html.Div(
    [
        
        dcc.Location(id='url', refresh=True),
        
        
        
        dcc.Store(id='sessionlogout', data=False, storage_type='session'),
        
        
        dcc.Store(id='currentuserid', data=0, storage_type='session'),
        
        
        dcc.Store(id='currentrole', data=-1, storage_type='session'),
        
        html.Div(
            cm.navbar,
            id='navbar_div'
        ),
        
        
        html.Div(id='page-content', style=CONTENT_STYLE),
    ]
)



@app.callback(
    [
        Output('page-content', 'children'),
        Output('navbar_div', 'style'),
        Output('currentuserid', 'clear_data'),
    ],
    [
        Input('url', 'pathname'),
    ],
    [
        State('sessionlogout', 'data'),
        State('currentuserid', 'data'),
    ]
)
def displaypage(pathname, sessionlogout, currentuserid):
    
    
    ctx = dash.callback_context
    if ctx.triggered:
       
        eventid = ctx.triggered[0]['prop_id'].split('.')[0]
    else:
        raise PreventUpdate
    
    if eventid == 'url':
        print(currentuserid)
        if not currentuserid:
            if pathname in ['/']:
                returnlayout = login.layout
            elif pathname == '/signup':
                returnlayout = signup.layout
            else:
                returnlayout = '404: request not found'
            
        else:
            if pathname == '/logout':
                returnlayout = login.layout
                sessionlogout = True
                
            elif pathname in ['/', '/home']:
                returnlayout = home.layout
                
            elif pathname == '/transactions':
                returnlayout = trans_home.layout
            elif pathname == '/transactions/trans_new':
                    returnlayout = trans_new.layout
            elif pathname == '/pets':
                    returnlayout = pets_home.layout
            elif pathname == '/pets/pets_profile':
                    returnlayout = pets_profile.layout
            elif pathname == '/owners':  
                    returnlayout = owners_home.layout
            elif pathname == '/owners/owners_profile':  
                    returnlayout = owners_profile.layout
            elif pathname == '/doctors':  
                    returnlayout = doctors_home.layout
            elif pathname == '/doctors/doctor_profile':  
                    returnlayout = doctor_profile.layout
            elif pathname == '/services':  
                    returnlayout = services_home.layout
            elif pathname == '/services/services_profile':  
                    returnlayout = services_profile.layout
            elif pathname == '/inventory':  
                    returnlayout = inventory_home.layout
            elif pathname == '/inventory/inventory_profile':  
                    returnlayout = inventory_profile.layout
            elif pathname == '/reports':  
                    returnlayout = reports_home.layout
            else:
                raise PreventUpdate
    
    navbar_div = {'display': 'unset'}
    return [returnlayout, navbar_div, sessionlogout]



if __name__ == '__main__':
    webbrowser.open('http://127.0.0.1:8050/', new=0, autoraise=True)
    app.run_server(debug=False)