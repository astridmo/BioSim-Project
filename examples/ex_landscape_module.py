#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
This is an example of how the landscape module will work on its own.
"""

__author__ = 'Therese Aase Knapskog and Astrid Moum'
__email__ = 'therese.knapskog@nmbu.no and astridmo@nmbu.no'

from biosim.landscape import Lowland
import matplotlib.pyplot as plt

herb_pop = [dict(species='Herbivore', age=5, weight=20) for _ in range(50)]
lowland = Lowland(herb_pop)
lowland.add_land_pop(herb_pop)
num_herb = []
print(lowland.pop_count_herb())
for _ in range(50):
    lowland.feeding()
    lowland.procreation()
    lowland.aging()
    lowland.loss_of_weight()
    lowland.death()
    num_herb.append(lowland.pop_count_herb())

figure = plt.figure()
ax1 = plt.subplot2grid((1, 1), (0, 0))

ax1_plot = ax1.plot(num_herb)
plt.title('Number of herbs in one Lowland cell')
plt.show()


