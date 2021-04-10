#!python
# -*- coding: utf-8 -*-

"""
Create instance of landscape; Lowland, Highland, Dessert and/or Water.

Note
----
The module is built up by one superclass, Landscape,
and four subclasses Lowland, Highland, Dessert and Water.

If the landscape has an initial population, landscape
subclasses creates instances of animal species Herbivore
or Carnivore. See module `animals`.

The subclasses inherit methods and attributes,
but differentiates on subclass level
by subclass variables.

Inhereted:
    - Attributes:
        - herb_pop
        - carn_pop
    - Methods:
        - add_land_pop()
        - aging()
        - deadth()
        - feeding()
        - loss_of_weight()
        - migration(nearby_cells)
        - pop_count_carn()
        - pop_count_herb()
        - procreation()
        - dying()
        - fitness_update()
        - migrate()
        - weight_gain()
        - weight_loss()
    - Class method:
        - set_param(new_params)

Class variables set at subclass level:
    - accessible
        - `True` for Lowland, Highland and Dessert
        - `False` for Water
    - cell_type
        - `L` for Lowland
        - `H` for Highland
        - `D` for Dessert
        - `W` for Water
    - f_max
        - `800` default for Lowland
        - `800` default for Lowland
        - `0` default for Dessert
        - `None` equal to superclass, for Water

See Landscape for documentation on inherited features.
See subclasses for documentation on class varaiables
overwritten at subclass level.

Examples
--------
>>> land_1 = Lowland([dict(species='Herbivore', age=5, weight=20) for _ in range(10)])
>>> print("land_1 have {0} Herbivores, but {1} Carnivores"
...       .format(land_1.pop_count_herb(),land_1.pop_count_carn()))
land_1 have 10 Herbivores, but 0 Carnivores

>>> land_2, land_3 = Highland(), Water()
>>> print("Land accessible? For highland == {}, while water == {}"
...       .format(land_2.accessible,land_3.accessible))
Land accessible? For highland == True, while water == False

"""

__author__ = 'Therese Aase Knapskog and Astrid Moum'
__email__ = 'therese.knapskog@nmbu.no and astridmo@nmbu.no'

from .animals import Herbivore, Carnivore
import random
import operator


class Landscape:
    """Implementing a landscape with an ecosystem.

     The ecosystem can contain two animal species and fodder.
     In addition to annual development (through methods).

    ...

    Parameters
    ----------
    init_pop : list of dict {str:}, default None, meaning no animal population
        A list of dictionaries describing the initial animal population.
        With the following legal keys:

        - `species`: str, stating "Herbivore" or "Carnivore
        - `age`: int, stating the animals initial age
        - `weight`: float, stating the animals initial weight

    Attributes
    ----------
    herb_pop : list of class objects
        A list of Herbivore class instances.
    carn_pop : list of class object
        A list of Carnivore class instances.
    param: dict
        Dictionary of parameters for each landscape

    fodder : float
        Amount of fodder in landscape.

    Note
    ----
    This is a superclass, which has four subclasses;
    Lowland, Highland, Dessert and Water.
    It is not supposed to be utilized directly.

    """

    param = None  #: (`dict`) - class variable with parameters used in methods
    accessible = True  #: bool : `True` if landscape can inhabit animal populations.

    _species_mapping = {
        'Herbivore': Herbivore,
        'Carnivore': Carnivore}

    @classmethod
    def set_param(cls, new_params):
        """
        Set new parameters for landscape.

        Parameters
        ----------
        new_params : dict of {str : float}
            Legal keys are
                - 'f_max'

        Raises
        ------
        ValueError
            If parameters is not positive or not an float or int.

        """
        try:
            for k in new_params:
                if k not in cls.param:
                    raise ValueError('Invalid parameter name {}. Only param is f_max'.format(k))
                if new_params[k] < 0:
                    raise ValueError('All parameters has to be positive')
                cls.param[k] = new_params[k]
        except TypeError:
            raise ValueError('The value of the param must be an int or a float')

    def __init__(self, init_pop=None):
        self.herb_pop = []
        self.carn_pop = []
        #self.fodder = None
        if init_pop is not None:
            self.add_land_pop(init_pop)

    def add_land_pop(self, pop):
        """
        Add population to landscape.

        Population can only be added if the landscape is accessible.
        For each dictionary in list one animal instances is created
        and added to a list of species population.

        Parameters
        ----------
        pop : `list` [`dict` [`str`, `int`, `float`] ], optional
            A list of dictionaries describing the initial animal population.
            With the following keys:
                - `species` : a `str` stating "Herbivore", not optional
                - `age` : an `int` representing the animals age
                - `weight` : an `float` representing the animals weight

        """
        if not self.accessible:
            raise ValueError("Animals are not allowed to be placed in water")

        for animal in pop:
            animal["species"].title()
            if animal["species"] == "Herbivore":
                self.herb_pop.append(Herbivore(animal["age"], animal["weight"]))
            elif animal["species"] == "Carnivore":
                self.carn_pop.append(Carnivore(animal["age"], animal["weight"]))
            else:
                raise ValueError("Either unrecognizable species or no species given")

    def pop_count_herb(self):
        """
        Count amount of herbivore in landscape.

        Returns
        -------
        int
            Number of herbivores in population in landscape.

        """
        return len(self.herb_pop)

    def pop_count_carn(self):
        """
        Count amount of carnivore in landscape.

        Returns
        -------
        int
            Number of Carnivore in population in landscape.

        """
        return len(self.carn_pop)

    def feeding(self):
        """
        Feeding all animals in landscape.

        Feeding consist of three steps:
            1. Growth of fodder, where the amount of fodder in landscape
               is updated to `f_max`.
            2. Herbivore eats in random order of available fodder. Fodder
               available decreases for each Herbivore that eats.
            3. Carnivore try tries to kill Herbivore. Carnivores hunt in
               turn and the carnivore with highest fitness hunts first.
               When a carnivore hunt, it starts by hunting at the Herbivore
               with lowest fitness and continues to hunt in that order till
               satisfied. If a herbivore is killed it dies and the amount
               of available prey decreases.

        All Herbivores that die is removed from `herb_pop`.

        """

        fodder = self.param['f_max']  # Growth of fodder to landscape maximum fodder level

        random.shuffle(self.herb_pop)  # Population is shuffled to a random order
        for herb in self.herb_pop:
            fodder -= herb.eat_fodder(fodder)  # Herbivore eats of available fodder

        self.herb_pop.sort(key=operator.attrgetter('fitness'))  # Herb sorted from low to high fitness
        self.carn_pop.sort(key=operator.attrgetter('fitness'), reverse=True)  # Carn sorted from high to low fitness
        for carn in self.carn_pop:  # Carnivore tries to kill and eat Herbivore
            self.herb_pop = carn.eat_herb(self.herb_pop)  # Returning all Herbivores that survived

    def procreation(self):
        """
        Procreation of animal populations.

        Each species try to birth, depending on number of animals in landscape.
        If a population gets newborns, the newborns are added to the list of
        species population.

        """

        def _newborns(anim_pop):
            """
            Birth of of newborns for animal population.

            Parameters
            ----------
            anim_pop: list of class objects
                Animal population of same species to procreate.

            Returns
            -------
            List of class objects
                Animal newborns of same species as animal population procreating.

            """
            num_animals = len(anim_pop)  # calculate number of animals of same species in population
            return [nb for nb in [parent.birth(num_animals) for parent in anim_pop] if nb is not None]

        self.herb_pop.extend(_newborns(self.herb_pop))  # add Herbivore newborn to list of Herbivore population
        self.carn_pop.extend(_newborns(self.carn_pop))  # add Carnivore newborn to list of Carnivore population

    def migration(self, nearby_cells):  # not applicable before migration
        """
        Migrate to nearby landscapes/cells.

        Migration is determined by the following steps:
            1. Check which animals want to move



        of the some animals to neighbouring cells. The animals can only move once per year.

        The function follows the following steps:

        2. Animals randomly chose which cell they want to move to from the nearby cells
        3. If the chosen cell is not water, the animal moves
        4. The migrated animal is flagged so that one animal can move only once per year
        5. After all migrations, the flag is reset so that all animals can migrate the upcoming year
        The method will update the nearby cells that animals migrate to.
        The current cell will be updated to remove the migrated animals

        Parameters
        ----------
        nearby_cells : list
                    List of objects of the class Landscape. The list is of the possible cells that 
                    the animals in the current cell can move to. This means the neighbouring cells,
                    but not cells diagonally displaced

        See Also
        --------
        biosim.animals.migrate
            Checks if animal wants to migrate or not

        """

        def _migrators(anim_pop):
            """
            Find animals from population that wants to move.

            Parameters
            ----------
            anim_pop : list of class objects
                Population of one animal species.

            Returns
            -------
            list of class objects
                Animals in animal population that wants to move.

            """
            return [anim for anim in anim_pop if anim.migrate()]

        herb_mig, carn_mig = _migrators(self.herb_pop), _migrators(self.carn_pop)
        migrated_herb = []
        migrated_carn = []
        for herb in herb_mig:
            chosen = random.choice(nearby_cells)
            if chosen.accessible is True and herb.migrated is False:
                chosen.herb_pop.append(herb)
                migrated_herb.append(herb)
                herb.migrated = True

        for carn in carn_mig:
            chosen = random.choice(nearby_cells)
            if chosen.accessible is True and carn.migrated is False:
                chosen.carn_pop.append(carn)
                migrated_carn.append(carn)
                carn.migrated = True

        self.herb_pop = [anim for anim in self.herb_pop if anim not in migrated_herb]
        self.carn_pop = [anim for anim in self.carn_pop if anim not in migrated_carn]

        for anim in self.herb_pop + self.carn_pop:
            anim.migrated = False



    def aging(self):
        """
        Increase animal age by one for all animals in populations.

        See Also
        --------
        biosim.animals.age_change()
            The animal gets one year older
        """
        [anim.age_change() for anim in self.herb_pop + self.carn_pop]

    def loss_of_weight(self):
        """
        Loss of weight for all animals in landscape populations.

        See Also
        --------
        biosim.animals.weight_loss()
        """
        [anim.weight_loss() for anim in self.herb_pop + self.carn_pop]

    def death(self):
        """
        Delete animals that die this year from the animal population.

        This is done by updating populations to the animals that survive the annual dying-method.

        See Also
        --------
        biosim.animals.dying()
            Returns True if animal dies

        """

        self.herb_pop = [herb for herb in self.herb_pop if not herb.dying()]
        self.carn_pop = [carn for carn in self.carn_pop if not carn.dying()]


class Lowland(Landscape):
    """
    Implements the landscape Lowland.

    ...

    Note
    ----
    This is a subclass of `Landscape`. See Landscape attributed and methods
    for documentation on inherited attributes and methods.

    Examples
    --------


    """
    param = dict(f_max=800)  #: dict of str : Desert param to parameterize methods


class Highland(Landscape):
    """
    Implements the landscape Highland.

    ...

    Note
    ----
    This is a subclass of `Landscape`. See Landscape attributed and methods
    for documentation on inherited attributes and methods.

    Examples
    --------


    """
    param = dict(f_max=300)  #: dict of str : Desert param to parameterize methods


class Desert(Landscape):
    """
    Implements the landscape Dessert.

    ...

    Note
    ----
    This is a subclass of `Landscape`. See Landscape attributed and methods
    for documentation on inherited attributes and methods.

    Examples
    --------

    """

    param = dict(f_max=0)  #: dict of str : Desert param to parameterize methods


class Water(Landscape):
    """
    Implements the landscape Water.

    ...

    Note
    ----
    This is a subclass of `Landscape`. See Landscape attributed and methods
    for documentation on inherited attributes and methods.

    Examples
    --------

    """

    accessible = False  #: bool : `False` if landscape cannot inhabit animal populations.
