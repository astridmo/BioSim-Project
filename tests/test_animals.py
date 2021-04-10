#!python
# -*- coding: utf-8 -*-

"""
Test for the animals module
"""

__author__ = 'Therese Aase Knapskog and Astrid Moum'
__email__ = 'therese.knapskog@nmbu.no and astridmo@nmbu.no'

from biosim.animals import Herbivore, Carnivore
import math
import pytest
import random
import scipy.stats as stats


def test_input_age_weight():
    """Test for input"""
    h = Herbivore(3, 40)
    assert h.age == 3
    assert h.weight == 40


class AnimalDefaultAttribute:
    @pytest.fixture(autouse=True)
    def __init__(self):
        self.herb = Herbivore()
        self.carn = Carnivore()

    def test_initial_age_zero(self):
        """Testing that age is 0 when no input"""
        assert self.herb.age == 0
        assert self.carn.age == 0

    def test_annual_age_change(self):
        """Testing that an animal will age"""
        [self.herb.age_change() for _ in range(5)]
        self.herb.age_change()
        self.carn.age_change()
        assert self.herb.age == 5
        assert self.carn.age == 1

    def test_fitness_value_interval(self):
        """Testing that fitness level is >= 0 and <=1"""
        assert 0 <= self.herb.fitness <= 1

    def test_zero_fitness(self):
        """Testing that fitness will be zero at weight <= 0"""
        self.carn.weight = 0
        self.carn.fitness_update()
        assert self.carn.fitness != 0
        self.carn.weight = -10
        self.carn.fitness_update()
        assert self.carn.fitness == 0


def test_negative_age():
    """Testing that negative age returns error"""
    with pytest.raises(ValueError):
        Herbivore(age=-1)


def test_negative_weight():
    """Testing that negative weight returns ValueError"""
    with pytest.raises(ValueError):
        Herbivore(age=5, weight=-3)


class TestProbabilityDeathBirthMigrate:
    @pytest.fixture(autouse=True)
    def default_anims(self):
        self.herb = Herbivore(age=5, weight=20)
        self.carn = Carnivore(age=5, weight=50)
        self.seed = 123  # random seed for tests
        self.n = 100
        self.alpha = 0.01  # significance level for statistical tests

    def phi_calc(self, x, p):
        mean = self.n * p
        var = self.n * p * (1 - p)  # variance
        z = (x - mean) / math.sqrt(var)  # number of instances minus the mean. divided by standard deviation
        phi = 2 * stats.norm.cdf(-abs(z))  # two tailed test
        return phi

    def test_probability_death(self):
        """
        Using Z-test to test that the probability of dying follows a normal distribution.
        Null hypothesis: The data follows a normal distribution
        Z = (point estimate - mean)/(standard deviation).
        phi is the probability for observing number of instances that is >Z* or <-Z*. That means the
        probability to be in one of the outer edges of the tail.
        We will do a two tailed test, therefore phi has to be multiplied with 2.

        If phi < alpha, the null hypothesis is discarded. Therefore, the test will pass if phi > alpha
        """
        random.seed(self.seed)
        p = self.herb.param['omega'] * (1 - self.herb.fitness)  # p = 0.1076
        x = sum(self.herb.dying() for _ in range(self.n))
        assert self.phi_calc(x, p) > self.alpha

    def test_death_zero_weight(self):
        """
        Testing that animal dies if weight <= 0
        """
        self.herb.weight = 0
        self.carn.weight = 0
        assert self.herb.dying() is True
        assert self.carn.dying() is True

    def test_absolute_death(self):
        """
        Testing that animal dies if calculated probability of dying is 1
        """
        self.herb.param['omega'] = 1
        self.herb.fitness = 0
        assert self.herb.dying() is True

    def test_survival(self):
        """Animal will not die if fitness is 1. Test that list only contains False"""
        self.herb.fitness = 1
        assert not any([self.herb.dying() for _ in range(10)])

    def test_zero_probability_birth(self):
        """
        Tests that the probability of birth is zero if:
        1. The animal is a newborn (weight too low)
        2. The animal is alone in the cell
        """
        herb2 = Herbivore()
        assert self.herb.birth(1) is None
        assert herb2.birth(10) is None

    def test_absolute_birth(self):
        self.herb.weight = 100
        self.herb.param['gamma'] = 1
        self.herb.fitness = 1
        assert self.herb.birth is not None

    def test_birth(self):
        self.herb.weight = 50
        num_animals = 10
        list_h = [nb for nb in [self.herb.birth(num_animals) for _ in range(100)] if nb is not None]
        assert len(list_h) != 0

    def test_migrate(self):
        """
        Using Z-test to test that the probability of dying follows a normal distribution.
        Null hypothesis: The data follows a normal distribution
        Z = (point estimate - mean)/(standard deviation).
        phi is the probability for observing number of instances that is >Z* or <-Z*. That means the
        probability to be in one of the outer edges of the tail.
        We will do a two tailed test, therefore phi has to be multiplied with 2.

        If phi < alpha, the null hypothesis is discarded. Therefore, the test will pass if phi > alpha
        """
        random.seed(self.seed)
        p = self.herb.param['mu'] * self.herb.fitness  # p = 0.183
        x = sum(self.herb.migrate() for _ in range(self.n))
        assert self.phi_calc(x, p) > self.alpha


def test_no_fodder():
    """
    Test to see that weight and fitness does not change if amount of fodder is zero
    """
    herbivore = Herbivore()
    cell_fodder_amount = 0
    assert herbivore.eat_fodder(cell_fodder_amount) == 0


def test_max_fodder():
    """
    Test to see that the maximum consumed fodder is the parameter 'F'
    """
    herbivore = Herbivore()
    cell_fodder_amount = 50
    assert herbivore.eat_fodder(cell_fodder_amount) == herbivore.param['F']


def test_no_weightgain_herb():
    """
    Test to see that weight gain is zero when there is no fodder available
    """
    herbivore = Herbivore()
    weight = herbivore.weight
    fitness = herbivore.fitness
    consumed_fodder = 0
    herbivore.weight_gain(consumed_fodder)
    assert herbivore.weight == weight
    assert herbivore.fitness == fitness


def test_no_weightgain_carn():
    """
    Test to see that weight gain is zero when carnivore does not kill any herbivore
    """
    carn = Carnivore()
    weight = carn.weight
    fitness = carn.fitness
    consumed_herb = 0
    carn.weight_gain(consumed_herb)
    assert carn.weight == weight
    assert carn.fitness == fitness


def test_max_weightgain_herb():
    """
    Test to see that maximum weight gain is correct
    """
    herbivore = Herbivore()
    herbivore.weight = 7
    cell_fodder_amount = 50
    herbivore.eat_fodder(cell_fodder_amount)
    assert herbivore.weight == 16


def test_no_weightgain():
    """
    Test to see no weightgain if consumed food is zero
    """
    herbivore = Herbivore()
    weight = herbivore.weight
    consumed_food = 0
    herbivore.weight_gain(consumed_food)
    assert herbivore.weight == weight


def test_no_kill():
    """Carnivore cannot kill if fitness is lower than herbivores fitness"""
    herb, carn = Herbivore(), Carnivore()
    herb.fitness, carn.fitness = 0.8, 0.6
    herb_list = [herb]
    assert carn.eat_herb(herb_list) == [herb]


def test_absolute_kill():
    """Absolute kill when DeltaPhi (difference in fitness) > DeltaPhiMax"""
    herb, carn = Herbivore(), Carnivore()
    herb.fitness, carn.fitness = 0.6, 12  # Note that this is not possible as fitness always is in interval[0,1].
    list_herb = [herb]
    assert carn.eat_herb(list_herb) == []  # The test is only to see an absolute kill where DeltaPhi > DeltaPhiMax


def test_herb_left():
    """Test that some herbivores will survive when a carnivore tries to kill them"""
    herb_list = [Herbivore(3, 10) for _ in range(100)]
    carn = Carnivore(8, 50)
    herb_survivors = carn.eat_herb(herb_list)
    assert herb_survivors != []
    assert herb_survivors != herb_list


def test_weight_loss():
    """Test that annual weight loss works"""
    herbivore = Herbivore()
    herbivore.weight = 5
    herbivore.weight_loss()
    assert herbivore.weight == 4.75


def test_type():
    """Test that the type of the subclass is correct"""
    herb = Herbivore()
    assert type(herb) == Herbivore
    assert herb.__repr__() == 'Herbivore()'
