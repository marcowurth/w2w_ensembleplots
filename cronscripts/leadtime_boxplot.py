#####################################################################################################
###  script for plotting verification leadtime boxplots of point data of icon-eu-eps and icon-eu  ###
#####################################################################################################

from sys import argv

import sys
current_path = sys.path[0]
ex_op_str = current_path[current_path.index('scripts')+8 : current_path.index('w2w_ensembleplots')-1]
sys.path.append('/lsdfos/kit/imk-tro/projects/MOD/Gruppe_Knippertz/nw5893/scripts/{}'.format(ex_op_str))
from w2w_ensembleplots.core.leadtime_boxplot import boxplot_leadtime


def main(pointname):

    #date = dict(year = 2019, month = 4, day = 13, hour = 12)
    date = None     # if None: get latest run

    verbose = True

    if pointname == 'All21':
        pointnames = ['Karlsruhe','Mainz','Munich',\
                      'Amsterdam','Athens','Berlin','Bologna','Brussels','Copenhagen','Dublin','Hamburg',\
                      'Madrid','Leeds','Lisbon','London','Paris','Rome','Toulouse','Valencia','Vienna','Warsaw']
    else:
        pointnames = [pointname]


    boxplot_leadtime(pointnames, date, verbose)

    return

########################################################################
########################################################################
########################################################################

if __name__ == '__main__':
    import time
    t1 = time.time()
    main(argv[1])
    t2 = time.time()
    print('total script time:  {:.1f}s'.format(t2-t1))
