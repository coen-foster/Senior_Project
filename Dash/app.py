import pandas as pd
from dash import Dash, dcc, html, Output, Input
from pymongo import MongoClient
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime

app = Dash(__name__)

# MongoDB connection
dbclient = MongoClient("mongodb+srv://coenfoster:Fall2024@test-server.mongocluster.cosmos.azure.com/?tls=true&authMechanism=SCRAM-SHA-256&retrywrites=false&maxIdleTimeMS=120000")
db = dbclient['test_db']

app.layout = html.Div([
    html.H1("Money Printer", style={'text-align': 'center', 'color': '#3e9c35'}),

    # Ticker Dropdown
    html.Div([
        dcc.Dropdown(id="slct_ticker",
                     options=[{"label": ticker, "value": ticker} for ticker in db.list_collection_names()],
                     multi=False,
                     value="SPY",
                     placeholder="Select a Ticker",
                     style={'width': "40%"}),
    ], style={'text-align': 'center', 'margin-bottom': '20px'}),

    # Lookback Dropdown
    html.Div([
        dcc.Dropdown(id="slct_lookback",
                     options=[
                         {"label": "One Month", "value": 1},
                         {"label": "Three Months", "value": 3},
                         {"label": "Six Months", "value": 6},
                         {"label": "One Year", "value": 12},
                         {"label": "All Time", "value": -1}],
                     multi=False,
                     value=-1,
                     placeholder="Select a Lookback Period",
                     style={'width': "40%"}),
    ], style={'text-align': 'center', 'margin-bottom': '20px'}),

    # Graph Section
    dcc.Loading(
        id="loading",
        type="circle",
        children=[
            dcc.Graph(id="figure", figure={})
        ]
    )
])

@app.callback(
    Output(component_id='figure', component_property='figure'),
    [Input(component_id='slct_ticker', component_property='value'),
     Input(component_id='slct_lookback', component_property='value')]
)
def update_data(ticker, lookback):
    if not ticker:
        return go.Figure()

    # Fetch data from MongoDB
    collection = db[ticker]
    cur = collection.find({})
    df = pd.DataFrame(list(cur))

    # Validate data
    if df.empty:
        return go.Figure()

    df = df[['date', 'o', 'c', 'h', 'l']]
    df['date'] = pd.to_datetime(df['date'])
    df = df.sort_values(by='date')

    # Apply lookback filter
    if lookback > 0:
        cutoff_date = datetime.now() - pd.DateOffset(months=lookback)
        df = df[df['date'] >= cutoff_date]

    df['date'] = df['date'].dt.strftime('%Y-%m-%d')

    # Format numeric columns as currency
    for col in ['o', 'c', 'h', 'l']:
        df[col] = df[col].apply(lambda x: f"${x:,.2f}")

    # Create subplot figure
    fig = make_subplots(
        rows=2, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.05,
        specs=[[{"type": "table"}],
                [{"type": "scatter"}]]
    )

    # Add table
    fig.add_trace(
        go.Table(
            header=dict(
                values=["Date", "Open", "Close", "High", "Low"],
                font=dict(size=12, color="white"),
                fill_color="#3e9c35",
                align="center"
            ),
            cells=dict(
                values=[df[k].tolist() for k in df.columns],
                fill_color="lavender",
                align="center")
        ),
        row=1, col=1
    )

    # Add line chart (use unformatted numeric data for y-axis)
    df_numeric = df.copy()
    for col in ['o', 'c', 'h', 'l']:
        df_numeric[col] = df_numeric[col].str.replace('[$,]', '', regex=True).astype(float)

    fig.add_trace(
        go.Scatter(
            x=df["date"],
            y=df_numeric["h"],
            mode="lines",
            name="High",
            line=dict(color="#3e9c35", width=2)
        ),
        row=2, col=1
    )

    fig.update_layout(
        title=f"Data for {ticker}",
        height=700,
        margin=dict(l=20, r=20, t=50, b=20),
        plot_bgcolor="#f9f9f9",
        paper_bgcolor="#f9f9f9"
    )

    return fig

if __name__ == '__main__':
    app.run_server(debug=True, port=8050)