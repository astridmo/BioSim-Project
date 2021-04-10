#!python
# -*- coding: utf-8 -*-


"""
Test for the island module
"""

__author__ = 'Therese Aase Knapskog and Astrid Moum'
__email__ = 'therese.knapskog@nmbu.no and astridmo@nmbu.no'

from biosim.island import Island
import pytest


class TestIsland:
    @pytest.fixture(autouse=True)
    def create_island(self):
        """Create a default island"""
        geogr = """\
                        WWWWW
                        WLLLW
                        WLLLW
                        WLLLW
                        WWWWW"""
        ini_pop = [{'loc': (3, 3),
                    'pop': [{'species': 'Herbivore', 'age': 5, 'weight': 50} for _ in range(100)]},
                   {'loc': (3, 3),
                    'pop': [{'species': 'Carnivore', 'age': 5, 'weight': 50} for _ in range(100)]}
                   ]
        self.island = Island(ini_pop, geogr)

    def test_num_animals(self):
        """Test that the number of animals on the island is correct"""
        n_cells = 1
        herb_num = 100
        carn_num = 100
        herb_tot, carn_tot = self.island.anim_count()  # Gjøre om for tuple når du legger inn carnivore
        assert herb_tot == n_cells * herb_num
        assert carn_tot == n_cells * carn_num

    @pytest.mark.parametrize('geogr',
                             ["""\
                             WWWWW
                             WLLLW
                             WLLLWW
                             WLLLW
                             WWWWW""", """\
                    WWWWW
                    WLLLW
                    WLLLK
                    WLLLW
                    WWWWW""", """\
                             WWWWW
                             WLLLW
                             WLLLL
                             WLLLW
                             WWWWW""", """\
                    WWWWW
                    WLLLW
                    WL4LW
                    WLLLW
                    WWWWW"""])
    def test_wrong_landscape(self, geogr):
        """Test that the program returns ValueError if the map is not correct"""
        with pytest.raises(ValueError):
            Island(geogr=geogr)


class TestMigration:
    @pytest.fixture(autouse=True)
    def create_island(self):
        """Create a default island"""
        geogr = """\
                            WWWWW
                            WLLLW
                            WLLLW
                            WLLLW
                            WWWWW"""
        ini_pop = [{'loc': (3, 3),
                    'pop': [{'species': 'Herbivore', 'age': 5, 'weight': 50} for _ in range(100)]},
                   {'loc': (3, 3),
                    'pop': [{'species': 'Carnivore', 'age': 5, 'weight': 50} for _ in range(100)]}
                   ]
        self.island = Island(ini_pop, geogr)

        # Running migration for one year
        self.island.annual_migration()

    @pytest.mark.parametrize('row, col',
                             [(1, 1), (3, 1), (1, 3), (3, 3)])
    def test_no_diagonal_migration(self, row, col):
        """Animals are not allowed to migrate diagonally"""
        assert self.island.anim_matrix()[0][row, col] == 0
        assert self.island.anim_matrix()[1][row, col] == 0

    @pytest.mark.parametrize('row, col',
                             [(2, 1), (1, 2), (3, 2), (2, 3)])
    def test_some_migration_happens(self, row, col):
        """
        After one cycle, some animals will have moved.
        The start cell will have less animals, and the neighbouring cells will not be empty
        """
        start_cell = 2, 2
        assert self.island.anim_matrix()[0][start_cell] != 100
        assert self.island.anim_matrix()[1][start_cell] != 100
        assert self.island.anim_matrix()[0][row, col] != 0
        assert self.island.anim_matrix()[1][row, col] != 0

    def test_no_anim_change(self):
        """
        When only annual migration is running, the number of animals
        on the island will be constant
        """
        num_herb, num_carn = self.island.anim_count()
        [self.island.annual_migration() for _ in range(10)]
        assert num_herb, num_carn == self.island.anim_count()

