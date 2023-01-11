import dash
import logging

app = dash.Dash(__name__, external_stylesheets=["assets/bootstrap.css"])
app.config.suppress_callback_exceptions = True
app.css.config.serve_locally = True
app.scripts.config.serve_locally = True
app.title = 'Vet Med System'

log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)