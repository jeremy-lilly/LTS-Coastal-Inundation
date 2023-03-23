#!/usr/bin/env python


import numpy as np
import matplotlib.pyplot as plt


fig, ax = plt.subplots()

dcSpeedups = [32.50477445, 35.5107034, 32.22793169, 8.126746003, -15.63280368]
dcRatios = [{'CR': 1.88, 'RR': 15},
            {'CR': 1.71, 'RR': 30},
            {'CR': 1.71, 'RR': 30},
            {'CR': 0.46, 'RR': 60},
            {'CR': 0.12, 'RR': 120}]
waSpeedups = [36.23397654, 34.23015892, 35.04975594, 6.651533162, -18.66965828]
waRatios = [{'CR': 0.92, 'RR': 60},
            {'CR': 1.28, 'RR': 60},
            {'CR': 1.28, 'RR': 60},
            {'CR': 0.39, 'RR': 120},
            {'CR': 0.11, 'RR': 240}]
labels = ['DelBay2km', 'DelBay1km', 'DelBay500m', 'DelBay250m', 'DelBay125m']

width = 0.3

# data
ec_bars = plt.bar(np.arange(len(dcSpeedups)), dcSpeedups,
                  width=width, label='EC')
wa_bars = plt.bar(np.arange(len(waSpeedups)) + width, waSpeedups,
                  width=width, label='WA')

for i, bar in enumerate(ec_bars):
    ax.text(bar.get_x() + bar.get_width()/6, 12,
            'CR = {}\nRR = {}'.format(dcRatios[i]['CR'], dcRatios[i]['RR']), rotation=90, fontsize='x-small')
# END for

for i, bar in enumerate(wa_bars):
    ax.text(bar.get_x() + bar.get_width()/6, 12,
            'CR = {}\nRR = {}'.format(waRatios[i]['CR'], waRatios[i]['RR']), rotation=90, fontsize='x-small')
# END for

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

