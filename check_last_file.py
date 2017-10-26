#!python
import os
from glob import glob
from lofasm import parse_data as pdat
from lofasm.parse_data_H import Baselines
import numpy as np
import matplotlib
matplotlib.use('agg')
import matplotlib.pyplot as plt

def get_freqs():
    return np.arange(1024)*100.0/1024

def get_latest_file_in_directory(dirPath):
    '''
    return the path to the latest (finished) data file in dirPath.
    '''

    flist = glob(os.path.join(dirPath, '*.lofasm*'))
    flist.sort()
    return flist[-2]

def get_latest_data_file():
    LofasmConfig = os.path.join(os.environ['HOME'], '.lofasm/lofasm.cfg')
    #LofasmConfig = "testlofasmconfig"

    LofasmConfigContents = {}

    with open(LofasmConfig, 'r') as f:
        # read config file and ignore #comments
        lines = [tuple(x.strip('\n').split()) for x in f.readlines() if not x.startswith('#')]
        LofasmConfigContents = dict(tuple([l for l in lines if l])) # remove empty elements on the fly
    
    DataRoot = LofasmConfigContents['dataroot']

    return get_latest_file_in_directory(DataRoot)

def generate_first_spectral_sample_plot(fpath, pol):
    c = pdat.LoFASMFileCrawler(fpath)
    c.open()
    data = np.array(c.autos[pol][:1024])
    
    # create figure
    plt.plot(10*np.log10(data))
    figname = os.path.join("/home/controller/var/run/lofasm-slack-alerts/",
                           os.path.basename(fpath) + '_' + pol + '.png')
    plt.savefig(figname)
    plt.clf()
    return figname

def generate_plot_all_channels(fpath):
    '''
    create a single plot showing all channels
    '''

    auto_baselines = [b for b in Baselines if b[0]==b[1]]
    cross_baselines = [b for b in Baselines if b not in auto_baselines]
    freqs = get_freqs()

    # open lofasm file
    c = pdat.LoFASMFileCrawler(fpath)
    c.open()
    fig = plt.figure(figsize=(10,10))
    plt.suptitle(fpath)

    # setup plot handles and locations
    auto_subplots = [plt.subplot2grid((4,4), (i,i)) for i in range(4)]
    cross_subplots = [plt.subplot2grid((4,4),(0,1)),
                      plt.subplot2grid((4,4),(0,2)),
                      plt.subplot2grid((4,4),(0,3)),
                      plt.subplot2grid((4,4),(1,2)),
                      plt.subplot2grid((4,4),(1,3)),
                      plt.subplot2grid((4,4),(2,3))]
    overlay_plot = plt.subplot2grid((4,4),(2,0), colspan=2, rowspan=2)

    auto_lines = []
    cross_lines = []
    overlay_lines = []

    fig.subplots_adjust(hspace=0.5)
    xmin = 0.0
    xmax = 100.0
    ymin = 0.0
    ymax = 100.0
    # set titles & plot
    for i in range(len(cross_baselines)):

        if i < 4:
            #autos
            auto_title = auto_baselines[i]
            auto_subplots[i].set_title(auto_title)
            auto_subplots[i].set_xlim(xmin, xmax)
            auto_subplots[i].set_ylim(ymin, ymax)
            auto_subplots[i].grid()
            auto_lines.append(auto_subplots[i].plot(freqs,10*np.log10(c.autos[auto_baselines[i]][:1024]))[0])

            #overlays
            overlay_title = 'All Channels'
            if i == 0:
                overlay_plot.set_title(overlay_title)
                overlay_plot.set_xlim(xmin, xmax)
                overlay_plot.set_ylim(ymin, ymax)
                overlay_plot.grid()
            overlay_lines.append(overlay_plot.plot(freqs,10*np.log10(c.autos[auto_baselines[i]][:1024]))[0])

        cross_title = cross_baselines[i]
        cross_subplots[i].set_title(cross_title)
        cross_subplots[i].set_xlim(xmin, xmax)
        cross_subplots[i].grid()


        cross_subplots[i].set_ylim(ymin, ymax)
        cross_lines.append(cross_subplots[i].plot(freqs, 10*np.log10(np.abs(c.cross[cross_baselines[i]][:1024])**2))[0])
    
    figname = os.path.join("/home/controller/var/run/lofasm-slack-alerts/",
                           os.path.basename(fpath) + '_ALL' + '.png')
    plt.savefig(figname)
    plt.clf()
    return figname




if __name__ == "__main__":
    import slack_funcs as sf
    fpath = get_latest_data_file()
    print "Uploading sample of {}".format(fpath)

    figname = generate_plot_all_channels(fpath)
    sf.uploadImage(figname)
    os.remove(figname)
