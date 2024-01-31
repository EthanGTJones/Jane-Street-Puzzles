from gurobipy import *
import gurobipy as gp
from gurobipy import GRB

# Define the size of the grid
grid_size = 17

# Predefined row and column sums
row_sums = [14, 24, 24, 39, 43, 39, 22, 23, 29, 28, 34, 36, 29, 26, 26, 24, 20]
col_sums = [13, 20, 22, 28, 30, 36, 35, 39, 49, 39, 39, 22, 23, 32, 23, 17, 13]

# Create a new model
m = gp.Model("grid_problem")

# Model parameters
m.setParam(GRB.Param.PoolSearchMode, 2)
m.setParam(GRB.Param.PoolSolutions, 1)

# Create variables for 1's, 2's, and 3's
x = m.addVars(grid_size, grid_size, vtype=GRB.BINARY, name="x")  # For 1's
y = m.addVars(grid_size, grid_size, vtype=GRB.BINARY, name="y")  # For 2's
z = m.addVars(grid_size, grid_size, vtype=GRB.BINARY, name="z")  # For 3's

# Constraint: Each cell can only be 0, 1, 2, or 3
for i in range(grid_size):
    for j in range(grid_size):
        m.addConstr(x[i, j] + y[i, j] + z[i, j] <= 1)

# Add row and column sum constraints
for i in range(grid_size):
    m.addConstr(sum(x[i, j] + 2 * y[i, j] + 3 * z[i, j] for j in range(grid_size)) == row_sums[i])
for j in range(grid_size):
    m.addConstr(sum(x[i, j] + 2 * y[i, j] + 3 * z[i, j] for i in range(grid_size)) == col_sums[j])

# Adding constraints for cells containing 2 and 3
for i in range(grid_size):
    for j in range(grid_size):
        # Determine the adjacent cells
        adjacent_cells_x = []  # For cells containing 1
        adjacent_cells_y = []  # For cells containing 2
        adjacent_cells_z = []  # For cells containing 3
        for di, dj in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            ni, nj = i + di, j + dj
            if 0 <= ni < grid_size and 0 <= nj < grid_size:
                adjacent_cells_x.append(x[ni, nj])
                adjacent_cells_y.append(y[ni, nj])
                adjacent_cells_z.append(z[ni, nj])

        # Constraint for cell with 1: at least one adjacent cell must also be 1
        if adjacent_cells_x:
            m.addConstr(x[i, j] <= sum(adjacent_cells_x))

        # Constraint for cell with 2: at least two adjacent cells must also be 2
        if adjacent_cells_y:
            m.addConstr(y[i, j] * 2 <= sum(adjacent_cells_y))

        # Constraint for cell with 3: at least two adjacent cells must also be 3
        if adjacent_cells_z:
            m.addConstr(z[i, j] * 2 <= sum(adjacent_cells_z))


# Auxiliary integer variables for ensuring sums of 2's and 3's are multiples of 2 and 3
half_row_sum_2s = m.addVars(grid_size, vtype=GRB.INTEGER, name="half_row_sum_2s")
third_row_sum_3s = m.addVars(grid_size, vtype=GRB.INTEGER, name="third_row_sum_3s")

half_col_sum_2s = m.addVars(grid_size, vtype=GRB.INTEGER, name="half_col_sum_2s")
third_col_sum_3s = m.addVars(grid_size, vtype=GRB.INTEGER, name="third_col_sum_3s")

# Row and column constraints for sums of 2's and 3's
for i in range(grid_size):
    m.addConstr(2 * half_row_sum_2s[i] == sum(y[i, j] for j in range(grid_size)))
    m.addConstr(3 * third_row_sum_3s[i] == sum(z[i, j] for j in range(grid_size)))

for j in range(grid_size):
    m.addConstr(2 * half_col_sum_2s[j] == sum(y[i, j] for i in range(grid_size)))
    m.addConstr(3 * third_col_sum_3s[j] == sum(z[i, j] for i in range(grid_size)))

# Define the regions
# (row, col)
regions = {
    # Red region
    "reg1": [(0,0),(1,0),(2,0),(3,0),(4,0),(5,0),(6,0),(7,0),(8,0),(9,0),
             (10,0),(11,0),(12,0),(13,0),(14,0),(15,0),(16,0),(0,1),(1,1),
             (15,1),(16,1),(1,2),(16,2),(16,3),(16,4),(15,4),(13,4),(13,4),
             (16,5)],

    # Blue regions
    "reg2": [(2,1),(3,1),(4,1),(5,1),(6,1),(7,1),(8,1),(9,1),(10,1),(11,1),
             (12,1),(13,1),(14,1),(2,2),(3,2),(14,2),(15,2),(2,3),(15,3)],
    "reg3": [(2,8),(3,8),(3,7),(4,7),(4,6),(4,5),(4,4),(5,4)],
    "reg4": [(14,6),(15,5),(15,6),(16,6),(16,7),(16,8),(16,9),
             (16,10),(16,11),(16,12)],
    "reg5": [(4,9),(4,10),(5,10),(6,10),(7,10),(8,10),(9,10),(8,8),(8,9),(8,11),(8,12),(7,12),(9,12)],
    "reg6": [(2,11),(1,11),(1,12),(1,13),(1,14),(2,14),(3,14),(3,13),(4,13),(5,13),(5,14),(6,14)],
    "reg7": [(11,12),(11,13),(12,13),(13,13),(14,10),(14,11),(13,11),(13,12),(13,14),(14,14),(14,15)],

    # Yellow regions
    "reg8": [(6,2),(7,2),(8,2),(9,2),(10,2),(11,2),(12,2),(7,3),(8,3),(9,3),(10,3),(11,3),(8,4),(9,4),
             (10,4),(9,5)],
    "reg9": [(9,8),(9,9),(10,9),(10,10),(11,10),(11,11),(12,11),(12,12)],
    "reg10": [(0,10),(0,11),(0,12),(0,13),(0,14),(0,15),(0,16),(1,10),(1,15),(1,16),(2,10),(2,12),
              (2,13),(2,16),(3,10),(3,11),(3,12),(3,16),(4,11),(4,12),(4,16),(5,11),(5,12),(6,11),
              (6,12),(7,11)],

    # Green regions
    "reg11": [(0,2),(0,3),(1,3),(1,4),(1,5),(1,6),(2,4),(2,5),(2,6),(3,3),(3,4),(3,5),(3,6),(4,3)],
    "reg12": [(4,8),(5,6),(5,7),(5,8),(6,6),(6,7),(6,8),(7,5),(7,6),(8,5),(8,6)],
    "reg13": [(13,9),(14,9),(15,9),(15,7),(15,8),(15,10),(15,11),(15,12),(14,12),(14,13),(15,13),(16,13)],
    "reg14": [(13,2),(12,3),(13,3),(14,3),(12,5),(13,5),(11,6),(12,6),(13,6),(10,7),(11,7),(12,7),(13,7),
              (10,8),(11,8),(12,4),(13,4)],
    "reg15": [(6,13),(7,13),(8,13),(8,14),(9,13),(9,11),(10,11),(10,12),(10,13),(10,14),(10,15),(11,15)],

    # Purple regions
    "reg16": [(4,2),(5,2),(5,3),(6,3),(6,4),(7,4),(5,5),(6,5)],
    "reg17": [(5,9),(6,9),(7,9),(7,8),(7,7),(8,7),(9,7),(9,6),(10,6),(10,5),(11,4),(11,5)],
    "reg18": [(14,7),(14,8),(13,8),(12,8),(12,9),(11,9),(12,10),(13,10)],
    "reg19": [(0,4),(0,5),(0,6),(0,7),(0,8),(0,9),(1,7),(1,8),(1,9),(2,7),(2,9),(3,9)],
    "reg20": [(2,15),(3,15),(4,14),(4,15),(5,15),(5,16),(6,15),(6,16),(7,14),(7,15),(7,16),(8,15),(8,16),
              (9,14),(9,15),(9,16),(10,16),(11,16),(11,14),(12,14),(12,15),(12,16),(13,15),
              (13,16),(14,16),(15,14),(15,15),(15,16),(16,14),(16,15),(16,16)]
}

# Calculate the sum of values in each region
region_sums = {}
for reg, coords in regions.items():
    region_sums[reg] = sum(x[i, j] + 2 * y[i, j] + 3 * z[i, j] for i, j in coords)

# Add constraints to ensure the sums of values in each region are equal
first_region_sum = region_sums[next(iter(regions))]  # Use the first region as a reference
for reg_sum in region_sums.values():
    m.addConstr(reg_sum == first_region_sum)

# Optimize model
m.setParam('MIPGap', 0)
m.setParam('MIPFocus', 2)
m.optimize()

# Print solutions
num_solutions = m.SolCount
print(f"Number of solutions found: {num_solutions}")

for s in range(num_solutions):
    m.setParam(GRB.Param.SolutionNumber, s)
    print(f"Solution {s + 1}:")
    for i in range(grid_size):
        print([int(m.getVarByName(f"x[{i},{j}]").Xn + 2 * m.getVarByName(f"y[{i},{j}]").Xn + 3 * m.getVarByName(f"z[{i},{j}]").Xn) for j in range(grid_size)])
    print()