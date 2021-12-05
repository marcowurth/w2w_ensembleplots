###############################################################################
###  script for plotting boxplot meteograms of point data of icon-eu-eps    ###
###############################################################################

import os

import sys
current_path = sys.path[0]
ex_op_str = current_path[current_path.index('progs')+6: current_path.index('w2w_ensembleplots')-1]
sys.path.append('/progs/{}'.format(ex_op_str))
from w2w_ensembleplots.core.meteogram_boxplot import boxplot_forecast_raw, boxplot_forecast_pp
from w2w_ensembleplots.core.download_forecast import calc_latest_run_time


def main():

  ###########################################################
    models = 'both-eps'     # plot icon-eu-eps only if global not available
    date = 'latest'
    #date = dict(year = 2021, month = 12, day = 4, hour = 18)
    var = 'all_available'
    pointnames_raw =   ['Karlsruhe','Mainz','Munich','Berlin','Hamburg','Offenbach',\
                        'Amsterdam','Athens','Bologna','Brussels','Copenhagen','Dublin',\
                        'Madrid','Leeds','Lisbon','London','Paris','Rome',\
                        'Toulouse','Valencia','Vienna','Warsaw','Zurich']
    #pointnames_raw = ['Karlsruhe']
    pointnames_pp = ['Karlsruhe','Mainz','Munich','Berlin','Hamburg']
    point_type = 'operational_city'
    verbose = True

  ###########################################################

    path = dict(base = '/',
                plots = 'data/plots/operational/meteogram_boxplot/forecast/operational_cities/',
                webserver = '/home/iconeps/Data3/plots/icon/meteogram_boxplot/forecast/operational_cities',
                rscripts = '/home/benedikt/R_scripts/')


    # plot raw model output meteograms and save the German cities data to textfiles #

    for pointname in pointnames_raw:
        if verbose:
            print('--- next meteogram (raw) point is {} ---'.format(pointname))

        if pointname in ['Karlsruhe','Mainz','Munich','Offenbach','Berlin','Hamburg']:
            save_point_data = True
        else:
            save_point_data = False

        y_axis_limits = 'raw'
        boxplot_forecast_raw(models, date, var, dict(name = pointname),
                             point_type, save_point_data, y_axis_limits, verbose)


    # run post-processing #

    os.system('Rscript ' + path['rscripts'] + 'pp_init.R')
    print('-------- pp calculation done ---------')


    # plot post-processed meteograms and replot with adjusted y-axis the corresponding raw meteograms #

    for pointname in pointnames_pp:
        if verbose:
            print('--- next meteogram (pp) point is {} ---'.format(pointname))
        boxplot_forecast_pp(date, var, dict(name = pointname), verbose)

        save_point_data = False
        y_axis_limits = 'raw_and_pp'
        boxplot_forecast_raw(models, date, var, dict(name = pointname),
                             point_type, save_point_data, y_axis_limits, verbose)


    # create latest_run file #

    if date == 'latest':
        date = calc_latest_run_time('icon-eu-eps')

    filename_latest_run = 'latest_run_boxplot_meteograms.txt'
    with open(path['base'] + path['plots'] + filename_latest_run, 'w') as file:
        file.write('{:4d}{:02d}{:02d}{:02d}'.format(date['year'], date['month'], date['day'], date['hour']))


    # copy all meteograms and latest_run file to webserver #

    subfolder = 'run_{}{:02}{:02}{:02}'.format(date['year'], date['month'], date['day'], date['hour'])
    os.system('scp -q -r ' + path['base'] + path['plots'] + subfolder + ' '\
              + 'iconeps@imk-tss-web.imk-tro.kit.edu:' + path['webserver'])
    os.system('scp -q ' + path['base'] + path['plots'] + filename_latest_run + ' '\
              + 'iconeps@imk-tss-web.imk-tro.kit.edu:' + path['webserver'])

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
