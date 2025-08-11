import pulp

# Example hourly demand for 5 hours
hours = [1, 2, 3, 4, 5]
demand = {1: 90, 2: 100, 3: 80, 4: 110, 5: 95}

# Cost per MWh
coal_cost = 50
wind_cost = 20

# Hourly capacity limits
coal_capacity = 80  # MWh per hour
wind_capacity = {1: 40, 2: 50, 3: 30, 4: 45, 5: 35}  # variable wind per hour

# 1. Create the optimization problem
model = pulp.LpProblem("Stage2_MultiHourEnergyOptimization", pulp.LpMinimize)

# 2. Decision variables
#    For each hour, how much energy from Coal and from Wind?
coal = pulp.LpVariable.dicts("Coal", hours, lowBound=0)
wind = pulp.LpVariable.dicts("Wind", hours, lowBound=0)

# 3. Objective function: Minimize total cost across all hours
model += pulp.lpSum(
    coal_cost * coal[h] + wind_cost * wind[h] for h in hours
), "TotalDailyCost"

# 4. Constraints
for h in hours:
    # Meet demand each hour
    model += coal[h] + wind[h] >= demand[h], f"Demand_hour_{h}"
    # Coal capacity per hour
    model += coal[h] <= coal_capacity, f"CoalCap_hour_{h}"
    # Wind capacity varies by hour
    model += wind[h] <= wind_capacity[h], f"WindCap_hour_{h}"

# 5. Solve
model.solve()

# 6. Results
print("Status:", pulp.LpStatus[model.status])
for h in hours:
    print(f"Hour {h}: Coal={coal[h].varValue} MWh, Wind={wind[h].varValue} MWh")
print("Total Daily Cost ($) =", pulp.value(model.objective))
