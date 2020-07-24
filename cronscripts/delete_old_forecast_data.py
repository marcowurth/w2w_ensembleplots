############################################################################
###  script for deleting old forecast data from all four icon models     ###
############################################################################

import os
import shutil
import datetime

import sys
current_path = sys.path[0]
ex_op_str = current_path[current_path.index('progs')+6: current_path.index('w2w_ensembleplots')-1]
sys.path.append('/progs/{}'.format(ex_op_str))
from w2w_ensembleplots.core.download_forecast import calc_latest_run_time


def main():

    max_days_to_keep_data = 3       # set this to required time (in days)


    path = dict(base = '/')
    models = ['icon-eu-eps', 'icon-global-eps', 'icon-eu-det', 'icon-global-det']
    date_now  = datetime.datetime.now()

    for model in models:
        #print(model)
        path['data'] = 'data/model_data/{}/forecasts/'.format(model)
        run_folders = os.listdir(path['base'] + path['data'])
        for run_folder in run_folders:
            #print(run_folder)
            date_run = datetime.datetime(int(run_folder[4:8]), int(run_folder[8:10]),
                                         int(run_folder[10:12]), int(run_folder[12:14]))
            timedelta = date_now - date_run
            #print(timedelta)

            if timedelta.days > max_days_to_keep_data:
                shutil.rmtree(path['base'] + path['data'] + run_folder)
        #print('--------------------------')

    return

########################################################################
########################################################################
########################################################################

if __name__ == '__main__':
    import time
    t1 = time.time()
    main()
    t2 = time.time()
    delta_t = t2-t1
    if delta_t < 60:
        print('total script time:  {:.1f}s'.format(delta_t))
    elif 60 <= delta_t <= 3600:
        print('total script time:  {:.0f}min{:.0f}s'.format(delta_t//60, delta_t-delta_t//60*60))
    else:
        print('total script time:  {:.0f}h{:.1f}min'.format(delta_t//3600, (delta_t-delta_t//3600*3600)/60))
