# property,for_date,transact_date,type,for,amount,recurring,taxable,debt
import os
import pandas as pd
from datetime import datetime
from pandas.tseries.offsets import *
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
import json

import dash
import dash_table
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import dash_auth

import plotly.graph_objs as go
import helpers.helpers as helpers

# Google Sheet
import gspread
from oauth2client.service_account import ServiceAccountCredentials

if os.environ.get('IS_HEROKU', None) is not None:
    u = os.environ.get('USERNAME')
    p = os.environ.get('PASSWORD')
    CRED_DICT = json.loads(os.environ.get('JSON'))
else:
    import credentials.username_password as cu
    u = cu.USERNAME
    p = cu.PASSWORD
    with open("./credentials/propertyManagementDashboard-2883708096cc.json") as k:
        CRED_DICT = json.loads(k.read())

USERNAME_PASSWORD_PAIRS = [['username','password'],[u, p]]

LAST_UPDATED = datetime.now()

# Google Spreadsheets
def get_data_from_google():
    global LAST_UDPATED
    scope = ["https://spreadsheets.google.com/feeds","https://www.googleapis.com/auth/spreadsheets","https://www.googleapis.com/auth/drive.file","https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_dict(CRED_DICT, scope)
    client = gspread.authorize(creds)
    sheet = client.open("property_transaction").sheet1
    data = sheet.get_all_records()
    LAST_UPDATED = datetime.now()
    return data

# Import Raw Data
df = pd.DataFrame(get_data_from_google())
df = helpers.initial_cleaning(df)

def update_df():
    global df
    temp_df = pd.DataFrame(get_data_from_google())
    df = helpers.initial_cleaning(temp_df)

sched = BackgroundScheduler(daemon=True)
sched.add_job(update_df,'interval',hours=24)
sched.start()

# Instantiate the app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.title = 'Property Management v1.0'
# auth = dash_auth.BasicAuth(app, USERNAME_PASSWORD_PAIRS)
server = app.server

def generate_property_options():
    l = df.property.unique().tolist()
    return [{'label': one_prop, 'value': one_prop.upper()} for one_prop in l]

def generate_date_picker_options():
    for_date = df['for_date']
    transact_date = df['transact_date']
    mix = for_date.append(transact_date)
    return [(mix.min() - MonthBegin()), mix.max(), (mix.max() - pd.DateOffset(years=1) - MonthBegin()), mix.max()]

def serve_layout():
    # Run the option functions
    property_options = generate_property_options()
    date_options = generate_date_picker_options()

    return html.Div([
    html.Div(
        children = [
            html.H1(
                children="Property Management",
                style = {
                    'display': 'inline-block',
                    'marginBottom': '0',
                    'marginRight': '5px',
                    'marginTop': '0'
                }
            ),
            html.I(
                "v1.0",
                style = {
                    'color': 'silver'
                }
            ), helpers.generate_read_more()
            ,
            html.P(
                children = [
                    "Please refresh the page to get the latest data - ",
                    html.Label(" last updated at {}".format(LAST_UPDATED.strftime("%Y/%m/%d %H:%M %Z")), style={'color': 'grey'})
                ],style = { 'fontSize': '80%'}
            )
        ],
        style = {
            'padding': '10px 0px'
        }
    ),
    html.Div(
        [html.P(
            children = 'Filters',
            style = {
                'color': 'grey',
                'marginBottom': '0',
                'display': 'block'
            }
        ),
        html.Div(
            [html.P(
                "Date Range",
                style = {
                    'marginBottom': '5px',
                    'fontSize': '12px'
                }
            ),
            html.Div(
                dcc.DatePickerRange(
                    id='date-picker',
                    min_date_allowed=date_options[0],
                    max_date_allowed=date_options[1],
                    start_date=date_options[2],
                    end_date=date_options[3]
                ),
                style = {
                    'width': '100%'
                }
            )],
            style = {
                'display': 'inline-block',
                'verticalAlign': 'top',
                'height': '100%'
            }
        ),
        html.Div(
            [html.P(
                "Cash or Accrual",
                style = {
                    'marginBottom': '5px',
                    'fontSize': '12px'
                }
            ),
            dcc.Dropdown(
                id='cash-accrual-dropdown',
                options=[
                    {'label':'Cash', 'value': 'c'},
                    {'label':'Accrual', 'value': 'a'}
                ],
                value="a",
                clearable = False
            )],
            style = {
                'display': 'inline-block',
                'width': '18%',
                'marginLeft': '5px',
                'verticalAlign': 'top',
                'height': '100%'
            }
        ),
        html.Div(
            [html.P(
                "Property",
                style = {
                    'marginBottom': '5px',
                    'fontSize': '12px'
                }
            ),
            dcc.Dropdown(
                id = 'property-dropdown',
                options=property_options,
                value=df.property.unique().tolist(),
                clearable = False,
                multi=True
            )],
            style = {
                'display': 'inline-block',
                'width': '22%',
                'marginLeft': '5px',
                'verticalAlign': 'top',
                'height': '100%'
            }
        )],
        style =  {
            'paddingTop': '5px',
            'paddingBottom': '10px',
            'padding': '5px 0 10px 10px',
            'border': '1px solid lightgrey'
        }
    )
    ,
    html.Div(
        id = 'graphs-wrapper',
        children = [html.Div(
            dcc.Graph(id = "bar-chart"),
            style = {
                'width': '65%',
                'display': 'inline-block'
            }
        ), html.Div(
            children = [
                html.Div(id = "widget-1"),
                html.Div(id = "widget-2", style={'marginTop': '8px'}),
                html.Div(id = "widget-3", style={'marginTop': '8px'})
            ],
            style = {
                'width': '30%',
                'display': 'inline-block',
                'verticalAlign': 'top',
                'padding': '10px',
                'paddingTop': '30px'
            }
        )],
        style = {
            'padding': '10px',
            'border': '1px solid lightgrey',
            'marginTop': '10px'
        }
    ),
    html.Div(
        html.Div(
            id = 'datatable-wrapper'
        ),
        style = {
            'width': '100%',
            'marginTop': '10px'
        }
    ),
    # For the clean data
    html.Div(id='filtered-data', style={'display': 'none'})
], style = {
    'padding': '10px 30px 10px 30px',
    'font-family': 'sans-serif'
})

app.layout = serve_layout

# Change in Data
@app.callback(Output('filtered-data', 'children'), [
    Input('cash-accrual-dropdown','value'),
    Input('property-dropdown', 'value'),
    Input('date-picker', 'start_date'),
    Input('date-picker', 'end_date')
])
def filter_data(ca, p, s, e):
    # global MODE
    # global FILTERED_DF
    # global JSON_DF
    MODE = ca

    filtered_df = helpers.filter_data(df, ca, p, s, e)
    FILTERED_DF = filtered_df.to_json(date_format='iso', orient='split')
    processed_df = helpers.process_bar(filtered_df, MODE)

    TOTAL_PROFIT = processed_df['signed_amount'].sum()
    TOTAL_INCOME = processed_df['income'].sum()
    TOTAL_EXPENSE = processed_df['expense'].sum()
    JSON_DF = processed_df.to_json(date_format='iso', orient='split')
    return [JSON_DF, FILTERED_DF, TOTAL_PROFIT, TOTAL_INCOME, TOTAL_EXPENSE, MODE]

# Update bar chart
@app.callback(Output('bar-chart', 'figure'),[
    Input('filtered-data', 'children')
])
def update_bar_chart(dfs):
    df1 = pd.read_json(dfs[0], orient='split')

    trace1 = go.Bar(
        x = df1['month'],
        y = df1['income'],
        name = 'Income',
        marker = dict(
            color = "#85bf4b"
        )
    )
    trace2 = go.Bar(
        x = df1['month'],
        y = df1['signed_amount'],
        name = 'Net Profit',
        marker = dict(
            color = "#50bfbf"
        )
    )
    trace3 = go.Bar(
        x = df1['month'],
        y = df1['expense'],
        name = 'Expense',
        marker = dict(
            color = "#bf0413"
        )
    )
    return {'data': [trace1, trace2, trace3],
            'layout': go.Layout(
                    title="Profit & Lost by Month Report",
                    xaxis= {
                        'tickformat': '%Y/%m',
                        'title': 'Year/Month'
                    },
                    yaxis = {
                        'title': 'Dollar($)'
                    }
                )}

# Widget 1
@app.callback(Output('widget-1', 'children'), [
    Input('filtered-data', 'children')
])
def update_widget_1(dfs):

    if dfs[2] >= 0:
        c = "#50bfbf"
    else:
        c = "#bf0413"

    return html.Div(
        [
            html.P(
                "Total Profit",
                style = {
                    'color': 'grey'
                }
            ),
            html.H1(
                dfs[2],
                style = {
                    'color': c
                }
            )
        ],
        style = {
            'textAlign': 'center',
            'border': '1px solid lightgrey',
            'verticalAlign': 'top',
        }
    )

# Widget 2
@app.callback(Output('widget-2', 'children'), [
    Input('filtered-data', 'children')
])
def update_widget_2(dfs):

    return html.Div(
        [
            html.P(
                "Total Income",
                style = {
                    'color': 'grey'
                }
            ),
            html.H1(
                dfs[3],
                style = {
                    'color': '#85bf4b'
                }
            )
        ],
        style = {
            'textAlign': 'center',
            'border': '1px solid lightgrey',
            'verticalAlign': 'top',
        }
    )

# Widget 3
@app.callback(Output('widget-3', 'children'), [
    Input('filtered-data', 'children')
])
def update_widget_3(dfs):

    return html.Div(
        [
            html.P(
                "Total Expense",
                style = {
                    'color': 'grey'
                }
            ),
            html.H1(
                dfs[4],
                style = {
                    'color': '#bf0413'
                }
            )
        ],
        style = {
            'textAlign': 'center',
            'border': '1px solid lightgrey',
            'verticalAlign': 'top',
        }
    )

# Datatable
@app.callback(Output('datatable-wrapper', 'children'), [
    Input('filtered-data', 'children')
])
def update_datatable(dfs):
    FILTERED_DF = pd.read_json(dfs[1], orient='split')
    td = helpers.initial_cleaning(FILTERED_DF).copy()
    td = helpers.add_month(td, dfs[5])
    td = td[['property', 'month', 'type', 'for', 'signed_amount', 'recurring', 'taxable', 'debt', 'note']].sort_values("month", ascending=False)
    table = dash_table.DataTable(
        id = 'datatable',
        columns = [{'name': i, "id": i} for i in td.columns],
        data = td.to_dict('records'),
        style_cell = {
            'overflow': 'hidden',
            'textOverflow': 'ellipse',
            'textAlign': 'left',
            'font-family':'sans-serif',
            'fontSize': '80%'
        },
        style_table={
            'overflowX': 'scroll',
            'maxHeight': '600px',
            'overflowY': 'scroll',
            'border': 'thin lightgrey solid'
        },
        style_header={
            'backgroundColor': 'white',
            'fontWeight': 'bold'
        },
        filter_action='native',
        sort_action = 'native'
    )
    return table

# Open & Close Modal
@app.callback(
    Output("modal", "is_open"),
    [Input("open", "n_clicks"), Input("close", "n_clicks")],
    [State("modal", "is_open")],
)
def toggle_modal(n1, n2, is_open):
    if n1 or n2:
        return not is_open
    return is_open

if __name__ == '__main__':
    app.run_server()
