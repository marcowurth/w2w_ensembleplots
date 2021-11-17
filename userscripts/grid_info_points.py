#######################################################################
###    Script for Calling Plotting Scripts and Merging the Plots    ###
#######################################################################

import sys
current_path = sys.path[0]
ex_op_str = current_path[current_path.index('progs')+6: current_path.index('w2w_ensembleplots')-1]
sys.path.append('/progs/{}'.format(ex_op_str))
from w2w_ensembleplots.core.grid_information_around_point import plot_point_information_eu


def main():

    #pointnames =   ['Karlsruhe','Mainz','Munich',\
    #                'Amsterdam','Athens','Berlin','Bologna','Brussels','Copenhagen','Dublin','Hamburg',\
    #                'Madrid','Leeds','Lisbon','London','Paris','Rome','Toulouse','Valencia','Vienna','Warsaw']
    pointnames =   ['Offenbach']
    #pointnames =   ['Cotonou_sea','Cotonou_land','Accra','Kumasi','Abidjan','Sal','Dakar_sea', 'Dakar_land','Bamako','Ouagadougou','Niamey',\
    #                'Douala','Ngaoundere','Abuja','Agadez','Parakou','Libreville_sea','Libreville_land']

    models_type = 'eu-eps'     # icon-eu-eps and icon-global-eps
    #models_type = 'eu-det'     # icon-eu-det and icon-global-det
    #models_type = 'global-eps'     # icon-global-eps
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
    delta_t = t2-t1
    if delta_t < 60:
        print('total script time:  {:.1f}s'.format(delta_t))
    elif 60 <= delta_t <= 3600:
        print('total script time:  {:.0f}min{:.0f}s'.format(delta_t//60, delta_t-delta_t//60*60))
    else:
        print('total script time:  {:.0f}h{:.1f}min'.format(delta_t//3600, (delta_t-delta_t//3600*3600)/60))
