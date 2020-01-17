#######################################################################
###    Script for Calling Plotting Scripts and Merging the Plots    ###
#######################################################################

import sys
current_path = sys.path[0]
ex_op_str = current_path[current_path.index('scripts')+8 : current_path.index('w2w_ensembleplots')-1]
sys.path.append('/lsdfos/kit/imk-tro/projects/MOD/Gruppe_Knippertz/nw5893/scripts/{}'.format(ex_op_str))
from w2w_ensembleplots.core.grid_information_around_point import plot_point_information_eu


def main():

    pointnames =   ['Karlsruhe','Mainz','Munich',\
                    'Amsterdam','Athens','Berlin','Bologna','Brussels','Copenhagen','Dublin','Hamburg',\
                    'Madrid','Leeds','Lisbon','London','Paris','Rome','Toulouse','Valencia','Vienna','Warsaw']
    pointnames =   ['BuenosAires']
    pointnames =   ['Cotonou','Accra','Kumasi','Abidjan','Sal','Dakar','Bamako','Ouagadougou','Niamey',\
                    'Douala','Ngaoundere','Abuja','Agadez','Parakou','Libreville']

    #models_type = 'eu-eps'     # icon-eu-eps and icon-global-eps
    #models_type = 'eu-det'     # icon-eu-det and icon-global-det
    models_type = 'global-eps'     # icon-global-eps
    #models_type = 'global-det'     # icon-global-det

    no_title = True
    #no_title = False

    for pointname in pointnames:
        plot_point_information_eu(pointname, models_type, no_title)
        #plot_point_information_global(pointname, models_type, no_title)


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
