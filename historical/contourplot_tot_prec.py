
import os
from ensembleplots.container_download import calc_latest_run_time


def main():

    ##### settings #####

    run = calc_latest_run_time('icon-eu-eps')
    if run['hour'] == 0:
        hours = list(range(24, 120+1, 24))
    else:
        hours = list(range(48 - run['hour'], 120+1, 24))


    #run = dict(year = 2019, month = 10, day = 4, hour = 6)

    #hours = list(range(24, 120+1, 24))       # 00Z run
    #hours = list(range(24+18, 120+1, 24))    # 06Z run
    #hours = list(range(24+12, 120+1, 24))    # 12Z run
    #hours = list(range(24+6, 120+1, 24))    # 18Z run
    #hours = [120]

    stat_processing_list = []
    stat_processing_list.append(dict(method = 'max'))
    stat_processing_list.append(dict(method = 'min'))
    #stat_processing_list.append(dict(method = 'median'))
    #stat_processing_list.append(dict(method = '10p'))
    #stat_processing_list.append(dict(method = '90p'))
    #stat_processing_list.append(dict(method = 'spread'))
    #stat_processing_list.append(dict(method = 'member_extract', member = 'all'))
    #stat_processing_list.append(dict(method = 'member_extract', member = '1'))

    stat_processing_list.append(dict(method = 'prob_of_exc', threshold = 0.1))
    #stat_processing_list.append(dict(method = 'prob_of_exc', threshold = 1))
    stat_processing_list.append(dict(method = 'prob_of_exc', threshold = 3))
    stat_processing_list.append(dict(method = 'prob_of_exc', threshold = 10))
    #stat_processing_list.append(dict(method = 'prob_of_exc', threshold = 20))
    stat_processing_list.append(dict(method = 'prob_of_exc', threshold = 50))
    #stat_processing_list.append(dict(method = 'prob_of_exc', threshold = 100))

    domains = []
    domains.append(dict(method = 'centerpoint', radius = 1400, deltalat =   0, deltalon =   0,\
                  lat = 48.0, lon =  9.0, name = 'europe'))
    #domains.append(dict(method = 'deltalatlon', radius =    0, deltalat = 500, deltalon = 550,\
    #              lat = 50.8, lon = 10.0, name = 'germany'))


    # make small map plots #

    path = '/lsdfos/kit/imk-tro/projects/MOD/Gruppe_Knippertz/nw5893/scripts/experimental/dwd-ensembleplots/'
    for stat_processing in stat_processing_list:
        for hour in hours:
            variable = dict(name = 'tot_prec', hour_start = hour - 24, hour_end = hour)

            scriptname = 'callfile_contourplot_tot_prec.py'
            if stat_processing['method'] == 'member_extract':
                last_str = stat_processing['member']
            elif stat_processing['method'] == 'prob_of_exc':
                last_str = '{:.2f}'.format(stat_processing['threshold'])
            else:
                last_str = 'nothing'

            for domain in domains:
                if stat_processing['method'] == 'prob_of_exc':
                    print('{:2d}-{:2d}h, prob_of_exc, {}mm, {}'.format(hour - 24, hour, stat_processing['threshold'],\
                          domain['name']))
                elif stat_processing['method'] == 'member_extract':
                    print('{:2d}-{:2d}h, member {}, {}'.format(hour - 24, hour, stat_processing['member'],\
                          domain['name']))
                else:
                    print('{:2d}-{:2d}h, {}, {}'.format(hour - 24, hour, stat_processing['method'],\
                          domain['name']))

                command = 'python {}{} '.format(path, scriptname)
                arguments = '{} {:d} {:d} {:d} {:d} {:d} {:d} {} {:.2f} {:.2f} {:.2f} {:.2f} {:.2f} {} {} {}'.format(\
                            variable['name'], variable['hour_start'], variable['hour_end'],\
                            run['year'], run['month'], run['day'], run['hour'],\
                            domain['method'], domain['radius'], domain['deltalat'], domain['deltalon'],\
                            domain['lat'], domain['lon'], domain['name'],\
                            stat_processing['method'], last_str)
                os.system(command + arguments)

    triangle_contourplot(variable, run, domain, stat_processing, plot_type)

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
