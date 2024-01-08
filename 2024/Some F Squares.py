from gurobipy import *

# Given row and column sums
row_sums = [3, 9, 10, 13, 13, 8, 7, 2]
col_sums = [9, 12, 12, 10, 8, 8, 4, 2]

# Gurobi model
model = Model("JaneStreet: Some F Squares")

# Variables for each cell in the grid
grid = [[model.addVar(vtype=GRB.INTEGER, lb=0, ub=9, name=f"cell_{r}_{c}") for c in range(8)] for r in range(8)]

# Add constraints to enforce row and column sums
for r in range(8):
    model.addConstr(quicksum(grid[r][c] for c in range(8)) == row_sums[r], f"row_sum_{r}")

for c in range(8):
    model.addConstr(quicksum(grid[r][c] for r in range(8)) == col_sums[c], f"col_sum_{c}")    

# Optimise the model
model.setParam('MIPGap', 0)
model.setParam('MIPFocus', 2)
model.optimize()

# Check the status of the optimization
# Check for solution and print results.
if model.status == GRB.OPTIMAL:
    solution = [[int(grid[i][j].x) for j in range(8)] for i in range(8)]
    total_sum = sum(sum(row) for row in solution)
    print(f"Optimal sum: {total_sum}")
    print("Grid:")
    for row in solution:
        print(' '.join(map(str, row)))
else:
    print("No optimal solution found")
