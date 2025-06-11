import dash
from dash import dcc
from dash import html
import pandas as pd
import plotly.express as px
import dash_bootstrap_components as dbc
from dash import dash_table

# Chargez votre fichier CSV
# Assurez-vous que 'votre_fichier.csv' est le nom correct et que le fichier est dans le même répertoire
try:
    df = pd.read_csv(r'C:\Users\gallemand\Desktop\Projet Plotly Dash\Medicaldataset.csv')
except FileNotFoundError:
    print("Erreur : Le fichier 'votre_fichier.csv' n'a pas été trouvé. Veuillez vérifier le nom et le chemin du fichier.")
    exit()

# Initialiser l'application Dash avec des thèmes Bootstrap
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# Définir la mise en page de l'application en utilisant les composants Bootstrap
app.layout = dbc.Container(fluid=True, children=[
    dbc.Row(className="my-4", children=[
        dbc.Col(html.H1("Tableau de Bord Médical Interactif", className="text-center display-4 mb-0 text-primary"), width=12)
    ]),
    dbc.Row(children=[
        dbc.Col(md=3, children=[
            dbc.Card(
                dbc.CardBody([
                    html.H4("Contrôles des Données", className="card-title text-primary"),
                    html.Hr(className="my-3"),
                    html.Label("Sélectionnez une colonne pour l'axe X :", className="form-label mt-3"),
                    dcc.Dropdown(
                        id='x-column-dropdown',
                        options=[{'label': col, 'value': col} for col in df.columns],
                        value=df.columns[0] if not df.columns.empty else None,
                        className="mb-3 dbc"
                    ),

                    html.Label("Sélectionnez une colonne pour l'axe Y (si applicable) :", className="form-label"),
                    dcc.Dropdown(
                        id='y-column-dropdown',
                        options=[{'label': col, 'value': col} for col in df.columns],
                        value=df.columns[1] if len(df.columns) > 1 else (df.columns[0] if not df.columns.empty else None),
                        className="mb-3 dbc"
                    ),

                    html.Label("Sélectionnez le type de graphique :", className="form-label"),
                    dcc.Dropdown(
                        id='graph-type-dropdown',
                        options=[
                            {'label': 'Histogramme', 'value': 'histogram'},
                            {'label': 'Nuage de Points', 'value': 'scatter'},
                            {'label': 'Graphique en Barres', 'value': 'bar'}
                        ],
                        value='histogram',
                        className="mb-3 dbc"
                    ),

                    html.Label("Filtrer par Résultat :", className="form-label"),
                    dcc.RadioItems(
                        id='result-filter',
                        options=[
                            {'label': 'Tous', 'value': 'all'},
                            {'label': 'Positif', 'value': 'positive'},
                            {'label': 'Négatif', 'value': 'negative'}
                        ],
                        value='all',
                        inline=True,
                        className="mb-3 radio-items-custom"
                    )
                ]),
                className="h-100 shadow-sm"
            )
        ]),
        dbc.Col(md=9, children=[
            dbc.Card(
                dbc.CardBody([
                    dcc.Loading(id="loading-graph-output", type="default", children=[
                        dcc.Graph(
                            id='main-graph',
                            figure={},
                            className="dbc"
                        )
                    ])
                ]),
                className="mb-4 h-100 shadow-sm"
            )
        ])
    ]),
    dbc.Row(children=[
        dbc.Col(width=12, children=[
            dbc.Card(
                dbc.CardBody([
                    html.H4("Données Brutes", className="card-title text-primary"),
                    html.Hr(className="my-3"),
                    dash_table.DataTable(
                        id='data-table',
                        columns=[{"name": i, "id": i} for i in df.columns],
                        data=df.to_dict('records'), # Données initiales
                        page_size=10, # 10 lignes par page
                        style_table={'overflowX': 'auto'},
                        style_cell={'textAlign': 'left', 'padding': '8px'},
                        style_header={
                            'backgroundColor': 'rgb(230, 230, 230)',
                            'fontWeight': 'bold'
                        },
                        style_data_conditional=[
                            {
                                'if': {'row_index': 'odd'},
                                'backgroundColor': 'rgb(248, 248, 248)'
                            }
                        ],
                        export_format="csv" # Option d'exportation CSV
                    )
                ]),
                className="shadow-sm"
            )
        ])
    ])
])

# Callback pour mettre à jour le graphique et le tableau en fonction des sélections
@app.callback(
    [
        dash.dependencies.Output('main-graph', 'figure'),
        dash.dependencies.Output('data-table', 'data') # Nouvelle sortie pour le tableau
    ],
    [
        dash.dependencies.Input('x-column-dropdown', 'value'),
        dash.dependencies.Input('y-column-dropdown', 'value'),
        dash.dependencies.Input('graph-type-dropdown', 'value'),
        dash.dependencies.Input('result-filter', 'value') # Nouvelle entrée pour le filtre
    ]
)
def update_graph_and_table(selected_column_x, selected_column_y, selected_graph_type, selected_result_filter):
    # Filtrer le DataFrame en fonction du filtre de résultat
    filtered_df = df.copy()
    if selected_result_filter != 'all':
        filtered_df = filtered_df[filtered_df['Result'] == selected_result_filter]

    # Gérer la figure du graphique (similaire à avant, mais utilise filtered_df)
    fig = {} # Initialise une figure vide

    if selected_column_x is None or selected_graph_type is None:
        return {}, filtered_df.to_dict('records')

    if selected_graph_type == 'histogram':
        fig = px.histogram(filtered_df, x=selected_column_x, title=f'Histogramme de {selected_column_x}')
    elif selected_graph_type == 'scatter':
        if selected_column_y is None: 
            return {}, filtered_df.to_dict('records')
        fig = px.scatter(filtered_df, x=selected_column_x, y=selected_column_y,
                         title=f'Nuage de Points: {selected_column_x} vs {selected_column_y}')
    elif selected_graph_type == 'bar':
        if selected_column_y is None: 
            return {}, filtered_df.to_dict('records')
        fig = px.bar(filtered_df, x=selected_column_x, y=selected_column_y,
                     title=f'Graphique en Barres: {selected_column_x} vs {selected_column_y}')
    
    return fig, filtered_df.to_dict('records') # Retourne la figure et les données filtrées pour le tableau

# Exécuter l'application
if __name__ == '__main__':
    app.run(debug=True) 