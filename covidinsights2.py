import numpy as np
import pandas as pd
import plotly
import plotly.offline as pyo
import plotly.graph_objs as go
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import plotly_express as px


# external_stylesheets = [
#    'https://codepen.io/mikesmith1611/pen/QOKgpG.css',
 #   'https://codepen.io/chriddyp/pen/bWLwgP.css',
#    'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.8.1/css/all.min.css',]
# , external_stylesheets=external_stylesheets

app = dash.Dash(__name__)
server = app.server

mapbox_token = 'pk.eyJ1IjoiaGFycnljaHUiLCJhIjoiY2s3b3BwdzV0MGNlcTNvbXR1N3BzNmJsaCJ9.yP7C8lbyMtgnoJCmpt9KTQ'

popu = pd.read_csv('https://raw.githubusercontent.com/zhanghuaihua/covid-19/master/pop_corona_data.csv')

covid_df = pd.read_csv('https://raw.githubusercontent.com/zhanghuaihua/covid-19/master/Mar28_covid_19_clean_complete.csv')
covid_df['Province/State'].fillna('NA', inplace=True)
covid_df.rename( columns={'Confirmed': 'Confirmed Cases', 'Recovered': 'Recovered Cases'}, inplace=True)
outcome_list = ['Confirmed Cases', 'Deaths', 'Recovered Cases']

covid_df_total = covid_df.loc[covid_df['Date'] == '3/28/20', :]
df_country_sum = covid_df_total.groupby('Country/Region')[['Confirmed Cases', 'Deaths', 'Recovered Cases']].sum().reset_index()
df_country_sum.loc[165,'Country/Region'] = 'United States'
df_country_sum['Recovered/Confirmed (%)'] = df_country_sum['Recovered Cases'] / df_country_sum['Confirmed Cases'] * 100
df = pd.merge(df_country_sum, popu, left_on='Country/Region', right_on='Country', how='left')

df_density = df[['Country/Region', 'Population', 'Confirmed Cases', 'Density', 'HDI', 'Hospital_beds_per_1000']].dropna()
df_bed = df[['Country/Region', 'Population', 'Confirmed Cases', 'Deaths', 'Recovered Cases', 'Hospital_beds_per_1000', 'HDI']].dropna()

df_density['Incidence (per 100,000)'] = df_density['Confirmed Cases'] / df_density['Population'] * 100000
df_bed['Case Fatality (%)'] = df_bed['Deaths'] / df_bed['Confirmed Cases'] * 100
df_bed['Incidence (per 100,000)'] = df_density['Incidence (per 100,000)']
df_bed['Recovered/Confirmed (%)'] = df_bed['Recovered Cases'] / df_bed['Confirmed Cases'] * 100
df_bed['Mortality (per 100,000)'] = df_bed['Deaths'] / df_bed['Population'] * 100000
df_density['Case Fatality (%)'] = df_bed['Case Fatality (%)']
df_density['Mortality (per 100,000)'] = df_bed['Mortality (per 100,000)']
country_list = list(df_density['Country/Region'].unique())
country_list2 = list(df_bed['Country/Region'].unique())
oc_list = ['Incidence (per 100,000)', 'Case Fatality (%)', 'Mortality (per 100,000)']

px.set_mapbox_access_token(mapbox_token)

df_density.to_csv('covid_comparison')
def description():
    return html.Div(id='description',
                    children=[
                              html.H2(children=['COVID-19 Insights: Exploring possible associations']),
                              html.Div(id='intro',
                                       children=['In the 3D plot below, select outcome type and country(s) to '
                                                 'detect the possible associations between population density (people per km2), '
                                                 'Human development index (HDI), or Hospital beds per 1000 people and Incidence or Mortality of COVID-19.'
                                                 ' The data were last updated on March 28th, 2020.'],
                                       )
                              ]
                    )




def default_3d():
    fig3 = px.scatter_3d(df_density, x='Density', y='HDI', z='Hospital_beds_per_1000', color='Country/Region',
                         size='Incidence (per 100,000)', size_max=90, hover_name='Country/Region')
    fig3.update_layout(showlegend=False, hovermode='closest', margin=dict(l=50, b=80, t=40, r=30))
    return fig3



app.layout = html.Div(
    children=[
        html.Div(
            id="upper-column",
            children=[description(),
                      html.Br()],
            style={'width': '70%'}
        ),
        html.Div(
            id="bottom-column",
            children=[
                html.Div(
                    id='two scatters',
                    children=[
                        html.Div(
                            children=[
                                html.H4(['Select Outcome Type for 3D Plot']),
                                dcc.Dropdown(id='Select_oc',
                                             options=[{'label': i, 'value': i} for i in oc_list],
                                             value=oc_list[0]),
                                html.Br(),
                                html.H4('Select Country/Region for 3D Plot'),
                                dcc.Dropdown(id='Select_country',
                                             options=[{'label': i, 'value': i} for i in country_list],
                                             value=country_list[:],
                                             multi=True
                                             ),
                                html.Br(),
                                html.Button(id='button', children=['Generate 3D Plot'], n_clicks=0),
                                html.Br()
                            ],
                            style={'display': 'inline_block', 'width': '30%', 'float': 'left', 'height': 200}
                        ),
                        html.Div(
                            children=[dcc.Graph(id='3d',figure=default_3d(), config={'displayModeBar': False})],
                            style={'display': 'inline_block', 'width': '70%', 'float': 'right', 'height': 200}
                        )
                    ]
                )
            ]),
    ]
)




@app.callback(Output('3d', 'figure'),
              [Input('button', 'n_clicks')],
              [State('Select_oc', 'value'), State('Select_country', 'value')])
def plot_3d(nclicks, oc, ctry):
    filtered_df = df_density[df_density['Country/Region'].isin(ctry)]
    fig1 = px.scatter_3d(filtered_df, x='Density', y='HDI', z='Hospital_beds_per_1000', color='Country/Region',
                         size=oc, size_max=90, hover_name='Country/Region',
                         height=690)
    fig1.update_layout(showlegend=False, hovermode='closest', margin=dict(l=50, b=80, t=40, r=30), height=700)
    return fig1


if __name__ == '__main__':
    app.run_server()


