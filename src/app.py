import pandas as pd
import dash_bootstrap_components as dbc
from dash import Dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Header image
image_path = 'assets/GreenTrace_Logo_v004.png'

app = Dash(__name__, external_stylesheets=[dbc.themes.MINTY],
    meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"},])
server = app.server

# Do not display exception till callback gets executed
app.config.suppress_callback_exceptions = True

# Read data and clean it
gh_data = pd.read_csv('assets/historical_emissions.csv')
gh_data.drop(['Data source', 'Sector', 'Gas', 'Unit'], axis=1, inplace=True)
for x in range(1990, 1998):
    gh_data.drop([f'{x}'], axis=1, inplace=True)
df = gh_data.set_index('Country').T
df.reset_index(inplace=True)
df.rename(columns={'index': 'Year'}, inplace=True)
df.sort_values(by=['Year'], inplace=True)
df.reset_index(drop=True, inplace=True)
df['Year'] = df['Year'].astype(int)

year_list = [i for i in range(1998, 2018+1, 1)]
country_list = df.columns[2:]

world_fig = px.line(df, x='Year', y='World',
                    labels={
                        "Year": "Year (1998-2018)", "World": "World CO2 Emission (in MtCO₂e)"},
                    title='World CO2 Emission from 1998-2018')
world_fig.update_layout(title_x=0.5, title_y=0.85)

# Read world avg data
world_data = pd.read_csv('assets/world_historical_emissions.csv', usecols=[
                         'Sector', '2018,avg', '2017,avg', '2016,avg', '2015,avg', '2014,avg', '2013,avg', '2012,avg', '2011,avg', '2010,avg', '2009,avg', '2008,avg'])
world_data = world_data.rename(columns={
    '2018,avg': '2018',
    '2017,avg': '2017',
    '2016,avg': '2016',
    '2015,avg': '2015',
    '2014,avg': '2014',
    '2013,avg': '2013',
    '2012,avg': '2012',
    '2011,avg': '2011',
    '2010,avg': '2010',
    '2009,avg': '2009',
    '2008,avg': '2008'
})
# Convert the data to long form
world_data_long = pd.melt(
    world_data, id_vars=['Sector'], var_name='Year', value_name='Emissions')

# Create the World Average Historical Emissions plot
fig_world = go.Figure()
for sector in world_data_long['Sector'].unique():
    sector_data = world_data_long[world_data_long['Sector'] == sector]
    fig_world.add_trace(go.Scatter(
        x=sector_data['Year'], y=sector_data['Emissions'], name=sector))
font = dict(
    family='Arial',
    size=14,
    color='#7f7f7f'
)
fig_world.update_layout(
    title={
        'text': "World Average Historical Emissions",
        'font': font
    },
    xaxis=dict(
        title='Year',
        titlefont=font,
        tickfont=dict(
            family='Arial',
            size=8,
            color='#7f7f7f')
    ),
    yaxis=dict(
        title='Emissions',
        titlefont=font,
        tickformat='s'
    ),
    legend=dict(
        font=font
    )
)

app.layout = html.Div(children=[
    # Add header image
    html.Img(src=image_path, alt='GreenTrace', style={'width': '100%'}),

    # Add instructions
    html.Div([html.H1('Welcome to GreenTrace!', style={'text-align':'center'}),
            html.P('We have 3 goals:'),
            html.P(['1) Display CO2 emission trends from 1998-2018 for world and specific countries -- ', 
                   html.A("Dataset from Kaggle", href='https://www.kaggle.com/datasets/ankanhore545/carbon-dioxide-emissions-of-the-world', target="_blank")]),
            html.P(['2) Display global average emission from difference sources (ie. Energy, Electricity, etc) -- ', 
                   html.A("Dataset from Climate Watch", href='https://www.climatewatchdata.org/data-explorer/historical-emissions?historical-emissions-data-sources=climate-watch&historical-emissions-gases=all-ghg&historical-emissions-regions=All%20Selected&historical-emissions-sectors=total-including-lucf%2Ctotal-including-lucf&page=1', target="_blank")]),
            html.P(['3) Calculate individual carbon footprint based on your inputs -- ', 
                   html.A("Carbon Footprint Calculations", href='https://justenergy.com/blog/how-to-calculate-your-carbon-footprint/', target="_blank")]),
            ]
    ),
    
    html.Br(),

    html.Div([html.H2('CO2 Emission Trends Worldwide and for Specific Countries', style={'margin-right': '2em'}),
            # Add a graph for World CO2 emission data
            dcc.Graph(figure=world_fig),
            ]),

    # Dropdown creation, create an outer division
    html.Div([
        # Add an division
        html.Div([
            # Add dropdown
            html.Div([html.H5('Select country from dropdown to see CO2 emission:', style={'margin-right': '2em'})]),
            
            dcc.Dropdown(id='input-country',
                        options=[{'label': i, 'value': i} for i in country_list],
                        multi=True,
                        placeholder="Select a country here",
                        searchable=True),

            html.Br(),

            # Add slider
            html.Div([html.Label("After country selection, please toggle year range:"),
                      dcc.RangeSlider(id='year-slider',
                                      min=1998, max=2018, step=1,
                                      marks={1998: '1998', 2000: '2000', 2002: '2002', 2004: '2004', 2006: '2006', 2008: '2008',
                                             2010: '2010', 2012: '2012', 2014: '2014', 2016: '2016', 2018: '2018'},
                                      value=[1998, 2018])]),
        ])]),

    # Add line graph for CO2 emission for selected country and years
    html.Div([html.Div([], id='line_plot')]),

    html.Br(),
    html.Br(),

    html.H2(children='Global Average Emissions from Different Sources'),
    html.Div([
        dcc.Graph(
            id='avg-emissions-graph',
            figure=fig_world
        )
    ]),

    html.H2(children='Calculate Your Carbon Footprint'),
    html.Div([html.Div([html.Label('Monthly Electric Bill:', style={'font-weight': 'bold', 'font-size': '16px'}),
                        dcc.Input(id='input1', type='number', value=1, style={'width': '100px', 'margin-left': '10px'})],
                        style={'text-align': 'center'}),

              html.Div([html.Label('Monthly Gas Bill:', style={'font-weight': 'bold', 'font-size': '16px'}),
                        dcc.Input(id='input2', type='number', value=1, style={'width': '100px', 'margin-left': '10px'})],
                        style={'text-align': 'center'}),

              html.Div([html.Label('Monthly Oil Bill:', style={'font-weight': 'bold', 'font-size': '16px'}),
                        dcc.Input(id='input3', type='number', value=1, style={'width': '100px', 'margin-left': '10px'})],
                        style={'text-align': 'center'}),

              html.Div([html.Label('Total Yearly Mileage on Your Car:', style={'font-weight': 'bold', 'font-size': '16px'}),
                        dcc.Input(id='input4', type='number', value=1, style={'width': '100px', 'margin-left': '10px'})],
                        style={'text-align': 'center'}),

              html.Div([html.Label('Number of Flights You have taken in the past year (4 hours or less):', style={'font-weight': 'bold', 'font-size': '16px'}),
                        dcc.Input(id='input5', type='number', value=1, style={'width': '100px', 'margin-left': '10px'})], 
                        style={'text-align': 'center'}),

              html.Div([html.Label('Number of Flights You have taken in the past year (4 hours or more):', style={'font-weight': 'bold', 'font-size': '16px'}),
                        dcc.Input(id='input6', type='number', value=1, style={'width': '100px', 'margin-left': '10px'})], 
                        style={'text-align': 'center'}),

              html.Div([html.Label('Do You Recycle Aluminum and Tin (Yes: "0", No: "166"):', style={'font-weight': 'bold', 'font-size': '16px'}),
                        dcc.Input(id='input7', type='number', value=1, style={'width': '100px', 'margin-left': '10px'})],
                        style={'text-align': 'center'}),

              html.Div([html.Label('Do You Recycle paper (Yes: "0", No: "184"):', style={'font-weight': 'bold', 'font-size': '16px'}),
                        dcc.Input(id='input8', type='number', value=1, style={'width': '100px', 'margin-left': '10px'})],
                        style={'text-align': 'center'}),

              ], 
              style={'display': 'grid', 'grid-template-columns': 'repeat(4, 1fr)', 'grid-row-gap': '20px'}),
              html.Div(id='output-graph'),
              html.Div(id='output-div', style={'textAlign': 'center','margin-top': '5px'})            

])

@app.callback(Output(component_id='line_plot', component_property='children'),
            Input(component_id='input-country', component_property='value'),
            Input(component_id='year-slider', component_property='value'),
            prevent_initial_call = True)

def get_line_graph(country, year):
    year_df = df[df['Year'].between(year[0], year[1], inclusive='both')]['Year']
    country_df = df[df['Year'].between(year[0], year[1], inclusive='both')][country]
    filtered_df = pd.concat([year_df, country_df], axis=1)
    
    # Graph line graph
    line_fig = px.line(filtered_df, x='Year', y=country, labels={"value": "CO2 Emission (in MtCO₂e)", "variable": "Country"},
                  title=f'CO2 Emission (in MtCO₂e) between {year[0]} and {year[1]}')
    line_fig.update_layout(title_x=0.5, title_y=0.85)

    return dcc.Graph(figure=line_fig)

@app.callback(
    Output('output-graph', 'children'),
    [Input('input1', 'value'),
     Input('input2', 'value'),
     Input('input3', 'value'),
     Input('input4', 'value'),
     Input('input5', 'value'),
     Input('input6', 'value'),
     Input('input7', 'value'),
     Input('input8', 'value')])

def update_graph(value1, value2, value3, value4, value5, value6, value7, value8):
    # Filter the data based on the user input
    fig_personal = go.Figure()
    fig_personal.add_trace(
        go.Pie(labels=['Electric', 'Gas', 'Oil', 'Miles Driven', 'Short Flight', 'Long Flight', 'Recycle(Aluminum and Tin)', 'Recycle(Paper)'],
               values=[value1*105, value2*105, value3*113, value4*0.79, value5*1100, value6*4400, value7, value8]))
    fig_personal.update_layout(title='Doughnut Plot')
    fig_personal.update_traces(hole=.6, hoverinfo="label+percent")
    fig_personal.update_layout(
        title_text="Personal Carbon Footprint Percentage ",
        # Add annotations in the center of the donut pies.
        annotations=[
            dict(text='Your Carbon Footprint', x=0.5, y=0.5, font_size=12, showarrow=False)])

    # Return the graph as a dcc.Graph component
    return dcc.Graph(id='doughnut graph', figure=fig_personal)

@app.callback(
    Output('output-div', 'children'),
    [Input('input1', 'value'),
     Input('input2', 'value'),
     Input('input3', 'value'),
     Input('input4', 'value'),
     Input('input5', 'value'),
     Input('input6', 'value'),
     Input('input7', 'value'),
     Input('input8', 'value')])
def update_output(input1, input2, input3, input4, input5, input6, input7, input8):
    sum_val = input1*105 + input2*105 + input3*113 + input4*0.79 + input5*1100 + input6*4400 + input7 + input8
    return html.Div([
        html.H4('Your total carbon footprint is: {}'.format(sum_val)),
        html.P('Ideal carbon footprint: 6,000 ~ 15,999 pounds per year.'),
        html.P('Average carbon footprint 16,000 ~ 22,000 pounds per year.'),
        html.P('Over 22,000 you may want to take some of these “living green” practices into consideration.')
    ])

if __name__ == '__main__':
    app.run_server(debug=True)