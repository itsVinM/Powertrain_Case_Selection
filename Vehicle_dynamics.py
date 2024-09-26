import numpy as np


""" 
Define longitudinal vehicle dynamics where I want to find the propulsive force

param:
    F_prop=F_Aero+F_Rolling+F_Gravity+F_Inertial
    
    F_Aero=0.5*rho*A_F*(V_x+V_wind)^2
        V_wind=0 m/s 
        A_F from formula *82% ~ 1.88m2 » formula True only for vehicle with mass 800Kg-2000Kg
        Cd=0.25-0.3 » choose the latter for the worst case
    
    F_Rolling=Cr*m*g
    F_Gravity=m*g*sin(theta)
    F_Inertia=m*a     
"""

def longitudinal_dynamics(speed, gradient, acceleration, mass):
    v=speed/3.6             #conversion in [m/s]
    theta=gradient          #gradient uphill 10%
    a=acceleration          #vehicle acceleration in [m/s2]
    m=mass                  #vehicle mass in [Kg]
    g=9.81                  #[m/s2]
    Cr=0.01                 #rolling resitance 
    Caero=0.3

    F_prop=round(((0.5*1.225*1.88*(v**2)*Caero)+(Cr*m*g*np.cos(theta))+(g*m*np.sin(theta))+m*a),2)
    Power=round(F_prop*v)/1000
    Torque=F_prop*0.3

    return F_prop, Power, round(Torque), round((v/0.3)*30/np.pi,2), round(v,2)


print("Case 1 ->> only v=200km/hr")
print("Force[N], Power[kW], Torque [Nm], w[rpm]:")
print(longitudinal_dynamics(200, 0, 0, 2000))
print(" ")
print("Case 2 ->> v=10km/hr, 10% gradient uphill, a=9.81")
print("Force[N], Power[kW], Torque [Nm], w[rpm]:")
print(longitudinal_dynamics(10, 0.0996, 9.81, 2000))
print(" ")
print("Case 3 ->> v=50km/hr a=g/2 0% gradient uphill")
print("Force[N], Power[kW], Torque [Nm], w[rpm]:")
print(longitudinal_dynamics(50, 0, 9.81/2, 2000))
print(" ")
