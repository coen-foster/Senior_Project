import pandas as pd
import plotly.express as px
from dash import Dash, dcc, html, Output, Input
from pymongo import MongoClient
from datetime import datetime
from pandas.tseries.holiday import USFederalHolidayCalendar
from pandas.tseries.offsets import CustomBusinessDay
import pandas as pd

def create_date_list(start_date, end_date):
    # Convert start and end dates from string format to datetime objects
    start = datetime.strptime(start_date, "%Y-%m-%d")
    end = datetime.strptime(end_date, "%Y-%m-%d")
    
    # Define a custom business day calendar that excludes weekends and US stock market holidays
    us_business_day = CustomBusinessDay(calendar=USFederalHolidayCalendar())
    
    # Generate the list of business dates in reverse order within the specified range
    business_dates = pd.date_range(start=start, end=end, freq=us_business_day)[::-1]
    date_list = [{"label": date.strftime("%m/%d/%y"), "value": date.strftime("%Y-%m-%d")} for date in business_dates]
    
    return date_list

app = Dash(__name__)
dbclient = MongoClient("mongodb+srv://coenfoster:Fall2024@test-server.mongocluster.cosmos.azure.com/?tls=true&authMechanism=SCRAM-SHA-256&retrywrites=false&maxIdleTimeMS=120000")
db = dbclient['test_db']
collection = db['code']

# Retrieve all dates from the collection
date_list = [datetime.strptime(doc['date'], "%Y-%m-%d") for doc in collection.find({}, {'date': 1})]

# Find the minimum and maximum dates
earliest_date = min(date_list)
latest_date = max(date_list)

# Call create_date_list with the min and max dates as strings
date_list = create_date_list(earliest_date.strftime("%Y-%m-%d"), latest_date.strftime("%Y-%m-%d"))

print(earliest_date.strftime("%Y-%m-%d"))

app.layout = html.Div([
    html.H1("Money Printer", style={'text-align': 'center', 'color': '#3e9c35'}),
       
    dcc.Dropdown(id="slct_day",
        options=date_list,
        multi=False,
        value=earliest_date.strftime("%Y-%m-%d"),
        style={'width': "40%"}
        ),

    html.Div(id='open_container', children=[]),
    html.Div(id='high_container', children=[]),
    html.Div(id='low_container', children=[]),
    html.Div(id='close_container', children=[])
])

@app.callback(
    [Output(component_id='open_container', component_property='children'),
     Output(component_id='high_container', component_property='children'),
     Output(component_id='low_container', component_property='children'),
     Output(component_id='close_container', component_property='children')],
    [Input(component_id='slct_day', component_property='value')]
)
def update_data(option):
    cur = collection.find_one({'date':option})
    open_output = "Open: {}".format(cur['o'])
    high_output = "High: {}".format(cur['h'])
    low_output = "Low: {}".format(cur['l'])
    close_output = "Close: {}".format(cur['c'])
    return [open_output], [high_output], [low_output], [close_output]

if __name__ == '__main__':
    app.run_server(debug=True, port=8050)