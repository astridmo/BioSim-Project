#!python
# -*- coding: utf-8 -*-

"""
Implements an island with many landscapes.

"""

__author__ = 'Therese Aase Knapskog and Astrid Moum'
__email__ = 'therese.knapskog@nmbu.no and astridmo@nmbu.no'

from .landscape import Lowland, Highland, Desert, Water
import numpy as np


class Island:
    """A landscape for animal species with measurement of population,
    food and population development.

    ...

    Parameters
    ----------
    ini_pop : `list` [`dict` [`tuple`, `list`] ], optional
        `init_herb` is a list of dictionaries describing the initial
        animal population. With the following keys:

        - `loc` : The location coordinate of the animal(s) as a `tuple`
        - `pop` : A list of `dict` with three keys to define the animal

            - `species` : a `str` stating "Herbivore", not optional
            - `age` : an `int` representing the animals age
            - `weight` : an `float` representing the animals weight

    geogr : dict
        A map of the geography on the island

    Attributes
    ----------
    island_map : dict
        dict where an index for location is key and the landscape type is the object.
        Note that the index will start at [0,0], and is therefore not the same as the `loc`
    map_size : tuple
        Gives the dimensions of the map

    Note
    ----
    This is a superclass, which has four subclasses;
    Lowland, Highland, Dessert and Water.
    It is not supposed to be utilized directly.

    """

    landscape_mapping = {
        'D': Desert,
        'W': Water,
        'H': Highland,
        'L': Lowland
    }

    def __init__(self, ini_pop=None, geogr=''):
        self.island_map = {}  # empty dict for storing the map
        self.map_size = self.init_map(geogr)  # initializing map and storing the size of the map
        self.add_island_pop(ini_pop)

    def add_island_pop(self, pop):
        """
        Adding population to given a given location.

        Parameters
        ----------
        pop : `list` [`dict` [`tuple`, `list`] ], optional
            `init_herb` is a list of dictionaries describing the initial
            animal population. With the following keys:

            - `loc` : The location coordinate of the animal(s) as a `tuple`
            - `pop` : A list of `dict` with three keys to define the animal

                - `species` : a `str` stating "Herbivore", not optional
                - `age` : an `int` representing the animals age
                - `weight` : an `float` representing the animals weight


        """
        for _dict in pop:
            i, j = _dict['loc']
            anim_pop = _dict['pop']
            self.island_map[i - 1, j - 1].add_land_pop(anim_pop)    # Adding animals to given location

    def map_check(self, i, j, char, num_row, num_col):
        """
        Checking that the island is surrounded by water and that the island only contains defined landscape types

        Parameters
        ----------
        i : int
            Row index
        j : int
            Column index
        char: str
            Landscape type
        num_row: int
            Number of rows in the map
        num_col: int
            Number of columns in the map

        Raises
        -------
        ValueError

        """
        if i == 0 and char != 'W' or i == num_row and char != 'W' or \
                j == 0 and char != 'W' or j == num_col and char != 'W':
            raise ValueError('The island must be surrounded by water')
        if char not in self.landscape_mapping.keys():
            raise ValueError(
                'The given landscape "{char}" is not defined. Defined landscapes are {landscapes}'.format(
                    char=char, landscapes=self.landscape_mapping.keys()))

    def init_map(self, geostr):
        """
        Initializing the map.

        Checks that the map size is ok -> That the number of columns is constant.
        Making a dictionary of the map, with keys (index) and value the landscape object

        Parameters
        ----------
        geostr : str
            String of the map

        Returns
        -------
        map_size : tuple
            The size of the map
        """
        cell_matrix = np.array([[char for char in row] for row in geostr.split()])
        map_size = np.shape(cell_matrix)

        # Test that the map size is ok
        try:
            num_row = map_size[0] - 1
            num_col = map_size[1] - 1
        except IndexError:
            raise ValueError('All the rows of the island must be of the same length')

        for i, row in enumerate(cell_matrix):
            for j, char in enumerate(row):
                self.map_check(i, j, char, num_row, num_col)

                # Adding to dict -> key is index and value is the given landscape type
                # (This is NOT the loc, but index for the island-dict. The index will start at [0,0])
                self.island_map[i, j] = self.landscape_mapping[char]()

        return map_size

    @staticmethod
    def anim_in_cell(cell):
        """
        Not running annual cycle for lanscape Water of if there is no aminals in the cell

        Parameters
        ----------
        cell : class object
            Landscape object of Lowland, Highland, Water or Dessert.

        Returns
        -------
        Boolean or None
            'True' if cycle shall be run.
            'None' if cycle is not run.
        """
        if cell.accessible is True and len(cell.herb_pop) + len(cell.carn_pop) != 0:
            return True

    def annual_migration(self):
        """
        Migrate animals to nearby cells.

        Creates an index for nearby cells, then checks if animals want
        to migrate cell by cell. If they move animals are added to
        population list in new location.

        """
        def _nearby_cells(_index):
            """
            Finding the neighbouring cells. (Not diagonally)

            Parameters
            ----------
            _index : tuple
                the key in self.island_map dict

            Returns
            -------
            nearby_cells : object
                The landscape-objects of the nearby cells
            """
            row = _index[0]
            col = _index[1]
            # Making a list of the neighbouring landscape-object
            nearby_cells = [self.island_map[row - 1, col], self.island_map[row, col - 1],
                            self.island_map[row, col + 1], self.island_map[row + 1, col]]
            return nearby_cells

        # for index, cell in self.island_map.items():
        #     if self.anim_in_cell(cell):
        #         cell.migration(_nearby_cells(index))

        def _migrate_anim(index, cell):
            # cell.herb_pop = [
            #     anim for anim in cell.herb_pop
            #     if not _move_single_anim(index, anim)
            # ]
            # cell.carn_pop = [
            #     anim for anim in cell.carn_pop
            #     if not _move_single_anim(index, anim)
            # ]
            for key in cell.pop.keys():
                pop[key] = [anim for anim in pop[key] if not _move_single_anim(index, anim, key)]

        def _move_single_anim(index, anim, key):
            if anim.migrated is False and anim.migrate():
                chosen = random.choice(_nearby_cells(index))
                if chosen.accessible:
                    # if type(anim).__name__ is "Herbivore":
                    #     chosen.herb_pop.append(anim)
                    #     anim.migrated = True
                    # else:
                    #     chosen.carn_pop.append(anim)
                    #     anim.migrated = True
                    chosen[key].append(anim)
                    anim.migrated = True
                    return True 

        for index, cell in self.map.items():
            if self.anim_in_cell(cell):
                _migrate_anim(index, cell)









    def annual_cycle(self):
        """
        Function for the annual cycle of each cell.

        Function goes through all cells that are not water and that has animals in it.
        The function then performs the each step in annual cycle on all cells, before
        next step is conducted.

        Steps are:

            1. Feeding
            2. Procreation
            3. Migration
            4. Aging
            5. Annual loss of weight
            6. Annual death of animals

        See Also
        --------
        landscape.feeding
        landscape.procreation
        annual_migration
        landscape.aging
        landscape.loss_of_weight
        landscape.death

        """

        [cell.feeding() for cell in self.island_map.values() if self.anim_in_cell(cell)]
        [cell.procreation() for cell in self.island_map.values() if self.anim_in_cell(cell)]
        self.annual_migration()
        [cell.aging() for cell in self.island_map.values() if self.anim_in_cell(cell)]
        [cell.loss_of_weight() for cell in self.island_map.values() if self.anim_in_cell(cell)]
        [cell.death() for cell in self.island_map.values() if self.anim_in_cell(cell)]

    def anim_count(self):
        """
        Get total amount of herbivores and carnivores on island.

        Returns
        -------
        Tuple
            (num_herb, num_carn)
        """

        num_herb = 0
        num_carn = 0

        for cell in self.island_map.values():
            if self.anim_in_cell(cell):
                num_herb += cell.pop_count_herb()
                num_carn += cell.pop_count_carn()

        return num_herb, num_carn

    def anim_matrix(self):
        """
        Get a matrix of animal species distribution on island.

        Returns
        -------
        tuple
            (matrix_herb, matrix_carn)

        """
        # Making nested list of zeros with same size as the map
        count_herb_matrix = np.zeros(self.map_size, dtype=int)
        count_carn_matrix = np.zeros(self.map_size, dtype=int)

        for index, cell in self.island_map.items():
            if self.anim_in_cell(cell):
                count_herb_matrix[index] = cell.pop_count_herb()
                count_carn_matrix[index] = cell.pop_count_carn()

        return count_herb_matrix, count_carn_matrix

    def hist_data(self):
        """
        Get fitness, age and weight for all animals on island.

        Returns
        -------
        List of List
            First level of nested list representing fitness, weight and age.
            Second level of nested listed separating data for each species.

                - data_hist[0][0], list of animal fitness levels for Herbivore
                - data_hist[0][1], list of animal fitness levels for Carnivore
                - data_hist[1][0], list of animal weight values for Herbivore
                - data_hist[1][1], list of animal weight values for Carnivore
                - data_hist[2][0], list of animal age values for Herbivore
                - data_hist[2][1], list of animal age values for Carnivore

         """
        herb_fit, carn_fit = [], []
        herb_weight, carn_weight = [], []
        herb_age, carn_age = [], []

        for cell in self.island_map.values():
            for herb in cell.herb_pop:
                herb_fit.append(herb.fitness)
                herb_weight.append(herb.weight)
                herb_age.append(herb.age)
            for carn in cell.carn_pop:
                carn_fit.append(carn.fitness)
                carn_weight.append(carn.weight)
                carn_age.append(carn.age)

        return [[herb_fit, carn_fit], [herb_weight, carn_weight], [herb_age, carn_age]]
