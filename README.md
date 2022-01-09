# planslab

`planslab` is a python repository intended to be a laboratory for playing around with the `plans` model concepts, which itself is based in TOPMODEL.

##local machines

to run `planslab` on a local machine you will need to pre-install:
* `python3` 
* `numpy`
* `pandas`
* `matplotlib`
* `scipy`
* `imageio`

there is plenty of information on the web about how to do it for different operating systems, so go check it out. 

## cloud - google colab
alternatively you may run it in the cloud using google's `colab` platform so you do not need to worry about any of these libraries.
1) create a google account for you;
2) create a `colab` blank notebook on https://colab.research.google.com/;
3) clone this repository;
4) upload all python files using the upload tool on the side bar;
5) create a directory for storing the data on the side bar;
6) upload all data files in the directory you just created;
7) start writing your scripts.

## recipes

Included in the repo there is this `cookbook.py` file. you may check it for some neat examples.

### sensitivity analysis of the `m` parameter

For instance, consider the `TOPMODEL` concepts of the local and global deficits and the `m` exponential decay parameter for baseflow discharge.

Then ask yourself how the saturated areas would change if the `m` is different. 

In other words: what is the sensitivity of local deficits and saturated areas to the `m` parameter?

This may be answered with the following typical recipe:

```python
# import tool:
from tools import sal_d_by_m

# define TWI raster file:
_ftwi = './data/twi.asc'

# define TWI raster file:
_fbasin = './data/basin.asc'

# define output folder:
_outfolder = '/content/output'

# call tool and parameters:
sal_d_by_m(ftwi=_ftwi,
           fbasin=_fbasin,
           m1=1,
           m2=5,
           dmax=50,
           size=30,
           label='lab',
           wkpl=True,
           folder=_outfolder)
```
Thus yielding a nice gif animation:

![sal_m](https://github.com/ipo-exe/planslab/blob/main/docs/animation.gif "sal")
