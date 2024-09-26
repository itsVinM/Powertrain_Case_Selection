import numpy as np
import plotly.graph_objs as go
from plotly.subplots import make_subplots
import pandas as pd
import math
from scipy.interpolate import make_interp_spline
from motor_graphs_powertrain import *

# Define vehicle scenarios with realistic gearbox speeds
scenarios = [
    {'max_speed_vehicle': 1768.39, 'torque': 352, 'power': 65.167, 'max_speed_gearbox':6, 'condition':'high_speed'},  
    {'max_speed_vehicle': 88.42, 'torque': 6530, 'power': 60.467, 'max_speed_gearbox':6, 'condition':'low_speed'},  
    {'max_speed_vehicle': 442.1, 'torque': 3020, 'power': 139.81, 'max_speed_gearbox':6, 'condition':'idle'}     
]

# Define engine characteristics
engines = {
    'Engine1': {'low_speed': 2000, 'high_speed': 8000, 'high_torque': 1000, 'low_torque': 200},
    'Engine2': {'low_speed': 2300, 'high_speed': 8900, 'high_torque': 500, 'low_torque': 110},
    'Engine3': {'low_speed': 3000, 'high_speed': 10000, 'high_torque': 1000, 'low_torque': 60},
    'Engine4': {'low_speed': 2500, 'high_speed': 8500, 'high_torque': 465, 'low_torque': 110},
    'Engine5': {'low_speed': 2000, 'high_speed': 10000, 'high_torque': 510, 'low_torque': 100},
    'Engine6': {'low_speed': 4000, 'high_speed': 8000, 'high_torque': 200, 'low_torque': 115},
    'Engine7': {'low_speed': 3500, 'high_speed': 8500, 'high_torque': 500, 'low_torque': 160},
    'Engine8': {'low_speed': 3000, 'high_speed': 9000, 'high_torque': 700, 'low_torque': 100}
}

calculator = EngineGearRatioCalculator(engines, scenarios)
# Calculate the gear ratios for each motor-gearbox combination
gear_ratios = calculator.calculate_gear_ratios()
# Create instances of TorqueSpeedGraph and PowerSpeedGraph
torque_speed_graph = TorqueSpeedGraph(engines, scenarios, gear_ratios)
power_speed_graph = PowerSpeedGraph(engines, scenarios, gear_ratios)

# Plot torque-speed and power-speed graphs
fig_torque_speed = torque_speed_graph.plot()
fig_power_speed = power_speed_graph.plot()

combined_fig = make_subplots(rows=1, cols=2, subplot_titles=('Torque-Speed Graph', 'Power-Speed Graph'))

# Add torque-speed graph to the first subplot
for trace in fig_torque_speed['data']:
    combined_fig.add_trace(trace, row=1, col=1)

# Add power-speed graph to the second subplot
for trace in fig_power_speed['data']:
    combined_fig.add_trace(trace, row=1, col=2)

# Set layout for the combined figure
combined_fig.update_xaxes(title_text='Speed (RPM)', row=1, col=1)
combined_fig.update_yaxes(title_text='Torque (Nm)', row=1, col=1)
combined_fig.update_xaxes(title_text='Speed (RPM)', row=2, col=1)
combined_fig.update_yaxes(title_text='Power (kW)', row=2, col=1)

# Update layout titles and display the combined figure
combined_fig.show()

# Create an instance of EngineGearRatioCalculator
calculator = EngineGearRatioCalculator(engines, scenarios)

# Create the table
headers, rows = calculator.create_table()


engine_colors = {
            'Engine1': 'whitesmoke',
            'Engine3': 'snow',
            'Engine7': 'whitesmoke',
}
      
# Create Plotly table trace
table_trace = go.Table(
    header=dict(values=headers),
    cells=dict(
        values=list(zip(*rows)),
        # Set the background color for each cell based on the engine number
        fill=dict(color=[engine_colors.get(row[0], 'white') for row in rows])
    )
)

# Create Plotly figure with the table trace
fig = go.Figure(data=table_trace)

# Set layout for the table
fig.update_layout(title='Gear Ratios Table')

# Display the table
fig.show()
