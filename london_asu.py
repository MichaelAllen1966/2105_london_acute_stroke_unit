#!/usr/bin/env python
# coding: utf-8

# # London ASU model

# ## Requirements and module imports
# 
# Code in this simulation uses a standard Anaconda Python environment (https://www.anaconda.com/distribution/#download-section). Additionally this model uses SimPy3 (https://simpy.readthedocs.io/en/latest/). Install SimPy3 with `pip install 'simpy<4'`.

# In[5]:


import simpy
import inspect
from sim_utils.replication import Replicator
from sim_utils.parameters import Scenario


# ## Set up scenarios
# 
# Parameters defined in scenarios will overwrite default values in the parameters python file.

# In[6]:


# Set up a dictionary to hold scenarios
scenarios = {}

# Baseline sceanrio (model defaults)
scenarios['base'] = Scenario()


# ## Run model

# In[7]:


replications = 30
replications = Replicator(scenarios, replications)
replications.run_scenarios()


# ## Show model default parameters
# 
# Run the code below to model defaults (these are over-ridden by scenario values above).

# In[ ]:


print(inspect.getsource(Scenario.__init__))

