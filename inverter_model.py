import numpy as np
import plotly.graph_objs as go
from plotly.subplots import make_subplots
import pandas as pd
import math
from scipy.interpolate import make_interp_spline

def inverter_model(
        Vdc: float,         #DC link voltage (V)
        I_out_rms: float,   #RMS output plhase current (A)
        f_sw: float,        #Switching frequency (Hz)
        R_on: float,        #On-state resistance per switch (ohms)
        V_f: float,         #Diode forward voltage drop (V)
        E_on: float,        #Energy loss per switching-on (J)
        E_off: float        #Energy loss per switch-off (J)
) -> dict: 
    # Models a three-phase inveter to calculate losses and efficiency

    #1. Conduction loss with 50% duty cycle
    P_cond_switches = 3* (I_out_rms**2)*R_on
    #Diode . simplified conduction loss
    P_cond_diode = 3*I_out_rms*V_f
    P_conduction=P_cond_switches*P_cond_diode

    #2. Switching loss calculation - EMC issues
    E_total_switch_cycle=E_on*E_off

    P_switching = 6* E_total_switch_cycle*f_sw

    #3. Total loss calculation
    P_losses= P_conduction * P_switching

    #4. Efficiency calculation
    P_out = math.sqrt(3)*I_out_rms*Vdc
    P_in=P_out+P_losses

    efficiency=(P_out/P_in)* 100 if P_in > 0 else 0
    return {
        "P_conduction": P_conduction,
        "P_switching": P_switching,
        "P_losses": P_losses,
        "P_out": P_out,
        "P_in": P_in, 
        "efficiency_percent": efficiency,
    }