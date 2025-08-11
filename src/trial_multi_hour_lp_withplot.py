import pulp
import matplotlib.pyplot as plt

# --------------------------
# 1. INPUT DATA
# --------------------------

# List of time periods (hours in a day for this example)
hours = [1, 2, 3, 4, 5]

# Demand in MWh for each hour
# Dictionary format: hour -> demand value
demand = {1: 90, 2: 100, 3: 80, 4: 110, 5: 95}

# Cost per MWh of each technology
coal_cost = 50  # expensive
wind_cost = 20  # cheap

# Max capacity (MWh per hour) for coal plant
coal_capacity = 80

# Max wind capacity varies per hour (to simulate changing wind speeds)
wind_capacity = {
    1: 40,
    2: 50,
    3: 30,
    4: 45,
    5: 35
}

# --------------------------
# 2. CREATE OPTIMIZATION PROBLEM
# --------------------------
# LpMinimize → tells PuLP we want to minimize the objective function
model = pulp.LpProblem("Stage2_MultiHourEnergyOptimization", pulp.LpMinimize)

# --------------------------
# 3. DECISION VARIABLES
# --------------------------
# For each hour, we have a variable for coal production and one for wind production.
# lowBound=0 → production cannot be negative
coal = pulp.LpVariable.dicts("Coal", hours, lowBound=0)
wind = pulp.LpVariable.dicts("Wind", hours, lowBound=0)

# --------------------------
# 4. OBJECTIVE FUNCTION
# --------------------------
# Minimize total cost across all hours
# pulp.lpSum() efficiently adds up costs for all hours
model += pulp.lpSum(
    coal_cost * coal[h] + wind_cost * wind[h] for h in hours
), "TotalDailyCost"

# --------------------------
# 5. CONSTRAINTS
# --------------------------
for h in hours:
    # 5.1 Meet hourly demand exactly or more (>=)
    model += coal[h] + wind[h] >= demand[h], f"Demand_hour_{h}"

    # 5.2 Coal capacity limit per hour
    model += coal[h] <= coal_capacity, f"CoalCap_hour_{h}"

    # 5.3 Wind capacity limit per hour (varies each hour)
    model += wind[h] <= wind_capacity[h], f"WindCap_hour_{h}"

# --------------------------
# 6. SOLVE THE PROBLEM
# --------------------------
model.solve()

# --------------------------
# 7. DISPLAY RESULTS
# --------------------------
print("Status:", pulp.LpStatus[model.status])
coal_output = []
wind_output = []

for h in hours:
    coal_val = coal[h].varValue
    wind_val = wind[h].varValue
    coal_output.append(coal_val)
    wind_output.append(wind_val)
    print(f"Hour {h}: Coal={coal_val} MWh, Wind={wind_val} MWh")

# Print total daily cost
print("Total Daily Cost ($) =", pulp.value(model.objective))

# --------------------------
# 8. PLOT RESULTS
# --------------------------
plt.figure(figsize=(8, 5))

# Stacked bar chart: coal first (bottom), wind on top
plt.bar(hours, coal_output, label="Coal", color="gray")
plt.bar(hours, wind_output, bottom=coal_output, label="Wind", color="skyblue")

# Plot demand line for reference
plt.plot(hours, [demand[h] for h in hours], "r--", label="Demand")

plt.xlabel("Hour")
plt.ylabel("Energy Production (MWh)")
plt.title("Optimal Hourly Energy Dispatch")
plt.legend()
plt.grid(True, linestyle="--", alpha=0.5)
plt.show()
