from youtube_dl import YoutubeDL
import dash
from dash.dependencies import Input, Output, State
from dash import dcc, html

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
from process import *

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
# intial layout
app.layout = html.Div([
    # dcc.Upload(
    #     id='upload-image',
    #     children=html.Div([
    #         'Drag and Drop or ',
    #         html.A('Select Files')
    #     ]),
    #     style={
    #         'width': '100%',
    #         'height': '60px',
    #         'lineHeight': '60px',
    #         'borderWidth': '1px',
    #         'borderStyle': 'dashed',
    #         'borderRadius': '5px',
    #         'textAlign': 'center',
    #         'margin': '10px'
    #     },
    #     # Allow multiple files to be uploaded
    #     multiple=True
    # ),
    dcc.Input(
        placeholder='Ingrese la url del video...',
        type='text',
        value='',
        id='link',
        style={
            'width': '100%',
            'height': '60px',
            'lineHeight': '60px',
            'borderWidth': '1px',
            'borderStyle': 'dashed',
            'borderRadius': '5px',
            'textAlign': 'center',
            'margin': '10px'
        },
    ),
    html.Button(id='submit-button', type='submit', children='Submit'),
    html.Div(id='output_div'),
])


# layout after an upload is detected
def parse_contents(link):
    if link is not None:
        audio = ""
        extension = ""
        grupos = []

        with YoutubeDL({'outtmpl': 'assets/%(id)s.%(ext)s', 'format': 'bestaudio'}) as ydl:
            info = ydl.extract_info(link, download=True)
            extension = info["ext"]
            id = info["id"]
            audio = "assets/" + id + "." + extension
            file_ready = convert_to_wav(id, audio, extension)
            do_diarization(file_ready)
            grupos = do_grouping()
            gidx, speakers = do_split(id, grupos)
            nuevodiv = do_transcribe(id, gidx, speakers)
        return html.Div([
            html.H5(link),
            html.Audio(id="player", autoPlay=True, src=audio, controls=True, style={"width": "50%"}),
            html.Hr(),
            html.Div('Transcript'),
            html.Plaintext(audio),
            nuevodiv
        ])


@app.callback(Output('output_div', 'children'),
              [Input('submit-button', 'n_clicks')],
              [State('link', 'value')],
              )
def update_output(clicks, input_value):
    if clicks is not None:
        return parse_contents(input_value)


if __name__ == '__main__':
    app.run_server(debug=True, dev_tools_hot_reload=False)
