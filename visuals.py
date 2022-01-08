import matplotlib.pyplot as plt
import matplotlib as mpl
import numpy as np
import warnings

warnings.filterwarnings("ignore")


def sal_deficit_frame(dgbl, d1, vsa1, d2, vsa2, p1, p2,
                      p_lbl='m',
                      vmax=500,
                      vmin=0,
                      dgbl_max=100,
                      filename='SAL_d_frame_X',
                      folder='C:/bin', supttl='Sensitivity to the m parameter'):
    fig = plt.figure(figsize=(10, 6), )  # Width, Height
    fig.suptitle(supttl)
    gs = mpl.gridspec.GridSpec(2, 3, wspace=0.3, hspace=0.45)
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

