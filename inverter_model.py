import numpy as np
import plotly.graph_objs as go
from plotly.subplots import make_subplots
import pandas as pd
import math
from scipy.interpolate import make_interp_spline

dimport math

def inverter_model(
    V_dc: float,           # DC link voltage (V)
    I_out_rms: float,      # RMS output phase current (A)
    f_sw: float,           # Switching frequency (Hz)
    R_on: float,           # On-state resistance per switch (ohms)
    V_f: float,            # Diode forward voltage drop (V)
    E_on: float,           # Energy loss per switch-on event (J)
    E_off: float,          # Energy loss per switch-off event (J)
    V_out_rms: float,      # RMS output phase voltage (V)
    pf: float = 0.9       # Power Factor (assumed)
) -> dict:
    """
    Models a three-phase inverter to calculate losses and efficiency.
    """
    
    # 1. Conduction Loss Calculation
    P_cond_switches = 3 * (I_out_rms**2) * R_on
    P_cond_diodes = 3 * I_out_rms * V_f
    P_conduction = P_cond_switches + P_cond_diodes

    # 2. Switching Loss Calculation
    E_total_switch_cycle = E_on + E_off
    P_switching = 6 * E_total_switch_cycle * f_sw
    
    # 3. Total Loss Calculation
    P_losses = P_conduction + P_switching

    # 4. Power Calculation
    P_out_ac = math.sqrt(3) * V_out_rms * I_out_rms * pf
    P_in_dc = P_out_ac + P_losses
    
    efficiency = (P_out_ac / P_in_dc) * 100 if P_in_dc > 0 else 0

    return {
        "P_conduction": P_conduction,
        "P_switching": P_switching,
        "P_losses": P_losses,
        "P_out_ac": P_out_ac,
        "P_in_dc": P_in_dc,
        "efficiency_percent": efficiency,
    }