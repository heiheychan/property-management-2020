# property,for_date,transact_date,type,for,amount,recurring,taxable,debt
import pandas as pd
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html

def initial_cleaning(df):
    df['property'] = df['property'].astype(str)
    df['amount'] = df['amount'].astype(int)
    if "signed_amount" not in df.columns:
        signed_amount = []
        for count, one_type in enumerate(df['type']):
            if one_type == "IN":
                signed_amount.append(df.iloc[count].amount)
            else:
                signed_amount.append(df.iloc[count].amount*-1)
        df['signed_amount'] = pd.Series(signed_amount)
    df['for_date'] = pd.to_datetime(df['for_date'], errors='coerce')
    df['transact_date'] = pd.to_datetime(df['transact_date'], errors='coerce')
    df['recurring'] = df['recurring'].astype(bool)
    df['taxable'] = df['taxable'].astype(bool)
    df['debt'] = df['debt'].astype(bool)
    return df

def filter_data(df, ca, p, s, e):
    # Should we make a deep copy here?
    dff = df.copy()
    d = ('for_date' if (ca == 'a') else 'transact_date')
    dff.dropna(subset=[d], how='all', inplace=True)
    mask1 = dff['property'].isin(p)
    mask2 = dff[d].between(s, e)
    return dff[mask1 & mask2]

def process_bar(df ,m):
    dff = df.copy()
    if m == 'a':
        d = 'for_date'
    elif m == 'c':
        d = 'transact_date'
    dff['month'] = dff[d].dt.strftime('%Y/%m')
    signed_amount = dff.groupby(by='month').sum()['signed_amount'].to_frame()
    income_mask = dff['type'] == 'IN'
    income_amount = dff[income_mask].groupby(by='month').sum()['amount'].to_frame().rename(columns={'amount':'income'})
    expense_mask = dff['type'] == 'OUT'
    expense_amount = dff[expense_mask].groupby(by='month').sum()['amount'].to_frame().rename(columns={'amount':'expense'})
    d = pd.merge(signed_amount, income_amount, on='month', how='outer').merge(expense_amount, on='month', how='outer')
    d['signed_amount'].fillna(0, inplace=True)
    d['income'].fillna(0, inplace=True)
    d['expense'].fillna(0, inplace=True)
    d.reset_index(inplace=True)
    d.month = pd.to_datetime(d.month)
    return d

def add_month(df, m):
    tdd = df.copy()
    if m == 'a':
        d = 'for_date'
    elif m == 'c':
        d = 'transact_date'
    tdd['month'] = tdd[d].dt.strftime('%Y/%m')
    return tdd

def generate_read_more():
    return html.Div([
        dbc.Button("About this Dashboard", id='open', color='info', className='mr-1', style={'marginTop': '8px'}),
        dbc.Modal([
            dbc.ModalHeader('About this Dashboard'),
            dbc.ModalBody(
                children=[
                    html.H2("Objective"),
                    html.P("This dashboard is made for anyone who has to manage their rental properties. This dashboard offers a clean interface where you could see the Profit & Loss for each months, the overall financial standings, and each transactions that happened in a specified period. The data is also filterable by date, accounting method, and property."),
                    html.Hr(),
                    html.H2("Data Source"),
                    html.P("The data source is from a Google spreadsheet and the data will get updated in a set interval with the background work scheduler and Google Drive API. The following is the data structure:"),
                    html.Table(
                        [html.Tr(
                            [html.Th('Name'),
                            html.Th('Data Type')]
                        ),
                        html.Tr(
                            [html.Td("property"),
                            html.Td("String")]
                        ),
                        html.Tr(
                            [html.Td("for_date"),
                            html.Td("Datetime")]
                        ),
                        html.Tr(
                            [html.Td("transact_date"),
                            html.Td("Datetime")]
                        ),
                        html.Tr(
                            [html.Td("type"),
                            html.Td("String")]
                        ),
                        html.Tr(
                            [html.Td("amount"),
                            html.Td("Number")]
                        ),
                        html.Tr(
                            [html.Td("recurring"),
                            html.Td("Boolean")]
                        ),
                        html.Tr(
                            [html.Td("taxable"),
                            html.Td("Boolean")]
                        ),
                        html.Tr(
                            [html.Td("debt"),
                            html.Td("Boolean")]
                        ),
                        html.Tr(
                            [html.Td("note"),
                            html.Td("String")]
                        )],
                    ),
                    html.Hr(),
                    html.H2("Libraries & Tools"),
                    html.P(
                        "Libraries & Tools: Pandas, Dash, Plotly, Oauth, Apscheduler, Json, Google API, Heroku (Deployment)"
                    ),
                    html.Hr(),
                    html.H2("Creator"),
                    html.P("Bill Chan"),
                    html.P(
                        "Email: billchan@gwmail.gwu.edu"
                    ),
                    html.P(
                        html.I(
                            html.A('Linkedin', href='https://www.linkedin.com/in/billcch/')
                        )
                    ),
                    html.Hr(),
                    html.H2("Developer Note"),
                    html.P("""
                        I enjoyed every moments of building this dashboard.
                        During the development process, there were definitely setbacks and challenges that stem from the limitations and design of Dash
                        libraries, particularly the callback-related issues that could be time-consuming and tedious to resolve.
                        """),
                    html.P("""
                        Few other implementations in this project would be connecting the app to Google Drive, updating data in a set interval, deployment, etc.
                        Building this dashboard definitely hones my skill in data visualization and triggers me to dive deeper into this field.
                    """),
                    html.Br(),
                    html.H1(
                        html.I("Thank You & Happy Coding!")
                    )
                ]
            ),
            dbc.ModalFooter(
                dbc.Button("Close", id="close", className="ml-auto")
            )
        ],
        id='modal',
        size='lg')
    ],
    style = {
        'display': 'inline-block',
        'float': 'right'
    })
