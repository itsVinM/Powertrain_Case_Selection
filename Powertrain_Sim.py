import streamlit as st
import numpy as np
import plotly.graph_objs as go
from plotly.subplots import make_subplots
import pandas as pd
import math
from scipy.interpolate import make_interp_spline
from motor_graphs_powertrain import *

st.set_page_config(
      page_title="Powertrain calculator",
      page_icon=":car",
      layout="wide"
      )

## App Layout and Content

st.title("Powertrain Performance Analysis")
st.markdown("This application displays the torque-speed and power-speed curves for various engine scenarios and a corresponding table of gear ratios.")

# ---

tab1, tab2 =st.tabs(["User-defined inputs",'Plots'])
## User-Defined Inputs

with tab1:

    # Define default vehicle scenarios as a DataFrame
    scenarios_df = pd.DataFrame([
        {'max_speed_vehicle': 1768.39, 'torque': 352, 'power': 65.167, 'max_speed_gearbox': 6, 'condition': 'high_speed'},
        {'max_speed_vehicle': 88.42, 'torque': 6530, 'power': 60.467, 'max_speed_gearbox': 6, 'condition': 'low_speed'},
        {'max_speed_vehicle': 442.1, 'torque': 3020, 'power': 139.81, 'max_speed_gearbox': 6, 'condition': 'idle'}
    ])

    # Use st.data_editor for an editable scenarios table
    st.subheader("Vehicle Scenarios")
    edited_scenarios_df = st.data_editor(
        scenarios_df,
        num_rows="dynamic",  # Allows adding or removing rows
        column_config={
            "condition": st.column_config.TextColumn(
                "Condition", help="e.g., high_speed, low_speed, idle"
            )
        }
    )

    # Convert the edited DataFrame back to a list of dictionaries for the class
    user_scenarios = edited_scenarios_df.to_dict('records')

    st.markdown("---")

    # Define default engine characteristics as a DataFrame
    engines_df = pd.DataFrame([
        {'Engine': 'Engine1', 'low_speed': 2000, 'high_speed': 8000, 'high_torque': 1000, 'low_torque': 200},
        {'Engine': 'Engine2', 'low_speed': 2300, 'high_speed': 8900, 'high_torque': 500, 'low_torque': 110},
        {'Engine': 'Engine3', 'low_speed': 3000, 'high_speed': 10000, 'high_torque': 1000, 'low_torque': 60},
        {'Engine': 'Engine4', 'low_speed': 2500, 'high_speed': 8500, 'high_torque': 465, 'low_torque': 110},
        {'Engine': 'Engine5', 'low_speed': 2000, 'high_speed': 10000, 'high_torque': 510, 'low_torque': 100},
        {'Engine': 'Engine6', 'low_speed': 4000, 'high_speed': 8000, 'high_torque': 200, 'low_torque': 115},
        {'Engine': 'Engine7', 'low_speed': 3500, 'high_speed': 8500, 'high_torque': 500, 'low_torque': 160},
        {'Engine': 'Engine8', 'low_speed': 3000, 'high_speed': 9000, 'high_torque': 700, 'low_torque': 100}
    ])

    # Use st.data_editor for an editable engines table
    st.subheader("Engine Characteristics")
    edited_engines_df = st.data_editor(engines_df, num_rows="dynamic")

    # Convert the edited DataFrame back to the required dictionary format
    user_engines = edited_engines_df.set_index('Engine').T.to_dict()

    # ---
    st.divider()

with tab2:
    ## Plotting Graphs
    st.header("Engine Performance Graphs")

    # Create instances of necessary classes using the user-defined data
    calculator = EngineGearRatioCalculator(user_engines, user_scenarios)
    gear_ratios = calculator.calculate_gear_ratios()
    torque_speed_graph = TorqueSpeedGraph(user_engines, user_scenarios, gear_ratios)
    power_speed_graph = PowerSpeedGraph(user_engines, user_scenarios, gear_ratios)

    # Plot torque-speed and power-speed graphs
    fig_torque_speed = torque_speed_graph.plot()
    fig_power_speed = power_speed_graph.plot()

    # Combine the two graphs into a single subplot figure
    combined_fig = make_subplots(rows=1, cols=2, subplot_titles=('Torque-Speed Graph', 'Power-Speed Graph'))

    for trace in fig_torque_speed['data']:
        combined_fig.add_trace(trace, row=1, col=1)

    for trace in fig_power_speed['data']:
        combined_fig.add_trace(trace, row=1, col=2)

    combined_fig.update_xaxes(title_text='Speed (RPM)', row=1, col=1)
    combined_fig.update_yaxes(title_text='Torque (Nm)', row=1, col=1)
    combined_fig.update_xaxes(title_text='Speed (RPM)', row=1, col=2)
    combined_fig.update_yaxes(title_text='Power (kW)', row=1, col=2)

    st.plotly_chart(combined_fig, use_container_width=True)

    # ---
    st.divider()

    # ---
    ## Gear Ratios Table
    st.header("Gear Ratios Table")

    headers, rows = calculator.create_table()

    # Updated color palette for better visibility
    engine_colors = {
        'Engine1': "#021E39",  
        'Engine3': "#034703",  
        'Engine7': "#420505", 
    }

    # Convert the list of tuples to a Pandas DataFrame
    df = pd.DataFrame(rows, columns=headers)

    # Apply a custom background color to the 'Engine' column based on the dictionary
    def highlight_rows(row):
        color = engine_colors.get(row['Engine'], 'white')
        return [f'background-color: {color}' for _ in row]

    # Check if the 'Engine' column exists before applying the style
    if 'Engine' in df.columns:
        styled_df = df.style.apply(highlight_rows, axis=1)
    else:
        styled_df = df.style

    # Display the styled DataFrame
    st.dataframe(styled_df, use_container_width=True)

