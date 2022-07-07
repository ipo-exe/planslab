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

---

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
mathematically after a set of assumptions. We invite you to come with some new 
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

The local structure of `TOPMODEL` is quite simple: it has a root zone water stock, the
vadose zone water stock (unsaturated zone) and the saturated zone water stock 
(calculated as the saturation deficit). `plans` is sligthly more complicated than 
the original `TOPMODEL`, since it has more water stocks and related parameters. 
In `plans` there is a canopy water stock, a surface water stock (representing both 
depressions and organic soil horizon) and the root zone stock is actually a 
threshold depth within the vadose and saturated water stocks.

The global structure of `plans` (similar of `TOPMODEL`):

![gbl](https://github.com/ipo-exe/planslab/blob/main/docs/model_global.png "gbl")

The local structure of `plans` includes some extra parameters:
* `cpmax`: canopy water stock capacity, in mm;
* `sfmax`: surface water stock capacity, in mm, and;
* `erz` (or simply `roots`): effective root zone depth, in mm.

![lcl](https://github.com/ipo-exe/planslab/blob/main/docs/model_local.png "lcl")


## recharge `Qv`

Recharge is a vertical flow in the vadose zone (unsaturated zone). At the local
level, the hypothesis is that it tends to be the daily hydraulic conductivity
as this stock gets saturated:

```markdown
qvi = ksat * unzi / di
```
Where:
* `qvi` is the local recharge in mm/d;
* `ksat` is the daily hydraulic conductivity in mm/d;
* `unzi` is the local water stock in the vadose zone;
* `di` is the local deficit in mm;

As any global variable, global recharge `Qv` is the basin-wide average of `qvi`:
```markdown
Qv = avg(qvi)
```

## streamflow `Q`

Streamflow is the sum of baseflow `Qb` and stormflow `Qs`:

```markdown
Q = Qb + Qs
```

## baseflow `Qb`

Baseflow is the streamflow component coming soil water drainage. 
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

## stormflow `Qs`

Stormflow is the streamflow component coming from runoff `R`. While runoff is computed as a local
variable, stormflow is the output at the basin outlet. The routing procedure in `plans` is the
`nash` model, that is, a cascade of linear reservoirs. 

For a pulse of runoff `r` at timestep `t`:

```markdown
Qs = R * ((t / k) ^ (n - 1)) * exp(- t / k) / (k * gamma(n)), n >= 1, k >= 1
```
Where:
* `n` is the number of linear reservoirs;
* `k` is the detention time of the linear reservoirs, in days;

## processing

### `hist`: the histogram approach
One important advantage of the similarity concept is that it allows fast processing. 
To avoid large grid computations all you need is to process discrete
hydrological units and only later use the _histogram_ of such units to scale the 
variables back in the map. 

This `hist` approach is mostly appealing for large basins, calibration exercices and 
uncertainty estimation. However, this mode demands some level of sacrifice in 
spatial continuity.

### `g2g` : grid to grid
When computation speed (and memory!) is not a constrain, one may process the model in 
a _grid to grid_ (`g2g`) mode. This approach process the whole grid of the basin so the
modeller has the freedom do provide detailed parameter maps.

For instance, consider the hypothesis that the observed `NDVI` in a given basin may be a 
good proxy for the heterogeneity of the canopy water stock capacity. While in `g2g` mode
all you need to do is provide the full `NDVI` map as the spatial proxy paramater.

The `g2g` approach is mostly appealing for small basins and scientific studies.

---

# recipes

Included in the repo there is this `cookbook.py` file. you may check it for some neat examples.

## `SAL` (sensitivity analysis) of `di` to the `m` parameter

For instance, consider the `TOPMODEL` concepts of the local and global deficits and the `m` exponential decay parameter for baseflow discharge.

Then ask yourself how the saturated areas `VSA` would change if the `m` is different. 

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

---

## `SAL` (sensitivity analysis) of `di` to the `lambda` parameter

In the `TOPMODEL`, `lambda` is defined as the average `TWI` value within the catchment 
basin. But who cares about the standard definition? In the formula `lambda` really
works as a threshold for mapping local deficits. In `plans` it is relaxed as a regular
model parameter. And thus we can perform some more `SAL`:

```python
import inp
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
meta, twi = inout.asc_raster(file=_ftwi, dtype='float32')
# load basin map
meta, basin = inout.asc_raster(file=_fbasin, dtype='float32')
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

---

## `SAL` (sensitivity analysis) of `di` to the `TWI` map

`TWI` - the Topographic Wetness Index is among the core ideas behind the `TOPMODEL` approach. 
It is a similarity index map for the propensity to saturation of a given element in the catchment.

Again, there is the standard TWI formula derived from the assumptions made when `TOPMODEL` was developed.

And again, we do not care much about the standard formulas. 
What if the propensity to saturation if different? 
This type of question opens the doors for many new hypothesis of how this propensity to saturation 
can be mapped.

As we mentined above, we provide the novel `HTWI` index map so we may perform some more `SAL` on this.

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

---

## `g2g` simulation

`planslab` offers a standard simulation tool for the `g2g` mode.

### playing with the model

The model is a python function that requires some input parameters. 
So if you want to play directly with the model you may need some
help:

```python
from model import simulation

print(help(simulation))
```
The output will be something like this:
```markdown
Help on function sim_g2g in module model:

sim_g2g(series_df, basin, twi, qt0, cpmax, sfmax, roots, qo, m, lamb, ksat, n, k, scale=1000, trace=True, tracevars='D-Cpy', integrate=False, integratevars='D-Qv')
    g2g simulation model
    
    Simulated variables:
    
    'D',    # saturated water stock deficit
    'Unz',  # unsaturated zone water stock
    'Sfs',  # surface water stock
    'Cpy',  # canopy water stock
    'VSA',  # variable source area
    'Prec', # precipitation
    'PET',  # potential evapotranspiration
    'Intc', # interceptation in canopy
    'Ints', # interceptation in surface
    'TF',   # throughfall
    'R',    # runoff
    'RIE',  # infiltration excess runoff (Hortonian)
    'RSE',  # saturation excess runoff (Dunnean)
    'RC',   # runofff coeficient (%)
    'Inf',  # infiltration
    'Qv',   # recharge
    'Evc',  # evaporation from the canopy
    'Evs',  # evaporation from the surface
    'Tpun', # transpiration from the unsaturated zone
    'Tpgw', # transpiration from the saturated zone
    'ET',   # evapotranspiration
    'Qb',   # baseflow
    'Qs',   # stormflow
    'Q'     # streamflow
    
    :param series_df: pandas dataframe of timeseries
    :param basin: 2d numpy array of basin area (pseudo-boolean)
    :param twi: 2d numpy array of TWI map (positive values only)
    :param qt0: float of initial condition of baseflow in mm/d
    :param cpmax: float or 2d numpy array of canopy water stock capacity in mm
    :param sfmax: float or 2d numpy array of surface water stock capacity in mm
    :param roots: float or 2d numpy array of effective root zone depth in mm
    :param qo: float of full saturation baseflow in mm/d
    :param m: float of the scaling parameter in mm
    :param lamb: float the TWI threshold
    :param ksat: float or 2d numpy array of daily hydraulic conductivity in mm/d
    :param n: float of number of linear reservoirs (n >= 1)
    :param k: float of detention time of linear reservoirs (k >= 1)
    :param scale: int value to scale maps to integer format (recommended scale >= 1000)
    :param trace: boolean to trace back daily maps of variables
    :param tracevars: string of variables to trace back. Variables must be concatenated by `-`.
    Example: D-Cpy-VSA
    :param integrate: boolean to integrate back maps of variables
    :param integratevars: string of variables to integrate back. Variables must be concatenated by `-`.
    Example: D-Cpy-VSA
    :return: python dict containing:
    
    {'Series': simulated time series pandas dataframe,
     'Trace': dict of 3d numpy arrays of traced variables,
     'Integration': dict of 2d numpy arrays of integrated variables}
```
### the basic script
A very basic simulation script would look like this:

```python
import pandas as pd
import matplotlib.pyplot as plt
import inp
from model import simulation

# inform series dataset file
fseries = './data/series_short.txt'

# inform TWI map file
ftwi = './data/twi.asc'

# inform basin map file
fbasin = './data/basin.asc'

# load serie to dataframe
df = pd.read_csv(fseries, sep=';', parse_dates=['Date'])

# load twi map
meta, twi = inout.asc_raster(file=ftwi, dtype='float32')
# load basin map
meta, basin = inout.asc_raster(file=fbasin, dtype='float32')

# define parameter values
cpmax = 15
sfmax = 30
roots = 40
qo = 10
m = 8
lamb = 7
ksat = 3
qt0 = qo / 100  # a fraction of qo - very dry condition
k = 1.5
n = 2

# scale factor for maps
scale = 1000

# call model function
sim = simulation(series_df=df,
                 twi=twi,
                 basin=basin,
                 cpmax=cpmax,
                 sfmax=sfmax,
                 rzd=roots,
                 qo=qo,
                 m=m,
                 lamb=lamb,
                 ksat=ksat,
                 qt0=qt0,
                 k=k,
                 n=n,
                 tracevars=False,  # no map traceback
                 integrate=False,  # no map integration
                 scale=scale)

# plot some variables series:
plt.plot(sim['Series']['Date'], sim['Series']['Prec'], 'lightgrey', label='Precipitation')
plt.plot(sim['Series']['Date'], sim['Series']['Q'], 'black', label='Streamflow')
plt.plot(sim['Series']['Date'], sim['Series']['Qb'], 'navy', label='Baseflow')
plt.ylabel('mm/d')
plt.legend()
# 
# show plot
plt.show()
```

And then some output like this will show up:

![plot01](https://github.com/ipo-exe/planslab/blob/main/docs/plot_01.PNG "plot01")


### `ipo` g2g tool

A standard Input-Process-Output (`ipo`) tool is available in the `tools.py` module.
By using this function, all data must be provided by filepaths, including the 
parameters. 

_Note: the values in the parameter index maps are taken as multipliers for the `Set`
value informed in the parameter file. If a parameter index map file is passed as
`none`, the value considered is only that of the parameter file (constant value)_

```python
import tools

tools.slh_sim_g2g(fseries='./data/series_short.txt',  # series file
                  ftwi='./data/twi.asc',  # TWI map file
                  fbasin='./data/basin.asc',  # basin map file
                  fparams='./data/params.txt',  # parameter dataframe file
                  fcpmax='./data/ndvi.asc',  # index map for cpmax
                  fsfmax='./data/ndvi.asc', # index map for sfmax
                  froots='./data/ndvi.asc', # index map for roots
                  fksat='none',  # no index map provided
                  pannel=True, # export simulation pannel
                  trace=True, # do traceback
                  tracevars='VSA-D-R', # which maps to traceback
                  animate=True,  # animate maps in .gif file
                  integrate=True,  # do integrate some maps
                  integratevars='D-Cpy-R',  # which maps to integrate
                  folder='/content/output', # output folder
                  wkpl=True, # consider output folder a workplace
                  tui=True  # print progress in the screen
                  ) 
```

#### trace and animate

`trace` means that all daily maps are going to be returned by the simulation. Note 
that depending on the number of time steps and variables this may consume a large
piece of computer memory and your machine might crash.

But it is worth since the `animate` feature creates cool gifs like this, for runoff:

![anim_r](https://github.com/ipo-exe/planslab/blob/main/docs/anim_r.gif "anim_r")

#### integrate

integrate is a less memory intensive feature. It accumulates flows and take stocks
averages along the simulation run. The output images may inform you the spatial
process dominance, like where runoff occurs more or less:

![r_int](https://github.com/ipo-exe/planslab/blob/main/docs/R_integration.png "r_int")


### input data formats

#### maps
Maps are all in the `.asc` format. You may use the `gdal` `translate` tool in `QGIS` to convert `.tif` maps.
In this case, do not forget to inform the nodata parameter as `-1`. Example of an `.asc` map heading:

```markdown
ncols        95
nrows        77
xllcorner    639958.57
yllcorner    6699796.10
cellsize     30.0
NODATA_value  -1
6.7 9.0 8.1 8.2 10.9 ...
6.6 8.8 7.5 6.1 7.9 ...
         ...
6.8 8.3 7.9 6.6 7.4 ...
7.3 8.0 6.9 8.0 7.2 ...
```


**Remenber: all maps must have same dimensions**! That is, the same number of rows and columns.

#### time series
Daily time series must be in `.txt` format. Fields must be separated by `;`.

Mandatory fields:
* `Date` - daily date in format `YYYY-MM-DD`;
* `Prec` - daily precipitation in mm;
* `PET` - daily potential evapotranspiration in mm.

Optional fields:
* `Temp` - daily average temperature in Celcius degrees;
* `Qobs` - daily observed stream flow in mm;
* `ETobs` - daily observed average (basin-wide) evapotranspiration in mm;
* `IRI` - daily irrigation flow by inundation or dripping in mm;
* `IRA` - daily irrigation flow by aspersion in mm.

Example of a time series file heading:

```markdown
Date;        Prec;  Temp;  PET; Qobs
2018-05-01; 0.375;  25.0; 4.08; 2.36
2018-05-02;   0.0; 25.27; 4.10; 2.36
2018-05-03; 0.325;  25.2; 4.07; 2.35
2018-05-04;   0.0; 24.73; 3.99; 2.34
 ... 
```

#### parameter dataframe

Parameters can be provided by file. The file must be .txt and present the following dataframe 
structure:

```markdown
Parameter;   Set;  Min;  Max
        m;   5.0;  1.0;  50.0
     lamb;   7.7;  1.0; 10.0
       qo;  10.0;  1.0; 20.0
    cpmax;  20.0;  5.0; 20.0
    sfmax; 100.0;  5.0; 50.0
    roots;  50.0; 10.0; 1500
     ksat;   5.0;  1.0; 50.0
        k;   1.0;  1.0;  5.0
        n;   2.5;  1.1;  5.0
```

Where the `Set` field is taken for each parameter. `Mix` and `Max` fields are reserved for sensitivity
analysis and uncertainty estimation.
