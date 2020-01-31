###############################################################################
###  script for plotting boxplot meteograms of point data of icon-eu-eps    ###
###############################################################################

import sys
current_path = sys.path[0]
ex_op_str = current_path[current_path.index('scripts')+8 : current_path.index('w2w_ensembleplots')-1]
sys.path.append('/lsdfos/kit/imk-tro/projects/MOD/Gruppe_Knippertz/nw5893/scripts/{}'.format(ex_op_str))
from w2w_ensembleplots.core.meteogram_boxplot import boxplot_forecast


def main():

  ###########################################################
    #date = dict(year = 2019, month = 12, day = 12, hour = 6)
    date = None     # if None: get latest run
    include_global = False
    latest_fcst = True
    pointnames = ['Karlsruhe','Mainz','Munich',\
                  'Amsterdam','Athens','Berlin','Bologna','Brussels','Copenhagen','Dublin','Hamburg',\
                  'Madrid','Leeds','Lisbon','London','Paris','Rome','Toulouse','Valencia','Vienna','Warsaw']
    #pointnames = ['Madrid']
    verbose = True
  ###########################################################

    boxplot_forecast(pointnames, date, include_global, latest_fcst, verbose)

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
