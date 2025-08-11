import pulp
import matplotlib.pyplot as plt

# --------------------------
# 1. INPUT DATA (example)
# --------------------------
hours = [1, 2, 3, 4, 5]         # 5-hour toy example (replace with range(24) for full day)
demand = {1: 90, 2: 100, 3: 80, 4: 110, 5: 95}

# Costs ($/MWh) - coal is expensive in hours 4 and 5
coal_cost = {1: 50, 2: 50, 3: 50, 4: 80, 5: 80}
wind_cost = 20

# generation capacity (MWh/h)
coal_capacity = 80
wind_capacity = {1: 40, 2: 50, 3: 30, 4: 45, 5: 35}

# ----- Battery parameters -----
battery_capacity = 100        # maximum stored energy (MWh)
charge_power_limit = 50      # max charging rate (MWh/h)
discharge_power_limit = 50   # max discharging rate (MWh/h)

# Efficiency modeling:
# charge_eff: fraction of energy that actually gets stored when charging
# discharge_eff: fraction of energy that is delivered when discharging from stored energy
charge_eff = 0.95
discharge_eff = 0.95

# initial stored energy (at the start of hour 1). Could be 0 or some SOC.
initial_energy = 0.0

# --------------------------
# 2. CREATE MODEL
# --------------------------
model = pulp.LpProblem("Stage3_Battery_Storage", pulp.LpMinimize)

# --------------------------
# 3. DECISION VARIABLES
# --------------------------
# Generation from each tech per hour
coal = pulp.LpVariable.dicts("Coal", hours, lowBound=0)
wind = pulp.LpVariable.dicts("Wind", hours, lowBound=0)

# Battery variables per hour:
# charge[h]  = energy sent into battery during hour h (MWh)
# discharge[h] = energy taken out of battery during hour h that goes to demand (MWh)
# energy[h]  = stored energy at end of hour h (MWh)
charge = pulp.LpVariable.dicts("Charge", hours, lowBound=0, upBound=charge_power_limit)
discharge = pulp.LpVariable.dicts("Discharge", hours, lowBound=0, upBound=discharge_power_limit)
energy = pulp.LpVariable.dicts("Energy", hours, lowBound=0, upBound=battery_capacity)

# --------------------------
# 4. OBJECTIVE
# --------------------------
# Minimize total generation cost across all hours.
# Note: charging consumes generation (it appears in the demand balance), so its cost is naturally counted.
model += pulp.lpSum(coal_cost[h] * coal[h] + wind_cost * wind[h] for h in hours)


# --------------------------
# 5. CONSTRAINTS
# --------------------------
for h in hours:
    # 5.1 Demand balance:
    # Generation plus battery discharge must meet demand plus battery charging.
    # coal[h] + wind[h] + discharge[h] == demand[h] + charge[h]
    # Rearranged to equality for clarity:
    model += coal[h] + wind[h] + discharge[h] == demand[h] + charge[h], f"PowerBalance_hour_{h}"

    # 5.2 Generation capacity per hour
    model += coal[h] <= coal_capacity, f"CoalCap_hour_{h}"
    model += wind[h] <= wind_capacity[h], f"WindCap_hour_{h}"

    # 5.3 Charging/discharging limits are already enforced by variable bounds (upBound)
    # (but you could also add explicit constraints if you prefer)

    # 5.4 Battery energy state update (time-coupling)
    # energy[h] = energy[h-1] + charge_eff * charge[h] - discharge[h] / discharge_eff
    if h == hours[0]:
        # first hour uses initial_energy
        model += energy[h] == initial_energy + charge_eff * charge[h] - discharge[h] / discharge_eff, f"EnergyBalance_hour_{h}"
    else:
        model += energy[h] == energy[h-1] + charge_eff * charge[h] - discharge[h] / discharge_eff, f"EnergyBalance_hour_{h}"

    # 5.5 Battery capacity and non-negativity are enforced by energy variable bounds (0 to battery_capacity)

# Optional: enforce end-of-day state (e.g., return to initial energy)
# Uncomment if you want cyclic behavior (energy[end] == initial_energy)
# model += energy[hours[-1]] == initial_energy, "CyclicSOC"

# --------------------------
# 6. SOLVE
# --------------------------
model.solve()

# --------------------------
# 7. RESULTS (print)
# --------------------------
print("Status:", pulp.LpStatus[model.status])
print("Total Cost ($) =", pulp.value(model.objective))

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

    print(f"Hour {h}: Coal={c:.1f}, Wind={w:.1f}, Charge={ch:.1f}, Discharge={dis:.1f}, Energy={e:.1f}")

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
