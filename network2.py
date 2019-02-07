"""Moduł zawiera funkcje do rysowania grafu i tworzenia tabeli"""

from math import sqrt
from itertools import combinations
import networkx as nx
import plotly
import plotly.graph_objs as go
import dash_table


def draw_network(data=None, authors=None, units=None):
    """Funkcja na podstawie danych oraz podanych ograniczeń w postacji autorów i jednostek
    do których są przyporządkowani rysuje graf połączeń."""

    print('Creating graph...')
    authors_graph = nx.Graph()

    papers = []
    for author, values in  data['authors'].items():
        if (not authors or author in authors) and (not units or (set(values['units'])&set(units))):
            authors_graph.add_node(author, n_publications=len(values['papers']))
            papers.extend(values['papers'])

    for paper in papers:
        coauthors = data['papers'][paper]
        new_coauthors = []
        for coa in coauthors:
            if not units or (set(data['authors'][coa]['units']) & set(units)):
                new_coauthors.append(coa)

        ed = combinations(new_coauthors, 2)
        for pair in ed:
            n_common_papers = len(set(data['authors'][pair[0]]['papers']) &
                                  set(data['authors'][pair[1]]['papers']))
            authors_graph.add_edge(*pair, weight=n_common_papers)

            authors_graph.add_node(pair[0], n_publications=len(data['authors'][pair[0]]['papers']))
            authors_graph.add_node(pair[1], n_publications=len(data['authors'][pair[1]]['papers']))



    p = nx.spring_layout(authors_graph)
    nx.set_node_attributes(authors_graph, p, name='pos')

    edges_trace = []
    for edge in authors_graph.edges():
        edge_trace = go.Scatter(
            x=[],
            y=[],
            line=dict(width=1, color='#888'),
            hoverinfo='none',
            mode='lines')

        x0, y0 = authors_graph.node[edge[0]]['pos']
        x1, y1 = authors_graph.node[edge[1]]['pos']
        edge_trace['x'] += tuple([x0, x1, None])
        edge_trace['y'] += tuple([y0, y1, None])
        edge_trace['line']['width'] = authors_graph[edge[0]][edge[1]]['weight']

        edges_trace.append(edge_trace)


    node_trace = go.Scatter(
        x=[],
        y=[],
        text=[],
        mode='markers',
        hoverinfo='text',
        marker=dict(
            showscale=True,
            colorscale='Portland',
            color=[],
            size=[],
            colorbar=dict(
                thickness=15,
                title='Liczba publikacji',
                xanchor='left',
                titleside='right'
            ),
            line=dict(width=2, color='black'))
        )

    for node in authors_graph.nodes():
        x, y = authors_graph.node[node]['pos']
        node_trace['x'] += tuple([x])
        node_trace['y'] += tuple([y])

    for node in authors_graph.nodes():
        node_trace['marker']['color'] += tuple([authors_graph.node[node]['n_publications']])
        node_trace['marker']['size'] += tuple([sqrt(len(authors_graph[node]) + 1) * 10])  # liczba sąsiadów
        node_info = str(node) + ': liczba publikacji: '+str(authors_graph.node[node]['n_publications'])
        node_trace['text'] += tuple([node_info])

    figure_data = edges_trace + [node_trace]

    fig = go.Figure(data=figure_data,
                    layout=go.Layout(
                        showlegend=False,
                        hovermode='closest',
                        margin=dict(b=0, l=0, r=0, t=0),
                        annotations=[dict(
                            text="Źródło: <a href='https://apacz.matinf.uj.edu.pl/jednostki/1-"
                                  "wydzial-matematyki-i-informatyki-uj'> https://apacz.matinf."
                                  "uj.edu.pl/jednostki/1-wydzial-matematyki-i-informatyki-uj</a>",
                            showarrow=False,
                            xref="paper", yref="paper",
                            x=0.005, y=-0.002)],
                        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False)))

    print('Done.')
    return fig


def authors_table(data, authors=None, units=None):
    """Zwraca tablę z publikacjami danych autorów"""

    authors_info = data['authors']
    children = []
    if authors or units:
        paper_authors = [] if not authors else authors
        unit_authors = [] if not units else [author for author in authors_info if set(units) & set(authors_info[author]['units'])]

        authors = set(paper_authors) | set(unit_authors)
        table_rows = []
        for name in authors:
            for paper in authors_info[name]['papers']:
                units = acronym(authors_info[name]['units'])
                table_rows.append({'Name': name, 'Publications': trim_title(paper), 'Units': units})
            if len(table_rows) > 200:
                children.append("UWAGA: Część wierszy została ukryta z powodu zbyt dużej ilości danych.")
                break
        children.append(
            dash_table.DataTable(
                id='authors_table',
                columns=[{"name": i, "id": i} for i in ['Name', 'Publications', 'Units']],
                data=table_rows,
                style_header={'backgroundColor': 'rgb(226, 158, 9)', 
                            'font-family': 'Roboto, sans-serif',
                            'font-weight': 'bold',
                            'padding': '7px 7px 7px 10px', 
                            },
                style_cell={'textAlign': 'left',
                            'font-family': 'Roboto, sans-serif',
                            'paddingLeft': '5px',
                            },
                    style_cell_conditional=[
                        {'if': {'row_index': 'odd'},
                        'backgroundColor': 'rgb(240, 240, 240)'}
                    ]
            )
        )
    else:
        children.append("UWAGA: Proszę wybrać przynajmniej jednego autora lub jednostkę.")
    
    return children


def acronym(units):
    """Zwraca skróconą nazwę jednostki"""

    units_list = []
    for unit in units:
        units_list.append(''.join(word[0] for word in unit.split()))
    return ', '.join(units_list)


def trim_title(title, size=120):
    """Przycina zbyt długie nazwy publikacji"""

    ellipsis = '...'
    return (title[:size] + ellipsis) if len(title) > size + len(ellipsis) else title
