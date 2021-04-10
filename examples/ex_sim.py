#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
This is an example for how the simulation will work
"""

__author__ = 'Therese Aase Knapskog and Astrid Moum'
__email__ = 'therese.knapskog@nmbu.no and astridmo@nmbu.no'

from biosim.simulation import BioSim

island_map = """\
                        WWWWW
                        WLLLW
                        WLLLW
                        WLLLW
                        WWWWW"""
init_pop = [{'loc': (3, 3),
             'pop': [{'species': 'Herbivore', 'age': 5, 'weight': 50} for _ in range(500)]},
            {'loc': (3, 3),
             'pop': [{'species': 'Carnivore', 'age': 5, 'weight': 10} for _ in range(50)]}
            ]
seed = 150
hist_specs = {'fitness': {'max': 1.0, 'delta': 0.05}, 'age': {'max': 60.0, 'delta': 20}, 'weight': {'max': 60, 'delta': 2}}

sim = BioSim(island_map=island_map, ini_pop=init_pop, seed=seed, hist_specs=hist_specs, ymax_animals=2000)
new_params = {'zeta': 3, 'xi': 1.8}
species = "Herbivore"

sim.simulate(num_years=50, vis_years=1)




