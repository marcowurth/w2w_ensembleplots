#######################################################################
###    Script for Calling Plotting Scripts and Merging the Plots    ###
#######################################################################

import sys
current_path = sys.path[0]
ex_op_str = current_path[current_path.index('progs')+6: current_path.index('w2w_ensembleplots')-1]
sys.path.append('/progs/{}'.format(ex_op_str))
from w2w_ensembleplots.core.deterministic_contourplot import det_contourplot
from w2w_ensembleplots.core.download_forecast import calc_latest_run_time

def main():

    model = 'icon-global-det'

    run = calc_latest_run_time(model)
    #run = dict(year = 2020, month = 6, day = 21, hour = 12)

    domains =[]
    domains.append(dict(method = 'centerpoint', radius = 1400, deltalat =   0, deltalon =   0,
                   lat = 48.0, lon =  9.0, name = 'europe'))
    domains.append(dict(method = 'centerpoint', radius = 1900, deltalat =   0, deltalon =   0,
                   lat = 37.0, lon =  -99.0, name = 'usa'))
    #domains.append(dict(method = 'centerpoint', radius = 1400, deltalat =   0, deltalon =   0,
    #               lat = 48.0, lon =  -171, name = 'pacific'))
    #domains.append(dict(method = 'centerpoint', radius = 1400, deltalat =   0, deltalon =   0,
    #               lat = 90, lon =  0, name = 'north pole'))
    #domains.append(dict(method = 'centerpoint', radius = 2400, deltalat =   0, deltalon =   0,
    #               lat = -90, lon =  0, name = 'south pole'))

    variable1 = dict(name='prec_rate', unit='mm/h', grid='icosahedral')
    variable2 = dict(name='mslp', unit='hPa', grid='latlon_0.25')

    det_contourplot(domains, variable1, variable2, model, run)

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
