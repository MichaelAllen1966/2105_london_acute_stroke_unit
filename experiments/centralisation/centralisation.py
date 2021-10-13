import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

data = pd.read_csv('results.csv')
labels = [1,2,3,4]
width = 0.75


x = np.arange(len(labels))  # the label locations

fig = plt.figure(figsize=(9,6))

# Number people waiting 
ax1 = fig.add_subplot(121)

y1 = data['av_waiting'].values.flatten()

waiting = ax1.bar(x, y1, width, color='b')

ax1.set_ylabel('Average number of patients waiting for ASU bed')
ax1.set_xlabel('ASUs per region')
ax1.set_title('Average number of patients waiting\nfor ASU bed')
ax1.set_xticks(x)
ax1.set_xticklabels(labels)

ax2 = fig.add_subplot(122)

y2 = data['av_waiting_days'].values.flatten()
days = ax2.bar(x, y2, width, color='r')

ax2.set_ylabel('Average waiting time (days)')
ax2.set_xlabel('ASUs per region')
ax2.set_title('Average waiting time\n(days, for patients who have to wait)')
ax2.set_xticks(x)
ax2.set_xticklabels(labels)

plt.tight_layout(pad=2)
plt.savefig('centralisation.png', dpi=300)


plt.show()



