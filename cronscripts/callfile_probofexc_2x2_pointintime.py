
from sys import argv

import sys
current_path = sys.path[0]
ex_op_str = current_path[current_path.index('scripts')+8 : current_path.index('w2w_ensembleplots')-1]
sys.path.append('/lsdfos/kit/imk-tro/projects/MOD/Gruppe_Knippertz/nw5893/scripts/{}'.format(ex_op_str))
from w2w_ensembleplots.core.statistics_contourplot import triangle_contourplot


def main(variable_name, variable_unit, variable_hour,\
         run_year, run_month, run_day, run_hour,\
         domain_method, domain_radius, domain_deltalat, domain_deltalon, domain_lat, domain_lon, domain_name,\
         model, stat_processing_method, stat_processing_threshold, plot_type):

    variable = dict(name = variable_name, unit = variable_unit, hour = variable_hour)
    run = dict(year = run_year, month = run_month, day = run_day, hour = run_hour)
    domain = dict(method = domain_method, radius = domain_radius, deltalat = domain_deltalat,\
                  deltalon = domain_deltalon, lat = domain_lat, lon = domain_lon, name = domain_name)
    stat_processing = dict(method = stat_processing_method, threshold = stat_processing_threshold)

    triangle_contourplot(variable, run, domain, model, stat_processing, plot_type)

    return

########################################################################
########################################################################
########################################################################

if __name__ == '__main__':
    main(argv[1], argv[2], int(argv[3]),\
         int(argv[4]), int(argv[5]), int(argv[6]), int(argv[7]),\
         argv[8], float(argv[9]), float(argv[10]), float(argv[11]), float(argv[12]), float(argv[13]), argv[14],\
         argv[15], argv[16], float(argv[17]), argv[18])
