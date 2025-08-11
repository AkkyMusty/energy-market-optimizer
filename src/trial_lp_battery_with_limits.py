import pulp
import matplotlib.pyplot as plt

# --------------------------
# 1. INPUT DATA
# --------------------------
hours = [1, 2, 3, 4, 5]          # toy 5-hour example
demand = {1: 90, 2: 100, 3: 80, 4: 110, 5: 95}

# Wind generation limits (per hour)
wind_max = {1: 40, 2: 50, 3: 30, 4: 45, 5: 35}

# Coal capacity now varies: reduced in peak hours 4 & 5 to create a shortage
coal_max = {1: 70, 2: 70, 3: 70, 4: 50, 5: 50}

# Costs ($/MWh)
coal_cost = {1: 50, 2: 50, 3: 50, 4: 80, 5: 80}
wind_cost = 20

# Battery parameters
battery_capacity = 40      # MWh
charge_max = 20            # MWh/h
discharge_max = 20         # MWh/h
charge_eff = 0.95
discharge_eff = 0.95

# initial state of charge
initial_energy = 0.0

# --------------------------
# 2. CREATE MODEL
# --------------------------
model = pulp.LpProblem("Battery_Required_by_Capacity_Limits", pulp.LpMinimize)

# --------------------------
# 3. DECISION VARIABLES
# --------------------------
coal = pulp.LpVariable.dicts("Coal", hours, lowBound=0)
wind = pulp.LpVariable.dicts("Wind", hours, lowBound=0)
charge = pulp.LpVariable.dicts("Charge", hours, lowBound=0, upBound=charge_max)
discharge = pulp.LpVariable.dicts("Discharge", hours, lowBound=0, upBound=discharge_max)
energy = pulp.LpVariable.dicts("Energy", hours, lowBound=0, upBound=battery_capacity)

# --------------------------
# 4. OBJECTIVE
# --------------------------
# Minimize generation cost (charging cost is included because charging requires generation)
model += pulp.lpSum(coal_cost[h] * coal[h] + wind_cost * wind[h] for h in hours), "TotalCost"

# --------------------------
# 5. CONSTRAINTS
# --------------------------
for h in hours:
    # generation capacity limits
    model += coal[h] <= coal_max[h], f"CoalCap_hour_{h}"
    model += wind[h] <= wind_max[h], f"WindCap_hour_{h}"

    # power balance: generation + discharge == demand + charge
    model += coal[h] + wind[h] + discharge[h] == demand[h] + charge[h], f"PowerBalance_hour_{h}"

    # battery energy limits (energy variable bounds already enforce 0..battery_capacity)
    model += energy[h] <= battery_capacity, f"BatteryCap_hour_{h}"

# energy dynamics (time coupling)
for idx, h in enumerate(hours):
    if idx == 0:
        # energy at end of hour 1
        model += energy[h] == initial_energy + charge_eff * charge[h] - discharge[h] / discharge_eff, f"EnergyBalance_hour_{h}"
    else:
        prev = hours[idx - 1]
        model += energy[h] == energy[prev] + charge_eff * charge[h] - discharge[h] / discharge_eff, f"EnergyBalance_hour_{h}"

# Optional: require battery to be empty at the end (forces use within horizon)
model += energy[hours[-1]] == 0.0, "EndOfHorizon_SOC"

# --------------------------
# 6. SOLVE
# --------------------------
model.solve()

# --------------------------
# 7. OUTPUT RESULTS
# --------------------------
print("Status:", pulp.LpStatus[model.status])
print("Total Cost ($) =", pulp.value(model.objective))
print()

coal_out = []
wind_out = []
charge_out = []
discharge_out = []
energy_out = []

for h in hours:
    c = coal[h].varValue
    w = wind[h].varValue
    ch = charge[h].varValue
    dis = discharge[h].varValue
    e = energy[h].varValue

    coal_out.append(c)
    wind_out.append(w)
    charge_out.append(ch)
    discharge_out.append(dis)
    energy_out.append(e)

    print(f"Hour {h}: Coal={c:.2f}, Wind={w:.2f}, Charge={ch:.2f}, Discharge={dis:.2f}, Energy={e:.2f}")

# --------------------------
# 8. PLOT (visualize dispatch & battery SOC)
# --------------------------
plt.figure(figsize=(10, 6))

# stacked bars: coal bottom, wind above; battery charge/discharge shown separately as lines
plt.bar(hours, coal_out, label="Coal", color="gray")
plt.bar(hours, wind_out, bottom=coal_out, label="Wind", color="skyblue")

# show charge/discharge as stem or dashed lines for clarity
plt.step(hours, energy_out, where='mid', label="Battery SOC (MWh)", color="orange", linewidth=2)
plt.plot(hours, charge_out, '--', label="Charge (MWh/h)", color="green")
plt.plot(hours, discharge_out, '--', label="Discharge (MWh/h)", color="red")

plt.plot(hours, [demand[h] for h in hours], 'k:', label="Demand")

plt.xlabel("Hour")
plt.ylabel("MWh")
plt.title("Optimal Dispatch + Battery SOC")
plt.legend()
plt.grid(True, linestyle='--', alpha=0.5)
plt.show()

