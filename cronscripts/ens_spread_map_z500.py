#######################################################################
###    Script for Calling Plotting Scripts and Merging the Plots    ###
#######################################################################

import sys
current_path = sys.path[0]
ex_op_str = current_path[current_path.index('progs')+6: current_path.index('w2w_ensembleplots')-1]
sys.path.append('/progs/{}'.format(ex_op_str))
from w2w_ensembleplots.core.ensemble_spread_maps import ens_spread_contourplot
from w2w_ensembleplots.core.download_forecast import calc_latest_run_time
from w2w_ensembleplots.core.domain_definitions import get_domain

def main():

    model = 'icon-eu-eps'

    run = calc_latest_run_time(model)
    if run['hour'] == 6 or run['hour'] == 18:
        run['hour'] -= 6
    #run = dict(year = 2020, month = 10, day = 15, hour = 0)

    domains =[]
    domains.append(get_domain('EU-Nest'))

    variable1 = dict(name='gph_500hPa', unit='gpdm', grid='icosahedral')
    variable2 = dict(name='gph_500hPa', unit='gpdm', grid='latlon_0.2')

    ens_spread_contourplot(domains, variable1, variable2, model, run)

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
