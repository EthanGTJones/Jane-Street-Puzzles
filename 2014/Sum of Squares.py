from gurobipy import Model, GRB

# Initialise the model
model = Model("JaneStreet: Sum of Squares")

# Divisors for rows and columns.
# [0] to [4] are row divisors (top-bottom),
# [5] to [9] are column divisors (left-right)
divisors = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

# Create variables: a 5x5 grid of digits
grid = [[model.addVar(vtype=GRB.INTEGER, lb=0, ub=9, name=f"cell_{r}_{c}") for c in range(5)] for r in range(5)]

# Set the objective: Maximise the sum of all digits
model.setObjective(sum(sum(cell for cell in row) for row in grid), GRB.MAXIMIZE)

# Add constraints for divisibility
for i in range(5):
    # Row divisor constraints
    quotient_row = model.addVar(vtype=GRB.INTEGER, name=f"quotient_row_{i}")
    model.addConstr(sum(grid[i][j] * 10**(4-j) for j in range(5)) == divisors[i] * quotient_row, f"row_div_{i}")

    # Column divisor constraints
    quotient_col = model.addVar(vtype=GRB.INTEGER, name=f"quotient_col_{i}")
    model.addConstr(sum(grid[j][i] * 10**(4-j) for j in range(5)) == divisors[5+i] * quotient_col, f"col_div_{i}")

# Optimise the model
model.setParam('MIPGap', 0)
model.setParam('MIPFocus', 2)
model.optimize()

# Check for solution and print results.
if model.status == GRB.OPTIMAL:
    solution = [[int(grid[i][j].x) for j in range(5)] for i in range(5)]
    total_sum = sum(sum(row) for row in solution)
    print(f"Optimal sum: {total_sum}")
    print("Grid:")
    for row in solution:
        print(' '.join(map(str, row)))
else:
    print("No optimal solution found")
