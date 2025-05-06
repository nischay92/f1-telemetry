import dash
from dash import dcc, html
from dash.dependencies import Output, Input
import json
import os

app = dash.Dash(__name__)

def component_box(width=140, height=60):
    return {
        'backgroundColor': 'grey',
        'width': f'{width}px',
        'height': f'{height}px',
        'display': 'flex',
        'alignItems': 'center',
        'justifyContent': 'center',
        'margin': '5px',
        'color': 'white',
        'fontWeight': 'bold'
    }

# Layout
app.layout = html.Div([
    html.H2("🏎️ F1 Telemetry Dashboard"),

    # Engine centered
    html.Div(id='engine', style={**component_box(width=200, height=80), 'margin': 'auto'}),

    # Front row
    html.Div([
        html.Div([
            html.Div(id='Front-Left-brake', style=component_box()),
            html.Div(id='Front-Left-tire', style=component_box())
        ], style={'display': 'inline-block'}),
        html.Div(style={'display': 'inline-block', 'width': '100px'}),  # Spacer
        html.Div([
            html.Div(id='Front-Right-tire', style=component_box()),
            html.Div(id='Front-Right-brake', style=component_box())
        ], style={'display': 'inline-block'})
    ], style={'marginTop': '20px', 'textAlign': 'center'}),

    # Rear row
    html.Div([
        html.Div([
            html.Div(id='Rear-Left-brake', style=component_box()),
            html.Div(id='Rear-Left-tire', style=component_box())
        ], style={'display': 'inline-block'}),
        html.Div(style={'display': 'inline-block', 'width': '100px'}),  # Spacer
        html.Div([
            html.Div(id='Rear-Right-tire', style=component_box()),
            html.Div(id='Rear-Right-brake', style=component_box())
        ], style={'display': 'inline-block'})
    ], style={'marginTop': '20px', 'textAlign': 'center'}),

    # Logs section
    html.H3("🚨 Logs:"),
    html.Div(id='log-box', style={
        'height': '200px', 'overflowY': 'scroll',
        'backgroundColor': '#f4f4f4', 'padding': '10px',
        'border': '1px solid #ccc', 'whiteSpace': 'pre-line'
    }),

    dcc.Interval(id='interval-component', interval=3000, n_intervals=0)
])

# Load telemetry
def load_telemetry():
    try:
        with open('./logs/telemetry_state.json') as f:  # Updated path
            return json.load(f)
    except Exception as e:
        print(f"Error loading telemetry: {e}")
        return None

# Read logs
def read_aggregator_logs():
    try:
        with open('./logs/aggregator.log', 'r') as f:  # Updated path
            lines = f.readlines()
        return "".join(lines[-20:])
    except Exception as e:
        print(f"Error reading logs: {e}")
        return "No logs found."

def color_status(status):
    return {'red': '#FF4C4C', 'yellow': '#FFD700', 'green': '#4CAF50'}.get(status, 'grey')

# Telemetry callback
@app.callback(
    [Output('engine', 'children'), Output('engine', 'style'),
     Output('Front-Left-tire', 'children'), Output('Front-Left-tire', 'style'),
     Output('Front-Right-tire', 'children'), Output('Front-Right-tire', 'style'),
     Output('Rear-Left-tire', 'children'), Output('Rear-Left-tire', 'style'),
     Output('Rear-Right-tire', 'children'), Output('Rear-Right-tire', 'style'),
     Output('Front-Left-brake', 'children'), Output('Front-Left-brake', 'style'),
     Output('Front-Right-brake', 'children'), Output('Front-Right-brake', 'style'),
     Output('Rear-Left-brake', 'children'), Output('Rear-Left-brake', 'style'),
     Output('Rear-Right-brake', 'children'), Output('Rear-Right-brake', 'style')],
    Input('interval-component', 'n_intervals')
)
def update_dashboard(n):
    data = load_telemetry()
    if not data:
        empty = ('No Data', component_box())
        return empty * 9

    # Engine
    engine_temp = data['engine'].get('temp', None)
    engine_status = data['engine'].get('status', 'grey')
    engine_data = f"Engine {engine_temp:.1f}°C" if engine_temp is not None else "Engine: N/A"
    engine_style = {**component_box(width=200, height=80), 'backgroundColor': color_status(engine_status), 'margin': 'auto'}

    # Tires
    tires = []
    for tire in ['Front-Left', 'Front-Right', 'Rear-Left', 'Rear-Right']:
        psi = data['tires'].get(tire, {}).get('psi', None)
        status = data['tires'].get(tire, {}).get('status', 'grey')
        psi_display = f"{tire} PSI: {psi:.1f}" if psi is not None else f"{tire} PSI: N/A"
        tire_style = {**component_box(), 'backgroundColor': color_status(status)}
        tires.append((psi_display, tire_style))

    # Brakes
    brakes = []
    for brake in ['Front-Left', 'Front-Right', 'Rear-Left', 'Rear-Right']:
        temp = data['brakes'].get(brake, {}).get('temp', None)
        status = data['brakes'].get(brake, {}).get('status', 'grey')
        temp_display = f"{brake} Temp: {temp:.1f}°C" if temp is not None else f"{brake} Temp: N/A"
        brake_style = {**component_box(), 'backgroundColor': color_status(status)}
        brakes.append((temp_display, brake_style))

    return (engine_data, engine_style,
            tires[0][0], tires[0][1], tires[1][0], tires[1][1],
            tires[2][0], tires[2][1], tires[3][0], tires[3][1],
            brakes[0][0], brakes[0][1], brakes[1][0], brakes[1][1],
            brakes[2][0], brakes[2][1], brakes[3][0], brakes[3][1])

# Logs callback
@app.callback(
    Output('log-box', 'children'),
    Input('interval-component', 'n_intervals')
)
def update_logs(n):
    return read_aggregator_logs()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
