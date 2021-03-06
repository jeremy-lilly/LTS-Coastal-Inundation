#!/usr/bin/env python


import numpy as np
import matplotlib.pyplot as plt


#dcSpeedups = [32.38819058, 35.19573694, 32.43876219, 7.375053323, -17.2438708]
dcSpeedups = [32.50477445, 35.5107034, 32.22793169, 8.126746003, -15.63280368]
#waSpeedups = [39.3993047, 34.79578527, 37.53642414, 4.274424697, -20.63420947]
waSpeedups = [36.23397654, 34.23015892, 35.04975594, 6.651533162, -18.66965828]
labels = ['DelBay2km', 'DelBay1km', 'DelBay500m', 'DelBay250m', 'DelBay125m']

width = 0.3

# data
plt.bar(np.arange(len(dcSpeedups)), dcSpeedups, width=width, label='EC')
plt.bar(np.arange(len(waSpeedups)) + width, waSpeedups, width=width, label='WA')

# grid lines
plt.grid(color='#95a5a6', linestyle='--', linewidth=1, axis='y', alpha=0.3)

# x tick lables
plt.xticks(np.arange(len(waSpeedups)) + width/2, labels)

# axis labels
plt.xlabel('mesh')
plt.ylabel('% speedup')

# legend
plt.legend()

plt.savefig('speedups.pdf')

