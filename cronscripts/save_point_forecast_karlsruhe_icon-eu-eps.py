
import os

import astropy.table
import astropy.io

import sys
current_path = sys.path[0]
ex_op_str = current_path[current_path.index('progs')+6: current_path.index('w2w_ensembleplots')-1]
sys.path.append('/progs/{}'.format(ex_op_str))
from w2w_ensembleplots.core.download_forecast import calc_latest_run_time
from w2w_ensembleplots.core.read_data import read_forecast_data
from w2w_ensembleplots.core.meteogram_boxplot import get_meta_data


def main():

    model = 'icon-eu-eps'

    date = calc_latest_run_time(model)
    #date = dict(year = 2021, month = 9, day = 9, hour = 0)

    var_list = ['t_2m','wind_mean_10m','vmax_10m','mslp','clct','direct_rad','t_850hPa']

    grid = 'icosahedral'

    #point = dict(lat = 49.014, lon =  8.404)
    point = dict(name = 'Karlsruhe')


    path = dict(base = '/',
                points = 'data/model_data/icon-eu-eps/point-forecasts/kit-weather-ensemble-point-forecast-karlsruhe/',
                credentials = 'data/additional_data/')

    for var in var_list:
        data = read_forecast_data(model, grid, date, var, point = point)
        save_values(data, path, date, point, var, model)

    commit_and_push_files(path)

    return

########################################################################
########################################################################
########################################################################

def commit_and_push_files(path):

    with open(path['base'] + path['credentials'] + 'gitlab_credentials.txt', 'r') as f:
        lines = f.readlines()
        password = lines[0][4:-1]

    git_paths = '--git-dir={}{}.git/ --work-tree={}{} '.format(
               path['base'], path['points'], path['base'], path['points'])
    git_repo = 'https://nw5893:{}@git.scc.kit.edu/nw5893/kit-weather-ensemble-point-forecast-karlsruhe.git'.format(
                password)

    os.system('git ' + git_paths + 'add --all')
    os.system('git ' + git_paths + 'commit -m "Upload new point forecast files"')
    os.system('git ' + git_paths + 'push --repo=' + git_repo)
    os.system('git ' + git_paths + 'fetch origin')
    os.system('git ' + git_paths + 'status')

    return

########################################################################
########################################################################
########################################################################

def save_values(data_source, path, date, point, var, model):

    # write forecast times #

    if var == 'vmax_10m' or var == 'direct_rad':
        fcst_hours_list = list(range(1,48,1)) + list(range(48,72,3)) + list(range(72,120+1,6))
    else:
        fcst_hours_list = list(range(0,48,1)) + list(range(48,72,3)) + list(range(72,120+1,6))


    # print data values to string matrix #

    data = []
    data.append(fcst_hours_list)

    if model == 'icon-eu-eps' or model == 'icon-global-eps':
        for column in range(40):
            data_column = []
            for row in range(len(fcst_hours_list)):
                value = data_source[row, column]
                if abs(value) < 0.01:
                    value_str = '{:.0f}'.format(value)
                else:
                    value_str = '{:.2f}'.format(value)
                data_column.append(value_str)
            data.append(data_column)


        # make  header #

        header = [str(x) for x in range(1,41)]
        header.insert(0, 'fcst_hour')


    # make astropy table and add meta data #

    t = astropy.table.Table(data, names = header)
    meta = get_meta_data(var)
    str1 = 'variable: {}'.format(meta['var'])
    str2 = 'units: {}'.format(meta['units'])
    t.meta['comments'] = [str1, str2, '']


    # write table to file #

    filename = '{}_{}{:02}{:02}{:02}_{}_{}.txt'.format(
                model, date['year'], date['month'], date['day'], date['hour'], var, point['name'])

    astropy.io.ascii.write(t, output = path['base'] + path['points'] + filename,
                           overwrite = True, Writer = astropy.io.ascii.FixedWidth)

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
