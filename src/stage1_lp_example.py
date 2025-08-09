import pulp

# -------------------
# 1. Define the problem
# -------------------
model = pulp.LpProblem("Electricity_Supply_Optimization", pulp.LpMinimize)

# -------------------
# 2. Data
# -------------------
plants = ["Coal", "Wind"]
cities = ["A", "B", "C"]

# Cost per MWh from each plant to each city (could include transmission cost)
costs = {
    ("Coal", "A"): 50, ("Coal", "B"): 55, ("Coal", "C"): 60,
    ("Wind", "A"): 65, ("Wind", "B"): 60, ("Wind", "C"): 55
}

# Maximum generation capacity (MWh)
capacity = {
    "Coal": 150,
    "Wind": 100
}

# Demand for each city (MWh)
demand = {
    "A": 80,
    "B": 70,
    "C": 60
}

# -------------------
# 3. Decision variables
# -------------------
x = pulp.LpVariable.dicts(
    "Power",
    [(i, j) for i in plants for j in cities],
    lowBound=0,
    cat='Continuous'
)

# -------------------
# 4. Objective function
# -------------------
model += pulp.lpSum(costs[(i, j)] * x[(i, j)] for i in plants for j in cities)

# -------------------
# 5. Constraints
# -------------------
# Demand must be met
for j in cities:
    model += pulp.lpSum(x[(i, j)] for i in plants) == demand[j]

# Capacity limits
for i in plants:
    model += pulp.lpSum(x[(i, j)] for j in cities) <= capacity[i]

# -------------------
# 6. Solve
# -------------------
model.solve()

# -------------------
# 7. Results
# -------------------
print("Status:", pulp.LpStatus[model.status])
print("Total Cost = ", pulp.value(model.objective))
for i in plants:
    for j in cities:
        print(f"Electricity from {i} to {j}: {x[(i, j)].varValue} MWh")
