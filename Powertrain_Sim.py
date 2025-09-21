import streamlit as st
import numpy as np
import pandas as pd
import math
import plotly.graph_objs as go
from plotly.subplots import make_subplots
from motor_graphs_powertrain import EngineGearRatioCalculator, TorqueSpeedGraph, PowerSpeedGraph


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
    
    # Convert the list of tuples to a Pandas DataFrame
    df = pd.DataFrame(rows, columns=headers)
   
    # Display the styled DataFrame
    st.dataframe(df, use_container_width=True)

class EngineGearRatioCalculator:
    def __init__(self, engines, scenarios):
        self.engines = engines
        self.scenarios = scenarios
        self.max_speed_gearbox = 6
        
    def calculate_gear_ratios(self):
        gear_ratios = {}
        condition_map = {
            'low_speed': ('low_speed', 'high_torque'),    
            'high_speed': ('high_speed', 'low_torque'),  #high speed but I can limit it no?
            'idle': ('low_speed', 'high_torque')
        }
        
        for scenario_index, scenario in enumerate(self.scenarios):
            gear_ratios[scenario_index] = {}
            output_speed = scenario['max_speed_vehicle']
            output_torque = scenario['torque']
            condition = scenario['condition']
            driveline_efficiency = 1
            for engine, characteristics in self.engines.items():
                speed_type, torque_type = condition_map.get(condition, condition_map['idle'])
                speed = characteristics[speed_type]
                torque =characteristics[torque_type]
                # Calculate gear ratio
                #gear_ratio = round((output_torque/ torque) * driveline_efficiency)
                gear_ratio=math.ceil((output_torque)/torque)-0.5
                eta=0.86
                speed /=gear_ratio
                torque *= gear_ratio
                power_kw = torque * (2 * np.pi / 60) * speed/(eta*1000)
                gear_ratios.setdefault(engine, {})[scenario_index] = {
                    'Gear Ratio': round(gear_ratio,2),
                    'Engine Speed': round(speed),
                    'Engine Torque': round(torque),
                    'Condition': condition,
                    'vehicle power': scenario['power'],
                    'Output Speed': round(output_speed),
                    'Output Torque': round(output_torque),
                }
               

        return gear_ratios

    def create_table(self):
        gear_ratios = self.calculate_gear_ratios()
        headers = ['Engine',   'Engine Speed (RPM)', 'Engine Torque (Nm)', 'Torque Gear Ratio','Condition','vehicle power (kW)', 'Output Speed (RPM)', 'Output Torque (Nm)']
        rows = []

        for engine, scenarios in gear_ratios.items():
            for scenario, data in scenarios.items():
                rows.append([engine,data['Engine Speed'], data['Engine Torque'], data['Gear Ratio'],   data['Condition'], data['vehicle power'], data['Output Speed'], data['Output Torque']])

        return headers, rows


class TorqueSpeedGraph:
    def __init__(self, engines, scenarios, gear_ratios):
        self.engines = engines
        self.scenarios = scenarios
        self.gear_ratios = gear_ratios

    def plot(self):
        # Init figure Torque[Nm]-Speed[rpm]
        fig = go.Figure()
        colors = ['blue', 'orange', 'green', 'red', 'purple', 'brown', 'pink', 'gray']
        
        # Plot torque-speed graph for engines
        for idx, (engine, characteristics) in enumerate(self.engines.items()):
            base_speed = np.linspace(0, characteristics['low_speed'], 3)
            high_speed = np.linspace(characteristics['low_speed'], characteristics['high_speed'], 3)
            base_torque = np.full(3, characteristics['high_torque']) 
            high_torque = np.linspace(characteristics['high_torque'], characteristics['low_torque'], 3) 
            fig.add_trace(go.Scatter(x=np.concatenate((base_speed, high_speed)), 
                                     y=np.concatenate((base_torque, high_torque)), 
                                     mode='lines', name=f"{engine} - Torque [Nm] ", line=dict(color=colors[idx])))

        fig.update_xaxes(title_text='Speed (RPM)')
        fig.update_yaxes(title_text='Torque (Nm)')
        return fig


class PowerSpeedGraph:
    def __init__(self, engines, scenarios, gear_ratios):
        self.engines = engines
        self.scenarios = scenarios
        self.gear_ratios = gear_ratios

    def plot(self):
        fig = go.Figure()
        final_gear_ratio=3.5

        colors = ['blue', 'orange', 'green', 'red', 'purple', 'brown', 'pink', 'gray']
        engine_traces = {}  # To avoid duplicate traces
        
        # Plot power vs speed for engines
        for engine, characteristics in self.engines.items():
            engine_traces[engine] = False  # Flag to track if trace has been added
            for scenario in self.scenarios:
                condition = scenario['condition']
                speed_range = np.linspace(characteristics['low_speed'], characteristics['high_speed'],100)  # Reduced resolution to 10 points
                torque = np.linspace(characteristics['high_torque'], characteristics['low_torque'],100)  # Reduced resolution to 10 points
                base_torque = np.full(100, characteristics['high_torque'])
                speed_cst=np.linspace(0, characteristics['low_speed'],100)

                # Retrieve the gear ratio for the current engine and scenario
                gear_ratio = self.gear_ratios[engine][self.scenarios.index(scenario)]['Gear Ratio']
                eta=0.87

                base_torque=base_torque*gear_ratio
                torque=torque*gear_ratio
                speed_cst=speed_cst/gear_ratio
                speed_range=speed_range/gear_ratio
                # Calculate power using the gear ratio
                power_cst=(base_torque*(2*np.pi/60)*(speed_cst))/1000
                power = ((torque) * (2 * np.pi / 60) * (speed_range)) /(1000)  # Convert to kW
                
                # Add trace only if it hasn't been added yet for the current engine
                if not engine_traces[engine]:
                    fig.add_trace(go.Scatter(x=np.concatenate((speed_cst,speed_range)), y=np.concatenate((power_cst, power)), mode='lines', name=f"{engine} - Power [kW]", line=dict(color=colors[list(self.engines.keys()).index(engine)])))
                    engine_traces[engine] = True
            
        
        low_speed = []
        medium_speed = []
        high_speed = []
        low_torque = []
        medium_torque = []
        high_torque = []

        for scenario in self.scenarios:
            condition = scenario['condition']
            if condition == 'high_speed':
                high_speed.append(scenario['max_speed_vehicle'])
                low_torque.append(scenario['power'])
            elif condition == 'low_speed':
                low_speed.append(scenario['max_speed_vehicle'])
                high_torque.append(scenario['power'])
            else:
                medium_speed.append(scenario['max_speed_vehicle'])
                medium_torque.append(scenario['power'])
        # Interpolate the points using spline interpolation
        spl = make_interp_spline(np.concatenate((low_speed, medium_speed, high_speed)),
                                np.concatenate((high_torque, medium_torque, low_torque)),
                                k=2)  

        # Generate a denser set of points for smoother curve
        x_new = np.linspace(np.concatenate((low_speed, medium_speed, high_speed)).min(),
                            np.concatenate((low_speed, medium_speed, high_speed)).max(), 300)
        y_new = spl(x_new)

        fig.add_trace(go.Scatter(x=x_new, y=y_new, mode='lines', name="Vehicle", line=dict(dash='dash')))
        fig.update_xaxes(title_text='Speed (RPM)')
        fig.update_yaxes(title_text='Power (kW)')
        fig.update_layout(title_text='Power-Speed Graph')
        return fig
       
