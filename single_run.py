import time

from sim_utils.model import Model
from sim_utils.parameters import Scenario

time_start = time.time()
scenario = Scenario(allow_non_preferred_asu = True)
model = Model(scenario)
model.run()
time_end = time.time()
time_run = time_end - time_start
print(f'Finished in {time_run:.0f} seconds.')