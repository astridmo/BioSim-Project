# BioSim Project G19

__Norwegian University of Life Science (NMBU)__

Task : Modelling the Ecosystem of Rossumøya

Course : INF200 Advanced programming

Completed: January 2021

Authors: Astrid Lye Moum and Therese Aase Knapskog 

## Table of contents
* [General info](#general-info)
* [Package content](#package-content)
* [Setup](#setup)
* [Usage](#usage)
* [Note](#note)
* [Our focus](#our-focus)
* [Limitations](#limitations)

## General info
__This package is a result of a project request__ by Environmental Protection 
Agency of Pylandia (EPAP). EPAP's goal is to preserve the island Rossumøya
for future generations. They have requested a simulation to 
help __examine whether both species on the island can survive in a long-term 
perspective__.

As an answer to the request the package provides a dynamic population 
simulation, where main functionalities are:

    - Make a desired island,
    - with four varieties of landscape types; Lowland, Highland, Dessert and Water.
    - Place animal species, Herbivore and/or Carnivore, at desired locations.
    - Visualize the simulated results in desired time perspective (years)

## Package content
- biosim
    * animals.py
    * landscape.py
    * island.py
    * simulation.py
    * graphics.py
- examples
    * ex_landscape_module.py
    * ex_sim.py
- tests
    * test_animals.py
    * test_landscape.py
    * test_island.py
    * test_simulation.py
- docs
    * source
        - conf.py
        - base_modules.rst
        - index.rst
        - simulation.rst

## Setup
The package, hereby referred to as BioSim, consist of five modules:
- `animals`
- `landscape`
- `island`
- `simulation`
- `graphics`

The modules is built up by dependencies. To utilize separate
or all modules the first step is to import the BioSim package. 

```python
import biosim
```

## Usage

Use the class `BioSim()` to access the full extent of BioSim's package functionality.

The following subsections will illustrate how to use the `BioSim()`
class. Additionally, it will give a short summary of the package structure
by looking at the hierarchy of the package modules. 

### Simulating the ecosystem of an island

At the top of the dependencies hierarchy is the module `simulate`,
containing the packages main class `BioSim()`.

Through this class an island is constructed with types of landscapes
and one initial population. The class includes methods to set parameters, 
add an additional population during simulation period, save images or save
movies of the simulation. 

__The first step__ is to initialize the class `BioSim()`.

To do this, the code is (with required inputs):
- name of instance created = module.class(inputs)
- example = simulation.BioSim(inputs)

```python
import BioSim

example = simulation.BioSim(island_map, ini_pop, seed)

```

By writing the code above with the required inputs, a setup is created. 

The required inputs: A string of letters representing the island map, with 
landscape types. Information about the initial population, including start 
location, species, weight and age. Lastly a seed to generate random numbers.
The initial population has to be a dictionary on the following form
```python
ini_pop = {'loc': (2, 2),
           'pop': [{'species': 'Herbivore', 'age': 5, 'weight': 20} for _ in range(50)]}
```

In addition to these are several optional inputs. This includes visualisation parameters to 
change limits in plots. Image base meaning the path for where to save files 
+ image name, if you want to save images. Image filetype, default 'png'. 

By setting the correct inputs, and optionally directory for where images is
saved; __the second step is simulation__ and use of similar methods. 

This is how you run a simple simulation:
- name of class instance + .module.method(inputs)
- example + .simulation.simulate(inputs)

```python

example.simulate(num_years, vis_years, img_years=None)

```

The first two inputs determines number of years you want to simulate (num_years), 
and how many years you want to show in the visualisation (vis_years).

The output is an visualisation of the result, including:
- Count of year simulated
- Count of different animal species for each year simulated
- Map of island
- Heatmap of animal species, to see the spread of species of the current year
- Three histograms of animal age, weight and fitness of current year

It is possible to add a population during simulation:
- Start simulation
    - name of class instance + .module.method(inputs)
    - example.simulation.simulate(inputs)
- Add population
    - name of class instance + .module.method(inputs)
    - example.simulation.add_population(inputs)
- Continue simulation
    - name of class instance + .module.method(inputs)
    - example.simulation.simulate(inputs)

```python

example.simulate(num_years = 100, vis_years=1, img_years=None)
example.add_population(population=ini_carns)
example.simulate(num_years=100, vis_years=1)

```

In the code above a 100 years is simulated with the initial population, 
before an addition population is added to the island. Then the additional
100 years are simulated. In this case img_years is None, meaning that
no images are saved. 

### The BioSim hierarchy

From the example above, a population is added to an island. This is done
by using modules in a lower level. 

`simulation` is built on top of two modules; island and graphics. 
Below island is landscape, and below landscape is animals.

The graphics should only be used through simulation, while the other
modules can be used separately to create island, landscape or animals. 

Going back to the example above, modules build on each other. 

BioSim simulates an island, and the information about the island is
saved in the class `island` from `biosim.island` by creating an instance
of the class `BioSim.island.Island()`. To create an instance of island:
- name of instance created = module.class(inputs)
- example2 = island.Island(inputs)

The example below includes an example of the format for geography and initial
animal population. The map is letters identifying different landscapes, while
the initial population is a series of dictionaries with information about
start location, age, weight and fitness. 

```python
ex_map = """\
            WWW
            WLW
            WWW"""
ex_pop = [{'loc': (3, 3),
           'pop': [{'species': 'Herbivore', 'age': 5, 'weight': 50} for _ in range(100)]}]

example2 = island.Island(ini_pop=ex_pop, geogr=ex_map)

```

Below the level of the Island is landscape. Island stores information such as how many
animals species are in the same location (one landscape) or and how much fodder 
is available? This is stored in the classes `Lowland`, `Highland`, `Dessert` and 
`Water` from the module `BioSim.landscape. To create an instance of Lowland:
- name of instance created = module.class(inputs)
- example3 = landscape.Lowland(inputs)

```python

example3 = landscape.Lowland(init_pop)

```

Last in this hierarchy is animals, which landscape uses to save information about
species. Such as the information shown in the simulated result; age, weight and
fitness. To create a Herbivore instance:
- name of instance created = module.class(inputs)
- example4 = animals.Herbivore(inputs)

```python

example4 = animals.Herbivore(age, weight)

```

As shown `simulation`, `island`, `landscape` and `animal` can be used separately, 
but the modules in the higher level will use lower level modules - to complete
their information or functionality. In example, Biosim class sends the input data
several level down to define the population and landscapes.

Parameters set an lower level can me altered through BioSim, in this sense it is
not necessary to use lower level modules or class. However, it is possible. 


## Note
- The animals cannot be placed in water or be in the water
- The island must be surrounded by water
- Graphics parameters should to be set to ensure correct visualisation.

## Our focus
- Test driven development and make it work, then make it fast
- Good documentation
- Make the code robust for user input
- Make to code ready for further development

Optimization has been a focus, and profiling has been used to detect which areas 
of the code that use the most amount of time. Our effort has then been to optimize
the parts of the code that use the most amount of time.

Another focus has been do document well how the code works in the modules and
documentation through Sphinx. 

The code is correcting minor typing mistakes in parameter input. 
    - All lower and uppercase writing of Herbivore, Carnivore are allowed. 
    - The same goes for the landscape type, where the abbreviation can be both upper and lower case.
      NB! This works for `set_animal_parameters()` and `set_landscape_parameters()` input only  

````python
'herbivore', 'HERBIVORE', 'HERbivore'
'd', 'D'
````

While optimizing, the codes possibility to be further developed has been taken
into account. This means that we have not done optimizing on the cost of functionality. 

## Limitations
- The parameters are not set back to default. 
- Not possible to automatically log the simulation to a file, only visualisation
- Parameters in graphics is not adjusted automatically, meaning that large parts of 
  data can fall outside the picture. Or that picture is to big in relation to data. 
- No cmax is included
- The histspecs work only partly. This means that you have to set all parameters at once for it to work.
  In addition there is no test to make sure the input is correct
- If visyear > 1 the graph of animal counts will not be shown

