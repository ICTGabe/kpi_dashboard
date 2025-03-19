# Install requirements: pip install dash pandas plotly dash-bootstrap-components
import dash
from dash import dcc, html, Input, Output, State, dash_table
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd
import os
from datetime import datetime

# ============================================
# CSV Storage Setup
# ============================================
CSV_FILE = 'kpi_data.csv'
COLUMNS = ['date', 'sales', 'expenses', 'region', 'product']

def init_csv():
    if not os.path.exists(CSV_FILE):
        pd.DataFrame(columns=COLUMNS).to_csv(CSV_FILE, index=False)

def get_data():
    if os.path.exists(CSV_FILE):
        df = pd.read_csv(CSV_FILE)
        df['date'] = pd.to_datetime(df['date'], errors='coerce').dt.date
        return df.dropna()
    return pd.DataFrame(columns=COLUMNS)

def add_data(date, sales, expenses, region, product):
    clean_date = datetime.strptime(date.split('T')[0], "%Y-%m-%d").strftime("%Y-%m-%d")
    new_data = pd.DataFrame([[clean_date, sales, expenses, region, product]], 
                           columns=COLUMNS)
    new_data.to_csv(CSV_FILE, mode='a', header=False, index=False)

init_csv()

# ============================================
# Dash App Setup
# ============================================
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.title = "KPI Dashboard - CSV Version"

# ============================================
# Layout Components
# ============================================
controls = dbc.Card([
    dbc.CardBody([
        html.H4("Data Entry", className="card-title"),
        dbc.Row([
            dbc.Col(dcc.DatePickerSingle(
                id='date-picker',
                date=datetime.today(),
                display_format='YYYY-MM-DD'
            ), width=3),
            dbc.Col(dbc.Input(id='sales-input', type='number', placeholder="Sales"), width=2),
            dbc.Col(dbc.Input(id='expenses-input', type='number', placeholder="Expenses"), width=2),
            dbc.Col(dbc.Select(
                id='region-select',
                options=[{'label': r, 'value': r} for r in ['North', 'South', 'East', 'West']],
                placeholder="Region"
            ), width=2),
            dbc.Col(dbc.Select(
                id='product-select',
                options=[{'label': p, 'value': p} for p in ['Electronics', 'Furniture', 'Apparel']],
                placeholder="Product"
            ), width=2),
            dbc.Col(dbc.Button("Add Record", id='add-button', color="primary"), width=1)
        ], className="g-2")
    ])
], className="mb-3")

app.layout = dbc.Container([
    dbc.Row(dbc.Col(html.H1("Sales KPI Dashboard", className="text-center mb-4"))),
    dbc.Row([dbc.Col(controls)]),
    
    dbc.Row([
        dbc.Col(dbc.Card([html.H5("Total Sales"), html.H2(id='total-sales')], 
                className="text-center p-3 shadow"), md=3),
        dbc.Col(dbc.Card([html.H5("Total Expenses"), html.H2(id='total-expenses')], 
                className="text-center p-3 shadow"), md=3),
        dbc.Col(dbc.Card([html.H5("Net Profit"), html.H2(id='net-profit')], 
                className="text-center p-3 shadow"), md=3),
        dbc.Col(dbc.Card([html.H5("Profit Margin"), html.H2(id='profit-margin')], 
                className="text-center p-3 shadow"), md=3)
    ], className="mb-4 gx-2"),
    
    dbc.Row([
        dbc.Col(dcc.Graph(id='time-series-chart'), md=6),
        dbc.Col(dcc.Graph(id='product-bar-chart'), md=6)
    ], className="mb-4"),
    
    dbc.Row([
        dbc.Col(dcc.Graph(id='region-pie-chart'), md=6),
        dbc.Col(dcc.Graph(id='profit-pie-chart'), md=6)
    ], className="mb-4"),
    
    dbc.Row([
        dbc.Col([
            html.Div([
                html.H4("Transaction Records"),
                dash_table.DataTable(
                    id='data-table',
                    columns=[{'name': col, 'id': col} for col in COLUMNS],
                    page_size=10,
                    style_table={
                        'overflowX': 'auto',
                        'marginBottom': '150px',
                        'paddingBottom': '50px'
                    },
                    style_cell={'textAlign': 'left', 'padding': '8px'},
                    style_header={'fontWeight': 'bold'},
                    filter_action='native',
                    sort_action='native',
                    sort_mode='multi',
                    page_current=0
                )
            ], style={'position': 'relative', 'zIndex': 1})
        ])
    ])
], fluid=True, style={'padding': '20px', 'paddingBottom': '150px', 'minHeight': '100vh'})

# ============================================
# Callbacks
# ============================================
@app.callback(
    [Output('total-sales', 'children'),
     Output('total-expenses', 'children'),
     Output('net-profit', 'children'),
     Output('profit-margin', 'children'),
     Output('time-series-chart', 'figure'),
     Output('product-bar-chart', 'figure'),
     Output('region-pie-chart', 'figure'),
     Output('profit-pie-chart', 'figure'),
     Output('data-table', 'data')],
    [Input('add-button', 'n_clicks')],
    [State('date-picker', 'date'),
     State('sales-input', 'value'),
     State('expenses-input', 'value'),
     State('region-select', 'value'),
     State('product-select', 'value')]
)
def update_dashboard(n_clicks, date, sales, expenses, region, product):
    if all([date, sales, expenses, region, product]):
        add_data(date, sales, expenses, region, product)
    
    df = get_data()
    if not df.empty and not df[['sales', 'expenses']].isnull().all().all():
        try:
            df['date'] = pd.to_datetime(df['date'])
            df['profit'] = df['sales'] - df['expenses']
            
            # Monthly aggregation
            df_monthly = df.set_index('date').resample('M').agg({
                'sales': 'sum',
                'expenses': 'sum',
                'profit': 'sum'
            }).reset_index()
            
            # Format values
            total_sales = f"${df['sales'].sum():,.2f}"
            total_expenses = f"${df['expenses'].sum():,.2f}"
            net_profit = f"${df['profit'].sum():,.2f}"
            profit_margin = f"{df['profit'].sum()/df['sales'].sum()*100:.1f}%" if df['sales'].sum() > 0 else "0%"
            
            # Create charts
            time_fig = px.line(df_monthly, x='date', y=['sales', 'expenses', 'profit'],
                              title="Monthly Financial Performance")
            
            product_df = df.groupby('product', as_index=False).agg({'sales': 'sum'})
            bar_fig = px.bar(product_df, x='product', y='sales',
                            title="Sales by Product Category")
            
            region_pie = px.pie(df, names='region', values='sales', 
                               title="Sales Distribution by Region")
            
            profit_pie = px.pie(df, names='product', values='profit',
                               title="Profit Distribution by Product")
            
            return (total_sales, total_expenses, net_profit, profit_margin,
                    time_fig, bar_fig, region_pie, profit_pie, df.to_dict('records'))
        
        except Exception as e:
            print(f"Error processing data: {str(e)}")
    
    # Return empty state
    return ("$0.00", "$0.00", "$0.00", "0%",
            px.scatter(title="No Data Available"),
            px.scatter(title="No Data Available"),
            px.scatter(title="No Data Available"),
            px.scatter(title="No Data Available"),
            [])

# ============================================
# Run the App
# ============================================
if __name__ == '__main__':
    app.run(debug=True, dev_tools_ui=False)