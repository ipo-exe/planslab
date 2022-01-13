# planslab

`planslab` is a python repository intended to be a laboratory for playing around with the `plans` model concepts, which itself is based in `TOPMODEL`.

## local machines

To run `planslab` on a local machine you will need to pre-install:
* `python3` 
* `numpy`
* `pandas`
* `matplotlib`
* `scipy`
* `imageio`

There is a lot of information on the web about how to do it for different operating systems, so go check it out. 

## cloud - google colab
Alternatively you may run `planslab` in the cloud using google's `colab` platform so you do not need to worry about any of these libraries.
1) create a google account for you;
2) create a `colab` blank notebook on https://colab.research.google.com/;
3) clone this repository;
4) upload all python files using the upload tool on the side bar;
5) create a directory for storing the data on the side bar;
6) upload all data files in the directory you just created;
7) start writing your scripts.

# basics

## the `TWI` 

`TOPMODEL` (Beven & Kirkby, 1979) is a semi-distributed hydrological model, 
so is it based on the _hydrological similarity_ concept. 
It uses topographical information to predict the **propensity to soil saturation** in 
different
places within a given catchment. Such _similarity index_ is named `TWI` or 
_Topographical Wetness Index_ and it may be computed in a map grid as follows:

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


There is some physical justification for the `TWI` standard formula, which was derived based on 
a set of assumptions. We invite you to come with some new hypothesis for a saturation
propensity index. Here we got a new saturation index, the `HTWI`, which uses the `HAND` and `TWI`
in a composite formula:

![htwi](https://github.com/ipo-exe/planslab/blob/main/data/htwi.png "htwi")

## local deficits and variable source area




## recipes

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


