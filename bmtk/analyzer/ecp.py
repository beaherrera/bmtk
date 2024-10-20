import os
import h5py
import matplotlib.pyplot as plt
import numpy as np
from decimal import Decimal

from bmtk.utils.sonata.config import SonataConfig
from bmtk.simulator.utils import simulation_reports
from mpl_toolkits.axes_grid1.anchored_artists import AnchoredSizeBar
import matplotlib.font_manager as fm


def _get_ecp_path(ecp_path=None, config=None, report_name=None):
    if ecp_path is not None:
         return ecp_path

    elif config is not None:
        possible_paths = []
        sim_reports = simulation_reports.from_config(config)
        for report in sim_reports:
            if report.module in ['extracellular', 'ecp']:
                rname = report.report_name
                rfile = report.params['file_name']
                rpath = rfile if os.path.isabs(rfile) else os.path.join(report.params['tmp_dir'], rfile)
                if report_name is not None and report_name == rname:
                    possible_paths.append((rname, rpath))
                elif report_name is None:
                    possible_paths.append((rname, rpath))

        if len(possible_paths) == 0:
            msg = 'Could not find a ECP report '
            msg += '' if report_name is None else 'with report_name "{}"'.format(report_name)
            msg += ' from configuration file. . Use "report_path" parameter instead.'
            raise ValueError(msg)

        elif len(possible_paths) > 1:
            avail_reports = ', '.join(s[0] for s in possible_paths)
            raise ValueError('Configuration file contained multiple "extracelluar", use "report_name" or'
                             '"report_path" to pick which one to plot. Option values: {}'.format(avail_reports))

        else:
            return possible_paths[0]

    else:
        raise AttributeError('Could not find a compartment report SONATA file. Please user "config_file" or '
                             '"report_path" options.')


def plot_ecp(config_file=None, report_name=None, ecp_path=None, title=None, show=True):
    sonata_config = SonataConfig.from_json(config_file) if config_file else None

    _, ecp_path = _get_ecp_path(ecp_path=ecp_path, config=sonata_config, report_name=report_name)
    ecp_h5 = h5py.File(ecp_path, 'r')

    time_traces = np.arange(start=ecp_h5['/ecp/time'][0], stop=ecp_h5['/ecp/time'][1], step=ecp_h5['/ecp/time'][2])

    channels = ecp_h5['/ecp/channel_id'][()]
    fig, axes = plt.subplots(len(channels), 1)
    fig.text(0.04, 0.5, 'channel id', va='center', rotation='vertical')
    v_min, v_max = ecp_h5['/ecp/data'][()].min(), ecp_h5['/ecp/data'][()].max()
    # print(v_max - v_min)
    # exit()
    
    for idx, channel in enumerate(channels):
        data = ecp_h5['/ecp/data'][:, idx]
        # print(channel, np.min(data), np.max(data))
        axes[idx].plot(time_traces, data)
        axes[idx].spines["top"].set_visible(False)
        axes[idx].spines["right"].set_visible(False)
        axes[idx].set_yticks([])
        axes[idx].set_ylabel(channel)
        axes[idx].set_ylim([v_min, v_max])

        if idx+1 != len(channels):
            axes[idx].spines["bottom"].set_visible(False)
            axes[idx].set_xticks([])
        else:
            axes[idx].set_xlabel('timestamps (ms)')
        
        
        if idx == 0:
            scale_bar_size = (v_max-v_min)/2.0
            scale_bar_label = f'{scale_bar_size:.2E}'
            # print(scale_bar_label)
            # exit()
            fontprops = fm.FontProperties(size='x-small')

            scalebar = AnchoredSizeBar(
                axes[idx].transData,
                size=scale_bar_size, 
                label=scale_bar_label, 
                loc='upper right',
                pad=0.1,
                borderpad=0.5,
                sep=5,
                # color='b',
                frameon=False,
                size_vertical=scale_bar_size,
                # size_vertical=1.001,
                fontproperties=fontprops
            )            
            axes[idx].add_artist(scalebar)

            # label = scalebar.txt_label
            # label.set_rotation(270.0)
            # label.set_verticalalignment('bottom')
            # label.set_horizontalalignment('left') 

    if title:
        fig.set_title(title)

    if show:
        plt.show()
