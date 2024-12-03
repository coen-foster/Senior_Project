import pandas as pd
from dash import Dash, dcc, html, Output, Input
from pymongo import MongoClient
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import re
from datetime import datetime

app = Dash(__name__)

dbclient = MongoClient("mongodb+srv://coenfoster:Fall2024@test-server.mongocluster.cosmos.azure.com/?tls=true&authMechanism=SCRAM-SHA-256&retrywrites=false&maxIdleTimeMS=120000")

app.layout = html.Div([
    html.H1("Money Printer", style={'text-align': 'center', 'color': '#3e9c35'}),
       
    dcc.Dropdown(id="slct_ticker",
        options=[
            {"label": "SPY", "value": "SPY"},
            {"label": "KO", "value": "KO"},
            {"label": "CMG", "value": "CMG"}],
        multi=False,
        value="SPY",
        style={'width': "40%"}
    ),

    dcc.Dropdown(id="slct_lookback",
        options=[
            {"label": "One Month", "value": 1},
            {"label": "Three Months", "value": 3},
            {"label": "Six Months", "value": 6},
            {"label": "One Year", "value": 12},
            {"label": "All Time", "value": -1}],
        multi=False,
        value=-1,
        style={'width': "40%"}
    ),

    html.Div(id='open_container', children=[]),
    html.Div(id='high_container', children=[]),
    html.Div(id='low_container', children=[]),
    html.Div(id='close_container', children=[]),

    dcc.Graph(id="figure", figure={})
])

@app.callback(
    [Output(component_id='figure', component_property='figure')],
    [Input(component_id='slct_ticker', component_property='value'),
    Input(component_id='slct_lookback', component_property='value')]
)
def update_data(ticker, lookback):
    db = dbclient['test_db']
    collection = db[ticker]

    cur = collection.find({})

    df = pd.DataFrame(list(cur))
    df = df[['date', 'o', 'c', 'h', 'l']]
    #df['h'] = df['h'].apply(lambda x: "${:,.2f}".format(x))
    df = df.sort_values(by='date', axis=0)

    if lookback >= 0:
        df['date'] = pd.to_datetime(df['date'])
        months_ago = datetime.now() - pd.DateOffset(months=lookback)
        df = df[df['date'] >= months_ago]
        df['date'] = df['date'].dt.strftime('%Y-%m-%d')
        df = df.reset_index()
    else:
        df = df.reset_index()

    for i, row in enumerate(df["date"]):
        p = re.compile(" 00:00:00")
        datetime_x = p.split(df["date"][i])[0]
        df.iloc[i, 0] = datetime_x

    fig = make_subplots(
        rows=2, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.03,
        specs=[[{"type": "table"}],
            [{"type": "scatter"}]]
    )

    fig.add_trace(
        go.Scatter(
            x=df["date"],
            y=df["h"],
            mode="lines",
            name="High"
        ),
        row=2, col=1
    )

    fig.add_trace(
        go.Table(
            header=dict(
                values=["Date", "Open", "Close", "High", "Low"],
                font=dict(size=10),
                align="left"
            ),
            cells=dict(
                values=[df[k].tolist() for k in df.columns[1:]],
                align = "left")
        ),
        row=1, col=1
    )

    fig.update_layout(
        height=600
    )

    return [fig]

if __name__ == '__main__':
    app.run_server(debug=True, port=8050)