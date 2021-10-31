import sys
from indicators import grid_runner
from models import predictor_runner

print(sys.argv[1])
grid, grid_time = grid_runner.call_runner(sys.argv[1])
print(grid.shape)
predictor_runner.call_runner(grid, grid_time)