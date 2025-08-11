# src/pyomo_stage3_battery.py
from pyomo.environ import (
    ConcreteModel, Set, Param, Var, NonNegativeReals,
    Objective, Constraint, SolverFactory, value
)
import matplotlib.pyplot as plt

# --------------------------
# 0. Problem data (toy example; same numbers as before)
# --------------------------
hours = [1, 2, 3, 4, 5]
demand = {1: 90, 2: 100, 3: 80, 4: 110, 5: 95}

coal_max = {1: 70, 2: 70, 3: 70, 4: 50, 5: 50}
wind_max = {1: 40, 2: 50, 3: 30, 4: 45, 5: 35}
coal_cost = {1: 50, 2: 50, 3: 50, 4: 80, 5: 80}
wind_cost = 20

battery_capacity = 40
charge_power_limit = 20
discharge_power_limit = 20
charge_eff = 0.95
discharge_eff = 0.95
degradation_cost_per_mwh = 5.0
standing_loss_fraction = 0.0
initial_energy = 0.0

# --------------------------
# 1. Build Pyomo model
# --------------------------
m = ConcreteModel()

# index set
m.H = Set(initialize=hours)

# parameters
m.demand = Param(m.H, initialize=demand)
m.coal_cost = Param(m.H, initialize=coal_cost)
m.wind_cost = Param(initialize=wind_cost)  # scalar param
# capacity params (we'll use python dict lookup inside rules for simplicity)
m.coal_max = Param(m.H, initialize=coal_max)
m.wind_max = Param(m.H, initialize=wind_max)

# --------------------------
# 2. Variables
# --------------------------
m.coal = Var(m.H, domain=NonNegativeReals)         # coal generation (MWh)
m.wind = Var(m.H, domain=NonNegativeReals)         # wind generation (MWh)
m.charge = Var(m.H, domain=NonNegativeReals, bounds=(0, charge_power_limit))
m.discharge = Var(m.H, domain=NonNegativeReals, bounds=(0, discharge_power_limit))
# energy (SOC) variable; we enforce capacity with bounds via lambda
m.energy = Var(m.H, domain=NonNegativeReals, bounds=(0, battery_capacity))

# --------------------------
# 3. Objective: generation cost + degradation cost
# --------------------------
def objective_rule(model):
    gen_cost = sum(model.coal_cost[h] * model.coal[h] + model.wind_cost * model.wind[h] for h in model.H)
    # approximate throughput cost with average of charge & discharge (linear)
    deg_cost = sum(degradation_cost_per_mwh * 0.5 * (model.charge[h] + model.discharge[h]) for h in model.H)
    return gen_cost + deg_cost

m.TotalCost = Objective(rule=objective_rule, sense=1)  # sense=1 is minimize

# --------------------------
# 4. Constraints
# --------------------------
def power_balance_rule(model, h):
    # generation + discharge == demand + charge
    return model.coal[h] + model.wind[h] + model.discharge[h] == model.demand[h] + model.charge[h]
m.PowerBalance = Constraint(m.H, rule=power_balance_rule)

def coal_capacity_rule(model, h):
    return model.coal[h] <= model.coal_max[h]
m.CoalCap = Constraint(m.H, rule=coal_capacity_rule)

def wind_capacity_rule(model, h):
    return model.wind[h] <= model.wind_max[h]
m.WindCap = Constraint(m.H, rule=wind_capacity_rule)

# Energy (SOC) dynamics with efficiencies and optional standing loss
def energy_balance_rule(model, h):
    # find index of h to get previous hour
    idx = hours.index(h)
    loss = standing_loss_fraction
    if idx == 0:
        prev_energy = initial_energy
    else:
        prev = hours[idx - 1]
        prev_energy = model.energy[prev]
    # energy[h] == (1-loss)*prev_energy + charge_eff*charge[h] - discharge[h]/discharge_eff
    return model.energy[h] == (1 - loss) * prev_energy + charge_eff * model.charge[h] - model.discharge[h] / discharge_eff

m.EnergyBalance = Constraint(m.H, rule=energy_balance_rule)

# Optional: force end-of-horizon SOC to zero (avoid "value hiding" after horizon)
def end_soc_rule(model):
    last = hours[-1]
    return model.energy[last] == 0.0
m.EndOfHorizonSOC = Constraint(rule=end_soc_rule)

# --------------------------
# 5. Solve
# --------------------------
# Choose solver: try GLPK first. If you prefer CBC, change 'glpk' -> 'cbc'
solver_name = 'glpk'   # change to 'cbc' or 'gurobi' if you have it
solver = SolverFactory(solver_name)

# solve with solver output printed (tee=True) so you see solver log in PyCharm console
results = solver.solve(m, tee=True)

# --------------------------
# 6. Show results
# --------------------------
print("Solver status:", results.solver.status)
print("Solver termination condition:", results.solver.termination_condition)
print("Objective (total cost + degradation) = ", value(m.TotalCost))
print()

coal_out = [value(m.coal[h]) for h in hours]
wind_out = [value(m.wind[h]) for h in hours]
charge_out = [value(m.charge[h]) for h in hours]
discharge_out = [value(m.discharge[h]) for h in hours]
energy_out = [value(m.energy[h]) for h in hours]

for h in hours:
    print(f"Hour {h}: Coal={coal_out[h-1]:.2f}, Wind={wind_out[h-1]:.2f}, "
          f"Charge={charge_out[h-1]:.2f}, Discharge={discharge_out[h-1]:.2f}, SOC={energy_out[h-1]:.2f}")

# --------------------------
# 7. Plot (optional)
# --------------------------
plt.figure(figsize=(9,5))
plt.bar(hours, wind_out, label="Wind", color="skyblue", edgecolor='k')
plt.bar(hours, coal_out, bottom=wind_out, label="Coal", color="lightcoral", edgecolor='k')
plt.bar(hours, charge_out, label="Charge", color="green", alpha=0.6)
plt.bar(hours, [-d for d in discharge_out], label="Discharge", color="orange", alpha=0.6)
ax2 = plt.twinx()
ax2.plot(hours, energy_out, '-o', color='black', label='SOC')
plt.xlabel("Hour")
plt.ylabel("MWh")
plt.title("Pyomo: Dispatch with realistic battery costs & efficiencies")
plt.legend(loc='upper left')
plt.grid(True, linestyle='--', alpha=0.4)
plt.show()
