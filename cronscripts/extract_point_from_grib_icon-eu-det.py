###############################################################################
###  script for extracting point value data from icon-eu and saving it      ###
###############################################################################

from sys import argv

import sys
current_path = sys.path[0]
ex_op_str = current_path[current_path.index('scripts')+8 : current_path.index('w2w_ensembleplots')-1]
sys.path.append('/lsdfos/kit/imk-tro/projects/MOD/Gruppe_Knippertz/nw5893/scripts/{}'.format(ex_op_str))
from w2w_ensembleplots.core.extract_point_from_grib import point_savetofile_iconeudet


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


    point_savetofile_iconeudet(pointnames, date, None, None, False, verbose)

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
