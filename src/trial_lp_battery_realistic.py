import pulp
import matplotlib.pyplot as plt

# --------------------------
# 1. INPUT DATA (toy example)
# --------------------------
hours = [1, 2, 3, 4, 5]
demand = {1: 90, 2: 100, 3: 80, 4: 110, 5: 95}

# Generation caps and costs
coal_max = {1: 70, 2: 70, 3: 70, 4: 50, 5: 50}
wind_max = {1: 40, 2: 50, 3: 30, 4: 45, 5: 35}
coal_cost = {1: 50, 2: 50, 3: 50, 4: 80, 5: 80}
wind_cost = 20

# --------------------------
# 2. BATTERY PARAMETERS (more realistic)
# --------------------------
battery_capacity = 40        # MWh
charge_power_limit = 20      # MWh/h
discharge_power_limit = 20   # MWh/h

charge_eff = 0.95            # fraction stored when charging
discharge_eff = 0.95         # fraction delivered when discharging
# Round-trip efficiency = charge_eff * discharge_eff

# Degradation cost: $ per MWh throughput (captures wear & tear)
# Typical values depend on battery tech and assumed lifetime; try something small, e.g. $1–$10/MWh.
degradation_cost_per_mwh = 5.0

# Small standing loss per hour (fraction of SOC lost per hour).
# Set to 0.0 to ignore; e.g. 0.001 for 0.1%/hour leakage.
standing_loss_fraction = 0.0

# initial state of charge (MWh)
initial_energy = 0.0

# --------------------------
# 3. CREATE PROBLEM
# --------------------------
model = pulp.LpProblem("Stage3_Battery_Realistic", pulp.LpMinimize)

# --------------------------
# 4. DECISION VARIABLES
# --------------------------
coal = pulp.LpVariable.dicts("Coal", hours, lowBound=0)
wind = pulp.LpVariable.dicts("Wind", hours, lowBound=0)
charge = pulp.LpVariable.dicts("Charge", hours, lowBound=0, upBound=charge_power_limit)
discharge = pulp.LpVariable.dicts("Discharge", hours, lowBound=0, upBound=discharge_power_limit)
energy = pulp.LpVariable.dicts("Energy", hours, lowBound=0, upBound=battery_capacity)

# --------------------------
# 5. OBJECTIVE: generation cost + degradation cost
# --------------------------
# Degradation cost is applied to throughput (we use average of charge+discharge to approximate cycles).
# You could alternatively use just charge or just discharge; both are linear approximations.
gen_cost = pulp.lpSum(coal_cost[h] * coal[h] + wind_cost * wind[h] for h in hours)
deg_cost = pulp.lpSum(degradation_cost_per_mwh * 0.5 * (charge[h] + discharge[h]) for h in hours)
model += gen_cost + deg_cost, "TotalCost_with_Degradation"

# --------------------------
# 6. CONSTRAINTS
# --------------------------
for h in hours:
    # Generation capacity limits
    model += coal[h] <= coal_max[h], f"CoalCap_{h}"
    model += wind[h] <= wind_max[h], f"WindCap_{h}"

    # Battery charge/discharge bounds already enforced via upBound in variables

    # Power balance:
    # generation + discharge == demand + charge
    # note: charge increases the RHS (it is additional sink in the hour)
    model += coal[h] + wind[h] + discharge[h] == demand[h] + charge[h], f"PowerBalance_{h}"

    # Battery energy bounds already enforced by variable bounds

# Energy (SOC) dynamics with efficiencies & standing loss
for idx, h in enumerate(hours):
    loss_term = standing_loss_fraction
    if idx == 0:
        # SOC at end of first hour
        # energy = initial*(1-loss) + charge_eff*charge - discharge / discharge_eff
        model += energy[h] == (1 - loss_term) * initial_energy + charge_eff * charge[h] - discharge[h] / discharge_eff, f"EnergyBalance_{h}"
    else:
        prev = hours[idx - 1]
        model += energy[h] == (1 - loss_term) * energy[prev] + charge_eff * charge[h] - discharge[h] / discharge_eff, f"EnergyBalance_{h}"

# Optional: ensure battery is emptied at end (or comment out to allow residual SOC)
model += energy[hours[-1]] == 0.0, "EndOfHorizon_SOC"

# --------------------------
# 7. SOLVE
# --------------------------
model.solve()

# --------------------------
# 8. PRINT RESULTS
# --------------------------
print("Status:", pulp.LpStatus[model.status])
print("Objective (total cost + degradation) = ", pulp.value(model.objective))
print()

coal_out, wind_out, charge_out, discharge_out, energy_out = [], [], [], [], []
for h in hours:
    c = coal[h].varValue
    w = wind[h].varValue
    ch = charge[h].varValue
    dis = discharge[h].varValue
    e = energy[h].varValue

    coal_out.append(c); wind_out.append(w)
    charge_out.append(ch); discharge_out.append(dis); energy_out.append(e)

    print(f"Hour {h}: Coal={c:.2f}, Wind={w:.2f}, Charge={ch:.2f}, Discharge={dis:.2f}, SOC={e:.2f}")

# --------------------------
# 9. PLOT (optional)
# --------------------------
plt.figure(figsize=(9,5))
plt.bar(hours, wind_out, label="Wind", color="skyblue", edgecolor='k')
plt.bar(hours, coal_out, bottom=wind_out, label="Coal", color="lightcoral", edgecolor='k')
plt.bar(hours, charge_out, label="Charge", color="green", alpha=0.6)
plt.bar(hours, [-d for d in discharge_out], label="Discharge", color="orange", alpha=0.6)
plt.twinx().plot(hours, energy_out, '-o', color='black', label='SOC')
plt.xlabel("Hour")
plt.ylabel("MWh")
plt.title("Dispatch with realistic battery costs & efficiencies")
plt.legend(loc='upper left')
plt.grid(True, linestyle='--', alpha=0.4)
plt.show()
