#!python
# -*- coding: utf-8 -*-

"""
Provides a class for user interface with visualisation.

Each simulation is represented by a :class:`BioSim` instance. On each
instance, the :meth:`BioSim.simulate` method can be called as often as
you like to simulate a given number of steps.

The state of the system is visualized as the simulation runs, at intervals
that can be chosen. The graphics can also be saved to file at regular
intervals. By calling :meth:`BioSim.make_movie` after a simulation is complete,
individual graphics files can be combined into an animation.

Examples
--------
>>> ini_pop = [{'loc': (2, 2), 'pop': [{'species': 'Herbivore',
...             'age': 5, 'weight': 50} for _ in range(10)]}]
>>> island_map = str(WWW\nWLW\nWWW)
>>> sim = BioSim(island_map, ini_pop, 150)
>>> sim.simulate(10)

With this code:
    - BiosSim will first create an island, with 9 landscapes.
    - The pupulation of 10 Herbivores is placed at
      coordinate (1,1), meaning the Lowland.
    - After initializing the island with landscape and animals,
      the island is simulated with choosen period 10 years,
      visualating each year (default).

"""

__author__ = 'Therese Aase Knapskog and Astrid Moum'
__email__ = 'therese.knapskog@nmbu.no and astridmo@nmbu.no'

import numpy as np
from .island import Island
from .graphics import Graphics
from .animals import Herbivore, Carnivore


class BioSim:
    """
    Provides user interface for simulation with visualisation.

    ...

    Parameters
    -----------
    island_map : str
        A multiline string specifying island geography. Letters allowed
        are `L`, `H`, `W` and/or `D`, representing the landscape types.
        The island have to be surrounded by 'W'.
    ini_pop : list of dict {str:tuple, str:list}
        A list of dictionaries describing the initial animal population.
        Legal keys are:
            - 'loc': tuple, location coordinate of the animal(s).
            - 'pop': list of dict, with legal keys:
                - 'species': str, "Herbivore" or "Carnivore".
                - 'age': int, animals initial age.
                - 'weight': float, animals initial weight.
    seed : int
        A random generator seed.
    ymax_animals : int, default None, meaning the y-axis limit is automatic
        The y-axis limit for plot showing count of animal species.
    cmax_animals : dict, default None, meaning default values
        Specification of color-code limits for animal densities.
        Legal keys are:
            - 'Herbivore' : int, default value used is 50.
            - 'Carnivore' : int, default value used is 20.
    hist_specs : dict of {dict : float}, default None, meaning default values
        Specification of histograms with one entry(dict) per histogram plot.
        Legal keys are:
            - 'age' : dict, histogram plot for animal species age.
            - 'weight' : dict, histogram plot for animal species weight.
            - 'fitness' : dict, histogram plot for animal species fitness.
        Per plot two entries(keys) is required, legal keys are:
            - 'max' : float, upper value of data stored along the x-axis
            - 'delta' : float, bin width for the histogram
    img_base : str, default None, meaning no images written to file/saved
        Image path and beginning of a file name. Filenames are
        formed as ’{}_{:05d}.{}’.format(img_base, img_no, img_fmt). Where
        img_no are consecutive image numbers starting from 0.
    img_fmt : str, default 'png'
        File type for figure/images saved.

    Attributes
    ----------
    island : class object
        Island simulated, an instance of class :py:class:`Island()` from :py:mod:`BioSim.island`.
    ymax_animals, c_max_animals
        See parameters.

    See Also
    --------
    biosim.island
        Module to construct an island.
    biosim.graphics
        Module to visualize ecosystem of an island through plots, save image
        or save movie.
    biosim.landscape
        Module to construct landscapes instances Lowland, Highland, Dessert
        and Water, with animal population and/or fodder.
    biosim.animal
        Module to construct animal instances Herbivore and/or Carnivore with
        age, weight and fitness.

    """

    _species_mapping = {  # Used to set animal parameters.
        'Herbivore': Herbivore,
        'Carnivore': Carnivore}

    def __init__(self, island_map, ini_pop, seed, ymax_animals=None,
                 cmax_animals=None, hist_specs=None, img_base=None,
                 img_fmt='png'):
        np.random.seed(seed)  # random generator
        self.island = Island(ini_pop=ini_pop, geogr=island_map)  # island simulated

        if img_base is not None and not isinstance(img_base, str):
            raise ValueError('The img_base has to be a string')

        if ymax_animals is not None and ymax_animals < 0:
            raise ValueError('The y-limit for showing animal numbers cannot be negative')

        if cmax_animals is not None:
            for species in cmax_animals.keys():
                if species not in self._species_mapping.keys():
                    raise ValueError('Species is not defined. The species must be either Herbivore or Carnivore')
                if cmax_animals[species] < 0:
                    raise ValueError('The cmax_animals for showing animal densities cannot be negative')

        if hist_specs is not None:
            pass
            # Gå gjennom og sjekke at key er age, weight eller fitness.
            # Gå gjennom og sjekke at indre dict har kun keys max og delta
            # Sjekke at verdi er positiv


        # private methods used to visualize the simulation in :meth: simulate()
        self._graphics = Graphics(ymax_animals=ymax_animals,cmax_animals=cmax_animals,
                                  hist_specs=hist_specs, img_base=img_base, img_fmt=img_fmt)
        self._map = np.array([[char for char in row] for row in island_map.split()])
        self._final_step = None
        self.year = 0

    def add_population(self, population):
        """
        Add population to simulation.

        Parameters
        ----------
        population : list of dict {str:tuple, str:list}
            A list of dictionaries describing the initial animal population.
            Legal keys are:

            - 'loc': tuple, location coordinate of the animal(s).
            - 'pop': list of dict, with legal keys:

                - 'species': str, "Herbivore" or "Carnivore".
                - 'age': int, animals initial age.
                - 'weight': float, animals initial weight.

        """
        self.island.add_island_pop(population)

    def set_animal_parameters(self, species, anim_param):
        """
        Set animal parameters.

        First check which animal species to change parameters for,
        then change the animal parameters.

        Parameters
        ----------
        species : dict of str
            Dictionary of animal species.
            Legal keys are:

                - 'Herbivore'
                - 'Carnivore'

        anim_param : dict of {str : float}
            Legal keys are:

                - 'w_birth'
                - 'sigma_birth'
                - 'beta'
                - 'eta'
                - 'a_half'
                - 'phi_age'
                - 'w_half'
                - 'phi_weight'
                - 'mu'
                - 'gamma'
                - 'zeta'
                - 'xi'
                - 'omega'
                - 'F'
                - 'DeltaPhiMax'

        """
        species = species.title()
        if species not in self._species_mapping.keys():
            raise ValueError('Species is not defined. The species must be either Herbivore or Carnivore')
        species = self._species_mapping[species]
        species.set_params(anim_param)

    def set_landscape_parameters(self, land_type, land_param):
        """
        Set landscape parameters.

        First check which landscape type to change parameters for,
        then change the landscape parameters.

        Parameters
        ----------
        land_type : str
            Letter identifying land tupe; 'L', 'H', 'D', 'W'
        land_param : dict of {str : float}
            Legal keys are
                - 'f_max'

        """
        land_type = land_type.upper()
        if land_type not in self.island.landscape_mapping.keys():
            raise ValueError('Landscape is not defined. The Landscape must be either L, H, D or W')
        land_type = self.island.landscape_mapping[land_type]
        land_type.set_param(land_param)

    def simulate(self, num_years, vis_years=1, img_years=None):
        """Run simulation while visualizing the result.

        Parameters
        ----------
        num_years : int
            number of simulation steps to execute
        vis_years : int, optional
            interval between visualization updates (default: 1)
        img_years : int or None, optional
            interval between visualizations saved to files (default: vis_steps)

        Notes
        ------
        Image files will be numbered consecutively.

        """

        if img_years is None:
            img_years = vis_years

        if img_years is not None and img_years % vis_years != 0:
            raise ValueError('img_steps must be multiple of vis_steps')

        self._final_step = self.year + num_years
        self._graphics.setup(self._final_step, img_years, self._map)

        while self.year < self._final_step:
            self.island.annual_cycle()
            self.year += 1

            if self.year % vis_years == 0:
                self._graphics.update(self.year,
                                      self.island.anim_count(),
                                      self.island.anim_matrix(),
                                      self.island.hist_data())

    def make_movie(self, movie_fmt=None):
        """
        Creates MPEG4 movie from visualization images saved.

        The movie is stored as img_base + movie_fmt

        Parameters
        ----------
        movie_fmt : str, default None, meaning movie format 'mp4'

        Note
        ----
        Requires ffmpeg for MP4 and magick for GIF

        """

        self._graphics.make_movie(movie_fmt)

    @property
    def num_animals(self):
        """
        Total number of animals on island
        """
        return sum(self.island.anim_count())

    @property
    def num_animals_per_species(self):
        """
        Get number of animals per species in island.

        Returns
        -------
        dict
            Number of animals per species in island

        """
        return {'Herbivore': self.island.anim_count()[0], 'Carnivore': self.island.anim_count()[1]}
