from itertools import product

"""
# This module performs thermal insulation calculations according to DIN EN ISO 6946.
Thermal transmittance, also known as U-value, is the rate of transfer of heat through a structure 
(which can be a single material or a composite), divided by the difference in temperature across that structure. 
The units of measurement are W/m²K. 
The better-insulated a structure is, the lower the U-value will be.
 Thermal transmittance takes heat loss due to conduction, convection and radiation into account.
"""
# Setting the standard values for internal and external thermal resistance
rsi = 0.13 # Depending on the situation, a different standard value must be used
rse = 0.04 # je nach Situation muss ein anderer Norm-Wert verwendet werden

#We take into account only the following 3 layers
Spundschalung = [[0.022, 0.025, 0.027], 0.13] 
Zellulosefaserdämmung = [[0.16, 0.18, 0.20, 0.22, 0.24, 0.26, 0.28, 0.30, 0.32, 0.34, 0.36],0.038]
Gipsfaserplatte = [[0.010, 0.0125, 0.015,  0.018], 0.32]

combined = {
    "Spundschalung": Spundschalung,
    "Zellulosefaserdämmung": Zellulosefaserdämmung,
    "Gipsfaserplatte": Gipsfaserplatte
}
rsi = 0.13
rse = 0.04
# Should you keep the overall thickness constant ? but other layers does not match
def get_U_value_combination(combined, rsi = 0.13, rse = 0.04):
    combinations = list(product(*[v[0] for v in combined.values()]))
    lambdas = [v[1] for v in combined.values()]
    U_valiues_combinations = []
    for x,y,z in combinations:
        R_total = rse  + (x/ lambdas[0] + y/lambdas[1] + z/lambdas[2]) + rsi
        U_value =  round(1/R_total, 3)
        U_valiues_combinations.append(U_value)
    # print(combinations)
    return  U_valiues_combinations, combinations

#coin toss kind of algorithm to get the U-value combinations
U_values, combo = get_U_value_combination(combined, rsi = 0.13, rse = 0.04)
print(min(U_values), max(U_values), len(U_values))

# test0 = [Spundschalung[0][0], Zellulosefaserdämmung[0][0], Gipsfaserplatte[0][0]]
# test1 = [Spundschalung[0][1], Zellulosefaserdämmung[0][0], Gipsfaserplatte[0][0]]
# U_value_0 =  rse  + (test0[0]/ Spundschalung[1] + test0[1]/Zellulosefaserdämmung[1] + test0[2]/Gipsfaserplatte[1]) + rsi
# U_value_1 =  rse  + (test1[0]/ Spundschalung[1] + test1[1]/Zellulosefaserdämmung[1] + test1[2]/Gipsfaserplatte[1]) + rsi

expected_U_value = 0.13 
tolerance = 0.01
for i,j in zip(U_values, combo):
    if abs(i - expected_U_value )  <= tolerance:
        print(j)



# print(round(U_value_1 - U_value_0, 3))
# print([round(i / Spundschalung[1],3) for i in Spundschalung[0]])
# print([round(i/ Zellulosefaserdämmung[1],3) for i in Zellulosefaserdämmung[0]])
# print([round(i/ Gipsfaserplatte[1],3) for i in Gipsfaserplatte[0]])
# In diesem Modul werden Wärmeschutzberechnungen nach DIN EN ISO 6946 durc
# hgeführt.
# Aktueller Stand: nur für homogene Bauteilaufbauten
# Als Input werden alle Schichtdicken und die korrespondierenden Lambda-Werte benötigt

# Berechnung des U-Werts des kompletten Aufbaus
def get_u_value(r_tot: float)-> float:
    return 1/r_tot

# Berechnung des R-Werts einer einzelnen Schicht im Aufbau
def get_r_wert(thickness: float, lambda_value: float)-> float:
    return thickness/lambda_value

# Calculation of the total R-value (thermal resistance) for the component assembly
# This calculation applies only to homogeneous assemblies. 
# What does homogeneous assemblies mean?
# The calculation of inhomogeneous assemblies with upper and lower limits needs to be added.
def get_r_tot(rsi: float,r_value: list[float],rse: float)->float:
    return rsi + sum(r_value) + rse

def get_overrall_U_value(aufbau, rsi = 0.13, rse = 0.04):
    return  1/(rsi + sum([i[0]/i[1] for i in aufbau]) + rse)


# Ein Beispielaufbau von innen nach aussen
# thickness and lambda_value, what does lambda_value mean? calculated in cm ? so all attributes / 1000
mein_bauteilaufbau=[[0.015,0.32], # 15mm Fermacell
                    [0.24,0.038], # 240mm Zellulosedämmung
                    [.022,0.13]] # 22mm Holzschalung

rsi = 0.13 # Depending on the situation, a different standard value must be used
rse = 0.04 # je nach Situation muss ein anderer Norm-Wert verwendet werden

# r_werte=[]
# for schicht in mein_bauteilaufbau:
#     r_werte.append(get_r_wert(schicht[0],schicht[1]))

# r_tot=get_r_tot(rsi,r_werte,rse)
# print(f'{r_tot} m2K/W')

# u_value=get_u_value(r_tot)
# print(f'{u_value} W/m2K')