"""

PLANS visuals routines

Copyright (C) 2022 Iporã Brito Possantti

References:


************ GNU GENERAL PUBLIC LICENSE ************

https://www.gnu.org/licenses/gpl-3.0.en.html

Permissions:
 - Commercial use
 - Distribution
 - Modification
 - Patent use
 - Private use

Conditions:
 - Disclose source
 - License and copyright notice
 - Same license
 - State changes

Limitations:
 - Liability
 - Warranty

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.

"""
import matplotlib.pyplot as plt
import matplotlib as mpl
import numpy as np
import pandas as pd
import warnings

warnings.filterwarnings("ignore")


# silent routines
def _custom_cmaps():
    """

    get some custom cmaps

    :return:
    """
    from matplotlib import cm
    from matplotlib.colors import ListedColormap

    #
    earth_big = cm.get_cmap("gist_earth_r", 512)
    earthcm = ListedColormap(earth_big(np.linspace(0.10, 0.95, 256)))
    #
    jet_big = cm.get_cmap("jet_r", 512)
    jetcm = ListedColormap(jet_big(np.linspace(0.3, 0.75, 256)))
    #
    jet_big2 = cm.get_cmap("jet", 512)
    jetcm2 = ListedColormap(jet_big2(np.linspace(0.1, 0.9, 256)))
    #
    viridis_big = cm.get_cmap("viridis_r", 512)
    viridiscm = ListedColormap(viridis_big(np.linspace(0.05, 0.9)))
    return {
        "flow_v": jetcm,
        "D": jetcm2,
        "flow": earthcm,
        "stk": viridiscm,
        "sed": "hot_r",
    }


def _maps_dct():
    """

    get maps dict with cmaps and units

    :return: dict
    """
    cmaps = _custom_cmaps()
    dct_cmaps = {
        "dem": ["BrBG_r", "m"],
        "hand": ["BrBG_r", "m"],
        "slope": ["OrRd", "Degrees"],
        "c_usle": ["YlGn_r", "Index units"],
        "p_usle": ["YlOrBr", "Index units"],
        "k_usle": ["Oranges", "ton h MJ-1 mm-1 "],
        "s_rusle": ["OrRd", "Index units"],
        "l_rusle": ["OrRd", "Index units"],
        "a_usle_m": ["hot_r", "ton/year"],
        "n_load": ["YlOrBr", "kg-N/year"],
        "p_load": ["PuRd", "kg-P/year"],
        "twi": ["YlGnBu", "Index units"],
        "htwi": ["YlGnBu", "Index units"],
        "twito": ["YlGnBu", "Index units"],
        "fto": ["Blues", "Index units"],
        "etpat": ["Greys_r", "Index units"],
        "catcha": ["Blues", "Sq. Meters (log10)"],
        "ndvi": ["Greens", "NDVI units"],
        "basin": ["Greys", "Boolean"],
        "flow": [cmaps["flow"], "mm/d", "mm"],
        "flow_v": [cmaps["flow_v"], "mm/d", "mm"],
        "stock": [cmaps["stk"], "mm", "mm"],
        "deficit": [cmaps["D"], "mm", "mm"],
        "VSA": ["Blues", "Boolean", "%"],
        "RC": ["YlOrRd", "%", "%"],
        "anom": ["seismic_r", "Anomaly units"],
        "unc": ["inferno", "Uncertainty units", "%"],
        "lst": ["plasma", "Kelvin"],
        "else": ["Greys", "-"],
    }
    return dct_cmaps


# frames
def sal_deficit_frame(
    r_d_gbl,
    grd_d1,
    grd_vsa1,
    grd_d2,
    grd_vsa2,
    r_param1,
    r_param2,
    s_param_lbl="m",
    r_vmax=500,
    r_vmin=0,
    r_d_gbl_max=100,
    s_file_name="SAL_d_frame_X",
    s_dir_out="C:/bin",
    s_supttl="Sensitivity to the m parameter",
):
    """

    plot SAL deficit frame

    :param r_d_gbl: float global deficit
    :param grd_d1: 2d numpy array
    :param grd_vsa1: 2d numpy array
    :param grd_d2: 2d numpy array
    :param grd_vsa2: 2d numpy array
    :param r_param1: float
    :param r_param2: float
    :param s_param_lbl: string
    :param r_vmax: float
    :param r_vmin: float
    :param r_d_gbl_max: float
    :param s_file_name: string
    :param s_dir_out: string
    :param s_supttl: string
    :return:
    """
    fig = plt.figure(
        figsize=(10, 6),
    )  # Width, Height
    fig.suptitle(s_supttl)
    gs = mpl.gridspec.GridSpec(
        2, 3, wspace=0.3, hspace=0.45, left=0.05, bottom=0.05, top=0.95, right=0.95
    )
    #
    #
    ax = fig.add_subplot(gs[0, 0])
    im = plt.imshow(grd_d1, cmap="jet", vmin=r_vmin, vmax=r_vmax)
    plt.title("Local Deficit | {} = {:.1f}".format(s_param_lbl, r_param1), fontsize=10)
    plt.colorbar(im, shrink=0.4)
    plt.axis("off")
    #
    ax = fig.add_subplot(gs[1, 0])
    im = plt.imshow(grd_d2, cmap="jet", vmin=r_vmin, vmax=r_vmax)
    plt.title("Local Deficit | {} = {:.1f}".format(s_param_lbl, r_param2), fontsize=10)
    plt.colorbar(im, shrink=0.4)
    plt.axis("off")
    #
    ax = fig.add_subplot(gs[0, 1])
    im = plt.imshow(grd_vsa1, cmap="Blues", vmin=0, vmax=1)
    plt.title("Saturated Areas | {} = {:.1f}".format(s_param_lbl, r_param1), fontsize=10)
    plt.colorbar(im, shrink=0.4)
    plt.axis("off")
    #
    ax = fig.add_subplot(gs[1, 1])
    im = plt.imshow(grd_vsa2, cmap="Blues", vmin=0, vmax=1)
    plt.title("Saturated Areas | {} = {:.1f}".format(s_param_lbl, r_param2), fontsize=10)
    plt.colorbar(im, shrink=0.4)
    plt.axis("off")
    #
    ax = fig.add_subplot(gs[0, 2])
    plt.plot(0, r_d_gbl, "bo", markersize=10)
    plt.vlines(x=0, ymin=0, ymax=r_d_gbl_max, colors="k")
    plt.title("Global Deficit = {:.1f} mm".format(r_d_gbl), fontsize=10)
    plt.axis("off")
    #
    # plt.show()
    expfile = s_dir_out + "/" + s_file_name + ".png"
    plt.savefig(expfile)
    plt.close(fig)


def plot_map_view(
    grd_map2d,
    dct_meta,
    tpl_ranges,
    s_mapid="dem",
    s_mapttl="",
    s_file_name="view",
    s_dir_out="C:/bin",
    b_metadata=True,
    b_show=False,
    b_integration=False,
    b_png=True,
    n_nodata=-1,
):
    """

    Plot a generic map view

    :param grd_map2d: 2d numpy array of map
    :param dct_meta: dictionary of map metadata
    :param tpl_ranges: tuple of ranges
    :param s_mapid: string of map id
    :param s_mapttl: string of map title
    :param s_file_name: string filename
    :param s_dir_out: string folder path
    :param b_metadata: boolean to print metadata on figure
    :param b_show: boolean to show instead of saving
    :param b_integration: boolean to show integration units instead of instant units
    :param b_png: boolean to export as PNG
    :return: string file path
    """
    # get cmaps
    map_dct = _maps_dct()
    try:
        map_spec = map_dct[s_mapid]
    except KeyError:
        s_mapid = "else"
    #
    fig = plt.figure(figsize=(6, 4.5))  # Width, Height
    gs = mpl.gridspec.GridSpec(
        3, 4, wspace=0.0, hspace=0.0, left=0.05, bottom=0.05, top=0.95, right=0.95
    )
    #
    ax = fig.add_subplot(gs[:, :3])
    if s_mapid == "catcha":
        grd_map2d = np.log10(grd_map2d)
        tpl_ranges = np.log10(tpl_ranges)
    grd_map2d[grd_map2d == n_nodata] = np.nan
    im = plt.imshow(grd_map2d, cmap=map_dct[s_mapid][0], vmin=tpl_ranges[0], vmax=tpl_ranges[1])
    plt.title(s_mapttl)
    plt.axis("off")
    plt.colorbar(im, shrink=0.4)
    #
    #
    ax = fig.add_subplot(gs[:, 3:])
    if b_integration:
        plt.text(x=-0.45, y=0.75, s=map_dct[s_mapid][2])
    else:
        plt.text(x=-0.45, y=0.75, s=map_dct[s_mapid][1])
    if b_metadata:
        n_fsize = 9
        n_x = 0.1
        plt.text(x=n_x, y=0.3, s="Metadata:", fontsize=n_fsize)
        plt.text(x=n_x, y=0.25, s="Rows: {}".format(dct_meta["nrows"]), fontsize=n_fsize)
        plt.text(x=n_x, y=0.2, s="Columns: {}".format(dct_meta["ncols"]), fontsize=n_fsize)
        plt.text(
            x=n_x,
            y=0.15,
            s="Cell size: {:.1f} m".format(dct_meta["cellsize"]),
            fontsize=n_fsize,
        )
        plt.text(
            x=n_x, y=0.1, s="xll: {:.2f} m".format(dct_meta["xllcorner"]), fontsize=n_fsize
        )
        plt.text(
            x=n_x, y=0.05, s="yll: {:.2f} m".format(dct_meta["yllcorner"]), fontsize=n_fsize
        )
    plt.axis("off")
    #
    if b_show:
        plt.show()
        plt.close(fig)
    else:
        filepath = s_dir_out + "/" + s_file_name
        if b_png:
            filepath = filepath + ".png"
        else:
            filepath = filepath + ".jpg"
        plt.savefig(filepath)
        plt.close(fig)
        return filepath


def export_map_views(
    grd3_map3d,
    df_series,
    dct_meta,
    tpl_ranges,
    s_mapid="dem",
    s_mapttl="",
    s_file_name="mapview",
    s_dir_out="C:/bin",
    b_metadata=True,
    b_integration=False,
    b_png=True,
    n_nodata=-1,
    n_scale=1,
    b_tui=False,
):
    """

    export map views from time series of maps

    :param grd3_map3d: 3d numpy array of maps (time series of maps)
    :param df_series: pandas dataframe of time series
    :param dct_meta: dict of metadata
    :param tpl_ranges: tuple of ranges
    :param s_mapid: string map code
    :param s_mapttl: string map title
    :param s_file_name: string file name
    :param s_dir_out: string output dir
    :param b_metadata: boolean for metadata plot
    :param b_integration: boolean to consider integration map
    :param b_png: boolean to plot png
    :param n_nodata: float of no data value
    :param n_scale: float of scaling factor
    :param b_tui: boolean for TUI display
    :return: none
    """
    from backend import status

    dates_labels = pd.to_datetime(df_series["Date"], format="%Y%m%d")
    dates_labels = dates_labels.astype("str")
    for t in range(len(grd3_map3d)):
        if b_tui:
            status("exporting {} frame {} of {}".format(s_mapttl, t + 1, len(grd3_map3d)))
        lcl_filename = "{}_{}".format(s_file_name, str(t).zfill(5))
        lcl_map = grd3_map3d[t] / n_scale
        plot_map_view(
            grd_map2d=lcl_map,
            dct_meta=dct_meta,
            tpl_ranges=tpl_ranges,
            s_mapid=s_mapid,
            s_mapttl="{} | {}".format(s_mapttl, dates_labels.values[t]),
            s_file_name=lcl_filename,
            b_metadata=b_metadata,
            b_integration=b_integration,
            b_png=b_png,
            n_nodata=n_nodata,
            b_show=False,
            s_dir_out=s_dir_out,
        )


def pannel_global(
    df_series,
    b_obs=False,
    b_grid=True,
    b_show=False,
    s_dir_out="C:/bin",
    s_file_name="pannel",
    suff="",
):
    """
    visualize the model global variables in a single pannel
    :param df_series: pandas dataframe from hydrology.topmodel_sim()
    :param qobs: boolean for Qobs
    :param etobs: boolean for ETobs
    :param b_grid: boolean for grid
    :param s_dir_out: string to destination directory
    :param s_file_name: string file name
    :param suff: string suffix in file name
    :param b_show: boolean control to show figure instead of saving it
    :return: string file path
    """
    #
    fig = plt.figure(figsize=(20, 12))  # Width, Height
    fig.suptitle("Pannel of simulated hydrological processes")
    gs = mpl.gridspec.GridSpec(
        5, 18, wspace=0.0, hspace=0.2, left=0.05, bottom=0.05, top=0.95, right=0.95
    )  # nrows, ncols
    col1 = 8
    col2 = 10
    max_prec = 1.2 * np.max(df_series["Prec"].values)
    max_et = 1.5 * np.max(df_series["PET"].values)
    max_stocks = 1.2 * np.max(
        (df_series["Unz"].values, df_series["Sfs"].values, df_series["Cpy"].values)
    )
    max_int_flow = 1.2 * np.max((df_series["Inf"].values, df_series["Qv"].values))
    if "Qobs" in df_series.columns and b_obs:
        qobs = True
    else:
        qobs = False
    if "Etobs" in df_series.columns and b_obs:
        etobs = True
    else:
        etobs = False

    if qobs:
        qmin = 0.8 * np.min((df_series["Q"].values, df_series["Qobs"].values))
        qmax = 1.5 * np.max((df_series["Q"].values, df_series["Qobs"].values))
    else:
        qmin = 0.8 * np.min(df_series["Q"].values)
        qmax = 1.5 * np.max(df_series["Q"].values)

    #
    # Prec
    ax = fig.add_subplot(gs[0, 0:col1])
    plt.grid(b_grid)
    plt.plot(df_series["Date"], df_series["Prec"], label="Precipitation")
    plt.ylabel("mm/d (Prec)")
    plt.ylim(0, max_prec)
    plt.legend(loc="upper left", ncol=1, framealpha=1, fancybox=False)
    if "IRA" in df_series.columns and "IRI" in df_series.columns:
        max_irr = np.max((df_series["IRA"].values, df_series["IRI"].values))
        if max_irr == 0:
            pass
        else:
            ax2 = ax.twinx()
            plt.plot(
                df_series["Date"],
                df_series["IRA"],
                "orange",
                label="Irrigation by aspersion",
            )
            plt.plot(
                df_series["Date"],
                df_series["IRI"],
                "green",
                label="Irrigation by inundation",
            )
            plt.ylabel("mm/d (IRA, IRI)")
            plt.ylim(0, max_irr)
            plt.legend(loc="upper right", ncol=2, framealpha=1, fancybox=False)
    ax.tick_params(axis="x", which="major", labelsize=8)
    #
    # PET
    ax = fig.add_subplot(gs[0, col2:])
    plt.grid(b_grid)
    plt.plot(df_series["Date"], df_series["PET"], "tab:grey", label="Pot. ET")
    ncols = 2
    if etobs:
        ncols = ncols + 1
        plt.plot(df_series["Date"], df_series["ETobs"], "k.", label="Observed ET")
    plt.ylim(0, max_et)
    plt.ylabel("mm/d")
    plt.legend(loc="upper left", ncol=ncols, framealpha=1, fancybox=False)
    ax.tick_params(axis="x", which="major", labelsize=8)
    if "Temp" in df_series.columns:
        ax2 = ax.twinx()
        plt.plot(
            df_series["Date"], df_series["Temp"], "tab:orange", label="Temperature"
        )
        plt.ylabel("°C")
        plt.ylim(0, 1.3 * df_series["Temp"].max())
        plt.legend(loc="upper right", ncol=1, framealpha=1, fancybox=False)
    #
    # Runoff
    ax = fig.add_subplot(gs[1, 0:col1])
    plt.grid(b_grid)
    plt.plot(df_series["Date"], df_series["TF"], "skyblue", label="Troughfall")
    plt.plot(df_series["Date"], df_series["R"], "dodgerblue", label="Runoff")
    plt.plot(df_series["Date"], df_series["RIE"], "blue", label="Hortonian R.")
    plt.plot(df_series["Date"], df_series["RSE"], "navy", label="Dunnean R.")
    plt.ylabel("mm/d")
    plt.ylim(0, max_prec)
    plt.legend(loc="upper left", ncol=4, framealpha=1, fancybox=False)
    ax.tick_params(axis="x", which="major", labelsize=8)
    #
    # ET
    ax = fig.add_subplot(gs[1, col2:])
    plt.grid(b_grid)
    plt.plot(df_series["Date"], df_series["PET"], "tab:grey", label="PET")
    plt.plot(df_series["Date"], df_series["ET"], "tab:red", label="Actual ET")
    ncols = 2
    if etobs:
        ncols = ncols + 1
        plt.plot(df_series["Date"], df_series["ETobs"], "k.", label="Obs. ET")
    plt.ylim(0, max_et)
    plt.ylabel("mm/d")
    plt.legend(loc="upper right", ncol=ncols, framealpha=1, fancybox=False)
    ax.tick_params(axis="x", which="major", labelsize=8)
    #
    # Flow
    ax = fig.add_subplot(gs[2, 0:col1])
    plt.grid(b_grid)
    if qobs:
        plt.plot(
            df_series["Date"],
            df_series["Qobs"],
            "tab:grey",
            label="Observed Streamflow",
        )
    plt.plot(df_series["Date"], df_series["Q"], "tab:blue", label="Streamflow")
    plt.plot(df_series["Date"], df_series["Qb"], "navy", label="Baseflow")
    if qmax / qmin >= 100:
        plt.yscale("log")
        qmax = 10 * qmax
    plt.ylim(qmin, qmax)
    plt.ylabel("mm/d")
    plt.legend(loc="upper right", ncol=3, framealpha=1, fancybox=False)
    ax.tick_params(axis="x", which="major", labelsize=8)

    #
    # Ev
    ax = fig.add_subplot(gs[2, col2:])
    plt.grid(b_grid)
    plt.plot(df_series["Date"], df_series["PET"], "tab:grey", label="PET")
    plt.plot(df_series["Date"], df_series["Evc"], "tan", label="Evap. canopy")
    plt.plot(df_series["Date"], df_series["Evs"], "maroon", label="Evap. surface")
    ncols = 3
    if etobs:
        ncols = ncols + 1
        plt.plot(df_series["Date"], df_series["ETobs"], "k.", label="Obs. ET")
    plt.ylim(0, max_et)
    plt.ylabel("mm/d")
    plt.legend(loc="upper right", ncol=ncols, framealpha=1, fancybox=False)
    ax.tick_params(axis="x", which="major", labelsize=8)
    #
    # Inf
    ax = fig.add_subplot(gs[3, 0:col1])
    plt.grid(b_grid)
    plt.plot(df_series["Date"], df_series["Inf"], "tab:blue", label="Infiltration")
    plt.plot(df_series["Date"], df_series["Qv"], "navy", label="Groundwater recharge")
    plt.ylim(0, max_int_flow)
    plt.ylabel("mm/d")
    plt.legend(loc="upper left", ncol=2, framealpha=1, fancybox=False)
    #
    # Tp
    ax = fig.add_subplot(gs[3, col2:])
    plt.grid(b_grid)
    plt.plot(df_series["Date"], df_series["PET"], "tab:grey", label="PET")
    plt.plot(df_series["Date"], df_series["Tpu"], "yellowgreen", label="Transp. vadose")
    plt.plot(
        df_series["Date"], df_series["Tps"], "darkgreen", label="Transp. groundwater"
    )
    ncols = 3
    if etobs:
        ncols = ncols + 1
        plt.plot(df_series["Date"], df_series["ETobs"], "k.", label="Obs. ET")
    plt.ylim(0, max_et)
    plt.ylabel("mm/d")
    plt.legend(loc="upper right", ncol=ncols, framealpha=1, fancybox=False)
    ax.tick_params(axis="x", which="major", labelsize=8)
    #
    # D
    ax = fig.add_subplot(gs[4, 0:col1])
    plt.grid(b_grid)
    plt.plot(df_series["Date"], df_series["D"], "k", label="Groundwater stock deficit")
    plt.ylim(0, 1.5 * np.max(df_series["D"].values))
    plt.ylabel("mm")
    plt.legend(loc="upper left", ncol=2, framealpha=1, fancybox=False)
    ax2 = ax.twinx()
    plt.plot(df_series["Date"], df_series["Unz"], "teal", label="Vadose water stock")
    plt.ylim(0, max_stocks)
    plt.ylabel("mm")
    plt.legend(loc="upper right", ncol=1, framealpha=1, fancybox=False)
    ax.tick_params(axis="x", which="major", labelsize=8)
    #
    # Sfs
    ax = fig.add_subplot(gs[4, col2:])
    plt.grid(b_grid)
    plt.plot(
        df_series["Date"], df_series["Cpy"], "limegreen", label="Canopy water stock"
    )
    plt.plot(
        df_series["Date"], df_series["Sfs"], "tab:blue", label="Surface water stock"
    )
    plt.ylim(0, max_stocks)
    plt.ylabel("mm")
    plt.legend(loc="upper right", ncol=2, framealpha=1, fancybox=False)
    ax.tick_params(axis="x", which="major", labelsize=8)
    #
    #
    if b_show:
        plt.show()
        plt.close(fig)
    else:
        # export file
        if suff != "":
            filepath = s_dir_out + "/" + s_file_name + "_" + suff + ".png"
        else:
            filepath = s_dir_out + "/" + s_file_name + ".png"
        plt.savefig(filepath, dpi=600)
        plt.close(fig)
        plt.clf()
        return filepath
