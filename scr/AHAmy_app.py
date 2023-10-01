#my_app.py, funktioniert 01.10.2023
from dash import Dash, html
app = Dash(__name__)
app.layout = html.Div([
    html.Div(children='Hello World')
])
server=app.server

if __name__ == '__main__':
    app.run(debug=True)
