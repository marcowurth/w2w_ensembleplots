
import os
from PIL import Image

import sys
current_path = sys.path[0]
ex_op_str = current_path[current_path.index('scripts')+8 : current_path.index('w2w_ensembleplots')-1]
sys.path.append('/lsdfos/kit/imk-tro/projects/MOD/Gruppe_Knippertz/nw5893/scripts/{}'.format(ex_op_str))
from w2w_ensembleplots.core.download_forecast import calc_latest_run_time
from w2w_ensembleplots.core.probofexc_2x2 import plot_prob_of_exc_2x2_pointintime


def main():

    variable = dict(name = 'tqv', unit = 'mm')
    thresholds = [10.0, 15.0, 20.0, 30.0, 10.0]
    title_pos = 95
    only_0utc_12utc_runs = True

    plot_prob_of_exc_2x2_pointintime(variable, thresholds, title_pos, only_0utc_12utc_runs)


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
