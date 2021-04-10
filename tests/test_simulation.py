#!python
# -*- coding: utf-8 -*-

"""
Tests for the simulation module
"""

__author__ = 'Therese Aase Knapskog and Astrid Moum'
__email__ = 'therese.knapskog@nmbu.no and astridmo@nmbu.no'

from biosim.simulation import BioSim
from biosim.animals import Herbivore, Carnivore
from biosim.landscape import Highland
import pytest


class TestParamsAnimLand:

    @pytest.fixture(autouse=True)
    def create_island(self):
        """Create default island"""
        geogr = """\
                                WWWWW
                                WLLLW
                                WLLLW
                                WLLLW
                                WWWWW"""
        init_pop = [{'loc': (3, 3),
                     'pop': [{'species': 'Herbivore', 'age': 5, 'weight': 50} for _ in range(100)]},
                    {'loc': (3, 3),
                     'pop': [{'species': 'Carnivore', 'age': 5, 'weight': 50} for _ in range(100)]}
                    ]
        seed = 150
        self.sim = BioSim(seed=seed, ini_pop=init_pop, island_map=geogr)

    @pytest.mark.parametrize('new_param, species',
                             [({'zeta': 3.2, 'xi': 1.8}, "NoSpecies"), ({'notExist': 1.2}, "Herbivore")])
    def test_animparam_valueerrors(self, new_param, species):
        """
        Raise ValueError if:
        - Parameter is not defined
        - Species is not defined
        """
        with pytest.raises(ValueError):
            self.sim.set_animal_parameters(species, new_param)

    @pytest.mark.parametrize('land_type, land_param',
                             [("NoLand", {'f_max': 300.0}), ("Lowland", {'no_param': 300})])
    def test_landparam_valueerrors(self, land_type, land_param):
        """
        Raise ValueError if:
        - Parameter is not defined
        - Landscape is not defined
        """
        with pytest.raises(ValueError):
            self.sim.set_landscape_parameters(land_type, land_param)

    def test_neg_land_param(self):
        """Test that negative values for parameters raises error"""
        land_type = "L"
        land_param = {'f_max': -300.0}
        with pytest.raises(ValueError):
            self.sim.set_landscape_parameters(land_type, land_param)

    def test_param_herbivore(self):
        """Test that parameters are updated correctly for herbivores, and not changing for carnivores"""
        new_params = {'zeta': 3.2, 'xi': 1.8}
        species = "Herbivore"
        self.sim.set_animal_parameters(species, new_params)
        assert Herbivore.param['zeta'] == 3.2 and Herbivore.param['xi'] == 1.8
        assert Carnivore.param['zeta'] == 3.5 and Carnivore.param['xi'] == 1.1

    def test_float_param(self):
        """Test that all params are float. Input params will be made float"""
        new_anim_param = {'zeta': 3}
        species = "Herbivore"
        land_type = "H"
        self.sim.set_animal_parameters(species, new_anim_param)
        assert isinstance(Herbivore.param['zeta'], float)

    def test_type_error(self):
        """Test that wrong input for parameters raises error"""
        new_anim_param = {'zeta': "tre"}
        new_land_param = {'f_max': "hundre"}
        species = "Herbivore"
        land_type = "H"
        with pytest.raises(ValueError):
            self.sim.set_animal_parameters(species, new_anim_param)
        with pytest.raises(ValueError):
            self.sim.set_landscape_parameters(land_type, new_land_param)

    def test_typing_mistake(self):
        """
        Test that typing mistake for input of parameters correct the mistake,
        and that parameters is sat to the correct value
        ."""
        new_anim_param = {'zeta': 3}
        new_land_param = {'f_max': 300}
        species = "HERBivore"
        land_type = "h"
        self.sim.set_animal_parameters(species, new_anim_param)
        self.sim.set_landscape_parameters(land_type, new_land_param)
        assert Herbivore.param['zeta'] == 3.0
        assert Highland.param['f_max'] == 300


class TestOtherParams:

    @pytest.fixture(autouse=True)
    def create_island(self):
        """Create default island"""
        self.geogr = """\
                                    WWWWW
                                    WLLLW
                                    WLLLW
                                    WLLLW
                                    WWWWW"""
        self.init_pop = [{'loc': (3, 3),
                         'pop': [{'species': 'Herbivore', 'age': 5, 'weight': 50} for _ in range(100)]},
                         {'loc': (3, 3),
                          'pop': [{'species': 'Carnivore', 'age': 5, 'weight': 50} for _ in range(100)]}]
        self.seed = 150

    def test_ymax_cmaxanimals(self):
        """Test that the ymax raises error if input is negative"""
        ymax_animals = -1000
        with pytest.raises(ValueError):
            BioSim(island_map=self.geogr, ini_pop=self.init_pop, seed=self.seed, ymax_animals=ymax_animals)