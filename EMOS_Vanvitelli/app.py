import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from dash import Dash, dcc, html, dash_table, Input, Output
from datetime import datetime, timedelta
import geopandas as gpd
from sklearn.preprocessing import MinMaxScaler
from skimage import exposure


def plot_pollutant_importance(df, nuts3_name):
    """
    Plots a pie chart (cake graph) of pollutant importance for a given NUTS3 region.
    Parameters:
    df (pd.DataFrame): DataFrame containing pollutant importance data.
    nuts3_name (str): The NUTS3 region name to visualize.
    Returns:
    Plotly figure.
    """
    if nuts3_name not in df.index:
        raise ValueError(f"NUTS3 name '{nuts3_name}' not found in the DataFrame.")
    # Extract pollutant data for the selected region
    data = df.loc[nuts3_name, ["CO", "NO2", "SO2", "PM10", "PM2.5"]]
    # Create a pie chart
    fig = px.pie(
        names=data.index,
        values=data.values,
        title=f"Pollutant Importance for {nuts3_name}",
        hole=0.3  # Donut-style look
    )
    fig.update_traces(textinfo="percent+label")  # Show labels and percentages
    fig.update_layout(
        height=450,  # Increased height
        margin=dict(t=50, b=30, l=30, r=30)
    )
    return fig


def plot_time_series_with_limit(nuts3_name, indicator, data, limits, start_date=None, end_date=None):
    """
    Plot the time series of a selected NUTS3 region for a specific indicator with its corresponding limit.
    Parameters:
    - nuts3_name: The name of the NUTS3 region (must match an index in `data`).
    - indicator: The specific indicator to plot (must match a column in `data`).
    - data: Dictionary of DataFrames where dates are **columns** and NUTS3 names are indices.
    - limits: Dictionary with limits for each indicator.
    - start_date: Optional start date for the time range (format: "YYYY-MM-DD").
    - end_date: Optional end date for the time range (format: "YYYY-MM-DD").
    Returns:
    - A Plotly figure.
    """
    # Extract time series (TRANSPOSE the DataFrame)
    if indicator == "HAQI":
        indicator = "PM10"
    time_series = data[indicator].loc[nuts3_name].T  # Transpose so dates become the index
    # Convert index to datetime with correct format
    time_series.index = pd.to_datetime(time_series.index, format="%d/%m/%Y")  # Fix date format

    limit_value = limits[indicator]
    # Filter by date range if specified
    if start_date and end_date:
        start_date = pd.to_datetime(start_date)
        end_date = pd.to_datetime(end_date)
        time_series = time_series.loc[start_date:end_date]
    fig = go.Figure()
    # Add time series line with styling
    fig.add_trace(go.Scatter(
        x=time_series.index,
        y=time_series.values,
        mode='lines',
        name=f"{indicator} - {nuts3_name}",
        line=dict(color="royalblue", width=3, dash='solid')
    ))
    # Add limit line with styling
    fig.add_trace(go.Scatter(
        x=time_series.index,
        y=[limit_value] * len(time_series),  # Constant limit line
        mode='lines',
        name=f"{indicator} Limit",
        line=dict(color="darkred", width=2, dash="dot")
    ))

    # Layout adjustments for a cleaner look
    fig.update_layout(
        title=f"<b>Time Series of {indicator} in {nuts3_name}</b>",
        xaxis_title="<b>Time</b>",
        yaxis_title=f"<b>{indicator} Value</b>",
        title_x=0.5,
        height=450,  # Increased height
        template="plotly_white",  # Clean white template
        plot_bgcolor='rgba(250,250,250,0.9)',  # Light background
        margin=dict(l=50, r=30, t=50, b=50),
        showlegend=True,
        legend=dict(
            orientation="v",
            yanchor="top",
            y=1,
            xanchor="right",
            x=1
        )
    )
    # Add interactive features for zoom and hover
    fig.update_traces(mode='lines+markers', marker=dict(size=6))
    return fig


def plot_choropleth(geo_df, indicator_table, indicator, selected_region=None):
    """
    Create a choropleth map using Plotly for a selected indicator.
    Parameters:
    - geo_df: GeoDataFrame with geometries and NUTS3 regions.
    - indicator_table: DataFrame containing indicator values with 'nuts3_name' as the index.
    - indicator: The column name (string) representing the selected indicator.
    - selected_region: Optional; the NUTS3 region to highlight.
    Returns:
    - A Plotly figure.
    """
    if indicator not in indicator_table.columns:
        raise ValueError(
            f"Indicator '{indicator}' not found in indicator table. Available: {list(indicator_table.columns)}")
    # Reset index so nuts3_name becomes a column
    indicator_table = indicator_table.reset_index()
    # Merge GeoDataFrame with the indicator values
    merged = geo_df.merge(indicator_table, left_on="NUTS_NAME", right_on="nuts3_name")
    # Format HAQI to 4 decimal places
    merged['HAQI'] = merged['HAQI'].round(3)
    merged.index = merged['NUTS_NAME']
    
    # Apply histogram equalization to the indicator column
    merged[indicator] = exposure.equalize_hist(merged[indicator].to_numpy())

    # Add a column to indicate if the region is selected
    merged['selected'] = merged['NUTS_NAME'] == selected_region

    # Create the choropleth map
    fig = px.choropleth_mapbox(merged,
                               geojson=merged.geometry.__geo_interface__,  # Convert geometries to GeoJSON
                               locations=merged['NUTS_NAME'],  # Use nuts3_name as locations
                               color=indicator,
                               color_continuous_scale="Viridis",  # Invert the colormap
                               mapbox_style="carto-positron",
                               opacity=0.6,
                               hover_name="nuts3_name",
                               hover_data={indicator: True},
                               labels={indicator: indicator},
                               center={"lat": merged.geometry.centroid.y.mean(),
                                       "lon": merged.geometry.centroid.x.mean()},
                               zoom=4.5)

    # Update the color or opacity of the selected region
    if selected_region:
        fig.update_traces(marker=dict(opacity=0.3))  # Set default opacity for all regions
        fig.add_trace(go.Choroplethmapbox(
            geojson=merged.geometry.__geo_interface__,
            locations=merged['NUTS_NAME'],
            z=merged['selected'].astype(int),
            colorscale=[[0, 'rgba(0,0,0,0)'], [1, 'rgba(255,0,0,0.6)']],  # Highlight selected region in red
            showscale=False,
            marker=dict(opacity=0.6)
        ))

    fig.update_layout(
        height=600,  # Increased height for better visibility
        margin={"r": 0, "t": 40, "l": 0, "b": 0},
        title=f"<b>{indicator} Adjusted Index by NUTS-3</b>",
        title_x=0.5,
        legend_title_text=f"<b>{indicator} Value</b>",
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.2,
            xanchor="center",
            x=0.5
        )
    )

    return fig


def build_indicators_table(data,data_ndvi, limits, date_range):
    # Ensure date_range is in the correct format (DD/MM/YYYY)
    date_range_str = pd.date_range(start=date_range[0], end=date_range[1]).strftime("%d/%m/%Y").tolist()
    #data["NDVI"].columns = pd.to_datetime(data["NDVI"].columns).strftime("%d/%m/%Y")
    # Filter data by date_range
    data_filtered = {i: df.loc[:, df.columns.intersection(date_range_str)] for i, df in data.items()}
    data_ndvi_filtered = data_ndvi.loc[:, data_ndvi.columns.intersection(date_range_str)]
    # Compute indicators
    indi_tables = {i: (data_filtered[i] / limits[i])/data_ndvi_filtered for i in data_filtered}
    #print(indi_tables)
    # Count days where values exceed the limit
    days_above_limit = {i: (data_filtered[i] > limits[i]).sum(axis=1) for i in data_filtered}
    # Compute final indicator: mean * number of days exceeding limit
    indi_table = {i: (indi_tables[i].sum(axis=1) / indi_tables[i].shape[1]) * days_above_limit[i] 
                  if indi_tables[i].shape[1] > 0 else pd.Series(0, index=indi_tables[i].index)
                  for i in indi_tables}
 
    # Convert dictionary to DataFrame
    df = pd.DataFrame(indi_table)
 
    # Replace NaNs with 0 before normalization
    df.fillna(0, inplace=True)
 
    # Normalize using MinMaxScaler
    scaler = MinMaxScaler()
    df_norm = pd.DataFrame(scaler.fit_transform(df), index=df.index, columns=df.columns)
    #df_norm = df
 
    # Compute composite indicator
    df_norm["HAQI"] = df_norm.sum(axis=1)
 
    # Normalize composite indicator correctly
    df_norm["HAQI"] = scaler.fit_transform(df_norm[["HAQI"]])  # Reshape needed
 
    return df_norm

def plot_histogram(nuts3_name, indicator, data, start_date=None, end_date=None):
    """
    Plot a histogram of the selected indicator for a specific NUTS3 region.
    Parameters:
    - nuts3_name: The name of the NUTS3 region (must match an index in `data`).
    - indicator: The specific indicator to plot (must match a column in `data`).
    - data: Dictionary of DataFrames where dates are **columns** and NUTS3 names are indices.
    - start_date: Optional start date for the time range (format: "YYYY-MM-DD").
    - end_date: Optional end date for the time range (format: "YYYY-MM-DD").
    Returns:
    - A Plotly figure.
    """
    if indicator == "HAQI":
        indicator = "PM10"

    # Extract time series (TRANSPOSE the DataFrame)
    time_series = data[indicator].loc[nuts3_name].T  # Transpose so dates become the index
    # Convert index to datetime with correct format
    time_series.index = pd.to_datetime(time_series.index, format="%d/%m/%Y")  # Fix date format
    time_series_df = pd.DataFrame(time_series)
    time_series_df.columns = [indicator]

    # Filter by date range if specified
    if start_date and end_date:
        start_date = pd.to_datetime(start_date)
        end_date = pd.to_datetime(end_date)
        time_series = time_series.loc[start_date:end_date]

    # Create histogram
    fig = px.histogram(
        time_series_df,
        x=indicator,
        nbins=100,
        title=f"Histogram of {indicator} in {nuts3_name}",
        labels={'x': 'Date', 'y': f'{indicator} Value'}
    )

    # Add vertical line for the limit
    limit_value = limiti_UE[indicator]
    fig.add_vline(x=limit_value, line_width=3, line_dash="dash", line_color="red", annotation_text="Limit", annotation_position="top right")

    # Layout adjustments for a cleaner look
    fig.update_layout(
        height=450,  # Increased height
        template="plotly_white",  # Clean white template
        plot_bgcolor='rgba(250,250,250,0.9)',  # Light background
        margin=dict(l=50, r=30, t=50, b=50),
        showlegend=False
    )

    return fig


# Load geographical data and pollutant CSVs
geo_df = gpd.read_file("data/NUTS_RG_20M_2024_4326.geojson")
geo_df_italy = geo_df[geo_df["CNTR_CODE"] == "IT"]
geo_df_belgium = geo_df[geo_df["CNTR_CODE"] == "BE"]
nuts_3_italy = list(geo_df_italy["NUTS_NAME"])[:107]
nuts_3_belgium = list(geo_df_belgium["NUTS_NAME"])[:44]

data_italy = {"CO" : pd.read_csv("data/Italia_co_daily_all.csv", index_col=0).loc[nuts_3_italy],
              "NO2" : pd.read_csv("data/Italia_no2_daily_all.csv", index_col=0).loc[nuts_3_italy],
              "SO2" : pd.read_csv("data/Italia_so2_daily_all.csv", index_col=0).loc[nuts_3_italy],
              "PM10" : pd.read_csv("data/Italia_pm10_daily_all.csv", index_col=0).loc[nuts_3_italy],
              "PM2.5" : pd.read_csv("data/Italia_pm25_daily_all.csv", index_col=0).loc[nuts_3_italy],
             }
data_belgium = {"CO" : pd.read_csv("data/Belgio_co_daily_all.csv", index_col=0).loc[nuts_3_belgium],
                "NO2" : pd.read_csv("data/Belgio_no2_daily_all.csv", index_col=0).loc[nuts_3_belgium],
                "SO2" : pd.read_csv("data/Belgio_so2_daily_all.csv", index_col=0).loc[nuts_3_belgium],
                "PM10" : pd.read_csv("data/Belgio_pm10_daily_all.csv", index_col=0).loc[nuts_3_belgium],
                "PM2.5" : pd.read_csv("data/Belgio_pm25_daily_all.csv", index_col=0).loc[nuts_3_belgium],
               }
data_italy = {i: data_italy[i].loc[nuts_3_italy] for i in data_italy}
data_belgium = {j:data_belgium[j].loc[nuts_3_belgium] for j in data_belgium}

# Merge Italy and Belgium data for each pollutant
data_total = {
    pollutant: pd.concat([data_italy[pollutant], data_belgium[pollutant]], axis=0)
    for pollutant in data_italy.keys()
}

limiti_UE = {
    "CO": 4000,
    "NO2": 50,
    "SO2": 50,
    "PM10": 45,
    "PM2.5": 25
}

data_italy_ndvi = pd.read_csv("data/NDVI_italia.csv", index_col=0).rename(index = {"Valle d'Aosta/Vallée d’Aoste":"Valle d’Aosta/Vallée d’Aoste"}).loc[nuts_3_italy]

data_belgium_ndvi = pd.read_csv("data/NDVI_belgio.csv", index_col=0).rename(index = {"Arr. Brussel-Hoofdstad" : "Arr. de Bruxelles-Capitale/Arr. Brussel-Hoofdstad"}).loc[nuts_3_belgium]
 
data_total_ndvi = pd.concat([data_italy_ndvi, data_belgium_ndvi])

data_total_ndvi.columns = pd.to_datetime(data_total_ndvi.columns).strftime("%d/%m/%Y")
 
# Custom CSS for better styling
external_stylesheets = ['https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;700&display=swap']

app = Dash(__name__, external_stylesheets=external_stylesheets)

# Define a consistent color scheme
colors = {
    'background': '#f9f9f9',
    'text': '#333333',
    'primary': '#2c3e50',
    'secondary': '#3498db',
    'accent': '#e74c3c',
    'light': '#ecf0f1'
}

app.layout = html.Div([
    # Header
    html.Div([
        html.H1("Health-Adjusted Air Quality Index Dashboard - NUTS-3 Regional Analysis",
                style={
                    'textAlign': 'center',
                    'color': colors['primary'],
                    'fontFamily': 'Roboto, sans-serif',
                    'fontSize': '36px',
                    'padding': '20px 0',
                    'marginBottom': '10px'
                })
    ], style={'backgroundColor': colors['light'], 'borderRadius': '8px', 'margin': '10px'}),

    # Main container
    html.Div([
        # Controls Panel
        html.Div([
            html.Div([
                html.H3("Dashboard Controls",
                        style={'color': colors['primary'], 'marginBottom': '20px', 'textAlign': 'center'}),

                # Date Range Selector
                html.Div([
                    html.Label("Select Date Range:", style={'fontWeight': 'bold', 'fontSize': '16px'}),
                    dcc.DatePickerRange(
                        id='date-range',
                        min_date_allowed="2024-01-01",
                        max_date_allowed="2024-12-31",
                        initial_visible_month="2024-01-01",
                        start_date="2024-01-01",
                        end_date="2024-12-31",
                        style={'marginTop': '10px', 'width': '100%'}
                    ),
                ], style={'marginBottom': '30px', 'padding': '10px'}),

                # Indicator Selector
                html.Div([
                    html.Label("Select Indicator:", style={'fontWeight': 'bold', 'fontSize': '16px'}),
                    dcc.Dropdown(
                        id='indicator-dropdown',
                        options=[{'label': i, 'value': i} for i in
                                 ["CO", "NO2", "SO2", "PM10", "PM2.5", "HAQI"]],
                        value="HAQI",
                        style={'marginTop': '10px'}
                    ),
                ], style={'marginBottom': '30px', 'padding': '10px'}),

                # NUTS-3 Region Selector
                html.Div([
                    html.Label("Select NUTS-3 Region:", style={'fontWeight': 'bold', 'fontSize': '16px'}),
                    dcc.Dropdown(
                        id='nuts3-dropdown',
                        options=[{'label': name, 'value': name} for name in sorted(nuts_3_italy + nuts_3_belgium)],
                        value="Caserta",
                        style={'marginTop': '10px'}
                    ),
                ], style={'marginBottom': '20px', 'padding': '10px'})
            ], style={'backgroundColor': 'white', 'padding': '20px', 'borderRadius': '8px',
                      'boxShadow': '0px 0px 10px rgba(0,0,0,0.1)'}),
            html.Img(
                src='https://eurostat.github.io/eubd2025_docs/_images/EU-Big-Data-Hackathon-2025_horiz_0.jpg',
                style={
                    'marginTop': '20px',
                    'marginLeft': '10px',
                    'height': '85px',  # Adjust the height as needed
                    'width': '320px'    # Adjust the width as needed
                }
            )
        ], style={'width': '20%', 'display': 'inline-block', 'verticalAlign': 'top', 'padding': '6px'}),

        # Map Section
        html.Div([
            html.Div([
                dcc.Graph(id='geospatial-map')
            ], style={'backgroundColor': 'white', 'padding': '15px', 'borderRadius': '8px',
                      'boxShadow': '0px 0px 10px rgba(0,0,0,0.1)'})
        ], style={'width': '75%', 'display': 'inline-block', 'verticalAlign': 'top', 'padding': '10px'})
    ], style={'marginBottom': '20px'}),

    # Second Row - Data Table
    html.Div([
        html.Div([
            html.H3("Regional Indicator Data",
                    style={'color': colors['primary'], 'textAlign': 'center', 'marginBottom': '15px'}),
            dash_table.DataTable(
                id='data-table',
                style_table={'height': '400px', 'overflowY': 'auto'},
                style_cell={
                    'textAlign': 'left',
                    'padding': '10px',
                    'fontFamily': 'Roboto, sans-serif',
                    'fontSize': '14px'
                },
                style_header={
                    'backgroundColor': colors['light'],
                    'fontWeight': 'bold',
                    'borderBottom': '2px solid ' + colors['primary'],
                    'fontSize': '16px'
                },
                style_data_conditional=[
                    {
                        'if': {'row_index': 'odd'},
                        'backgroundColor': 'rgb(248, 248, 248)'
                    }
                ],
                page_size=15,
            )
        ], style={'backgroundColor': 'white', 'padding': '20px', 'borderRadius': '8px',
                  'boxShadow': '0px 0px 10px rgba(0,0,0,0.1)'})
    ], style={'margin': '0 10px 20px 10px'}),

    # Third Row - Detail Visuals
    html.Div([
        # Time Series
        html.Div([
            html.Div([
                dcc.Graph(id='time-series')
            ], style={'backgroundColor': 'white', 'padding': '15px', 'borderRadius': '8px',
                      'boxShadow': '0px 0px 10px rgba(0,0,0,0.1)'})
        ], style={'width': '40%', 'display': 'inline-block', 'verticalAlign': 'top', 'padding': '10px'}),

        # Pie Chart
        html.Div([
            html.Div([
                dcc.Graph(id='pie-chart')
            ], style={'backgroundColor': 'white', 'padding': '15px', 'borderRadius': '8px',
                      'boxShadow': '0px 0px 10px rgba(0,0,0,0.1)', 'marginBottom': '20px'})
        ], style={'width': '25%', 'display': 'inline-block', 'verticalAlign': 'top', 'padding': '10px'}),

        # Histogram
        html.Div([
            html.Div([
                dcc.Graph(id='histogram')
            ], style={'backgroundColor': 'white', 'padding': '15px', 'borderRadius': '8px',
                      'boxShadow': '0px 0px 10px rgba(0,0,0,0.1)', 'marginBottom': '20px'})
        ], style={'width': '25%', 'display': 'inline-block', 'verticalAlign': 'top', 'padding': '10px'})
    ]),

    # Footer
    html.Div([
        html.P("Health-Adjusted Air Quality Index Dashboard | Data Source: EU Environmental Agency",
               style={'textAlign': 'center', 'color': '#666', 'padding': '20px'})
    ])
], style={'backgroundColor': colors['background'], 'fontFamily': 'Roboto, sans-serif', 'padding': '0 20px 20px 20px'})


# Add a new callback to handle the click event on the map
@app.callback(
    Output('geospatial-map', 'figure'),
    [Input('geospatial-map', 'clickData'),
     Input('date-range', 'start_date'),
     Input('date-range', 'end_date'),
     Input('indicator-dropdown', 'value')]
)
def highlight_region(clickData, start_date, end_date, indicator):
    selected_region = None
    if clickData and 'points' in clickData and clickData['points']:
        selected_region = clickData['points'][0]['location']
    
    # Toggle highlighting
    if selected_region and selected_region == clickData['points'][0]['location']:
        selected_region = None
    
    # Filter data based on date range and indicator
    indicator_table = build_indicators_table(data_total, data_total_ndvi, limiti_UE, date_range=(start_date, end_date))
    map_fig = plot_choropleth(geo_df, indicator_table, indicator, selected_region)

    return map_fig

# Update the existing callback for the first row to remove the map update
@app.callback(
    [Output('data-table', 'data'),
     Output('data-table', 'columns')],
    [Input('date-range', 'start_date'),
     Input('date-range', 'end_date'),
     Input('indicator-dropdown', 'value')]
)
def update_first_row(start_date, end_date, indicator):
    # Filter data based on date range and indicator
    indicator_table = build_indicators_table(data_total, data_total_ndvi, limiti_UE, date_range=(start_date, end_date))

    # Reset index to make region names a column
    df = indicator_table.reset_index()

    # Rename the index column to 'Region'
    df = df.rename(columns={'index': 'nuts3_name'})
    df = df.sort_values(by=indicator, ascending=False)
    # Round values to 3 decimal places for better display
    for col in df.columns:
        if col != 'nuts3_name':
            df[col] = df[col].round(3)

    table_data = df.to_dict('records')
    table_columns = [{"name": "Region", "id": "nuts3_name"}] + [
        {"name": col, "id": col} for col in ["CO", "NO2", "SO2", "PM10", "PM2.5", "HAQI"]
    ]

    return table_data, table_columns


@app.callback(
    [Output('time-series', 'figure'),
     Output('pie-chart', 'figure'),
     Output('histogram', 'figure')],
    [Input('nuts3-dropdown', 'value'),
     Input('date-range', 'start_date'),
     Input('date-range', 'end_date'),
     Input('indicator-dropdown', 'value')]
)
def update_second_row(nuts3_name, start_date, end_date, indicator):
    # Convert dates for filtering
    start_dt = pd.to_datetime(start_date)
    end_dt = pd.to_datetime(end_date)

    # Calculate date range duration
    date_range_days = (end_dt - start_dt).days + 1

    # Filter data based on NUTS-3 region and date range
    indicator_table = build_indicators_table(data_total, data_total_ndvi, limiti_UE, date_range=(start_date, end_date))

    # Create time series figure
    time_series_fig = plot_time_series_with_limit(nuts3_name, indicator, data_total, limiti_UE,
                                                  start_date=start_date, end_date=end_date)

    # Create pie chart for indicator distribution
    pie_fig = plot_pollutant_importance(indicator_table, nuts3_name)

    # Create histogram for the selected indicator
    histogram_fig = plot_histogram(nuts3_name, indicator, data_total, start_date=start_date, end_date=end_date)

    return time_series_fig, pie_fig, histogram_fig


if __name__ == '__main__':
    app.run_server(debug=True)