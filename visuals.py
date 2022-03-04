import matplotlib.pyplot as plt
import matplotlib as mpl
import numpy as np
import pandas as pd
import warnings

warnings.filterwarnings("ignore")


def _custom_cmaps():
    from matplotlib import cm
    from matplotlib.colors import ListedColormap
    #
    earth_big = cm.get_cmap('gist_earth_r', 512)
    earthcm = ListedColormap(earth_big(np.linspace(0.10, 0.95, 256)))
    #
    jet_big = cm.get_cmap('jet_r', 512)
    jetcm = ListedColormap(jet_big(np.linspace(0.3, 0.75, 256)))
    #
    jet_big2 = cm.get_cmap('jet', 512)
    jetcm2 = ListedColormap(jet_big2(np.linspace(0.1, 0.9, 256)))
    #
    viridis_big = cm.get_cmap('viridis_r', 512)
    viridiscm = ListedColormap(viridis_big(np.linspace(0.05, 0.9)))
    return {'flow_v':jetcm, 'D':jetcm2, 'flow':earthcm, 'stk':viridiscm, 'sed':'hot_r'}


def sal_deficit_frame(dgbl, d1, vsa1, d2, vsa2, p1, p2,
                      p_lbl='m',
                      vmax=500,
                      vmin=0,
                      dgbl_max=100,
                      filename='SAL_d_frame_X',
                      folder='C:/bin',
                      supttl='Sensitivity to the m parameter'):
    fig = plt.figure(figsize=(10, 6), )  # Width, Height
    fig.suptitle(supttl)
    gs = mpl.gridspec.GridSpec(2, 3, wspace=0.3, hspace=0.45, left=0.05, bottom=0.05, top=0.95, right=0.95)
    #
    #
    ax = fig.add_subplot(gs[0, 0])
    im = plt.imshow(d1, cmap='jet', vmin=vmin, vmax=vmax)
    plt.title('Local Deficit | {} = {:.1f}'.format(p_lbl, p1), fontsize=10)
    plt.colorbar(im, shrink=0.4)
    plt.axis('off')
    #
    ax = fig.add_subplot(gs[1, 0])
    im = plt.imshow(d2, cmap='jet', vmin=vmin, vmax=vmax)
    plt.title('Local Deficit | {} = {:.1f}'.format(p_lbl, p2), fontsize=10)
    plt.colorbar(im, shrink=0.4)
    plt.axis('off')
    #
    ax = fig.add_subplot(gs[0, 1])
    im = plt.imshow(vsa1, cmap='Blues', vmin=0, vmax=1)
    plt.title('Saturated Areas | {} = {:.1f}'.format(p_lbl, p1), fontsize=10)
    plt.colorbar(im, shrink=0.4)
    plt.axis('off')
    #
    ax = fig.add_subplot(gs[1, 1])
    im = plt.imshow(vsa2, cmap='Blues', vmin=0, vmax=1)
    plt.title('Saturated Areas | {} = {:.1f}'.format(p_lbl, p2), fontsize=10)
    plt.colorbar(im, shrink=0.4)
    plt.axis('off')
    #
    ax = fig.add_subplot(gs[0, 2])
    plt.plot(0, dgbl, 'bo', markersize=10)
    plt.vlines(x=0, ymin=0, ymax=dgbl_max, colors='k')
    plt.title('Global Deficit = {:.1f} mm'.format(dgbl), fontsize=10)
    plt.axis('off')
    #
    # plt.show()
    expfile = folder + '/' + filename + '.png'
    plt.savefig(expfile)
    plt.close(fig)


def plot_map_view(map2d, meta, ranges,
                  mapid='dem',
                  mapttl='',
                  filename='mapview',
                  folder='C:/bin',
                  metadata=True,
                  show=False,
                  integration=False,
                  png=True,
                  nodata=-1):
    """

    Plot a generic map view

    :param map2d: 2d numpy array of map
    :param meta: dictionary of map metadata
    :param ranges: tuple of ranges
    :param mapid: string of map id
    :param mapttl: string of map title
    :param filename: string filename
    :param folder: string folder path
    :param metadata: boolean to print metadata on figure
    :param show: boolean to show instead of saving
    :param integration: boolean to show integration units instead of instant units
    :param png: boolean to export as PNG
    :return: string filepath
    """
    cmaps = _custom_cmaps()
    map_dct = {'dem': ['BrBG_r', 'Elevation'],
               'slope': ['OrRd', 'Degrees'],
               'c_usle':['YlGn_r', 'Index units'],
               'p_usle': ['YlOrBr', 'Index units'],
               'k_usle': ['Oranges', 'ton h MJ-1 mm-1 '],
               's_rusle': ['OrRd', 'Index units'],
               'l_rusle': ['OrRd', 'Index units'],
               'a_usle_m': ['hot_r', 'ton/year'],
               'n_load': ['YlOrBr', 'kg-N/year'],
               'p_load': ['PuRd', 'kg-P/year'],
               'twi': ['YlGnBu', 'Index units'],
               'twito': ['YlGnBu', 'Index units'],
               'fto': ['Blues', 'Index units'],
               'etpat': ['Greys_r', 'Index units'],
               'catcha': ['Blues', 'Sq. Meters (log10)'],
               'ndvi':['Spectral', 'NDVI units'],
               'basin': ['Greys', 'Boolean'],
               'flow':[cmaps['flow'], 'mm/d', 'mm'],
               'flow_v':[cmaps['flow_v'], 'mm/d', 'mm'],
               'stock':[cmaps['stk'], 'mm', 'mm'],
               'deficit':[cmaps['D'], 'mm', 'mm'],
               'VSA':['Blues', 'Boolean', '%'],
               'RC':['YlOrRd', '%', '%'],
               'anom': ['seismic_r', 'Anomaly units'],
               'unc':['inferno', 'Uncertainty units', '%']}
    #
    fig = plt.figure(figsize=(6, 4.5))  # Width, Height
    gs = mpl.gridspec.GridSpec(3, 4, wspace=0.0, hspace=0.0, left=0.05, bottom=0.05, top=0.95, right=0.95)
    #
    ax = fig.add_subplot(gs[:, :3])
    if mapid == 'catcha':
        map2d = np.log10(map2d)
        ranges = np.log10(ranges)
    map2d[map2d == nodata] = np.nan
    im = plt.imshow(map2d, cmap=map_dct[mapid][0], vmin=ranges[0], vmax=ranges[1])
    plt.title(mapttl)
    plt.axis('off')
    plt.colorbar(im, shrink=0.4)
    #
    #
    ax = fig.add_subplot(gs[:, 3:])
    if integration:
        plt.text(x=-0.45, y=0.75, s=map_dct[mapid][2])
    else:
        plt.text(x=-0.45, y=0.75, s=map_dct[mapid][1])
    if metadata:
        plt.text(x=0.0, y=0.3, s='Metadata:')
        plt.text(x=0.0, y=0.25, s='Rows: {}'.format(meta['nrows']))
        plt.text(x=0.0, y=0.2, s='Columns: {}'.format(meta['ncols']))
        plt.text(x=0.0, y=0.15, s='Cell size: {:.1f} m'.format(meta['cellsize']))
        plt.text(x=0.0, y=0.1, s='xll: {:.2f} m'.format(meta['xllcorner']))
        plt.text(x=0.0, y=0.05, s='yll: {:.2f} m'.format(meta['yllcorner']))
    plt.axis('off')
    #
    if show:
        plt.show()
        plt.close(fig)
    else:
        filepath = folder + '/' + filename
        if png:
            filepath = filepath + '.png'
        else:
            filepath = filepath + '.jpg'
        plt.savefig(filepath)
        plt.close(fig)
        return filepath


def export_map_views(map3d, series, meta, ranges,
                     mapid='dem',
                     mapttl='',
                     filename='mapview',
                     folder='C:/bin',
                     metadata=True,
                     integration=False,
                     png=True,
                     nodata=-1,
                     scale=1,
                     tui=False):
    from backend import status

    def id_label(id):
        if id < 10:
            return '000' + str(id)
        elif id >= 10 and id < 100:
            return '00' + str(id)
        elif id >= 100 and id < 1000:
            return '0' + str(id)
        elif id >= 1000 and id < 10000:
            return  str(id)

    dates_labels = pd.to_datetime(series['Date'], format='%Y%m%d')
    dates_labels = dates_labels.astype('str')
    for t in range(len(map3d)):
        if tui:
            status('exporting {} frame {} of {}'.format(mapttl, t + 1, len(map3d)))
        lcl_filename = '{}_{}'.format(filename, id_label(id=t))
        lcl_map = map3d[t] / scale
        plot_map_view(map2d=lcl_map,
                      meta=meta,
                      ranges=ranges,
                      mapid=mapid,
                      mapttl='{} | {}'.format(mapttl, dates_labels.values[t]),
                      filename=lcl_filename,
                      metadata=metadata,
                      integration=integration,
                      png=png,
                      nodata=nodata,
                      show=False,
                      folder=folder)


def pannel_global(series_df,
                  obs=False,
                  grid=True,
                  show=False,
                  folder='C:/bin',
                  filename='pannel',
                  suff=''):
    """
    visualize the model global variables in a single pannel
    :param series_df: pandas dataframe from hydrology.topmodel_sim()
    :param qobs: boolean for Qobs
    :param etobs: boolean for ETobs
    :param grid: boolean for grid
    :param folder: string to destination directory
    :param filename: string file name
    :param suff: string suffix in file name
    :param show: boolean control to show figure instead of saving it
    :return: string file path
    """
    #
    fig = plt.figure(figsize=(20, 12))  # Width, Height
    fig.suptitle('Pannel of simulated hydrological processes')
    gs = mpl.gridspec.GridSpec(5, 18, wspace=0.0, hspace=0.2, left=0.05, bottom=0.05, top=0.95, right=0.95)  # nrows, ncols
    col1 = 8
    col2 = 10
    max_prec = 1.2 * np.max(series_df['Prec'].values)
    max_et = 1.5 * np.max(series_df['PET'].values)
    max_stocks = 1.2 * np.max((series_df['Unz'].values, series_df['Sfs'].values, series_df['Cpy'].values))
    max_int_flow = 1.2 * np.max((series_df['Inf'].values, series_df['Qv'].values))
    if 'Qobs' in series_df.columns and obs:
        qobs = True
    else:
        qobs = False
    if 'Etobs' in series_df.columns and obs:
        etobs = True
    else:
        etobs = False

    if qobs:
        qmin = 0.8 * np.min((series_df['Q'].values, series_df['Qobs'].values))
        qmax = 1.5 * np.max((series_df['Q'].values, series_df['Qobs'].values))
    else:
        qmin = 0.8 * np.min(series_df['Q'].values)
        qmax = 1.5 * np.max(series_df['Q'].values)

    #
    # Prec
    ax = fig.add_subplot(gs[0, 0:col1])
    plt.grid(grid)
    plt.plot(series_df['Date'], series_df['Prec'], label='Precipitation')
    plt.ylabel('mm/d (Prec)')
    plt.ylim(0, max_prec)
    plt.legend(loc='upper left', ncol=1, framealpha=1, fancybox=False)
    if 'IRA' in series_df.columns and 'IRI' in series_df.columns:
        max_irr = np.max((series_df['IRA'].values, series_df['IRI'].values))
        if max_irr == 0:
            pass
        else:
            ax2 = ax.twinx()
            plt.plot(series_df['Date'], series_df['IRA'], 'orange', label='Irrigation by aspersion')
            plt.plot(series_df['Date'], series_df['IRI'], 'green', label='Irrigation by inundation')
            plt.ylabel('mm/d (IRA, IRI)')
            plt.ylim(0, max_irr)
            plt.legend(loc='upper right', ncol=2, framealpha=1, fancybox=False)
    ax.tick_params(axis='x', which='major', labelsize=8)
    #
    # PET
    ax = fig.add_subplot(gs[0, col2:])
    plt.grid(grid)
    plt.plot(series_df['Date'], series_df['PET'], 'tab:grey', label='Pot. ET')
    ncols = 2
    if etobs:
        ncols = ncols + 1
        plt.plot(series_df['Date'], series_df['ETobs'], 'k.', label='Observed ET')
    plt.ylim(0, max_et)
    plt.ylabel('mm/d')
    plt.legend(loc='upper left', ncol=ncols, framealpha=1, fancybox=False)
    ax.tick_params(axis='x', which='major', labelsize=8)
    if 'Temp' in series_df.columns:
        ax2 = ax.twinx()
        plt.plot(series_df['Date'], series_df['Temp'], 'tab:orange', label='Temperature')
        plt.ylabel('°C')
        plt.ylim(0, 1.3 * series_df['Temp'].max())
        plt.legend(loc='upper right', ncol=1, framealpha=1, fancybox=False)
    #
    # Runoff
    ax = fig.add_subplot(gs[1, 0:col1])
    plt.grid(grid)
    plt.plot(series_df['Date'], series_df['TF'], 'skyblue', label='Troughfall')
    plt.plot(series_df['Date'], series_df['R'], 'dodgerblue', label='Runoff')
    plt.plot(series_df['Date'], series_df['RIE'], 'blue', label='Hortonian R.')
    plt.plot(series_df['Date'], series_df['RSE'], 'navy', label='Dunnean R.')
    plt.ylabel('mm/d')
    plt.ylim(0, max_prec)
    plt.legend(loc='upper left', ncol=4, framealpha=1, fancybox=False)
    ax.tick_params(axis='x', which='major', labelsize=8)
    #
    # ET
    ax = fig.add_subplot(gs[1, col2:])
    plt.grid(grid)
    plt.plot(series_df['Date'], series_df['PET'], 'tab:grey', label='PET')
    plt.plot(series_df['Date'], series_df['ET'], 'tab:red', label='Actual ET')
    ncols = 2
    if etobs:
        ncols = ncols + 1
        plt.plot(series_df['Date'], series_df['ETobs'], 'k.', label='Obs. ET')
    plt.ylim(0, max_et)
    plt.ylabel('mm/d')
    plt.legend(loc='upper right', ncol=ncols, framealpha=1, fancybox=False)
    ax.tick_params(axis='x', which='major', labelsize=8)
    #
    # Flow
    ax = fig.add_subplot(gs[2, 0:col1])
    plt.grid(grid)
    if qobs:
        plt.plot(series_df['Date'], series_df['Qobs'], 'tab:grey', label='Observed Streamflow')
    plt.plot(series_df['Date'], series_df['Q'], 'tab:blue', label='Streamflow')
    plt.plot(series_df['Date'], series_df['Qb'], 'navy', label='Baseflow')
    if qmax / qmin >= 100:
        plt.yscale('log')
        qmax = 10 * qmax
    plt.ylim(qmin, qmax)
    plt.ylabel('mm/d')
    plt.legend(loc='upper right', ncol=3, framealpha=1, fancybox=False)
    ax.tick_params(axis='x', which='major', labelsize=8)

    #
    # Ev
    ax = fig.add_subplot(gs[2, col2:])
    plt.grid(grid)
    plt.plot(series_df['Date'], series_df['PET'], 'tab:grey', label='PET')
    plt.plot(series_df['Date'], series_df['Evc'], 'tan', label='Evap. canopy')
    plt.plot(series_df['Date'], series_df['Evs'], 'maroon', label='Evap. surface')
    ncols = 3
    if etobs:
        ncols = ncols + 1
        plt.plot(series_df['Date'], series_df['ETobs'], 'k.', label='Obs. ET')
    plt.ylim(0, max_et)
    plt.ylabel('mm/d')
    plt.legend(loc='upper right', ncol=ncols, framealpha=1, fancybox=False)
    ax.tick_params(axis='x', which='major', labelsize=8)
    #
    # Inf
    ax = fig.add_subplot(gs[3, 0:col1])
    plt.grid(grid)
    plt.plot(series_df['Date'], series_df['Inf'], 'tab:blue', label='Infiltration')
    plt.plot(series_df['Date'], series_df['Qv'], 'navy', label='Groundwater recharge')
    plt.ylim(0, max_int_flow)
    plt.ylabel('mm/d')
    plt.legend(loc='upper left', ncol=2, framealpha=1, fancybox=False)
    #
    # Tp
    ax = fig.add_subplot(gs[3, col2:])
    plt.grid(grid)
    plt.plot(series_df['Date'], series_df['PET'], 'tab:grey', label='PET')
    plt.plot(series_df['Date'], series_df['Tpu'], 'yellowgreen', label='Transp. vadose')
    plt.plot(series_df['Date'], series_df['Tps'], 'darkgreen', label='Transp. groundwater')
    ncols = 3
    if etobs:
        ncols = ncols + 1
        plt.plot(series_df['Date'], series_df['ETobs'], 'k.', label='Obs. ET')
    plt.ylim(0, max_et)
    plt.ylabel('mm/d')
    plt.legend(loc='upper right', ncol=ncols, framealpha=1, fancybox=False)
    ax.tick_params(axis='x', which='major', labelsize=8)
    #
    # D
    ax = fig.add_subplot(gs[4, 0:col1])
    plt.grid(grid)
    plt.plot(series_df['Date'], series_df['D'], 'k', label='Groundwater stock deficit')
    plt.ylim(0, 1.5 * np.max(series_df['D'].values))
    plt.ylabel('mm')
    plt.legend(loc='upper left', ncol=2, framealpha=1, fancybox=False)
    ax2 = ax.twinx()
    plt.plot(series_df['Date'], series_df['Unz'], 'teal', label='Vadose water stock')
    plt.ylim(0, max_stocks)
    plt.ylabel('mm')
    plt.legend(loc='upper right', ncol=1, framealpha=1, fancybox=False)
    ax.tick_params(axis='x', which='major', labelsize=8)
    #
    # Sfs
    ax = fig.add_subplot(gs[4, col2:])
    plt.grid(grid)
    plt.plot(series_df['Date'], series_df['Cpy'], 'limegreen', label='Canopy water stock')
    plt.plot(series_df['Date'], series_df['Sfs'], 'tab:blue', label='Surface water stock')
    plt.ylim(0, max_stocks)
    plt.ylabel('mm')
    plt.legend(loc='upper right', ncol=2, framealpha=1, fancybox=False)
    ax.tick_params(axis='x', which='major', labelsize=8)
    #
    #
    if show:
        plt.show()
        plt.close(fig)
    else:
        # export file
        if suff != '':
            filepath = folder + '/' + filename + '_' + suff + '.png'
        else:
            filepath = folder + '/' + filename + '.png'
        plt.savefig(filepath, dpi=600)
        plt.close(fig)
        plt.clf()
        return filepath



