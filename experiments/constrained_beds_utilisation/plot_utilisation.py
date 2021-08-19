import matplotlib.pyplot as plt
import pandas as pd

data = pd.read_csv('utilisation.csv')

fig = plt.figure(figsize=(10,10))

# Percent patients waiting for ASU bed
ax1 = fig.add_subplot(221)
x = data['Bed utilisation']
y1 = data['Percent patients waiting for ASU - Catchment']
y2 = data['Percent patients waiting for ASU - Free']
ax1.plot(x, y1, marker='o', label='No bed pooling')
ax1.plot(x, y2, marker='o', label='Bed pooling')
ax1.set_xlabel('Bed utilisation (%)')
ax1.set_ylabel('Percent patients who wait for ASU bed')
ax1.set_xlim(50, 100)
ax1.set_ylim(0)
ax1.legend()
ax1.grid()
ax1.set_title('Percent of patients who wait for an ASU bed')

# Percent patients displaced
ax2= fig.add_subplot(222)
x = data['Bed utilisation']
y1 = data['Percent patients displaced - Catchment']
y2 = data['Percent patients displaced - Free']
ax2.plot(x, y1, marker='o', label='No bed pooling')
ax2.plot(x, y2, marker='o', label='Bed pooling')
ax2.set_xlabel('Bed utilisation (%)')
ax2.set_ylabel('Percent patients displacedfrom catchment ASU')
ax2.set_xlim(50, 100)
ax2.set_ylim(0)
ax2.legend()
ax2.grid()
ax2.set_title('Percent of patients who are\ndisplaced from catchment ASU')

# Average wiait 
ax3= fig.add_subplot(223)
x = data['Bed utilisation']
y1 = data['Average wait (days) - Catchment']
y2 = data['Average wait (days) - Free']
ax3.plot(x, y1, marker='o', label='No bed pooling')
ax3.plot(x, y2, marker='o', label='Bed pooling')
ax3.set_xlabel('Bed utilisation (%)')
ax3.set_ylabel('Average wait (days)')
ax3.set_xlim(50, 100)
ax3.set_ylim(0)
ax3.legend()
ax3.grid()
ax3.set_title('Average wait for ASU for those\npatients who have to wait for ASU bed')

# Average number of waiters 
ax4= fig.add_subplot(224)
x = data['Bed utilisation']
y1 = data['Average patients waiting - Catchment']
y2 = data['Average patients waiting - Free']
ax4.plot(x, y1, marker='o', label='No bed pooling')
ax4.plot(x, y2, marker='o', label='Bed pooling')
ax4.set_xlabel('Bed utilisation (%)')
ax4.set_ylabel('Average number of patients waiting for ASU bed')
ax4.set_xlim(50, 100)
ax4.set_ylim(0)
ax4.legend()
ax4.grid()
ax4.set_title('Average number of patients waiting for ASU bed')

plt.savefig('utilisation.png', dpi=300)
plt.tight_layout(pad=2)
plt.show()


