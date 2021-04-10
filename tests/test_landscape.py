#!python
# -*- coding: utf-8 -*-

"""
Tests for the landscape module
"""

__author__ = 'Therese Knapskog and Astrid Moum'
__email__ = 'therese.knapskog@nmbu.no and astridmo@nmbu.no'

from biosim.landscape import Lowland
from biosim.animals import Herbivore
import pytest
from scipy.stats import binom_test


class TestGeneralAndFeeding:
    @pytest.fixture(autouse=True)
    def create_anims(self):
        """Create default animals"""
        self.herb_ini = [dict(species='Herbivore', age=5, weight=20) for _ in range(10)]
        carn_pop = [dict(species='Carnivore', age=5, weight=50) for _ in range(5)]
        self.land = Lowland(self.herb_ini)
        self.land.add_land_pop(carn_pop)

    def test_lowland_herbivore(self):
        """Test if all animals created are Herbivores"""
        for herb in self.land.herb_pop:
            assert isinstance(herb, Herbivore)

    def test_landscape_get_num_herbivore(self):
        """Testing the number of animals in the cell"""
        assert self.land.pop_count_herb() == 10
        assert self.land.pop_count_carn() == 5

    def test_herb_weight(self):
        """Test that the weight is correct"""
        for herb in self.land.herb_pop:
            assert herb.weight == 20

    def test_weight_gain(self):
        """Animals shall gain weight when eating"""
        land = Lowland(self.herb_ini)
        for herb in land.herb_pop:
            weight = herb.weight
            land.feeding()
            assert herb.weight > weight

    def test_herb_weight_gain(self):
        """The weight shall be gain with: fodder * beta = 10 * 0,9 += 9"""
        land = Lowland(self.herb_ini)
        land.feeding()
        for herb in land.herb_pop:
            assert herb.weight == 29.0


class TestAgingDying:
    @pytest.fixture(autouse=True)
    def create_anims(self):
        """Create default animals"""
        self.herb_ini = [
            dict(species='Herbivore', age=5, weight=20) for _ in range(10)]
        carn_pop = [
            dict(species='Carnivore', age=5, weight=20) for _ in range(5)]
        self.land = Lowland(self.herb_ini)
        self.land.add_land_pop(carn_pop)

    def test_aging_animalpop(self, mocker):
        """
        Test that:
         - The age change is correct
         - The age_change method is called the same amount of times as the
           number of animals
        """
        mocker.spy(Herbivore, 'age_change')
        self.land.aging()
        assert [animal.age == 6 for animal in self.land.herb_pop]
        assert Herbivore.age_change.call_count == self.land.pop_count_herb()

    def test_dying_animal(self):
        """Test that some animals will dye"""
        for index, animal in enumerate(self.land.herb_pop):
            if index == 1:
                animal.weight = 0
        self.land.death()
        assert self.land.pop_count_herb() <= 9

    def test_death(self):
        """Statistical test for death of carnivores"""
        p = 0.21515313753945986
        alpha = 0.01
        carn_num = self.land.pop_count_carn()
        self.land.death()
        died_carn = carn_num - self.land.pop_count_carn()

        assert binom_test(died_carn, carn_num, p) > alpha


class TestProcreation:
    def test_procreation(self):
        """Testing that procreation gives more animals in cell"""
        test_init_pop = [
            dict(species='Herbivore', age=5, weight=35) for _ in range(50)]
        land = Lowland(test_init_pop)
        for _ in range(2):
            num_herb = land.pop_count_herb()
            land.procreation()
            land.feeding()
            assert land.pop_count_herb() > num_herb
