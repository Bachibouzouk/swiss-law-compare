import difflib as dl
from pprint import pprint
from flask import Flask, send_from_directory
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate

from src.compare_versions import group_diffs, DiffObj

server = Flask(__name__)

app = dash.Dash(server=server, assets_folder='static')
app.index_string = '''
    <!DOCTYPE html>
    <html>

        <head>
            {%metas%}
            <meta charset="UTF-8">
            <meta description="NDC visualisation">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            {%css%}
        </head>

        <body>
            {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
        </body>

    </html>
    '''

d = dl.Differ()

app.layout = html.Div(
    className="grid-x center--align",
    children=[

    dcc.Textarea(id="txt1", className=" text cell large-5", value='''Celui qui recueille, remplit ou modifie systématiquement des bulletins de vote ou qui distribue des bulletins ainsi remplis ou modifiés sera puni des arrêts ou de l’amende.'''),
    dcc.Textarea(id="txt2", className="text cell large-offset-1 large-5", value='''Celui qui recueille, remplit ou modifie systématiquement des bulletins de vote ou qui distribue des bulletins ainsi remplis ou modifiés sera puni d’une amende.'''),
    html.Button(id="cmp-btn", children='compare', className="cell"),
    html.Div(children=html.Div(id="comp1", children='', className="diff cell"),
             className="cell center--align large-5 grid-x"),
    html.Div(children=html.Div(id="comp2", children='', className="diff cell"),
             className="cell center--align large-offset-1 large-5 grid-x"),
])

@app.callback(
    [
        Output(component_id='comp1', component_property='children'),
        Output(component_id='comp2', component_property='children'),
    ],
    [
        Input(component_id='cmp-btn', component_property='n_clicks')
    ],
    [
        State(component_id='txt1', component_property='value'),
        State(component_id='txt2', component_property='value'),
    ]
)
def process_diff(nclick, txt1, txt2):

    stored_diff = group_diffs(txt1.splitlines(keepends=True), txt2.splitlines(keepends=True))

    v1 = []
    v2 = []
    for s_diff in stored_diff:
        df = DiffObj(s_diff)
        v1.append(html.P(children=df.deleted, className="line"))
        v2.append(html.P(children=df.inserted, className="line"))

    return v1, v2


if __name__ == '__main__':
    app.run_server(debug=True)

