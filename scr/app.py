from dash import Dash, html
Myapp = Dash(__name__)
Myapp.layout = html.Div([
    html.Div(children='Hello World')
])
server=Myapp.server

if __name__ == '__main__':
    Myapp.run(debug=True)
