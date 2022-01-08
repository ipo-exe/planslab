
def demo_sal_m():
    from tools import sal_d_by_m
    _ftwi = './data/twi.asc'
    sal_d_by_m(ftwi=_ftwi,
               m1=1,
               m2=5,
               dmax=100,
               size=20,
               label='lab',
               wkpl=True,
               folder='C:/bin')

demo_sal_m()