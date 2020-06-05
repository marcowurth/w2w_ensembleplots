
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
    grid = 'latlon_0.25'
    #grid = 'latlon_0.0625'


    print(model)

    if grid == 'icosahedral':
        clat, clon, vlat, vlon = read_grid_coordinates(model, grid)
        print(clat.shape, clon.shape, vlat.shape, vlon.shape)
        print(clat.min(), clat.max())
        print(clon.min(), clon.max())
        print(vlat.min(), vlat.max())
        print(vlon.min(), vlon.max())

    elif grid == 'latlon_0.25':
        clat, clon = read_grid_coordinates(model, grid)
        print(clat.shape, clon.shape)
        print(clat.min(), clat.max())
        print(clon.min(), clon.max())
        print(clon[::10])

    elif grid == 'latlon_0.0625':
        clat, clon = read_grid_coordinates(model, grid)
        print(clat.shape, clon.shape)
        print(clat.min(), clat.max())
        print(clon.min(), clon.max())


    return

########################################################################
########################################################################
########################################################################

if __name__ == '__main__':
    import time
    t1 = time.time()
    main()
    t2 = time.time()
    print('total script time:  {:.0f}ms'.format( 1000 * (t2-t1) ))
