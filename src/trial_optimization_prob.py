import pulp

# 1. Create the optimization problem: minimize cost
model = pulp.LpProblem("Energy_Cost_Minimization", pulp.LpMinimize)

# 2. Define decision variables
coal = pulp.LpVariable('Coal', lowBound=0)  # electricity from coal plant
wind = pulp.LpVariable('Wind', lowBound=0)  # electricity from wind plant
# ^ These represent how many MWh we generate from each source.

# 3. Objective function
model += 50 * coal + 20 * wind
# ^ Cost per MWh: Coal = $50, Wind = $20
# ^ First 'model +=' defines the *objective* we want to minimize.

# 4. Constraints
model += coal + wind >= 100   # meet demand of 100 MWh
model += coal <= 80           # coal plant capacity = 80 MWh
model += wind <= 50           # wind plant capacity = 50 MWh
# ^ Each 'model +=' after the objective adds a constraint.

# 5. Solve the problem
model.solve()

# 6. Print results
print("Status:", pulp.LpStatus[model.status])        # shows if solution is Optimal
print("Coal MWh:", coal.varValue)                    # optimal coal generation
print("Wind MWh:", wind.varValue)                    # optimal wind generation
print("Total Cost:", pulp.value(model.objective))    # minimum total cost
