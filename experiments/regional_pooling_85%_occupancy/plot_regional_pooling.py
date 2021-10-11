import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

data = pd.read_csv('global_pivot.csv')
labels = ['No pooling', 'Regional pooling','Pool all units']
cols = ['constrained_beds',
        'constrained_beds_allow_region_redirect',
        'constrained_beds_allow_any_redirect']

x = np.arange(len(labels))  # the label locations
width = 0.35  # the width of the bars

fig = plt.figure(figsize=(6,6))

# Number people waiting 
ax1 = fig.add_subplot(111)

mask = ((data['kpi'] == 'asu_patients_unallocated') & 
       (data['statistic'] == 'mean'))
y1 = data[mask][cols].values.flatten()

mask = ((data['kpi'] == 'asu_patients_unallocated') & 
       (data['statistic'] == 'percentile_95'))
y2 = data[mask][cols].values.flatten()

medians = ax1.bar(x - width/2, y1, width, label='Mean', color='b')
percentiles = ax1.bar(x + width/2, y2, width, label='95th percentile', color='r')

ax1.set_ylabel('Patients waiting for ASU bed')
ax1.set_title('Patients waiting for ASU bed\n(at approx 85% average ASU occupancy)')
ax1.set_xticks(x)
ax1.set_xticklabels(labels)
ax1.legend()

plt.savefig('regional_pooling.png', dpi=300)


plt.show()



