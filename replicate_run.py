from sim_utils.replication import Replicator
from sim_utils.parameters import Scenario

import warnings
warnings.filterwarnings("ignore")

# Name & define all scenarios (set parameters that differ from defaults in 
# sim_utils/parameters.py)

# Set up a dictionary to hold scenarios
scenarios = {}

# Name & define all scenarios 
# Set parameters that differ from defaults in sim_utils/parameters_[date].py


# Baseline sceanrio (model defaults)

# Baseline sceanrio (model defaults)
scenarios['constrained_beds'] = Scenario(
    allow_non_preferred_asu = False)
scenarios['constrained_beds_allow_redirect'] = Scenario(
    allow_non_preferred_asu = True)
# Set up and call replicator
replications = 10
replications = Replicator(scenarios, replications)
replications.run_scenarios()
