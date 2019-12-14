
import numpy as np
import eccodes
from ensembleplots.container_uncertainty_shades import plot_tmax_uncertainty_shades
from ensembleplots.container_information_point import get_latlon_filter_distance
from contextlib import ExitStack


def main():

    path = dict(base = '/lsdfos/kit/imk-tro/projects/MOD/Gruppe_Knippertz/nw5893/',
                data = 'forecast_archive/pamore/heatwave_25.07.19/',
                grid = 'forecast_archive/icon-eu-eps/grid/',
                plots = 'plots/heatwave_25.07.19/point_plots/')

    run = dict(year = 2019, month = 7, day = 21, hour = 0)

    hours = [6,12,18,100,106,112,118,200,206,212,218,300,306,312,318,400,406,412,418,500]

    data_tmax_6h = np.empty((len(hours), 40, 75948))

    filenames_all = []
    for hour in hours:
        filenames_all.append(['iefff0{:03d}0000.m0{:02d}'.format(hour, member) for member in range(1, 41)])
    path['data_subfolder'] = 'run_{:4d}{:02d}{:02d}{:02d}/'.format(run['year'], run['month'], run['day'], run['hour'])

    with ExitStack() as stack:
        files_all = [[stack.enter_context(open(path['base'] + path['data'] + path['data_subfolder'] + filename,'rb'))\
          for filename in filenames_of_one_hour] for filenames_of_one_hour in filenames_all]

        for i, files_of_one_hour in enumerate(files_all):
            for j, file in enumerate(files_of_one_hour):
                grib_id = eccodes.codes_grib_new_from_file(file)
                data_tmax_6h[i, j, :] = eccodes.codes_get_array(grib_id, 'values')
                eccodes.codes_release(grib_id)
    del files_all, files_of_one_hour, file

    data_tmax_6h -= 273.15
    data_tmax_24h = data_tmax_6h.reshape(5, 4, 40, 75948).max(axis=1)

    points = []
    points.append(dict(lat = 49.014, lon =  8.350, name = 'Karlsruhe',  measurements=[30.0, 30.0, 30.0, 30.0, 30.0]))
    points.append(dict(lat = 48.860, lon =  2.350, name = 'Paris',      measurements=[30.0, 30.0, 30.0, 30.0, 30.0]))
    points.append(dict(lat = 50.937, lon =  6.954, name = 'Koeln',      measurements=[30.0, 30.0, 30.0, 30.0, 30.0]))
    points.append(dict(lat = 47.198, lon = -1.534, name = 'Nantes',     measurements=[30.0, 30.0, 30.0, 30.0, 30.0]))
    points.append(dict(lat = 52.519, lon = 13.407, name = 'Berlin',     measurements=[30.0, 30.0, 30.0, 30.0, 30.0]))
    points.append(dict(lat = 48.240, lon = 11.570, name = 'Munchen',    measurements=[30.0, 30.0, 30.0, 30.0, 30.0]))
    points.append(dict(lat = 52.489, lon = -3.462, name = 'Wales',      measurements=[30.0, 30.0, 30.0, 30.0, 30.0]))



    for point in points:
        index_nearest = get_point_index(path, point, 'icon-eu-eps')
        ens_data = data_tmax_24h[:, :, index_nearest]

        print(point['name'])
        #print(ens_data)


        plot_tmax_uncertainty_shades(path, run, point, ens_data)

    return

########################################################################
########################################################################
########################################################################

def get_point_index(path, point, model):

    # custom version of the function in container_information_point

    # get clat and clon 1D arrays

    filename_clat = 'icon-eu-eps_europe_icosahedral_time-invariant_2018121000_clat.grib2'
    filename_clon = 'icon-eu-eps_europe_icosahedral_time-invariant_2018121000_clon.grib2'
    with open(path['base'] + path['grid'] + filename_clat,'rb') as file:
        grib_id = eccodes.codes_grib_new_from_file(file)
        clat = eccodes.codes_get_array(grib_id, 'values')
        eccodes.codes_release(grib_id)
    with open(path['base'] + path['grid'] + filename_clon,'rb') as file:
        grib_id = eccodes.codes_grib_new_from_file(file)
        clon = eccodes.codes_get_array(grib_id, 'values')
        eccodes.codes_release(grib_id)


    # read out index of native point

    filter_distance = get_latlon_filter_distance(model)
    lat_near = list(np.where(abs(clat - point['lat']) < filter_distance)[0])
    lon_near = list(np.where(abs(clon - point['lon']) < filter_distance)[0])
    id_near = list(set(lat_near).intersection(lon_near))
    id_near.sort()
    distances = np.sqrt( np.square(abs(clat[id_near] - point['lat']) * 111.2) \
                        + np.square(abs(clon[id_near] - point['lon']) * 111.2 \
                                                 * np.cos(point['lat']*np.pi/180)) )
    index_nearest = id_near[np.argmin(distances)]

    #print(id_near)
    #print(distances)
    #print(index_nearest)
    #print(clat[index_nearest], clon[index_nearest])

    return index_nearest

########################################################################
########################################################################
########################################################################

if __name__ == '__main__':
    import time
    t1 = time.time()
    main()
    t2 = time.time()
    print('total script time:  {:.1f}s'.format(t2-t1))
