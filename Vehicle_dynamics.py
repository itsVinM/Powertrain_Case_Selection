import streamlit as st
import numpy as np

# ---
## Longitudinal Vehicle Dynamics Function

def longitudinal_dynamics(speed, gradient, acceleration, mass):
    """
    Calculates the propulsive force and related metrics for a vehicle.

    Args:
        speed (float): Vehicle speed in km/h.
        gradient (float): Road gradient in percentage (%).
        acceleration (float): Vehicle acceleration in m/s^2.
        mass (float): Vehicle mass in kg.

    Returns:
        tuple: A tuple containing F_prop (N), Power (kW), Torque (Nm), 
               w_rpm (rpm), and v_ms (m/s).
    """
    v = speed / 3.6  # Conversion to m/s
    theta = np.arctan(gradient / 100.0) # Convert % gradient to angle in radians
    a = acceleration
    m = mass
    g = 9.81  # m/s^2
    Cr = 0.01  # Rolling resistance coefficient
    Caero = 0.3 # Aerodynamic drag coefficient
    A_F = 1.88 # Frontal area in m^2
    rho = 1.225 # Air density in kg/m^3
    r_wheel = 0.3 # Wheel radius in meters

    # Force calculations
    F_aero = 0.5 * rho * A_F * (v**2) * Caero
    F_rolling = Cr * m * g * np.cos(theta)
    F_gravity = g * m * np.sin(theta)
    F_inertia = m * a
    F_prop = F_aero + F_rolling + F_gravity + F_inertia

    # Power, Torque, and RPM calculations
    Power = F_prop * v / 1000  # Power in kW
    Torque = F_prop * r_wheel  # Torque in Nm
    w_rpm = (v / r_wheel) * 30 / np.pi  # Engine speed in rpm
    
    return round(F_prop, 2), round(Power, 2), round(Torque, 2), round(w_rpm, 2), round(v, 2)

# ---
## Streamlit App Layout

st.title("Vehicle Dynamics Calculator")
st.markdown("Adjust the parameters below to see the required propulsive force, power, and torque.")


st.header("Vehicle Parameters")

# Use columns to organize the input widgets
col1, col2 = st.columns(2)

with col1:
    speed = st.slider('Speed (km/h)', 0, 250, 50)
    acceleration = st.slider('Acceleration ($m/s^2$)', -5.0, 10.0, 0.0, 0.1)
    
with col2:
    gradient = st.slider('Road Gradient (%)', -10.0, 30.0, 0.0, 0.1)
    mass = st.number_input('Vehicle Mass (kg)', 800, 3000, 2000, 10)

# Calculate dynamics based on user input
force, power, torque, w_rpm, v_ms = longitudinal_dynamics(speed, gradient, acceleration, mass)

# ---
st.divider()

# ---
st.header("Calculated Results")
st.markdown(f"""
- **Propulsive Force:** `{force}` N
- **Required Power:** `{power}` kW
- **Required Torque:** `{torque}` Nm
- **Engine Speed (w):** `{w_rpm}` rpm
- **Vehicle Speed (v):** `{v_ms}` m/s
""")