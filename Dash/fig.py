import plotly.graph_objects as go
from plotly.subplots import make_subplots
from pymongo import MongoClient

import pandas as pd
import re

#df = pd.read_csv("https://raw.githubusercontent.com/plotly/datasets/master/Mining-BTC-180.csv")

dbclient = MongoClient("mongodb+srv://coenfoster:Fall2024@test-server.mongocluster.cosmos.azure.com/?tls=true&authMechanism=SCRAM-SHA-256&retrywrites=false&maxIdleTimeMS=120000")
db = dbclient['test_db']
collection = db['SPY']

cur = collection.find({})

df = pd.DataFrame(list(cur))
df = df[['date', 'o', 'c', 'h', 'l']]
df = df.sort_values(by='date', axis=0)
df = df.reset_index()

print(df.head())

for i, row in enumerate(df["date"]):
    p = re.compile(" 00:00:00")
    datetime = p.split(df["date"][i])[0]
    df.iloc[i, 0] = datetime

print(df.head())

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
        y=df["o"],
        mode="lines",
        name="Open"
    ),
    row=2, col=1
)

fig.add_trace(
    go.Scatter(
        x=df["date"],
        y=df["c"],
        mode="lines",
        name="Close"
    ),
    row=2, col=1
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
    go.Scatter(
        x=df["date"],
        y=df["l"],
        mode="lines",
        name="Low"
    ),
    row=2, col=1
)

fig.add_trace(
    go.Table(
        header=dict(
            values=["date", "o", "c", "h", "l"],
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
    height=800,
    showlegend=False,
    title_text="Money Printer",
    title_x=0.5,
    title_font_color="green"
)

fig.show()