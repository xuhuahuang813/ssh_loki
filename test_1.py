from ortools.sat.python import cp_model

# Create a CSP model
model = cp_model.CpModel()

# Add boolean variables
x = model.NewBoolVar('x')
y = model.NewBoolVar('y')
z = model.NewBoolVar('z')

# Create a CSP solver
solver = cp_model.CpSolver()

# Get the number of boolean variables in the model
num_booleans = solver.NumBooleans()

print(f'Number of boolean variables: {num_booleans}')
