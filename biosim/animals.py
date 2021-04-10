#!python
# -*- coding: utf-8 -*-

"""
Create instances of animal species; Herbivore and Carnivore.

Note
----
The module is built up by one superclass, Animal,
and two subclasses Herbivore and Carnivore.

The subclasses inherit methods and attributes,
in addition to methods on subclass level which
differentiates according to animal species.

Inhereted attributes (characteristics):
    - Age
    - Weight
    - Fitness

Inhereted class variables and methods
    - migrated
    - param, determined by subclass
    - set_params()

Inhereted methods
    - age_change()
    - birth(num_animals)
    - dying()
    - fitness_update()
    - migrate()
    - weight_gain()
    - weight_loss()

Subclass methods
    - eat_herb(herb_list), a Carnivore method
    - eat_fodder(cell_fodder_amount), a Herbivore method

See animals for documentation on inherited features.
See Herbivore or Carnivore for documentation on eat_***
and their default parameters (`param`)

Examples
--------
>>> anim = Herbivore(age=10, weight=30)
>>> print("anim is {0} years old, weighs {1} and have {2} fitness"
...       .format(anim.age,anim.weight,anim.fitness))
anim is 10 years old, weighs 30 and have 0.8807970645633608 fitness

>>> anim = Carnivore(age=10, weight=30)
>>> print("anim is {0} years old, weighs {1} and {2} fitness"
...       .format(anim.age,anim.weight,anim.fitness))
anim is 10 years old, weighs 30 and have 0.9998461776222021 fitness

"""

__author__ = 'Therese Knapskog and Astrid Moum'
__email__ = 'therese.knapskog@nmbu.no and astridmo@nmbu.no'

import math
import random


class Animal:
    """
    Implements an animal.

    The animal consist of characteristics, which is represented by
    attributes. In addition to behaviour, which is represented by
    methods. Behaviour (utilized with methods), can change the
    animal's characteristics (attributes).

    ...

    Parameters
    ----------
    age : int, default 0, meaning newborn
        Age of animal.
    weight : float or None, default None, meaning a random weight
        Weight of animal.

    Attributes
    ----------
    age, weight : int, float
        See parameters.
        If `weight` == None, a random float is chosen from a Gaussian distribution
        with mean and standard deviation; `param['w_birth']` and `param['sigma_birth']`.
    fitness : float
        A value in the interval 0 to 1, calculated based on the animal `weight`
        and `age`.

    Note
    ----
    This is a superclass with methods and attributed inherited by subclasses.
    Thereby, is supposed to be utilized through subclasses and not directly.

    """

    param = None  #: (`dict`) - class variable with parameters used in methods
    migrated = False  #: (`bool`) - class variable; `True` if animal has migrated

    @classmethod
    def set_params(cls, new_params):
        """
        Set new animal parameters.

        Parameters
        ----------
        new_params : dict of {str : float}
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

        Raises
        ------
        ValueError
            If not all parameters are positive, w_birth is zero and/or
            eta is outside the interval [0,1].

        """
        try:
            for k in new_params:
                if k not in cls.param:
                    raise ValueError('Invalid parameter name: ' + k)
                if new_params[k] < 0:
                    raise ValueError('All parameters has to be positive')
                if k == 'w_birth' and new_params[k] == 0:
                    raise ValueError('Parameter "w_birth" cannot be zero')
                if k == 'eta' and new_params[k] > 1:
                    raise ValueError('Parameter "eta" must be in interval [0,1]')
                cls.param[k] = float(new_params[k])
        except TypeError:
            raise ValueError('The value of the param must be an int or a float')

    def __init__(self, age=0, weight=None):
        # control of user input
        # check if age has a positive value
        if age < 0:
            raise ValueError('Zero or positive value for age is required')
        # check if weight has a positive value
        if weight is not None and weight < 0:
            raise ValueError('Zero or positive value required')

        self.age = age  # set animal age to given input or default 0
        if weight is None:  # set animal weight depending on user input
            # weight set to random value from a Gaussian distribution
            self.weight = random.gauss(self.param['w_birth'], self.param['sigma_birth'])
        else:
            # weight set to user input
            self.weight = weight

        # set animal fitness by calculating fitness
        self.fitness = self.fitness_update()

    def __repr__(self):
        """
        Check object type of animal

        Returns
        -------
        type
            object type of animal

        """
        return f'{type(self).__name__}()'

    def age_change(self):  # should be called aging?
        """
        Increase animal age by one.

        As a result of changing the animal age,
        animal fitness is recalculated and updated.

        See Also
        --------
        fitness_update :
            calculates animal fitness based on animal age and weight.

        Examples
        --------
        >>> anim = Herbivore(age=10, weight=30)
        >>> anim.age_change()
        >>> print("anim was 10 years, but is now {0} years old".format(anim.age))
        anim was 10 years old, but is now 11 years old.

        """
        self.age += 1
        self.fitness = self.fitness_update()

    def birth(self, num_animals):
        """
        Decide if an animal gives birth.

        The animal gives birth if the following steps are `True`:

            1. The animals weigh is higher then parameterized minimum
               weight limit. Parameters are `param['zeta']`, `param['w_birth']
               and `param['sigma_birth'].
            2. A random number, with a value between 0 and 1, is
               higher then the probability of giving birth. The
               probability depends on `param['gamma'], animal fitness
               and `num_animals`.
            3. The animal's weight is higher then the weight of the
               newborn animal.

        If the animals gives the birth, the animals looses weight
        equal to the newborns weigh parameterized with `param`['xi'].
        As a result the animals weight and fitness is updated.

        Parameters
        ----------
        num_animals : int
            Number of animals of the same species in one location. If
            `num_animals` < 2, the probability of birth is 0. Meaning
            that the animal do not give birth.

        Returns
        -------
        None or class object
            `None` if animal do not give birth.
            `class object` if animal do give birth. Where the object is
            an instance of the same species.

        See Also
        --------
        fitness_update :
            calculates animal fitness based on animal age and weight.

        Examples
        --------
        >>> anim = Herbivore(age=20, weight=50)
        >>> new_animal = anim.birth(10)
        >>> print("anim gave birth to a newborn of type {0} and age {1}"
        ...       .format(new_animal.__repr__(),new_animal.age))
        anim gave birth to a newborn of type Herbivore() and age 0

        """

        def _birth_weightloss(_newborn):
            """
            Calculate the weight loss when giving birth.

            The newborn weight is parameterized with `param['xi']
            to calculate the weight loss

            Parameters
            ----------
            _newborn : class object
                A class object that is born if animals give birth.

            Returns
            -------
            float
                The animals weight loss if the animal gives birth.
            """
            return self.param['xi'] * _newborn.weight

        # Check the animals weight with parameterized minimum weight
        if self.weight < self.param['zeta'] * (self.param['w_birth']
                                               + self.param['sigma_birth']):
            p = 0
        else:  # calculate the probability [0, 1) of giving birth
            p = min(1, self.param['gamma'] * self.fitness * (num_animals - 1))

        if random.random() < p:  # check if random number is higher then p
            newborn = type(self)()  # creates a newborn of same class as animal
            # checks if newborn weighs less the animal and more then 0
            if _birth_weightloss(newborn) < self.weight and newborn.weight > 0:
                self.weight -= _birth_weightloss(newborn)  # animal looses weight
                self.fitness = self.fitness_update()  # animal fitness updated
                return newborn  # if animal give birth

        return None  # if the animal do not give birth

    def dying(self):
        """
        Check if the animal dies.

        The probability of death depend on animal fitness and the
        parameter `param['omega']`. If the animal's weight is
        equal to 0 or bellow the animal dies with certainty.


        Returns
        -------
        bool
            `True` if the animal dies do to weight or probability.
            `False` if the animal do not die.

        Examples
        --------
        >>> anim = Herbivore(age=90, weight=1)
        >>> print("Anim is dead == {0}".format(anim.dying()))
        Anim is dead == True

        """
        p = self.param['omega'] * (1 - self.fitness)  # Calculate the probability of death
        if self.weight <= 0:  # Dies with certainty of the weight is 0 or bellow
            return True
        else:
            # Generate random number [0,1), to decide if animal dies.
            return random.random() < p

    def fitness_update(self):
        """
        Calculate a new animal fitness, based on animal age and weight.

        To calculate fitness, age and weight is first parameterized then
        multiplied. Age is parameterized by `param['a_half']` and
        `param[phi_age]. Weight is parameterized by `param['w_half']` and
        `param[phi_weight]`.

        If the animal's weight is equal to or bellow 0 the animal should
        not be alive and the fitness value is set to 0.

        Returns
        -------
        float or int
            `float` if the animal gets a new fitness value.
            `int` if the animals has 0 weight and is not alive.

        Examples
        --------
        >>> anim = Herbivore(age=10, weight=30)
        >>> print("anim has fitness equal to {:2f}".format(anim.fitness_update()))
        anim has a fitness equal to 0.880797

        """
        if self.weight <= 0:
            return 0
        age_var = (1 / (1 + math.exp(self.param['phi_age'] * (self.age - self.param['a_half']))))
        weigh_var = (1 / (1 + math.exp(-1 * self.param['phi_weight'] * (self.weight - self.param['w_half']))))
        return age_var * weigh_var

    def migrate(self):
        """
        Check if animal wants to migrate.

        The animal wants to migrate if a random number in the interval [0, 1]
        is lower then the probability of moving. The probability of moving
        is determined by `param['mu']` and the animal fitness.

        Returns
        -------
        bool
            `True` if animal wants to migrate.
            `False` if animal does not want to migrate.

        Examples
        --------
        >>> anim = Herbivore(age=35, weight=17)
        >>> print("Anim wants to migrate? -> {0}".format(anim.migrate()))
        Anim wants to migrate? -> False

        """
        p = self.param['mu'] * self.fitness  # calculate probability of moving
        return random.random() < p  # random generated number to determine if animal moves

    def weight_gain(self, consumed_food):  # eat_weight_gain / wgt_gain_eat
        """
        Weight gained do to eating.
        
        Weight gain is determined by `param['beta']` and `consumed_food`. 
        The gain is added to the animal's weight and the animals 
        fitness is updated do to change in weight. 
        
        Parameters
        ----------
        consumed_food : int, float
            The amount of food consumed by the animal.

        See Also
        --------
        fitness_update :
            calculates animal fitness based on animal age and weight.

        Examples
        --------
        >>> anim = Herbivore(age=35, weight=17)
        >>> anim.weight_gain(8)
        >>> print("anim increased the weight from 17 to {0} due to eating"
        ...       .format(anim.weight))
        anim increased the weight from 17 to 24.2 due to eating

        """
        self.weight += self.param['beta'] * consumed_food
        self.fitness = self.fitness_update()

    def weight_loss(self):  # aging_weight_loss?
        """
        Loss of weight do to annual lifecycle / aging. 
        
        Determined by the animals weight and `param['eta']`. The animals
        fitness us updated do to change in weight.

        Examples
        --------
        >>> anim = Herbivore(age=35, weight=17)
        >>> anim.weight_loss()
        >>> print("anim had an annual weight loss of {0:2f}, from 17 to {1}"
        ...       .format(17-anim.weight,anim.weight))
        anim had an annual weight loss of 0.850000, from 17 to 16.15

        """
        self.weight -= self.param['eta'] * self.weight
        self.fitness = self.fitness_update()


class Carnivore(Animal):
    """
    Implements animal species Carnivore.

    The animal consist of characteristics, which is represented by
    attributes. In addition to behaviour, which is represented by
    methods. Behaviour (utilized with methods), can change the
    animal's characteristics (attributes).

    ...

    Note
    ----
    This is a subclass of `Animal`. See Animal attributed and methods
    for documentation on inherited attributes and methods.

    Examples
    --------
    >>> anim = Carnivore(age=10, weight=30)
    >>> print("anim is {0} years old, weighs {1} and {2} fitness"
    ...       .format(anim.age,anim.weight,anim.fitness))
    anim is 10 years old, weighs 30 and have 0.9998461776222021 fitness

    """

    param = dict(w_birth=6.0, sigma_birth=1.0, beta=0.75, eta=0.125,
                 a_half=40.0, phi_age=0.3, w_half=4.0, phi_weight=0.4,
                 mu=0.4, gamma=0.8, zeta=3.5, xi=1.1, omega=0.8, F=50.0,
                 DeltaPhiMax=10.0)  #: dict of str : Carnivore param to parameterize methods

    def eat_herb(self, available_prey):
        """
        Try to eat prey of available Herbivores until satisfied. The Carnivore will try to kill the
        Herbs in order of fitness, from low to high fitness.

        - If the Carnivore has lower fitness than the Herbivore, the Carnivore will stop trying to kill Herbs.
        - If difference in fitness between Herb and Carn is bigger than `param['DeltaPhiMax']`, the Carnivore
          will kill the Herbivore
        - If the fitness is lower than `param['DeltaPhiMax']`, the Carn will kill the Herb with a calculated
          probability. p is determined by carnivore fitness, herbivore fitness and `param['DeltaPhiMax']`
        - If the carnivore is satisfied, it will stop trying to kill herbs

        As a result of eating on or several Herbivores, the Carnivore weight
        and fitness level is updated for each prey eaten. The prey dies,
        even if the Carnivores does not eat the total weight of killed prey.

        Parameters
        ----------
        available_prey : list of Herbivore objects
            List of available Herbivores (prey), at the same location as Carnivore
            and shuffled in random order.


        Returns
        -------
        list of Herbivore objects
            A list of herbivore objects not eaten by Carnivores.

        See Also
        --------
        weight_gain :
            Calculates animal weight gain do to eating, updates Carnivore
            weight and fitness level.

        """
        eaten_food = 0  # Control of amount of Herbivore eaten - measured in Herbivore weight, start level
        herb_survivors = []  # List of surviving herbivores

        for i, herb in enumerate(available_prey):
            # If fitness level of Carn is lower than Herb, the Carn cannot kill any more herbs, and we return survivors
            if self.fitness <= herb.fitness:
                # If fitness is too low, return survivors
                return herb_survivors + available_prey[i:]

            elif 0 < self.fitness - herb.fitness < self.param['DeltaPhiMax']:  # Difference in fitness level
                # Probability for a carnivore to kill a herbivore
                p = (self.fitness - herb.fitness) / self.param['DeltaPhiMax']
                # With the given probability check if the Carnivore eats the Herbivore
                if random.random() < p and eaten_food < self.param['F']:  # Check if Carnivore is already satisfied
                    if eaten_food + herb.weight < self.param['F']:
                        self.weight_gain(herb.weight)  # increase Carnivore weight and update fitness
                        eaten_food += herb.weight  # increase amount eaten to eaten_food
                    else:
                        self.weight_gain(self.param['F'])
                        # If satisfied, return the survivors
                        return herb_survivors + available_prey[i + 1:]
                else:
                    herb_survivors.append(herb)  # Herbivore not eaten added to list of survivers
            # Else the carnivore kills the herb with p = 1

        return herb_survivors


class Herbivore(Animal):
    """
    Implements the animal species Herbivore.

    The animal consist of characteristics, which is represented by
    attributes. In addition to behaviour, which is represented by
    methods. Behaviour (utilized with methods), can change the
    animal's characteristics (attributes).
    
    ...

    Note
    ----
    This is a subclass of `Animal`. See Animal attributed and methods
    for documentation on inherited attributes and methods.

    Examples
    --------
    >>> anim = Herbivore(age=10, weight=30)
    >>> print("anim is {0} years old, weighs {1} and {2} fitness"
    ...       .format(anim.age,anim.weight,anim.fitness))
    anim is 10 years old, weighs 30 and have 0.8807970645633608 fitness

    """
    param = dict(w_birth=8.0, sigma_birth=1.5, beta=0.9, eta=0.05, a_half=40.0,
                 phi_age=0.6, w_half=10.0, phi_weight=0.1, mu=0.25, gamma=0.2,
                 zeta=3.5, xi=1.2, omega=0.4, F=10.0)  #: dict of str : Herbivore param to parameterize methods

    def eat_fodder(self, cell_fodder_amount):
        """
        Eat fodder.

        If there is enough fodder available, the Herbivore will eat till
        a satisfied level determined by `param['F']`. If available amount
        is bellow this param or equal to zero, the Herbivore will eat the
        remains of fodder.

        As a result of eating fodder the Herbivores weight and fitness
        level is updated for each prey eaten.

        Parameters
        ----------
        cell_fodder_amount : float
            Amount of fodder available in the cell/location of the Herbivore.

        Returns
        -------
        int or float
            `int` equal to 0 if there no more fodder available for the Herbivore to eat
            `float` if the Herbivore has eaten remaining or a max amount of `param['F']`
            fodder.

        See Also
        --------
        weight_gain :
            Calculates animal weight gain do to eating, updates Herbivore
            weight and fitness level.

        """
        consumed_fodder = self.param['F']  # Amount of fodder to satisfy Herbivore
        if cell_fodder_amount == 0:  # No fodder in the cell/location of the Herbivore
            return 0
        elif cell_fodder_amount < consumed_fodder:  # Amount available is less then amount of fodder to satisfy
            consumed_fodder = cell_fodder_amount  # Herbivore eats remaining fodder in cell/location
            self.weight_gain(consumed_fodder)  # Herbivore gains weight
            return consumed_fodder
        else:  # Amount in cell is enough to satisfy Herbivore
            self.weight_gain(consumed_fodder)  # Herbivore gains weight
            return consumed_fodder
