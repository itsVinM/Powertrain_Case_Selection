import numpy as np
import plotly.graph_objs as go
from plotly.subplots import make_subplots
import pandas as pd
import math
from scipy.interpolate import make_interp_spline



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
       
