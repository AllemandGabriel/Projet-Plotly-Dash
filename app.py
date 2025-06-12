import dash
from dash import dcc
from dash import html
import pandas as pd
import plotly.express as px
import dash_bootstrap_components as dbc
from dash import dash_table
import os # J'ajoute l'importation du module os

# Chargez votre fichier CSV
# Assurez-vous que 'Medicaldataset.csv' est le nom correct et que le fichier est dans le même répertoire
try:
    # Chemin relatif au répertoire du script
    csv_file_path = os.path.join(os.path.dirname(__file__), 'Medicaldataset.csv')
    df = pd.read_csv(csv_file_path)
except FileNotFoundError:
    print("Erreur : Le fichier 'Medicaldataset.csv' n'a pas été trouvé. Veuillez vérifier le nom et le chemin du fichier.")
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
                    html.H4("Choix des Données", className="card-title text-primary"),
                    html.Hr(className="my-3"),
                    html.Label("Sélectionnez une colonne pour l'axe X:", className="form-label mt-3"),
                    dcc.Dropdown(
                        id='x-column-dropdown',
                        options=[{'label': col, 'value': col} for col in df.columns],
                        value=df.columns[0] if not df.columns.empty else None,
                        className="mb-3 dbc",
                        searchable=False,
                        clearable=False,
                        multi=False
                    ),

                    html.Label("Sélectionnez une colonne pour l'axe Y:", className="form-label"),
                    dcc.Dropdown(
                        id='y-column-dropdown',
                        options=[{'label': col, 'value': col} for col in df.columns],
                        value=df.columns[1] if len(df.columns) > 1 else (df.columns[0] if not df.columns.empty else None),
                        className="mb-3 dbc",
                        searchable=False,
                        clearable=False,
                        multi=False
                    ),

                    html.Label("Sélectionnez le type de graphique:", className="form-label"),
                    dcc.Dropdown(
                        id='graph-type-dropdown',
                        options=[
                            {'label': 'Histogramme', 'value': 'histogram'},
                            {'label': 'Nuage de Points', 'value': 'scatter'},
                            {'label': 'Graphique en Barres', 'value': 'bar'}
                        ],
                        value='histogram',
                        className="mb-3 dbc",
                        searchable=False,
                        clearable=False,
                        multi=False
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
                            className="dbc",
                            style={'height': '500px'}
                        )
                    ]),
                    html.Div(id='graph-error-output', className="text-danger text-center mt-3")
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
        dash.dependencies.Output('data-table', 'data'),
        dash.dependencies.Output('graph-error-output', 'children') # Nouvelle sortie pour les messages d'erreur
    ],
    [
        dash.dependencies.Input('x-column-dropdown', 'value'),
        dash.dependencies.Input('y-column-dropdown', 'value'),
        dash.dependencies.Input('graph-type-dropdown', 'value'),
        dash.dependencies.Input('result-filter', 'value') # Nouvelle entrée pour le filtre
    ]
)
def update_graph_and_table(selected_column_x, selected_column_y, selected_graph_type, selected_result_filter):
    print(f"Callback déclenché avec :")
    print(f"  X-Column: {selected_column_x}")
    print(f"  Y-Column: {selected_column_y}")
    print(f"  Graph Type: {selected_graph_type}")
    print(f"  Result Filter: {selected_result_filter}")

    # Filtrer le DataFrame en fonction du filtre de résultat
    filtered_df = df.copy()
    graph_error_message = "" # Initialise le message d'erreur
    if selected_result_filter != 'all':
        filtered_df = filtered_df[filtered_df['Result'] == selected_result_filter]

    # Gérer la figure du graphique (similaire à avant, mais utilise filtered_df)
    fig = {} # Initialise une figure vide

    if selected_column_x is None or selected_graph_type is None:
        print("Retourne une figure vide car X-Column ou Graph Type est None.")
        graph_error_message = "Veuillez sélectionner une colonne pour l'axe X et un type de graphique."
        return {}, filtered_df.to_dict('records'), graph_error_message

    if selected_graph_type == 'histogram':
        fig = px.histogram(filtered_df, x=selected_column_x, title=f'Histogramme de {selected_column_x}')
    elif selected_graph_type == 'scatter':
        if selected_column_y is None:
            print("Retourne une figure vide car Y-Column est None pour Scatter.")
            graph_error_message = "Veuillez sélectionner une colonne pour l'axe Y pour le Nuage de Points."
            return {}, filtered_df.to_dict('records'), graph_error_message
        fig = px.scatter(filtered_df, x=selected_column_x, y=selected_column_y,
                         title=f'Nuage de Points: {selected_column_x} vs {selected_column_y}')
    elif selected_graph_type == 'bar':
        if selected_column_y is None:
            print("Retourne une figure vide car Y-Column est None pour Bar.")
            graph_error_message = "Veuillez sélectionner une colonne pour l'axe Y pour le Graphique en Barres."
            return {}, filtered_df.to_dict('records'), graph_error_message
        fig = px.bar(filtered_df, x=selected_column_x, y=selected_column_y,
                     title=f'Graphique en Barres: {selected_column_x} vs {selected_column_y}')

    print(f"Figure générée (non vide) : {bool(fig)}")
    print(f"Nombre de lignes filtrées pour le tableau : {len(filtered_df)}")
    return fig, filtered_df.to_dict('records'), graph_error_message # Retourne la figure, les données filtrées et le message d'erreur

# Exécuter l'application
if __name__ == '__main__':
    app.run(debug=True) 