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

text_v1 = [
html.H4("Discrimination raciale"),
html.P("Celui qui, publiquement, aura incité à la haine ou à la discrimination envers une personne ou un groupe de personnes en raison de leur appartenance raciale, ethnique ou religieuse;"),
html.P("celui qui, publiquement, aura propagé une idéologie visant à rabaisser ou à dénigrer de façon systématique les membres d’une race, d’une ethnie ou d’une religion;"),
html.P("celui qui, dans le même dessein, aura organisé ou encouragé des actions de propagande ou y aura pris part;"),
html.P("celui qui aura publiquement, par la parole, l’écriture, l’image, le geste, par des voies de fait ou de toute autre manière, abaissé ou discriminé d’une façon qui porte atteinte à la dignité humaine une personne ou un groupe de personnes en raison de leur race, de leur appartenance ethnique ou de leur religion ou qui, pour la même raison, niera, minimisera grossièrement ou cherchera à justifier un génocide ou d’autres crimes contre l’humanité;"),
html.P("celui qui aura refusé à une personne ou à un groupe de personnes, en raison de leur appartenance raciale, ethnique ou religieuse, une prestation destinée à l’usage public,"),
html.P("sera puni d’une peine privative de liberté de trois ans au plus ou d’une peine pécuniaire."),
]
text_v2 = [
html.H4("Discrimination raciale"),
html.P("Quiconque, publiquement, aura incité à la haine ou à la discrimination envers une personne ou un groupe de personnes en raison de leur appartenance raciale, ethnique ou religieuse ou de leur orientation sexuelle;"),
html.P("quiconque, publiquement, aura propagé une idéologie visant à rabaisser ou à dénigrer de façon systématique les membres d’une race, d’une ethnie ou d’une religion;"),
html.P("quiconque, dans le même dessein, aura organisé ou encouragé des actions de propagande ou y aura pris part;"),
html.P("quiconque aura publiquement, par la parole, l’écriture, l’image, le geste, par des voies "
       "de fait ou de toute autre manière, abaissé ou discriminé d’une façon qui porte atteinte à la dignité humaine une personne ou un groupe de personnes en raison de leur race, de leur appartenance ethnique ou religieuse ou de leur orientation sexuelle ou qui, pour la même raison, niera, minimisera grossièrement ou cherchera à justifier un génocide ou d’autres crimes contre l’humanité;"),
html.P("quiconque aura refusé à une personne ou à un groupe de personnes, en raison de leur appartenance raciale, ethnique ou religieuse ou de leur orientation sexuelle, une prestation destinée à l’usage public,"),
html.P("sera puni d’une peine privative de liberté de trois ans au plus ou d’une peine pécuniaire."),
]


def loop_nested(a_list):
    pure_text = []
    if isinstance(a_list, list):
        for el in a_list:
            pure_text = pure_text + loop_nested(el)

    if isinstance(a_list, str):
        return [a_list]

    if isinstance(a_list, dict):
        if a_list['namespace'] == "dash_html_components":
            return loop_nested(a_list['props']["children"])
    return pure_text


app.layout = html.Div(
    className="grid-x center--align",
    children=[
    html.Div(id="v1", className="cell large-5", children=text_v1, style={"display": "none"}),
    html.Div(id="v2", className="cell large-offset-1 large-5", children=text_v2, style={"display": "none"}),
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
        Input(component_id='v1', component_property='children'),
        Input(component_id='v2', component_property='children'),
    ]
)
def process_diff(txt1, txt2):

    lines1 = loop_nested(txt1)
    lines2 = loop_nested(txt2)
    v1 = []
    v2 = []
    for i in range(len(lines1)):
        stored_diff = group_diffs([lines1[i]], [lines2[i]])
        if stored_diff:
            df = DiffObj(stored_diff[0])
            v1.append(html.P(children=df.deleted, className="line"))
            v2.append(html.P(children=df.inserted, className="line"))
        else:
            v1.append(html.P(children=lines1[i]))
            v2.append(html.P(children=lines2[i]))

    return v1, v2


if __name__ == '__main__':
    app.run_server(debug=True)

