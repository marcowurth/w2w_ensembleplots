
import sys
current_path = sys.path[0]
ex_op_str = current_path[current_path.index('scripts')+8 : current_path.index('w2w_ensembleplots')-1]
sys.path.append('/lsdfos/kit/imk-tro/projects/MOD/Gruppe_Knippertz/nw5893/scripts/{}'.format(ex_op_str))
from w2w_ensembleplots.core.meteogram_uncertainty_shades import plot_t2m_uncertainty_shades


def main():

  ###########################################################
    run = None     # if None: get latest run
    #run = dict(year = 2019, month = 10, day = 7, hour = 0)
    pointnames = ['Karlsruhe','Mainz','Munich',\
                  'Amsterdam','Athens','Berlin','Bologna','Brussels','Copenhagen','Dublin','Hamburg',\
                  'Madrid','Leeds','Lisbon','London','Paris','Rome','Toulouse','Valencia','Vienna','Warsaw']
    #pointnames = ['Munich']
    #mode = '180h_raw'
    #mode = '120h_raw'
    mode = '48h_interpolated'
    #colorpalette_name = 'palettable_orange'
    colorpalette_name = 'custom'
    verbose = True
  ###########################################################

    plot_t2m_uncertainty_shades(pointnames, run, mode, colorpalette_name, verbose)

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
