#!python
# -*- coding: utf-8 -*-

"""
Provides graphics support for visualisation in :py:mod:`simulation`.

Notes
-----
The module requires the program ``ffmpeg`` or ``convert``.
Available from ``<http://ffmpeg.org>`` and ``<http://imagemagick.org>``,
or by installing ``ffmpeg`` using ``conda install ffmpeg``.

You need to set the  :const:`_FFMPEG_BINARY` and :const:`_CONVERT_BINARY`
constants below to the command required to invoke the programs.
In addition, set the :const:`_DEFAULT_FILEBASE` constant below to the
directory and file-name start you want to use for the graphics output
files.

"""

__author__ = 'Therese Aase Knapskog and Astrid Moum'
__email__ = 'therese.knapskog@nmbu.no and astridmo@nmbu.no'

import matplotlib.pyplot as plt
import numpy as np
import subprocess
import os

# Update these variables to point to your ffmpeg and convert binaries
# If you installed ffmpeg using conda or installed both software in
# standard ways on your computer, no changes should be required.
# _CONVERT_BINARY/magick is only needed if you want to create animated GIFs.
_FFMPEG_BINARY = 'ffmpeg'
_MAGICK_BINARY = 'magick'

# update this to the directory and file-name beginning
# for the graphics files
_DEFAULT_FILEBASE = os.path.join('..', 'data')
_DEFAULT_IMG_FORMAT = 'png'
_DEFAULT_MOVIE_FORMAT = 'mp4'  # alternatives: mp4, gif


class Graphics:
    """Provides graphics interface for simulation.

    ...

    Parameters
    ----------
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
        Image path and beginning of a file name; '/..map/filename'. Filenames
        are formed as ’{}_{:05d}.{}’.format(img_base, img_no, img_fmt). Where
        img_no are consecutive image numbers starting from 0.
    img_fmt : str, default 'png'
        File type for figure/images saved.

    Attributes
    ----------
    param : {}
        Dictionary of plot parameters either set by user or default.
        For the user to set hist_spec values, a complete dictionary must
        be given as input.
        Legal keys are:

            - 'ymax_anim' : float, see Parameters.
            - 'cmax-anim' : float, see Parameters.
            - 'age_lim_bins' : array-like, bin limits for age hist.
            - 'age_xlim' : float, x_limit for age hist.
            - 'weight_lim_bins' : array-like, bin limits for weight hist.
            - 'weight_xlim' : float, x_limit for weight hist
            - 'fitness_lim_bins' : array-like,  bin limits for fitness hist.
            - 'fitness_xlim' : float, x_limit for fitness hist.

    Note
    ----
    To change hist_specs input the complete dict of dict must be given with
    all legal keys. See parameter for hist_spec requirements.

    """

    def __init__(self, ymax_animals=None, cmax_animals=None, hist_specs=None,
                 img_base=None, img_fmt='png'):
        self.param = {}
        if ymax_animals is not None:  # check is user have set parameter ymax_animals
            self.param['ymax_anim'] = ymax_animals
        else:
            self.param['ymax_anim'] = None

        if cmax_animals is not None:  # check is user have set parameter cmax_animals
            # PAKK OPP DICT, OG HA CMAX_HERB OG CMAX_CARN KANSKJE?
            self.param['cmax_anim'] = cmax_animals
        else:
            self.param['cmax_anim'] = None

        if hist_specs is not None:  # check for user histogram specifications


            # self.param['age_lim_bins'] = np.arange(0, hist_specs['age']['max'],  # create array with bins limit
            #                                        hist_specs['age']['delta'])
            # self.param['wgt_lim_bins'] = np.arange(0, hist_specs['weight']['max'],
            #                                        hist_specs['weight']['delta'])
            # self.param['fit_lim_bins'] = np.arange(0, hist_specs['fitness']['max'],
            #                                        hist_specs['fitness']['delta'])
            for hist_key in hist_specs:
                self.param[hist_key+"_lim_bins"] = np.arange(0, hist_specs[hist_key]['max'],  # create array with bins limit
                                                   hist_specs[hist_key]['delta'])
                self.param[hist_key+"_xlim"] = hist_specs[hist_key]['max']

            # self.param['age_xlim'] = hist_specs['age']['max']  # limits for x-axis max
            # self.param['wgt_xlim'] = hist_specs['weight']['max']
            # self.param['fit_xlim'] = hist_specs['fitness']['max']
        else:  # set default values as parameter values
            self.param['age_lim_bins'] = np.arange(0, 1.0, 0.05)  # create array with bins limit
            self.param['wgt_lim_bins'] = np.arange(0, 60.0, 2)
            self.param['fit_lim_bins'] = np.arange(0, 60.0, 2)
            self.param['age_xlim'] = 1.0   # limits for x-axis max
            self.param['wgt_xlim'] = 60.0
            self.param['fit_xlim'] = 60.0

        # set image or movie specifications, img_no to enumerate images saved.
        if img_base is not None:
            # images saved to directory with img_name
            self._img_base = img_base
        else:
            # No images if directory is not specified
            self._img_base = None

        # file format specified with default 'png'
        self._img_fmt = img_fmt if img_fmt is not None else _DEFAULT_IMG_FORMAT

        self._img_no = 0  # image numbering if saving files
        self._img_years = 1  # interval between saving image to file

        # the following will be initialized by _setup
        self._fig = None  # Figure setup
        self._grid_dim = None  # Subplot dimension

        self._ax1_year = None  # 1th plot (main axes) for year count
        self._year_tmpl = None  # Template for texted plotted
        self._year_txt = None  # Text patch plotted / updated

        self._ax2_count = None  # 2nd plot (main axes) for sum of island population
        self._count_herb = None  # Carnivore line plotted
        self._count_carn = None  # Herbivore line plotted
        self._count_lg = None  # Count plot legend (axes patched)

        self._ax3_map = None  # 3rd plot (main axes) of island map
        self._map_lg = None  # Island map legend (axes patched)

        self._ax4_herb_dist = None  # 4th plot (main axes) of Herbivore distribution
        self._herb_dist_img = None  # Herbivore heatmap
        self._ax5_carn_dist = None  # 5th axes (main axes) of Carnivore distribution
        self._carn_dist_img = None  # Carnivore heatmap

        self._ax6_anim_age = None  # 6th plot (main axes) of age histogram
        self._age_herb = None  # Herbivore line
        self._age_carn = None  # Carnivore line
        self._ax7_anim_wgt = None  # 7th plot (main axes) of weight histogram
        self._wgt_herb = None  # Herbivore line
        self._wgt_carn = None  # Carnivore line
        self._ax8_anim_fit = None  # 8th plot (main axes) of fitness histogram
        self._fit_herb = None  # Herbivore line
        self._fit_carn = None  # Carnivore line
        self._hist_lg = None  # Histogram legend (axes patched)

    def setup(self, final_year, img_years, str_map):
        """Prepare graphics, first step in visualisation.

        Parameters
        ----------
        final_year : int
            Last time step to be visualised (upper limit of x-axis in mean plot).
        img_years : int
            Interval between saving image to file.
        str_map : multiline str
            String of letters representing the geography of the island.

        Note
        ----
        Call this before calling :py:meth:`update()` for the first time after
        the final time step has changed.

        """

        self._img_years = img_years

        if self._fig is None:  # create new figure if none exist
            self._fig = plt.figure(figsize=(10, 8))
            self._fig.suptitle('Simulation of an island', weight='bold')

        if self._grid_dim is None:  # create grid dimension for subplots
            self._grid_dim = (3, 4)

        self._setup_year()  # 1st plot with year count
        self._setup_animal_count(final_year)  # 2nd plt with animal species count
        self._setup_heatmap()  # 3rd and 4th plot of animal distribution
        self._setup_map(str_map)  # 5th plot of island map
        self._setup_histogram()  # 6-8th plot of three age, weight and fitness histogram

        plt.subplots_adjust(left=0.125, bottom=0.1, right=0.9, top=0.9, wspace=0.4, hspace=0.6)

    def _setup_year(self):
        """
        Plot 1 axis with count of year simulated.

        """
        if self._ax1_year is None:
            self._ax1_year = plt.subplot2grid(self._grid_dim, (0, 0))
            self._ax1_year.axis('off')  # remove gridlines
            self._year_tmpl = "Year: {:5d}"  # set template text
            self._year_txt = self._ax1_year.text(0.5, 0.5, self._year_tmpl.format(0),
                                                 horizontalalignment='right',
                                                 verticalalignment='center', weight='bold',
                                                 transform=self._ax1_year.transAxes)

    def _setup_animal_count(self, final_year):
        """
        Plot 2 axis with count of animal species.

        Parameters
        ----------
        final_year : int
            Last time step to be visualised (upper limit of x-axis in mean plot).

        """
        line_color = {'Herbivore': 'olive', 'Carnivore': 'darksalmon'}
        if self._ax2_count is None:
            self._ax2_count = plt.subplot2grid(self._grid_dim, (0, 1), colspan=2)
            if self.param['ymax_anim'] is not None:  # set ymax if specified by user
                self._ax2_count.set_ylim(0, self.param['ymax_anim'])
            else:
                self._ax2_count.set_ylim(0, 15000)
            self._ax2_count.set_title('Sum of animals')
            self._ax2_count.set_xlabel('years')
            self._ax2_count.set_ylabel('sum')

        self._ax2_count.set_xlim(0, final_year + 1)  # to use simulate() x_lim needs subsequent updating

        if self._count_herb is None:  # Herbivore line
            herb_plot = self._ax2_count.plot(np.arange(0, final_year + 1),
                                             np.full(final_year + 1, np.nan),
                                             color=line_color['Herbivore'])
            self._count_herb = herb_plot[0]
        else:
            x_data, y_data = self._count_herb.get_data()
            x_new = np.arange(x_data[-1] + 1, final_year + 1)
            if len(x_new) > 0:
                y_new = np.full(x_new.shape, np.nan)
                self._count_herb.set_data(np.hstack((x_data, x_new)),
                                          np.hstack((y_data, y_new)))

        if self._count_carn is None:  # Carnivore line
            carn_plot = self._ax2_count.plot(np.arange(0, final_year + 1),
                                             np.full(final_year + 1, np.nan),
                                             color=line_color['Carnivore'])
            self._count_carn = carn_plot[0]
        else:
            x_data, y_data = self._count_carn.get_data()
            x_new = np.arange(x_data[-1] + 1, final_year + 1)
            if len(x_new) > 0:
                y_new = np.full(x_new.shape, np.nan)
                self._count_carn.set_data(np.hstack((x_data, x_new)),
                                          np.hstack((y_data, y_new)))

        if self._count_lg is None:
            self._count_lg = plt.subplot2grid(self._grid_dim, (0, 3))
            self._count_lg.axis('off')
            for ix, name in enumerate(('Herbivore', 'Carnivore')):
                self._count_lg.add_patch(plt.Rectangle((0., ix * 0.2), 0.3, 0.1,
                                                       edgecolor='none',
                                                       facecolor=line_color[name]))
                self._count_lg.text(0.35, ix * 0.2, name, transform=self._count_lg.transAxes)

    def _setup_heatmap(self):
        """
        Plot 3rd and 4th axis showing animal species distribution.

        """
        if self._ax4_herb_dist is None:  # Herbivore
            self._ax4_herb_dist = plt.subplot2grid(self._grid_dim, (1, 0))
            self._herb_dist_img = None
            self._ax4_herb_dist.set_title('Herbivore distr.')

        if self._ax5_carn_dist is None:  # Carnivore
            self._ax5_carn_dist = plt.subplot2grid(self._grid_dim, (1, 1))
            self._carn_dist_img = None
            self._ax5_carn_dist.set_title('Carnivore distr.')

    def _setup_map(self, str_map):  # 5th plot of island map
        """
        Plot 5th axes of an map of the island simulated.

        Parameters
        ----------
        str_map : multiline str
            String of letters representing the geography of the island.

        """
        if self._ax3_map is None:
            self._ax3_map = plt.subplot2grid(self._grid_dim, (1, 2))
            self._ax3_map.set_title('Map of island')

            # Setting mapcolor  R    G    B
            rgb_value = {'W': (0.0, 0.0, 1.0),  # blue
                         'L': (0.0, 0.6, 0.0),  # dark green
                         'H': (0.5, 1.0, 0.5),  # light green
                         'D': (1.0, 1.0, 0.5)}  # light yellow
            map_rgb = [[rgb_value[column] for column in row]
                       for row in str_map]

            self._ax3_map.imshow(map_rgb)
            self._ax3_map.set_xticks(range(0, len(map_rgb[0]), 5))
            self._ax3_map.set_xticklabels(range(1, 1 + len(map_rgb[0]), 5))
            self._ax3_map.set_yticks(range(0, len(map_rgb), 5))
            self._ax3_map.set_yticklabels(range(1, 1 + len(map_rgb), 5))

            self._map_lg = plt.subplot2grid(self._grid_dim, (1, 3))  # legend for map
            self._map_lg.axis('off')
            for ix, name in enumerate(('Water', 'Lowland',
                                       'Highland', 'Desert')):
                self._map_lg.add_patch(plt.Rectangle((0., ix * 0.2), 0.3, 0.1,
                                                     edgecolor='none',
                                                     facecolor=rgb_value[name[0]]))
                self._map_lg.text(0.35, ix * 0.2, name, transform=self._map_lg.transAxes)

    def _setup_histogram(self):
        """
        Plot 6th - 8th axes of animal species histograms; age, weight and fitness.

        """
        # Plot for age of species histogram
        if self._ax6_anim_age is None:
            self._ax6_anim_age = plt.subplot2grid(self._grid_dim, (2, 0))
            self._ax6_anim_age.set_xlim(0, self.param['age_xlim'])
            self._ax6_anim_age.set_ylim(0, 2000)
            self._ax6_anim_age.set_title('Age')
            self._ax6_anim_age.set_ylabel('Num of animals', weight='bold')

            plot_age_herb = self._ax6_anim_age.step(self.param['age_lim_bins'][:-1],
                                                    np.zeros_like(self.param['age_lim_bins'][:-1]),
                                                    'b-', where='mid', color='olive')
            self._age_herb = plot_age_herb[0]

            plot_age_carn = self._ax6_anim_age.step(self.param['age_lim_bins'][:-1],
                                                    np.zeros_like(self.param['age_lim_bins'][:-1]),
                                                    'b-', where='mid', color='darksalmon')
            self._age_carn = plot_age_carn[0]

        # Plot for weight of species histogram
        if self._ax7_anim_wgt is None:
            self._ax7_anim_wgt = plt.subplot2grid(self._grid_dim, (2, 1))
            self._ax7_anim_wgt.set_xlim(0, self.param['wgt_xlim'])
            self._ax7_anim_wgt.set_ylim(0, 2000)
            self._ax7_anim_wgt.set_title('Weight')

            plot_wgt_herb = self._ax7_anim_wgt.step(self.param['wgt_lim_bins'][:-1],
                                                    np.zeros_like(self.param['wgt_lim_bins'][:-1]),
                                                    'b-', where='mid', color='olive')
            self._wgt_herb = plot_wgt_herb[0]

            plot_wgt_carn = self._ax7_anim_wgt.step(self.param['wgt_lim_bins'][:-1],
                                                    np.zeros_like(self.param['wgt_lim_bins'][:-1]),
                                                    'b-', where='mid', color='darksalmon')
            self._wgt_carn = plot_wgt_carn[0]

        # Plot for fitness of species histogram
        if self._ax8_anim_fit is None:
            self._ax8_anim_fit = plt.subplot2grid(self._grid_dim, (2, 2))
            self._ax8_anim_fit.set_xlim(0, self.param['fit_xlim'])
            self._ax8_anim_fit.set_ylim(0, 2000)
            self._ax8_anim_fit.set_title('Fitness')

            plot_fit_herb = self._ax8_anim_fit.step(self.param['fit_lim_bins'][:-1],
                                                    np.zeros_like(self.param['fit_lim_bins'][:-1]),
                                                    'b-', where='mid', color='olive')
            self._fit_herb = plot_fit_herb[0]

            plot_fit_carn = self._ax8_anim_fit.step(self.param['fit_lim_bins'][:-1],
                                                    np.zeros_like(self.param['fit_lim_bins'][:-1]),
                                                    'b-', where='mid', color='darksalmon')
            self._fit_carn = plot_fit_carn[0]

        line_color = {'Herbivore': 'olive', 'Carnivore': 'darksalmon'}  # legend
        if self._hist_lg is None:
            self._hist_lg = plt.subplot2grid(self._grid_dim, (2, 3))
            self._hist_lg.axis('off')
            for ix, name in enumerate(('Herbivore', 'Carnivore')):
                self._hist_lg.add_patch(plt.Rectangle((0., ix * 0.2), 0.3, 0.1,
                                                      edgecolor='none',
                                                      facecolor=line_color[name]))
                self._hist_lg.text(0.35, ix * 0.2, name, transform=self._hist_lg.transAxes)

    def update(self, step, anim_pop, anim_matrix, data_hist):
        """
        Update graphics with current data and save to file if necessary.

        Parameters
        ----------
        step : int
            Same as year of current simulation
        anim_pop : list
            Sum of animal species on island; herbivores[0] and carnivores[1].
        anim_matrix : tuple of array-like [float]
            Matrix of animal species population in each landscape in island.
            The first matrix is for Herbivore population spread, the second
            for Carnivore.
        data_hist : List of List
            First level of nested list representing fitness, weight and age.
            Second level of nested listed separating data for each species.

                - data_hist[0][0], list of animal fitness levels for Herbivore
                - data_hist[0][1], list of animal fitness levels for Carnivore
                - data_hist[1][0], list of animal weight values for Herbivore
                - data_hist[1][1], list of animal weight values for Carnivore
                - data_hist[2][0], list of animal age values for Herbivore
                - data_hist[2][1], list of animal age values for Carnivore
        """

        self._update_year_count(step)
        self._update_mean_graph(step, anim_pop)
        self._update_heatmap(anim_matrix)
        self._update_histogram(data_hist)
        self._fig.canvas.flush_events()  # ensure every thing is drawn
        plt.pause(1e-6)  # pause required to pass control to GUI

        self._save_graphics(step)

    def _update_year_count(self, step):
        """
        Update the count of year simulated in plot, to current step.

        Parameters
        ----------
        step : int
            Same as year of current simulation

        """
        self._year_txt.set_text(self._year_tmpl.format(step))

    def _update_mean_graph(self, step, population):
        """
        Update mean-graph with current mean data.

        Parameters
        ----------
        step : int
            Same as year of current simulation
        population : list
            Sum of animal species on island; herbivores[0] and carnivores[1].

        Note
        ----
        Currently the plot can only update one data point at the time,
        as a result the lines are not visible if a file is saved and
        "vis_years" is more then one.

        """
        # herbivore line

        # OPPDATERE YMAX
        # if self.ymax and self.ymax < self.num_animals:
        #     self._line_graph_ax.set_ylim(0, self.ymax)
        # else:
        #     self._line_graph_ax.set_ylim(0, self.num_animals * 1.3)

        y_data_herb = self._count_herb.get_ydata()
        y_data_herb[step] = population[0]
        self._count_herb.set_ydata(y_data_herb)

        # carnivore line
        y_data_carn = self._count_carn.get_ydata()
        y_data_carn[step] = population[1]
        self._count_carn.set_ydata(y_data_carn)

    def _update_heatmap(self, anim_matrix):
        """
        Update plot with current animal distribution.

        Parameters
        ----------
        anim_matrix : tuple of array-like [float]
            Matrix of animal species population in each landscape in island.
            The first matrix is for Herbivore population spread, the second
            for Carnivore.

        """
        if self._herb_dist_img is not None:  # heatmap for herbivores
            self._herb_dist_img.set_data(anim_matrix[0])
        else:
            self._herb_dist_img = self._ax4_herb_dist.imshow(anim_matrix[0],
                                                             interpolation='nearest',
                                                             vmin=-0, vmax=self.param["cmax_anim"]["Herbivore"])
            plt.colorbar(self._herb_dist_img, ax=self._ax4_herb_dist)

        if self._carn_dist_img is not None:  # heatmap for carnivores
            self._carn_dist_img.set_data(anim_matrix[1])
        else:
            self._carn_dist_img = self._ax5_carn_dist.imshow(anim_matrix[1],
                                                             interpolation='nearest',
                                                             vmin=-0, vmax=self.param["cmax_anim"]["Carnivore"])
            plt.colorbar(self._carn_dist_img, ax=self._ax5_carn_dist)

    def _update_histogram(self, hist_data):
        """
        Update histogram with current animal species fitness, weight and age.

        Parameters
        ----------
        hist_data : List of List
            First level of nested list representing fitness, weight and age.
            Second level of nested listed separating data for each species.
                - data_hist[0][0], list of animal fitness levels for Herbivore
                - data_hist[0][1], list of animal fitness levels for Carnivore
                - data_hist[1][0], list of animal weight values for Herbivore
                - data_hist[1][1], list of animal weight values for Carnivore
                - data_hist[2][0], list of animal age values for Herbivore
                - data_hist[2][1], list of animal age values for Carnivore

        """
        # update of age histograms
        herb_age_data, bins = np.histogram(hist_data[2][0], self.param['age_lim_bins'])
        self._age_herb.set_ydata(herb_age_data)
        carn_age_data, bins = np.histogram(hist_data[2][1], self.param['age_lim_bins'])
        self._age_carn.set_ydata(carn_age_data)

        # update of age histograms
        herb_wgt_data, bins = np.histogram(hist_data[1][0], self.param['wgt_lim_bins'])
        self._wgt_herb.set_ydata(herb_wgt_data)
        carn_wgt_data, bins = np.histogram(hist_data[1][1], self.param['wgt_lim_bins'])
        self._wgt_carn.set_ydata(carn_wgt_data)

        # update of age histograms
        herb_fit_data, bins = np.histogram(hist_data[0][0], self.param['fit_lim_bins'])
        self._fit_herb.set_ydata(herb_fit_data)
        carn_fit_data, bins = np.histogram(hist_data[0][1], self.param['fit_lim_bins'])
        self._fit_carn.set_ydata(carn_fit_data)

    def _save_graphics(self, step):
        """
        Saves graphics to file if _img_base is not None.

        Parameters
        ----------
        step : int
            Same as year of current simulation

        """

        if self._img_base is None or step % self._img_years != 0:
            return

        plt.savefig('{base}_{num:05d}.{type}'.format(base=self._img_base,
                                                     num=self._img_no,
                                                     type=self._img_fmt))
        self._img_no += 1

    def make_movie(self, movie_fmt):
        """
        Creates MPEG4 movie from visualization images saved.

        The movie is stored as img_base + movie_fmt

        Note
        ----
        Requires ffmpeg for MP4 and magick for GIF

        """

        if movie_fmt is None:
            movie_fmt = _DEFAULT_MOVIE_FORMAT

        if self._img_base is None:
            raise RuntimeError("No filename defined.")

        if movie_fmt == 'mp4':
            try:
                # Parameters chosen according to http://trac.ffmpeg.org/wiki/Encode/H.264,
                # section "Compatibility"
                subprocess.check_call([_FFMPEG_BINARY,
                                       '-i', '{}_%05d.png'.format(self._img_base),
                                       '-y',
                                       '-profile:v', 'baseline',
                                       '-level', '3.0',
                                       '-pix_fmt', 'yuv420p',
                                       '{}.{}'.format(self._img_base, movie_fmt)])
            except subprocess.CalledProcessError as err:
                raise RuntimeError('ERROR: ffmpeg failed with: {}'.format(err))
        elif movie_fmt == 'gif':
            try:
                subprocess.check_call([_MAGICK_BINARY,
                                       '-delay', '1',
                                       '-loop', '0',
                                       '{}_*.png'.format(self._img_base),
                                       '{}.{}'.format(self._img_base, movie_fmt)])
            except subprocess.CalledProcessError as err:
                raise RuntimeError('ERROR: convert failed with: {}'.format(err))
        else:
            raise ValueError('Unknown movie format: ' + movie_fmt)
