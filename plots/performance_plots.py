#!/usr/bin/env python


import numpy as np
import matplotlib.pyplot as plt


dcSpeedups = [32.38819058, 25.51713997, 32.43876219, 7.375053323, -17.2438708]
waSpeedups = [-12.29065634, 35.1037953, 39.44510494, 7.607244385, -16.84288361]
labels = ['ltsSandy0', 'ltsSandy1', 'ltsSandy2', 'ltsSandy3', 'ltsSandy4']

width = 0.3

# data
plt.bar(np.arange(len(dcSpeedups)), dcSpeedups, width=width, label='DC')
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

