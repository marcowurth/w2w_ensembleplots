
import os
from PIL import Image

import sys
current_path = sys.path[0]
ex_op_str = current_path[current_path.index('scripts')+8 : current_path.index('w2w_ensembleplots')-1]
sys.path.append('/lsdfos/kit/imk-tro/projects/MOD/Gruppe_Knippertz/nw5893/scripts/{}'.format(ex_op_str))
from w2w_ensembleplots.core.download_forecast import calc_latest_run_time
from w2w_ensembleplots.core.probofexc_2x2 import plot_prob_of_exc_2x2_timespan


def main():

    variable = dict(name = 'tot_prec_48h', unit = 'mm')
    #thresholds = [0.1, 3.0, 10.0, 50.0, 0.1]
    #thresholds = [10.0, 25.0, 50.0, 100.0, 0.1]
    thresholds = [40.0, 60.0, 80.0, 100.0, 0.1]
    title_pos = 130
    #only_0utc_12utc_runs = False
    only_0utc_12utc_runs = True
    #model = 'icon-eu-eps'
    model = 'icon-global-eps'

    domains = []
    #domains.append(dict(method = 'centerpoint', radius = 1400, deltalat =   0, deltalon =   0,
    #              lat = 48.0, lon =  9.0, name = 'europe'))
    #domains.append(dict(method = 'deltalatlon', radius =    0, deltalat = 500, deltalon = 550,
    #              lat = 50.8, lon = 10.0, name = 'germany'))
    domains.append(dict(method = 'deltalatlon', radius =    0, deltalat = 900, deltalon = 990,
                  lat = -34.5, lon = -61.0, name = 'central_argentina'))

    plot_prob_of_exc_2x2_timespan(variable, thresholds, domains, model, title_pos, only_0utc_12utc_runs)


    return

########################################################################
########################################################################
########################################################################

if __name__ == '__main__':
    import time
    t1 = time.time()
    main()
    t2 = time.time()
    print('total script time:  {:.1f}s'.format(t2-t1))
