import pulp
import pandas as pd

# -------------------
# 1. Data setup
# -------------------
hours = list(range(24))
plants = ["Coal", "Wind"]
cities = ["A", "B", "C"]

# Hourly demand for each city (MWh) — could come from a CSV later
demand_data = {
    "A": [80, 85, 90, 95, 100, 105, 110, 120, 130, 140, 150, 160,
          160, 155, 150, 145, 140, 135, 130, 120, 110, 100, 90, 85],
    "B": [70, 72, 75, 78, 80, 82, 85, 90, 95, 100, 105, 110,
          110, 108, 105, 102, 100, 98, 95, 90, 85, 80, 75, 72],
    "C": [60, 62, 64, 66, 68, 70, 72, 75, 78, 80, 82, 85,
          85, 84, 82, 80, 78, 76, 74, 72, 70, 68, 65, 62]
}

# Convert to DataFrame for convenience
demand_df = pd.DataFrame(demand_data, index=hours)

# Hourly capacity for each plant (MWh)
capacity = {
    "Coal": 150,
    "Wind": 100
}

# Hourly cost per MWh for each plant (can vary with time)
cost_data = {
    "Coal": [50]*24,  # constant price for simplicity
    "Wind": [40 if 8 <= h <= 18 else 60 for h in hours]  # cheaper during the day
}

# -------------------
# 2. Define the model
# -------------------
model = pulp.LpProblem("24h_Electricity_Supply", pulp.LpMinimize)

# Decision variables: x[(plant, city, hour)]
x = pulp.LpVariable.dicts(
    "Power",
    [(i, j, t) for i in plants for j in cities for t in hours],
    lowBound=0,
    cat='Continuous'
)

# Objective: Minimize total cost
model += pulp.lpSum(cost_data[i][t] * x[(i, j, t)]
                    for i in plants for j in cities for t in hours)

# Demand constraints: each city's hourly demand must be met
for j in cities:
    for t in hours:
        model += pulp.lpSum(x[(i, j, t)] for i in plants) == demand_df.loc[t, j]

# Capacity constraints: each plant can't produce more than capacity per hour
for i in plants:
    for t in hours:
        model += pulp.lpSum(x[(i, j, t)] for j in cities) <= capacity[i]

# -------------------
# 3. Solve
# -------------------
model.solve()

# -------------------
# 4. Results
# -------------------
print("Status:", pulp.LpStatus[model.status])
print("Total Daily Cost = ", pulp.value(model.objective))

# Show first few hours of allocations
for t in range(5):  # just first 5 hours
    print(f"\nHour {t}")
    for i in plants:
        for j in cities:
            print(f"{i} -> {j}: {x[(i, j, t)].varValue} MWh")
