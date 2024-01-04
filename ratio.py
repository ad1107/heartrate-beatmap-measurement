import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.graph_objs as go

app = dash.Dash(__name__)

# Number of points to display in the graph
num_points = 100

# Initialize the app layout
app.layout = html.Div(children=[
    dcc.Graph(id='live-update-graph'),
    dcc.Input(id='input-number', type='number', value=1),
    dcc.Interval(
        id='interval-component',
        interval=1000,  # in milliseconds
        n_intervals=0
    )
])

# Initialize empty data for the graph
data = {'x': [], 'y': []}

@app.callback(Output('live-update-graph', 'figure'),
              [Input('interval-component', 'n_intervals'),
               Input('input-number', 'value')])
def update_graph(n_intervals, input_number):
    # Append new values to the data
    data['x'].append(n_intervals)
    data['y'].append(input_number)

    # Ensure data length does not exceed num_points
    data['x'] = data['x'][-num_points:]
    data['y'] = data['y'][-num_points:]

    # Create the Plotly figure
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=data['x'], y=data['y'], mode='lines', name='Ratio'))
    fig.update_layout(title='Real-time Updating Line Graph',
                      xaxis=dict(range=[max(0, n_intervals - num_points), n_intervals]),
                      yaxis=dict(range=[0, 10]))

    return fig

if __name__ == '__main__':
    app.run_server(debug=True)
