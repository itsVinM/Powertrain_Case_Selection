import streamlit as st
import numpy as np
import pandas as pd
import math
import plotly.graph_objs as go
from plotly.subplots import make_subplots
from motor_graphs_powertrain import EngineGearRatioCalculator, TorqueSpeedGraph, PowerSpeedGraph
from inverter_model import inverter_model

st.set_page_config(
      page_title="Powertrain calculator",
      page_icon=":car",
      layout="wide"
      )

## App Layout and Content

st.title("Powertrain Performance Analysis")
st.markdown("This application displays the torque-speed and power-speed curves for various engine scenarios and a corresponding table of gear ratios.")

# ---

tab1, tab2, tab3=st.tabs(["Inputs",'Vehicle performance Graphs', 'Power electronics performances'])
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
        "max_speed_vehicle": st.column_config.NumberColumn(
            "Vehicle Speed (m/s)",
            help="Maximum vehicle speed for the scenario.",
            format="%.2f",
        ),
        "torque": st.column_config.NumberColumn(
            "Wheel Torque (Nm)",
            help="Torque at the wheels for the scenario.",
        ),
        "power": st.column_config.NumberColumn(
            "Required Power (kW)",
            help="Power required for the scenario.",
            format="%.3f",
        ),
        "max_speed_gearbox": st.column_config.NumberColumn(
            "Gearbox Speed (RPM)",
            help="The maximum speed of the gearbox.",
        ),
        "condition": st.column_config.TextColumn(
            "Driving Condition",
            help="e.g., high_speed, low_speed, idle.",
        ),
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
    edited_engines_df = st.data_editor(
    engines_df,
    num_rows="dynamic",
    column_config={
        "Engine": st.column_config.TextColumn(
            "Engine Name",
            help="Name of the engine model.",
        ),
        "low_speed": st.column_config.NumberColumn(
            "Min Speed (RPM)",
            help="Minimum operating speed of the engine.",
        ),
        "high_speed": st.column_config.NumberColumn(
            "Max Speed (RPM)",
            help="Maximum operating speed of the engine.",
        ),
        "low_torque": st.column_config.NumberColumn(
            "Min Torque (Nm)",
            help="Torque at the low speed.",
        ),
        "high_torque": st.column_config.NumberColumn(
            "Max Torque (Nm)",
            help="Torque at the high speed.",
        ),
    }
)
    # Convert the edited DataFrame back to the required dictionary format
    user_engines = edited_engines_df.set_index('Engine').T.to_dict()

    # ---
    st.divider()

with tab2:
    ## Plotting Graphs
    

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
    
    # Convert the list of tuples to a Pandas DataFrame
    df = pd.DataFrame(rows, columns=headers)
   
    # Display the styled DataFrame
    st.dataframe(df, use_container_width=True)

with tab3:
    
    st.markdown("Enter the characteristics of your power inverter to analyze its performance metrics.")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Inverter Parameters")
        # Use a slider for DC Voltage to show a typical range
        v_dc = st.slider("DC Link Voltage (V)", min_value=200.0, max_value=800.0, value=400.0, step=10.0)

        # Numerical inputs for semiconductor properties
        r_on = st.number_input("On-state Resistance (R_on) [ohms]", min_value=0.001, max_value=0.1, value=0.01, format="%.4f")
        v_f = st.number_input("Diode Forward Voltage (V_f) [V]", min_value=0.5, max_value=2.0, value=1.0, format="%.2f")
        e_on = st.number_input("On-state Energy Loss (E_on) [mJ]", min_value=0.1, max_value=5.0, value=1.5, format="%.2f") * 1e-3
        e_off = st.number_input("Off-state Energy Loss (E_off) [mJ]", min_value=0.1, max_value=5.0, value=1.0, format="%.2f") * 1e-3
        
        # A dropdown for switching frequency, showing common options
        f_sw_khz = st.selectbox("Switching Frequency (f_sw) [kHz]", [10, 20, 50, 100], index=1)
        f_sw = f_sw_khz * 1000

    with col2:
        st.subheader("Analysis Results")
        
        # We'll tie the inverter analysis to a specific vehicle scenario for context.
        st.markdown("Choose a scenario from the 'Inputs' tab to analyze the inverter's performance at that operating point.")
        scenario_names = [scenario['condition'] for scenario in user_scenarios]
        selected_scenario_name = st.selectbox("Select Scenario for Analysis", scenario_names)

        # Get the required power and torque for the selected scenario
        selected_scenario = next((item for item in user_scenarios if item['condition'] == selected_scenario_name), None)
        if selected_scenario:
            required_power_kw = selected_scenario['power']
            required_torque_nm = selected_scenario['torque']
            
            # Use the required power to estimate the AC output current (a simplified step for the app)
            # Assuming a simplified relationship: P = sqrt(3) * V_dc * I_out_rms
            # This is a simplification; a more complex model would consider modulation index etc.
            ac_power_watt = required_power_kw * 1000
            
            if v_dc > 0:
                # Assuming AC voltage is proportional to DC voltage (V_ac_rms = 0.707 * V_dc)
                # I_out_rms = P_ac / (sqrt(3) * V_ac_rms)
                # Simplifying further for app purposes:
                i_out_rms = ac_power_watt / (v_dc * 0.9)  # 0.9 is an arbitrary power conversion factor
                
                # Run the inverter model with the selected parameters
                inverter_metrics = inverter_model(
                    V_dc=v_dc,
                    I_out_rms=i_out_rms,
                    f_sw=f_sw,
                    R_on=r_on,
                    V_f=v_f,
                    E_on=e_on,
                    E_off=e_off
                )

                # Display the key performance metrics
                st.metric(label=f"AC Output Power for '{selected_scenario_name}'", value=f"{inverter_metrics['P_out'] / 1000:.2f} kW")
                st.metric(label="Calculated Inverter Losses", value=f"{inverter_metrics['P_losses']:.2f} W")
                st.metric(label="Overall Inverter Efficiency", value=f"{inverter_metrics['efficiency_percent']:.2f}%")
                st.metric(label="DC Input Power", value=f"{inverter_metrics['P_in'] / 1000:.2f} kW")
            else:
                st.error("DC Link Voltage must be greater than zero.")
        else:
            st.warning("Please select a valid scenario from the 'Inputs' tab.")

    st.markdown("---")

    # Optional: Plotting a simple efficiency curve to demonstrate model capability
    st.subheader("Inverter Efficiency Curve")
    st.markdown("This graph shows the inverter's efficiency across a range of output currents.")

    current_range = np.linspace(5, 200, 50)  # Analyze current from 5A to 200A
    efficiency_values = []
    
    for i_rms in current_range:
        results = inverter_model(
            V_dc=v_dc,
            I_out_rms=i_rms,
            f_sw=f_sw,
            R_on=r_on,
            V_f=v_f,
            E_on=e_on,
            E_off=e_off
        )
        efficiency_values.append(results['efficiency_percent'])

    efficiency_df = pd.DataFrame({
        'Output Current (A)': current_range,
        'Efficiency (%)': efficiency_values
    })

    fig = go.Figure(data=go.Scatter(x=efficiency_df['Output Current (A)'], y=efficiency_df['Efficiency (%)'], mode='lines+markers'))
    fig.update_layout(title='Inverter Efficiency vs. Output Current',
                      xaxis_title='Output Current (A)',
                      yaxis_title='Efficiency (%)',
                      yaxis_range=[70, 100])
    
    st.plotly_chart(fig, use_container_width=True)

