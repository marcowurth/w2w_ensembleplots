
import sys
current_path = sys.path[0]
ex_op_str = current_path[current_path.index('progs')+6: current_path.index('w2w_ensembleplots')-1]
sys.path.append('/progs/{}'.format(ex_op_str))
from w2w_ensembleplots.core.read_data import read_grid_coordinates


def main():

    #model = 'icon-eu-eps'
    #model = 'icon-global-eps'
    #model = 'icon-eu-det'
    model = 'icon-global-det'

    #grid = 'icosahedral'
    #grid = 'latlon_0.25'
    grid = 'latlon_0.1'
    #grid = 'latlon_0.0625'


    print(model)

    if grid == 'icosahedral':
        clat, clon, vlat, vlon = read_grid_coordinates(model, grid)
        print('clat:', clat.shape, 'clon:', clon.shape, 'vlat:', vlat.shape, 'vlon:', vlon.shape)
        print('clat min,max:', clat.min(), clat.max())
        print('clon min,max:', clon.min(), clon.max())
        print('vlat min,max:', vlat.min(), vlat.max())
        print('vlon min,max:', vlon.min(), vlon.max())

    elif grid == 'latlon_0.25' or grid == 'latlon_0.1':
        clat, clon = read_grid_coordinates(model, grid)
        print(clat.shape, clon.shape)
        print(clat.min(), clat.max())
        print(clon.min(), clon.max())
        print(clat[::20])
        print(clon[::0])

    elif grid == 'latlon_0.0625':
        clat, clon = read_grid_coordinates(model, grid)
        print(clat.shape, clon.shape)
        print(clat.min(), clat.max())
        print(clon.min(), clon.max())
        print(clat)
        print(clon)


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
