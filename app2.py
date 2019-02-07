"""
Główny moduł aplikacji
"""

import dash
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html

import plotly.graph_objs as go

from tools2 import load_data, parse_apacz
from network2 import draw_network, authors_table


APP = dash.Dash(__name__, external_stylesheets=['style.css'])

# parse_apacz('data', cache=True, json_filename='apacz.json')
APACZ, UNITS = load_data('data/apacz.json')

APP.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>Analiza współautorstwa - Jacek Hajto</title>
        <link rel="icon" type="image/x-icon" href="/assets/favicons/favicon.ico" />
        <link href="https://fonts.googleapis.com/css?family=Roboto" rel="stylesheet"> 
        <link href="css/bootstrap.min.css" rel="stylesheet">
        {%css%}
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
        </footer>
    </body>
</html>
'''

APP.layout = html.Div(
    html.Div([
        html.Div([
            html.Div([
                html.Div([
                    html.H1("Analiza współautorstwa"),
                    ], className='title-bar'),
                html.Div([
                    html.P(["Poniżej zaprezentowano graficzną prezentację powiązań pomiedzy "
                            "autorami publikacji pracowników Wydziału Matematyki i Informatyki "
                            "UJ. Dane pochodzą ze strony: ",
                            html.A("https://apacz.matinf.uj.edu.pl",
                                   href='https://apacz.matinf.uj.edu.pl/jednostki/1-wydzial-'
                                   'matematyki-i-informatyki-uj', target="_blank"),
                            "."]),
                    html.P("Po prawej stronie można wybrać różne opcje dotyczące filtrowanai "
                           "wyników oraz sposobu prezentacji wyników."),
                    ],
                         className='content'),
                ],
                     className='twelve columns')
            ], className='row'),

        html.Div([
            html.Div([
                html.Div([
                    html.H3("Graf współautorstwa"),
                    ], className='title-bar'),
                dcc.Graph(
                    id='network-graph',
                    style={'height': 700},
                    ),
                ], className='nine columns'),
            html.Div([
                html.Div([
                    html.H3("Opcje"),
                    ], className='title-bar'),
                html.Div([
                    html.P(["Wybór autorów do przedstawienia na wykresie (",
                            html.I("wszyscy współautorzy również zostaną ujęci na wykresie"),
                            ").",]),
                    dcc.Dropdown(
                        id='filter_authors',
                        options=[{'label': name, 'value': name} for name in APACZ['authors']],
                        value=[],
                        multi=True,
                        placeholder="Wybierz autorów",),
                    ],
                         className='content'),
                html.Div([
                    html.P(["Wybór jednostek do której autor jest przypisany (",
                            html.I("wykres będzie zawierał tylko osoby spełniające to kryterium"),
                            ").", ]),
                    dcc.Dropdown(
                        id='filter_units',
                        options=[{'label': name, 'value': name} for name in UNITS],
                        value=[],
                        multi=True,
                        placeholder="Wybierz jednostki",),
                    ],
                         className='content'),
                html.Div([
                    html.Button('Aktualizuj wykres', id='load_data_button', className='button'),
                    ],
                         className='content'),
                ],
                     className='three columns'),
            ], className='row'),

        html.Div([
            html.Div([
                html.Div([
                    html.H3("Szczegóły"),
                    ], className='title-bar'),
                html.Div("UWAGA: Proszę wybrać przynajmniej jednego autora lub jednostkę.",
                         id='data-table',
                         className='tbl',
                         )
                ], className='twelve columns'),
            ], className='row'),

        ], className='ten columns offset-by-one')
    )


@APP.callback(
    Output('network-graph', 'figure'),
    [Input('load_data_button', 'n_clicks'), ],
    [State('filter_authors', 'value'), State('filter_units', 'value')])
def update_figure(n_clicks, authors=None, units=None):
    """	Aktualizuje graf  filtrując jednocześnie autorów i jednostki w jakich pracują"""

    if n_clicks is not None:
        network_graph = draw_network(data=APACZ, authors=authors, units=units)
    else:
        network_graph = go.Figure(
                        data=[
                            go.Scatter( # edges
                                x=[0.5, 2, 5,],
                                y=[2, 0, 5,],
                                line=dict(width=5, color='#62ed40'),
                                hoverinfo='none',
                                mode='lines',
                                ),
                            go.Scatter( # nodes
                                x=[0.5, 2, 5,],
                                y=[2, 0, 5,],
                                mode='markers',
                                hoverinfo='text',
                                marker=dict(
                                    color=['red', 'black', 'black'],
                                    size=[25, 40, 20],
                                    line=dict(width=2))),
                            ],
                        layout=go.Layout(
                            showlegend=False,
                            yaxis=dict(scaleanchor="x", scaleratio=1, showgrid=False,
                                       zeroline=False, showticklabels=False),
                            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                        )
        )
    return network_graph


@APP.callback(
    Output('data-table', 'children'),
    [Input('load_data_button', 'n_clicks'), ],
    [State('filter_authors', 'value'),
     State('filter_units', 'value'),
     State('data-table', 'children')])
def update_table(n_clicks, authors, units, old_children):
    """Aktualizuje tabelę poniżej wykresu"""

    if n_clicks is not None:
        children = authors_table(data=APACZ, authors=authors, units=units)
    else:
        children = old_children
    return children


if __name__ == '__main__':
    APP.run_server(debug=True)
