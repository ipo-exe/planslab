# planslab

`planslab` is a python repository intended to be a laboratory for playing around with 
the `plans` model concepts, which itself is based in `TOPMODEL`.

## local machines

To run `planslab` on a local machine you will need to pre-install:
* `python3` 
* `numpy`
* `pandas`
* `matplotlib`
* `scipy`
* `imageio`

There is a lot of information on the web about how to do it for different operating
systems, so go check it out. 

## cloud - google colab
Alternatively you may run `planslab` in the cloud using google's `colab` platform so 
you do not need to worry about any of these libraries.
1) create a google account for you;
2) create a `colab` blank notebook on https://colab.research.google.com/;
3) clone this repository;
4) upload all python files using the upload tool on the side bar;
5) create a directory for storing the data on the side bar;
6) upload all data files in the directory you just created;
7) start writing your scripts.

# some basics

## the `TWI` 

`TOPMODEL` (Beven & Kirkby, 1979) is a semi-distributed hydrological model, 
so is it based on the _hydrological similarity_ concept. 
It uses topographical information to predict the **propensity to soil saturation** 
in different places within a given catchment. Such _similarity index_ is named 
`TWI` or _Topographical Wetness Index_ and it may be computed in a map grid as follows:

```markdown
TWI = ln (flowacc / (n * tan(slope)))
```

Where:
* `flowacc` is the accumulated draining area in sq. meters;
* `n` is the resolution of the grid cell in meters; 
* `slope` is the slope of the terrain in radians

This formula basically says that the propensity for soil saturation is higher in flat 
places and in places downstream the catchment. In a map it should look like this:

![twi](https://github.com/ipo-exe/planslab/blob/main/data/twi.png "twi")


There is some physical justification for the `TWI` standard formula, which was derived 
mathmatically after a set of assumptions. We invite you to come with some new 
hypothesis for a saturation propensity index. For instance, here we provide a new 
saturation propensity index, the `HTWI`, which uses the `HAND` (height above the 
nearest drainage) and `TWI` in a composite formula:

![htwi](https://github.com/ipo-exe/planslab/blob/main/data/htwi.png "htwi")

## local deficits and variable source area

But how `TWI` helps modelling? As you may realize, `TWI` is just an static map. In fact,
`TOPMODEL` uses the `TWI` for mapping the _local_ soil saturation _deficit_, while 
the _global deficit_ is kept in check using a lumped classic approach.

The mapping formula is:

```markdown
di = d + m * (lambda - twi) , di >= 0
```
Where:
* `di` is the local deficit (i.e., the deficit map) in mm;
* `d` is the global deficit (i.e., the basin-wide deficit) in mm;
* `m` is an scaling parameter in mm;
* `twi` is the `TWI` map;
* `lambda` is the basin-wide`TWI` average value.

By coupling this to a hydrology model we may compute deficit maps for each 
simulation timestep:

![d_anim](https://github.com/ipo-exe/planslab/blob/main/docs/animation_d.gif "d")

A place where full saturation happens is where the local deficit is zero. Any rainfall
that manages to hit such areas would eventually flow off the catchment as saturation
excess runoff. And since the deficit map is dynamic, we can also visualize the 
Variable Source Area `VSA` maps for each simulation timestep:

![vsa_anim](https://github.com/ipo-exe/planslab/blob/main/docs/animation_vsa.gif "VSA")


## model structure

`plans` is sligthly more complicated than the original `TOPMODEL`, since it has more 
water stocks and related parameters. 

The local structure of `plans`:

![lcl](https://github.com/ipo-exe/plans3/blob/main/docs/figs/local_model.PNG "lcl")

The local structure of `plans`:

![gbl](https://github.com/ipo-exe/plans3/blob/main/docs/figs/global_model.PNG "gbl")


## baseflow `Qb`

The baseflow equation of `TOPMODEL` and `plans` is the hypothesis of soil 
exponential depletion:
```markdown
Qb = qo * exp(-d / m)
```
Where:
* `Qb` is the baseflow in mm/d;
* `qo` is the maximum baseflow in the condition of full saturation in mm/d;
* `d` is the global deficit in mm;
* `m` is the scaling parameter (or decay parameter) in mm;

## recharge `Qv`

Recharge is a vertical flow in the vadose zone (unsaturated zone). At the local
level, the hypothesis is that it tends to be the daily hydraulic conductivity
as this stock gets saturated:

```markdown
Qvi = ksat * unzi / di
```
Where:
* `Qvi` is the local recharge in mm/d;
* `ksat` is the daily hydraulic conductivity in mm/d;
* `unzi` is the local water stock in the vadose zone;
* `di` is the local deficit in mm;

## processing

### `hist`: the histogram approach
One important advantage of the similarity concept is that it allows fast processing. 
To avoid large grid computations all you need is to process the _histogram_ of discrete
hydrological units and only later scale the variables back in the map. 

This `hist` approach is mostly appealing for large basins, calibration exercices and 
uncertainty estimation.

However, it demands some sacrifice in spatial continuity.

### `g2g` : grid to grid 

When computation speed (and memory!) is not a constrain, one may process the model in 
a _grid to grid_ (`g2g`) mode. This approach process the whole grid of the basin so the
modeller has the freedom do provide detailed parameter maps.

For instance, consider the hypothesis that the observed `NDVI` in a given basin may be a 
good proxy for the heterogeneity of the canopy water stock capacity. In `g2g` mode
all you need to do is provide the `NDVI` map as the spatial proxy paramater.


# recipes

Included in the repo there is this `cookbook.py` file. you may check it for some neat examples.

### `SAL` (sensitivity analysis) of the `m` parameter

For instance, consider the `TOPMODEL` concepts of the local and global deficits and the `m` exponential decay parameter for baseflow discharge.

Then ask yourself how the saturated areas would change if the `m` is different. 

In other words: what is the sensitivity of local deficits and saturated areas to the `m` parameter?

This may be answered with the following typical recipe:

```python
# import tool:
from tools import sal_d_by_m

# define TWI raster file:
_ftwi = './data/twi.asc'

# define basin raster file:
_fbasin = './data/basin.asc'

# define output folder:
_outfolder = '/content/output'

# define the first m parameter value:
_m1 = 1

# define the second m paramete value:
_m2 = 5

# call tool and parameters:
sal_d_by_m(ftwi=_ftwi,
           fbasin=_fbasin,
           m1=_m1,
           m2=_m1,
           dmax=50,
           size=30,
           label='lab',
           wkpl=True,
           folder=_outfolder)
```
Thus yielding a cool gif animation:

![sal_m](https://github.com/ipo-exe/planslab/blob/main/docs/animation_m.gif "sal")


### `SAL` (sensitivity analysis) of the `lambda` parameter

In the `TOPMODEL`, `lambda` is defined as the average `TWI` value within the catchment basin. 
But who cares about the standard definition? In the formula `lambda` really works as a threshold for mapping local deficits. 
In `plans` it is relaxed as a regular model parameter. 
And thus we can perform some more `SAL`:

```python
import inout
import numpy as np

# import tool:
from tools import sal_d_by_lamb

# define TWI raster file:
_ftwi = './data/twi.asc'

# define Basin map file
_fbasin = './data/basin.asc'

# define output folder:
_outfolder = '/content/output'

# compute the standard lambda
# load twi map
meta, twi = inout.inp_asc_raster(file=_ftwi, dtype='float32')
# load basin map
meta, basin = inout.inp_asc_raster(file=_fbasin, dtype='float32')
# standard lambda:
lamb_mean = np.sum(twi * basin) / np.sum(basin)

# the first lambda will be the standard:
lamb_1 = lamb_mean

# and the second one may be twice the standard:
lamb_2 = lamb_1 * 2

# call tool and parameters:
sal_d_by_lamb(ftwi=_ftwi,
              m=4,
              lamb1=lamb_1,
              lamb2=lamb_2,
              dmax=50,
              size=30,
              label='lab',
              wkpl=True,
              folder=_outfolder)
```

And then we got another cool gif animation:

![sal_lamb](https://github.com/ipo-exe/planslab/blob/main/docs/animation_lamb.gif "sal")


### `SAL` (sensitivity analysis) of the `TWI`

`TWI` - the Topographic Wetness Index is among the core ideas behind the `TOPMODEL` approach. 
It is a similarity index map for the propensity to saturation of a given element in the catchment.

Again, there is the standard TWI formula derived from the assumptions made when `TOPMODEL` was developed.
And again, we do not care much about the standard formulas. 
What if the propensity to saturation if different? 
This type of question opens the doors for many new hypothesis of how this propensity to saturation can be mapped.

And we may perform some more `SAL` on this.

```python
 # import tool:
from tools import sal_d_by_twi

# define TWI1 raster file:
_ftwi1 = './data/twi.asc'

# define TWI2 raster file:
_ftwi2 = './data/htwi.asc'

# define Basin map file
_fbasin = './data/basin.asc'

# define output folder:
_outfolder = '/content/output'

# call tool and set parameters:
sal_d_by_twi(ftwi1=_ftwi1,
             ftwi2=_ftwi2,
             fbasin=_fbasin,
             m=4,
             dmax=50,
             size=30,
             label='lab',
             wkpl=True,
             folder=_outfolder)
```

More cool gif animation:

![sal_twi](https://github.com/ipo-exe/planslab/blob/main/docs/animation_twi.gif "sal")


