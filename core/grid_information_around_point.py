#########################################
###  container for various functions  ###
#########################################

import numpy as np
import eccodes
import netCDF4 as nc
import Ngl
import os
from sys import argv
from PIL import Image


def which_grid_point(pointname, model):
    ###################################################################################################
    ##### this is the database for the different grid point and city coordinates                  #####
    ##### city: point of actual city                                                              #####
    ##### icon-xyz: point that lies within desired corresponding grid point of the model icon-xyz #####
    ###################################################################################################

    if model == 'city':
        allpoints =[dict(lat = 49.014, lon =  8.404, name = 'Karlsruhe'),\
                    dict(lat = 50.001, lon =  8.265, name = 'Mainz'),\
                    dict(lat = 48.141, lon = 11.580, name = 'Munich'),\
                    dict(lat = 52.519, lon = 13.391, name = 'Berlin'),\
                    dict(lat = 53.549, lon =  9.990, name = 'Hamburg'),\
                    dict(lat = 50.098, lon =  8.761, name = 'Offenbach'),\
                    dict(lat = 48.477, lon =  8.934, name = 'Rottenburg_am_Neckar'),\
                    dict(lat = 52.373, lon =  4.899, name = 'Amsterdam'),\
                    dict(lat = 48.210, lon = 16.371, name = 'Vienna'),\
                    dict(lat = 41.898, lon = 12.491, name = 'Rome'),\
                    dict(lat = 37.976, lon = 23.725, name = 'Athens'),\
                    dict(lat = 40.418, lon = -3.704, name = 'Madrid'),\
                    dict(lat = 39.474, lon = -0.377, name = 'Valencia'),\
                    dict(lat = 38.718, lon = -9.139, name = 'Lisbon'),\
                    dict(lat = 51.511, lon = -0.118, name = 'London'),\
                    dict(lat = 53.347, lon = -6.264, name = 'Dublin'),\
                    dict(lat = 55.678, lon = 12.576, name = 'Copenhagen'),\
                    dict(lat = 52.233, lon = 21.009, name = 'Warsaw'),\
                    dict(lat = 48.857, lon =  2.344, name = 'Paris'),\
                    dict(lat = 43.602, lon =  1.443, name = 'Toulouse'),\
                    dict(lat = 53.798, lon = -1.545, name = 'Leeds'),\
                    dict(lat = 44.496, lon = 11.343, name = 'Bologna'),\
                    dict(lat = 50.848, lon =  4.351, name = 'Brussels'),\
                    dict(lat =-34.617, lon =-58.416, name = 'BuenosAires'),\
                    dict(lat =-34.617, lon =-58.416, name = 'Kapstadt'),\
                    dict(lat = 47.373, lon =  8.539, name = 'Zurich'),\
                    dict(lat =  6.375, lon =  2.388, name = 'Cotonou_sea'),\
                    dict(lat =  6.375, lon =  2.388, name = 'Cotonou_land'),\
                    dict(lat =  5.594, lon = -0.186, name = 'Accra'),\
                    dict(lat =  6.681, lon = -1.616, name = 'Kumasi'),\
                    dict(lat =  5.349, lon = -4.011, name = 'Abidjan'),\
                    dict(lat = 16.740, lon =-22.931, name = 'Sal'),\
                    dict(lat = 14.712, lon =-17.467, name = 'Dakar_sea'),\
                    dict(lat = 14.712, lon =-17.467, name = 'Dakar_land'),\
                    dict(lat = 12.625, lon = -7.990, name = 'Bamako'),\
                    dict(lat = 12.365, lon = -1.522, name = 'Ouagadougou'),\
                    dict(lat = 13.505, lon =  2.125, name = 'Niamey'),\
                    dict(lat =  4.046, lon =  9.758, name = 'Douala'),\
                    dict(lat =  7.330, lon = 13.571, name = 'Ngaoundere'),\
                    dict(lat =  9.079, lon =  7.424, name = 'Abuja'),\
                    dict(lat = 16.972, lon =  7.986, name = 'Agadez'),\
                    dict(lat =  9.343, lon =  2.610, name = 'Parakou'),\
                    dict(lat =  0.405, lon =  9.459, name = 'Libreville_sea'),\
                    dict(lat =  0.405, lon =  9.459, name = 'Libreville_land')]
    elif model == 'icon-eu-eps':
        allpoints =[dict(lat = 49.014, lon =  8.350, name = 'Karlsruhe'),\
                    dict(lat = 50.003, lon =  8.268, name = 'Mainz'),\
                    dict(lat = 48.109, lon = 11.594, name = 'Munich'),\
                    dict(lat = 52.519, lon = 13.407, name = 'Berlin'),\
                    dict(lat = 53.500, lon =  9.993, name = 'Hamburg'),\
                    dict(lat = 50.098, lon =  8.761, name = 'Offenbach'),\
                    dict(lat = 48.477, lon =  8.934, name = 'Rottenburg_am_Neckar'),\
                    dict(lat = 52.373, lon =  4.899, name = 'Amsterdam'),\
                    dict(lat = 48.256, lon = 16.438, name = 'Vienna'),\
                    dict(lat = 41.890, lon = 12.481, name = 'Rome'),\
                    dict(lat = 37.984, lon = 23.690, name = 'Athens'),\
                    dict(lat = 40.420, lon = -3.730, name = 'Madrid'),\
                    dict(lat = 39.550, lon = -0.490, name = 'Valencia'),\
                    dict(lat = 38.754, lon = -9.200, name = 'Lisbon'),\
                    dict(lat = 51.507, lon =  0.000, name = 'London'),\
                    dict(lat = 53.400, lon = -6.350, name = 'Dublin'),\
                    dict(lat = 55.710, lon = 12.480, name = 'Copenhagen'),\
                    dict(lat = 52.217, lon = 21.033, name = 'Warsaw'),\
                    dict(lat = 48.860, lon =  2.350, name = 'Paris'),\
                    dict(lat = 43.602, lon =  1.400, name = 'Toulouse'),\
                    dict(lat = 53.850, lon = -1.500, name = 'Leeds'),\
                    dict(lat = 44.490, lon = 11.380, name = 'Bologna'),\
                    dict(lat = 50.930, lon =  4.330, name = 'Brussels'),\
                    dict(lat = 46.949, lon =  7.448, name = 'Bern'),\
                    dict(lat = 47.373, lon =  8.539, name = 'Zurich')]
    elif model == 'icon-eps' or model == 'icon-global-eps':
        allpoints =[dict(lat = 49.014, lon =  8.350, name = 'Karlsruhe'),\
                    dict(lat = 50.003, lon =  8.268, name = 'Mainz'),\
                    dict(lat = 48.109, lon = 11.594, name = 'Munich'),\
                    dict(lat = 52.519, lon = 13.407, name = 'Berlin'),\
                    dict(lat = 53.500, lon =  9.993, name = 'Hamburg'),\
                    dict(lat = 50.098, lon =  8.761, name = 'Offenbach'),\
                    dict(lat = 48.477, lon =  8.934, name = 'Rottenburg_am_Neckar'),\
                    dict(lat = 52.373, lon =  4.899, name = 'Amsterdam'),\
                    dict(lat = 48.256, lon = 16.438, name = 'Vienna'),\
                    dict(lat = 41.890, lon = 12.481, name = 'Rome'),\
                    dict(lat = 37.984, lon = 23.690, name = 'Athens'),\
                    dict(lat = 40.420, lon = -3.730, name = 'Madrid'),\
                    dict(lat = 39.550, lon = -0.490, name = 'Valencia'),\
                    dict(lat = 38.754, lon = -8.930, name = 'Lisbon'),\
                    dict(lat = 51.507, lon =  0.000, name = 'London'),\
                    dict(lat = 53.400, lon = -6.350, name = 'Dublin'),\
                    dict(lat = 55.710, lon = 12.480, name = 'Copenhagen'),\
                    dict(lat = 52.217, lon = 21.033, name = 'Warsaw'),\
                    dict(lat = 48.860, lon =  2.350, name = 'Paris'),\
                    dict(lat = 43.602, lon =  1.400, name = 'Toulouse'),\
                    dict(lat = 53.850, lon = -1.500, name = 'Leeds'),\
                    dict(lat = 44.490, lon = 11.380, name = 'Bologna'),\
                    dict(lat = 50.930, lon =  4.330, name = 'Brussels'),\
                    dict(lat = 46.949, lon =  7.448, name = 'Bern'),\
                    dict(lat =-34.800, lon =-58.400, name = 'BuenosAires'),\
                    dict(lat = 47.373, lon =  8.539, name = 'Zurich'),\
                    dict(lat =  6.375, lon =  2.388, name = 'Cotonou_sea'),\
                    dict(lat =  6.475, lon =  2.388, name = 'Cotonou_land'),\
                    dict(lat =  5.594, lon = -0.186, name = 'Accra'),\
                    dict(lat =  6.681, lon = -1.616, name = 'Kumasi'),\
                    dict(lat =  5.349, lon = -4.011, name = 'Abidjan'),\
                    dict(lat = 16.740, lon =-22.931, name = 'Sal'),\
                    dict(lat = 14.712, lon =-17.467, name = 'Dakar_sea'),\
                    dict(lat = 14.712, lon =-17.067, name = 'Dakar_land'),\
                    dict(lat = 12.625, lon = -7.990, name = 'Bamako'),\
                    dict(lat = 12.365, lon = -1.522, name = 'Ouagadougou'),\
                    dict(lat = 13.505, lon =  2.125, name = 'Niamey'),\
                    dict(lat =  4.046, lon =  9.758, name = 'Douala'),\
                    dict(lat =  7.330, lon = 13.571, name = 'Ngaoundere'),\
                    dict(lat =  9.079, lon =  7.424, name = 'Abuja'),\
                    dict(lat = 16.972, lon =  7.986, name = 'Agadez'),\
                    dict(lat =  9.343, lon =  2.610, name = 'Parakou'),\
                    dict(lat =  0.405, lon =  9.459, name = 'Libreville_sea'),\
                    dict(lat =  0.405, lon =  9.559, name = 'Libreville_land')]
    elif model == 'icon-eu-det':
        allpoints =[dict(lat = 49.014, lon =  8.404, name = 'Karlsruhe'),\
                    dict(lat = 50.001, lon =  8.265, name = 'Mainz'),\
                    dict(lat = 48.141, lon = 11.580, name = 'Munich'),\
                    dict(lat = 52.519, lon = 13.391, name = 'Berlin'),\
                    dict(lat = 53.549, lon =  9.990, name = 'Hamburg'),\
                    dict(lat = 50.098, lon =  8.761, name = 'Offenbach'),\
                    dict(lat = 48.477, lon =  8.934, name = 'Rottenburg_am_Neckar'),\
                    dict(lat = 52.373, lon =  4.899, name = 'Amsterdam'),\
                    dict(lat = 48.210, lon = 16.371, name = 'Vienna'),\
                    dict(lat = 41.898, lon = 12.491, name = 'Rome'),\
                    dict(lat = 37.976, lon = 23.725, name = 'Athens'),\
                    dict(lat = 40.418, lon = -3.704, name = 'Madrid'),\
                    dict(lat = 39.474, lon = -0.377, name = 'Valencia'),\
                    dict(lat = 38.718, lon = -9.139, name = 'Lisbon'),\
                    dict(lat = 51.511, lon = -0.118, name = 'London'),\
                    dict(lat = 53.347, lon = -6.264, name = 'Dublin'),\
                    dict(lat = 55.678, lon = 12.576, name = 'Copenhagen'),\
                    dict(lat = 52.233, lon = 21.009, name = 'Warsaw'),\
                    dict(lat = 48.857, lon =  2.344, name = 'Paris'),\
                    dict(lat = 43.602, lon =  1.443, name = 'Toulouse'),\
                    dict(lat = 53.798, lon = -1.545, name = 'Leeds'),\
                    dict(lat = 44.496, lon = 11.343, name = 'Bologna'),\
                    dict(lat = 50.848, lon =  4.351, name = 'Brussels'),\
                    dict(lat = 46.949, lon =  7.448, name = 'Bern'),\
                    dict(lat = 47.373, lon =  8.539, name = 'Zurich')]
    elif model == 'icon' or model == 'icon-global-det':
        allpoints =[dict(lat = 49.014, lon =  8.404, name = 'Karlsruhe'),\
                    dict(lat = 50.001, lon =  8.265, name = 'Mainz'),\
                    dict(lat = 48.141, lon = 11.580, name = 'Munich'),\
                    dict(lat = 52.519, lon = 13.391, name = 'Berlin'),\
                    dict(lat = 53.549, lon =  9.990, name = 'Hamburg'),\
                    dict(lat = 50.098, lon =  8.761, name = 'Offenbach'),\
                    dict(lat = 48.477, lon =  8.934, name = 'Rottenburg_am_Neckar'),\
                    dict(lat = 52.373, lon =  4.899, name = 'Amsterdam'),\
                    dict(lat = 48.210, lon = 16.371, name = 'Vienna'),\
                    dict(lat = 41.898, lon = 12.491, name = 'Rome'),\
                    dict(lat = 37.976, lon = 23.725, name = 'Athens'),\
                    dict(lat = 40.418, lon = -3.704, name = 'Madrid'),\
                    dict(lat = 39.474, lon = -0.377, name = 'Valencia'),\
                    dict(lat = 38.718, lon = -9.139, name = 'Lisbon'),\
                    dict(lat = 51.511, lon = -0.118, name = 'London'),\
                    dict(lat = 53.347, lon = -6.264, name = 'Dublin'),\
                    dict(lat = 55.678, lon = 12.576, name = 'Copenhagen'),\
                    dict(lat = 52.233, lon = 21.009, name = 'Warsaw'),\
                    dict(lat = 48.857, lon =  2.344, name = 'Paris'),\
                    dict(lat = 43.602, lon =  1.443, name = 'Toulouse'),\
                    dict(lat = 53.798, lon = -1.545, name = 'Leeds'),\
                    dict(lat = 44.496, lon = 11.343, name = 'Bologna'),\
                    dict(lat = 50.848, lon =  4.351, name = 'Brussels'),\
                    dict(lat = 46.949, lon =  7.448, name = 'Bern'),\
                    dict(lat =-34.617, lon =-58.416, name = 'BuenosAires'),\
                    dict(lat = 47.373, lon =  8.539, name = 'Zurich')]
    else:
        print('Wrong model name!')
        exit()


    for point in allpoints:
        if point['name'] == pointname:
            return point

    print('no point found with this name: {}'.format(pointname))
    return None

#######################################################################################################################
#######################################################################################################################
#######################################################################################################################
#######################################################################################################################
#######################################################################################################################
#######################################################################################################################
#######################################################################################################################
#######################################################################################################################

def get_latlon_filter_distance(model):
    ################################################################################################
    ##### filter distance in zonal and meridional direction in degrees (1 deg = 111.2km)       #####
    ##### formula for icosahedral grid RnBk:                                                   #####
    #####     filter_distance = (2/3)*sqrt(sqrt(3)*1.05*A_avg) [km]                            #####
    #####     A_avg: average cell area, 1.05: cell area can be up to 5% bigger as average area #####
    #####     A_avg = (pi/5)*r_e^2/(n^2*4^k)                                                   #####
    #####  -> filter_distance = 40.83/(n*2^k) [deg]                                            #####
    ##### put value in deg below for new grid                                                  #####
    ################################################################################################

    if model == 'icon-eu-eps':
        filter_distance = 0.160         # R2B7 icosahedral grid
    elif model == 'icon-global-eps':
        filter_distance = 0.319         # R2B6 icosahedral grid
    elif model == 'icon-eu-det':
        filter_distance = 0.065         # 0.0625deg latlon grid
    elif model == 'icon-global-det':
        filter_distance = 0.107         # R3B7 icosahedral grid

    return  filter_distance

#######################################################################################################################
#######################################################################################################################
#######################################################################################################################
#######################################################################################################################
#######################################################################################################################
#######################################################################################################################
#######################################################################################################################
#######################################################################################################################

def plot_point_information_eu(pointname, models_type, no_title):
    path = dict(base = '/',
                plots = 'data/plots/point_information/')

    print('plot {} information about {}'.format(models_type, pointname))

    if models_type == 'eu-eps':
        filenames = dict()
        filenames['oro_icon-eu-eps']            = plot_orography(pointname, 'icon-eu-eps')
        filenames['oro_icon-global-eps']        = plot_orography(pointname, 'icon-global-eps')
        filenames['landsea_icon-eu-eps']        = plot_landsea(pointname, 'icon-eu-eps')
        filenames['landsea_icon-global-eps']    = plot_landsea(pointname, 'icon-global-eps')
        filenames['composite']                  = 'grid_information_{}_{}.png'.format(pointname, models_type)

        img_combined = Image.new('RGB',(1500, 1300),(255,255,255))

        #img_example.crop((39, 44, 601, 596))   # (left, upper, right, lower) corner

        text_title = Image.open(path['base'] + path['plots'] + filenames['landsea_icon-eu-eps'])
        img_combined.paste(text_title.crop((15, 620, 760, 663)), (750-310, 20))
        text_iconeueps = Image.open(path['base'] + path['plots'] + filenames['oro_icon-eu-eps'])
        img_combined.paste(text_iconeueps.crop((154, 624, 464, 655)), (200+271-136, 170-36-15))
        text_iconeps = Image.open(path['base'] + path['plots'] + filenames['oro_icon-global-eps'])
        img_combined.paste(text_iconeps.crop((154, 624, 530, 655)), (200+542+20+271-170, 170-36-15))

        text_oro = Image.open(path['base'] + path['plots'] + filenames['oro_icon-eu-eps'])
        img_combined.paste(text_oro.crop((154, 701, 302, 732)), (38, 170+266-15))
        map_oro_iconeueps = Image.open(path['base'] + path['plots'] + filenames['oro_icon-eu-eps'])
        img_combined.paste(map_oro_iconeueps.crop((37, 42, 579, 574)), (200, 170))
        map_oro_iconeps = Image.open(path['base'] + path['plots'] + filenames['oro_icon-global-eps'])
        img_combined.paste(map_oro_iconeps.crop((37, 42, 579, 574)), (200+542+20, 170))
        lb_oro = Image.open(path['base'] + path['plots'] + filenames['oro_icon-eu-eps'])
        img_combined.paste(lb_oro.crop((606, 44, 746, 574)), (200+542+20+542+20, 172))

        text_landsea1 = Image.open(path['base'] + path['plots'] + filenames['landsea_icon-eu-eps'])
        img_combined.paste(text_landsea1.crop((77, 730, 255, 755)), (13, 170+532+20+266-12-20))
        text_landsea2 = Image.open(path['base'] + path['plots'] + filenames['landsea_icon-eu-eps'])
        img_combined.paste(text_landsea2.crop((268, 730, 378, 755)), (50, 170+532+20+266-12+20))
        map_landsea_iconeueps = Image.open(path['base'] + path['plots'] + filenames['landsea_icon-eu-eps'])
        img_combined.paste(map_landsea_iconeueps.crop((37, 42, 579, 574)), (200, 170+532+20))
        map_landsea_iconeps = Image.open(path['base'] + path['plots'] + filenames['landsea_icon-global-eps'])
        img_combined.paste(map_landsea_iconeps.crop((37, 42, 579, 574)), (200+542+20, 170+532+20))
        lb_landsea = Image.open(path['base'] + path['plots'] + filenames['landsea_icon-eu-eps'])
        img_combined.paste(lb_landsea.crop((623, 44, 746, 574)), (200+542+20+542+20, 172+532+20))

        img_combined.save(path['base'] + path['plots'] + 'eu/' + filenames['composite'],'png')

        os.remove(path['base'] + path['plots'] + filenames['oro_icon-eu-eps'])
        os.remove(path['base'] + path['plots'] + filenames['oro_icon-global-eps'])
        os.remove(path['base'] + path['plots'] + filenames['landsea_icon-eu-eps'])
        os.remove(path['base'] + path['plots'] + filenames['landsea_icon-global-eps'])


    elif models_type == 'eu-det':
        filenames = dict()
        filenames['oro_icon-eu-det']            = plot_orography(pointname, 'icon-eu-det')
        filenames['oro_icon-global-det']        = plot_orography(pointname, 'icon-global-det')
        filenames['landsea_icon-eu-det']        = plot_landsea(pointname, 'icon-eu-det')
        filenames['landsea_icon-global-det']    = plot_landsea(pointname, 'icon-global-det')
        filenames['composite']                  = 'grid_information_{}_{}.png'.format(pointname, models_type)
        path['plots'] += 'eu/'

        img_combined = Image.new('RGB',(1500, 1300),(255,255,255))

        #img_example.crop((39, 44, 601, 596))   # (left, upper, right, lower) corner

        text_title = Image.open(path['base'] + path['plots'] + filenames['landsea_icon-eu-det'])
        img_combined.paste(text_title.crop((15, 620, 760, 663)), (750-340, 20))
        text_iconeueps = Image.open(path['base'] + path['plots'] + filenames['oro_icon-eu-det'])
        img_combined.paste(text_iconeueps.crop((154, 624, 490, 655)), (200+271-136, 170-36-15))
        text_iconeps = Image.open(path['base'] + path['plots'] + filenames['oro_icon-global-det'])
        img_combined.paste(text_iconeps.crop((154, 624, 530, 655)), (200+542+20+271-170, 170-36-15))

        text_oro = Image.open(path['base'] + path['plots'] + filenames['oro_icon-eu-det'])
        img_combined.paste(text_oro.crop((154, 701, 302, 732)), (38, 170+269-15))
        map_oro_iconeueps = Image.open(path['base'] + path['plots'] + filenames['oro_icon-eu-det'])
        img_combined.paste(map_oro_iconeueps.crop((37, 40, 579, 578)), (200, 170))
        map_oro_iconeps = Image.open(path['base'] + path['plots'] + filenames['oro_icon-global-det'])
        img_combined.paste(map_oro_iconeps.crop((37, 40, 579, 578)), (200+542+20, 170))
        lb_oro = Image.open(path['base'] + path['plots'] + filenames['oro_icon-eu-det'])
        img_combined.paste(lb_oro.crop((605, 42, 746, 574)), (200+542+20+542+20, 172))

        text_landsea1 = Image.open(path['base'] + path['plots'] + filenames['landsea_icon-eu-det'])
        img_combined.paste(text_landsea1.crop((77, 730, 255, 755)), (13, 170+538+20+269-12-20))
        text_landsea2 = Image.open(path['base'] + path['plots'] + filenames['landsea_icon-eu-det'])
        img_combined.paste(text_landsea2.crop((268, 730, 378, 755)), (50, 170+538+20+269-12+20))
        map_landsea_iconeueps = Image.open(path['base'] + path['plots'] + filenames['landsea_icon-eu-det'])
        img_combined.paste(map_landsea_iconeueps.crop((37, 40, 579, 578)), (200, 170+538+20))
        map_landsea_iconeps = Image.open(path['base'] + path['plots'] + filenames['landsea_icon-global-det'])
        img_combined.paste(map_landsea_iconeps.crop((37, 40, 579, 578)), (200+542+20, 170+538+20))
        lb_landsea = Image.open(path['base'] + path['plots'] + filenames['landsea_icon-eu-det'])
        img_combined.paste(lb_landsea.crop((622, 42, 748, 574)), (200+542+20+542+20, 172+538+20))

        img_combined.save(path['base'] + path['plots'] + 'eu/' + filenames['composite'],'png')

        os.remove(path['base'] + path['plots'] + filenames['oro_icon-eu-det'])
        os.remove(path['base'] + path['plots'] + filenames['oro_icon-global-det'])
        os.remove(path['base'] + path['plots'] + filenames['landsea_icon-eu-det'])
        os.remove(path['base'] + path['plots'] + filenames['landsea_icon-global-det'])


    if models_type == 'global-eps':
        filenames = dict()
        filenames['oro_icon-global-eps']        = plot_orography(pointname, 'icon-global-eps')
        filenames['landsea_icon-global-eps']    = plot_landsea(pointname, 'icon-global-eps')
        filenames['composite']                  = 'grid_information_{}_{}.png'.format(pointname, models_type)

        img_combined = Image.new('RGB',(920, 1300),(255,255,255))

        #img_example.crop((39, 44, 601, 596))   # (left, upper, right, lower) corner

        text_title = Image.open(path['base'] + path['plots'] + filenames['landsea_icon-global-eps'])
        img_combined.paste(text_title.crop((15, 620, 760, 663)), (500-360, 20))
        text_iconeps = Image.open(path['base'] + path['plots'] + filenames['oro_icon-global-eps'])
        img_combined.paste(text_iconeps.crop((154, 624, 530, 655)), (200+271-170, 170-36-15))

        text_oro = Image.open(path['base'] + path['plots'] + filenames['oro_icon-global-eps'])
        img_combined.paste(text_oro.crop((154, 701, 302, 732)), (38, 170+266-15))
        map_oro_iconeps = Image.open(path['base'] + path['plots'] + filenames['oro_icon-global-eps'])
        img_combined.paste(map_oro_iconeps.crop((37, 42, 579, 574)), (200, 170))
        lb_oro = Image.open(path['base'] + path['plots'] + filenames['oro_icon-global-eps'])
        img_combined.paste(lb_oro.crop((606, 44, 746, 574)), (200+542+20, 172))

        text_landsea1 = Image.open(path['base'] + path['plots'] + filenames['landsea_icon-global-eps'])
        img_combined.paste(text_landsea1.crop((77, 730, 255, 755)), (13, 170+532+20+266-12-20))
        text_landsea2 = Image.open(path['base'] + path['plots'] + filenames['landsea_icon-global-eps'])
        img_combined.paste(text_landsea2.crop((268, 730, 378, 755)), (50, 170+532+20+266-12+20))
        map_landsea_iconeps = Image.open(path['base'] + path['plots'] + filenames['landsea_icon-global-eps'])
        img_combined.paste(map_landsea_iconeps.crop((37, 42, 579, 574)), (200, 170+532+20))
        lb_landsea = Image.open(path['base'] + path['plots'] + filenames['landsea_icon-global-eps'])
        img_combined.paste(lb_landsea.crop((623, 44, 746, 574)), (200+542+20, 172+532+20))

        img_combined.save(path['base'] + path['plots'] + 'global/' + filenames['composite'],'png')

        os.remove(path['base'] + path['plots'] + filenames['oro_icon-global-eps'])
        os.remove(path['base'] + path['plots'] + filenames['landsea_icon-global-eps'])


    elif models_type == 'global-det':
        filenames = dict()
        filenames['oro_icon-global-det']        = plot_orography(pointname, 'icon-global-det')
        filenames['landsea_icon-global-det']    = plot_landsea(pointname, 'icon-global-det')
        filenames['composite']                  = 'grid_information_{}_{}.png'.format(pointname, models_type)

        img_combined = Image.new('RGB',(920, 1300),(255,255,255))

        #img_example.crop((39, 44, 601, 596))   # (left, upper, right, lower) corner

        text_title = Image.open(path['base'] + path['plots'] + filenames['landsea_icon-global-det'])
        img_combined.paste(text_title.crop((15, 620, 760, 663)), (500-360, 20))
        text_iconeps = Image.open(path['base'] + path['plots'] + filenames['oro_icon-global-det'])
        img_combined.paste(text_iconeps.crop((154, 624, 530, 655)), (200+271-170, 170-36-15))

        text_oro = Image.open(path['base'] + path['plots'] + filenames['oro_icon-global-det'])
        img_combined.paste(text_oro.crop((154, 701, 302, 732)), (38, 170+269-15))
        map_oro_iconeps = Image.open(path['base'] + path['plots'] + filenames['oro_icon-global-det'])
        img_combined.paste(map_oro_iconeps.crop((37, 40, 579, 578)), (200, 170))
        lb_oro = Image.open(path['base'] + path['plots'] + filenames['oro_icon-global-det'])
        img_combined.paste(lb_oro.crop((605, 42, 746, 574)), (200+542+20, 172))

        text_landsea1 = Image.open(path['base'] + path['plots'] + filenames['landsea_icon-global-det'])
        img_combined.paste(text_landsea1.crop((77, 730, 255, 755)), (13, 170+538+20+269-12-20))
        text_landsea2 = Image.open(path['base'] + path['plots'] + filenames['landsea_icon-global-det'])
        img_combined.paste(text_landsea2.crop((268, 730, 378, 755)), (50, 170+538+20+269-12+20))
        map_landsea_iconeps = Image.open(path['base'] + path['plots'] + filenames['landsea_icon-global-det'])
        img_combined.paste(map_landsea_iconeps.crop((37, 40, 579, 578)), (200, 170+538+20))
        lb_landsea = Image.open(path['base'] + path['plots'] + filenames['landsea_icon-global-det'])
        img_combined.paste(lb_landsea.crop((622, 42, 748, 574)), (200+542+20, 172+538+20))

        img_combined.save(path['base'] + path['plots'] + 'global/' + filenames['composite'],'png')

        os.remove(path['base'] + path['plots'] + filenames['oro_icon-global-det'])
        os.remove(path['base'] + path['plots'] + filenames['landsea_icon-global-det'])


    if no_title:
        if models_type == 'eu-eps' or models_type == 'eu-det':
            img_with_title = Image.open(path['base'] + path['plots'] + 'eu/' + filenames['composite'])
            img_no_title = img_with_title.crop((0, 100, 1500, 1300))
            img_no_title.save(path['base'] + path['plots'] + 'eu/' + filenames['composite'],'png')

        if models_type == 'global-eps' or models_type == 'global-det':
            img_with_title = Image.open(path['base'] + path['plots'] + 'global/' + filenames['composite'])
            img_no_title = img_with_title.crop((0, 100, 920, 1300))
            img_no_title.save(path['base'] + path['plots'] + 'global/' + filenames['composite'],'png')

    del filenames

    return

#######################################################################################################################
#######################################################################################################################
#######################################################################################################################
#######################################################################################################################
#######################################################################################################################
#######################################################################################################################
#######################################################################################################################
#######################################################################################################################

def plot_orography(pointname, model):

    point_city = which_grid_point(pointname, 'city')
    point_grid = which_grid_point(pointname, model)

    plot_name = '{}_orography_{}'.format(model, pointname)

    filenames = dict()
    path = dict(base = '/',
                plots = 'data/plots/point_information/')

    path['data'] = 'data/model_data/{}/invariant/'.format(model)
    path['grid'] = 'data/model_data/{}/grid/'.format(model)

    if model == 'icon-eu-eps':
        filenames['cells'] = 'icon_grid_0028_R02B07_N02.nc'
        filenames['oro'] = 'icon-eu-eps_europe_icosahedral_time-invariant_2021021700_hsurf.grib2'

    elif model == 'icon-global-eps':
        filenames['cells'] = 'icon_grid_0024_R02B06_G.nc'
        filenames['oro'] = 'icon-eps_global_icosahedral_time-invariant_2019010800_hsurf.grib2'

    elif model == 'icon-eu-det':
        filenames['lat'] = 'icon-eu_europe_regular-lat-lon_time-invariant_2019040800_RLAT.grib2'
        filenames['lon'] = 'icon-eu_europe_regular-lat-lon_time-invariant_2019040800_RLON.grib2'
        filenames['oro'] = 'icon-eu_europe_regular-lat-lon_time-invariant_2019061400_HSURF.grib2'

    elif model == 'icon-global-det':
        filenames['cells'] = 'icon_grid_0026_R03B07_G.nc'
        filenames['oro'] = 'icon_global_icosahedral_time-invariant_2019061400_HSURF.grib2'

    if model == 'icon-eu-det':
        with open(path['base'] + path['grid'] + filenames['lat'],'rb') as file:
            grib_id = eccodes.codes_grib_new_from_file(file)
            clat = eccodes.codes_get_array(grib_id, 'values')
            eccodes.codes_release(grib_id)
        with open(path['base'] + path['grid'] + filenames['lon'],'rb') as file:
            grib_id = eccodes.codes_grib_new_from_file(file)
            clon = eccodes.codes_get_array(grib_id, 'values')
            eccodes.codes_release(grib_id)
            #np.where(clon < 0.0, 360.0 - clon, clon)
    else:
        mpi_file = nc.Dataset(path['base'] + path['grid'] + filenames['cells'], 'r')
        vlat = mpi_file.variables['clat_vertices'][:].data * 180./np.pi
        vlon = mpi_file.variables['clon_vertices'][:].data * 180./np.pi
        clat = mpi_file.variables['clat'][:].data * 180./np.pi
        clon = mpi_file.variables['clon'][:].data * 180./np.pi
        mpi_file.close()

    with open(path['base'] + path['data'] + filenames['oro'],'rb') as file:
        grib_id = eccodes.codes_grib_new_from_file(file)
        oro_hgt = eccodes.codes_get_array(grib_id, 'values')
        eccodes.codes_release(grib_id)
    oro_hgt += 10    # offset of colormap

    if model == 'icon-eu-det':
        clon = np.reshape(clon,(1097, 657),'F')
        clat = np.reshape(clat,(1097, 657),'F')
        oro_hgt = np.reshape(oro_hgt,(1097, 657),'F')

    ########################################################################

    x_resolution        = 770
    y_resolution        = 770
    wks_res             = Ngl.Resources()
    wks_res.wkWidth     = x_resolution
    wks_res.wkHeight    = y_resolution

    wks_type    = 'png'
    wks         = Ngl.open_wks(wks_type, path['base'] + path['plots'] + plot_name, wks_res)
    resources   = Ngl.Resources()

    resources.mpProjection = 'Hammer'
    resources.mpCenterLonF = point_grid['lon']
    resources.mpCenterLatF = point_grid['lat']

    if model == 'icon-eu-det' or model == 'icon-global-det':
        radius = 100    # image radius in km around centered point
    else:
        radius = 200    # image radius in km around centered point

    cutout_plot = dict(
                        lat_min = point_grid['lat'] - radius / 111.2,
                        lat_max = point_grid['lat'] + radius / 111.2,
                        lon_min = point_grid['lon'] - radius / (111.2 * np.cos(point_grid['lat']*np.pi/180)),
                        lon_max = point_grid['lon'] + radius / (111.2 * np.cos(point_grid['lat']*np.pi/180)),
                       )

    resources.mpLimitMode   = 'latlon'
    resources.mpMinLonF     = cutout_plot['lon_min']
    resources.mpMaxLonF     = cutout_plot['lon_max']
    resources.mpMinLatF     = cutout_plot['lat_min']
    resources.mpMaxLatF     = cutout_plot['lat_max']

    resources.nglMaximize   = False
    resources.vpXF          = 0.05
    resources.vpYF          = 0.95
    resources.vpWidthF      = 0.7
    resources.vpHeightF     = 0.7

    ########################################################################

    # Turn on filled map areas:
    resources.mpFillOn = True

    # Set colors for [FillValue, Ocean, Land , InlandWater]:
    resources.mpFillColors = ['pink','blue','white','blue']

    resources.mpDataBaseVersion         = 'MediumRes'
    resources.mpDataSetName             = 'Earth..4'
    resources.mpOutlineBoundarySets     = 'national'

    resources.mpGeophysicalLineThicknessF   = 7.0 * x_resolution / 1000
    resources.mpNationalLineThicknessF      = 7.0 * x_resolution / 1000
    #resources.mpGridAndLimbDrawOrder        = 'postdraw'

    resources.mpGridAndLimbOn               = False
    #resources.mpLimbLineColor               = 'black'
    #resources.mpLimbLineThicknessF          = 10
    #resources.mpGridLineColor               = 'black'
    #resources.mpGridLineThicknessF          = 1.0
    #resources.mpGridSpacingF                = 1

    resources.mpPerimOn                     = True
    resources.mpPerimLineColor              = 'black'
    resources.mpPerimLineThicknessF         = 8.0 * x_resolution / 1000

    resources.tmXBOn = False
    resources.tmXTOn = False
    resources.tmYLOn = False
    resources.tmYROn = False

    resources.sfDataArray       = oro_hgt
    resources.sfXArray          = clon
    resources.sfYArray          = clat
    resources.sfMissingValueV   = 9999
    if model != 'icon-eu-det':
        resources.sfXCellBounds     = vlon
        resources.sfYCellBounds     = vlat

    resources.cnFillOn              = True
    if model == 'icon-eu-det':
        resources.cnFillMode            = 'RasterFill'
        resources.cnRasterSampleFactorF = 0.0
    else:
        resources.cnFillMode            = 'CellFill'
        resources.cnCellFillEdgeColor   = 'black'

    resources.cnMissingValFillColor = 'black'
    resources.cnFillPalette         = 'OceanLakeLandSnow' #'MPL_terrain'
    resources.cnLevelSelectionMode  = 'ManualLevels'

    minlevel                        = 0.0
    maxlevel                        = 1000.0
    numberoflevels                  = 250
    resources.cnMinLevelValF        = minlevel
    resources.cnMaxLevelValF        = maxlevel
    resources.cnLevelSpacingF       = (maxlevel - minlevel) / numberoflevels

    # Turn off contour lines and labels:
    resources.cnLinesOn         = False
    resources.cnLineLabelsOn    = False

    # Set resources for a nice label bar
    resources.lbLabelBarOn          = True
    resources.lbAutoManage          = False
    resources.lbOrientation         = 'vertical'
    resources.lbLabelOffsetF        = 0.05
    #resources.lbBoxMinorExtentF     = 0.2

    resources.lbLabelStride         = 50
    resources.lbLabelFontHeightF    = 0.02
    resources.lbBoxSeparatorLinesOn = False
    resources.lbBoxLineThicknessF   = 4.0
    #resources.lbBoxEndCapStyle     = 'TriangleBothEnds'
    resources.lbLabelAlignment      = 'BoxCenters'

    resources.lbTitleString         = 'meters above sea level'
    resources.lbTitleFontHeightF    = 0.02
    resources.lbTitlePosition       = 'Right'
    resources.lbTitleDirection      = 'Across'
    resources.lbTitleAngleF         = 90.0
    resources.lbTitleExtentF        = 0.1
    resources.lbTitleOffsetF        = 0.0

    resources.nglFrame = False
    plot = Ngl.contour_map(wks, oro_hgt, resources)

    ########################################################################

    text = 'Orography'
    x = 0.2
    y = 0.05

    text_res_1 = Ngl.Resources()
    text_res_1.txFontHeightF    = 0.03
    text_res_1.txJust           = 'BottomLeft'

    Ngl.text_ndc(wks, text, x, y, text_res_1)

    ########################################################################

    if model == 'icon-eu-eps':
        text = 'ICON-EU-EPS (20km)'
    elif model == 'icon-global-eps':
        text = 'ICON-Global-EPS (40km)'
    elif model == 'icon-eu-det':
        text = 'ICON-EU-DET (6.5km)'
    elif model == 'icon-global-det':
        text = 'ICON-Global-DET (13km)'

    x = 0.2
    y = 0.15

    text_res_2 = Ngl.Resources()
    text_res_2.txFontHeightF    = 0.03
    text_res_2.txJust           = 'BottomLeft'

    Ngl.text_ndc(wks, text, x, y, text_res_2)

    ########################################################################

    filter_distance = get_latlon_filter_distance(model)

    if model == 'icon-eu-det':
        lat_near = list(np.where(abs(clat.flatten('F') - point_grid['lat']) < filter_distance)[0])
        lon_near = list(np.where(abs(clon.flatten('F') - point_grid['lon']) < filter_distance)[0])
        id_near = list(set(lat_near).intersection(lon_near))
        id_near.sort()
        distances = np.sqrt( np.square(abs(clat.flatten('F')[id_near] - point_grid['lat']) * 111.2) \
                            + np.square(abs(clon.flatten('F')[id_near] - point_grid['lon']) * 111.2 \
                                                     * np.cos(point_grid['lat']*np.pi/180)) )
        index_nearest = id_near[np.argmin(distances)]

        linelats = np.zeros(5)
        linelats[0] = clat.flatten('F')[index_nearest] + 0.03125
        linelats[1] = clat.flatten('F')[index_nearest] + 0.03125
        linelats[2] = clat.flatten('F')[index_nearest] - 0.03125
        linelats[3] = clat.flatten('F')[index_nearest] - 0.03125
        linelats[4] = linelats[0]    # end point is start point
        linelons = np.zeros(5)
        linelons[0] = clon.flatten('F')[index_nearest] - 0.03125
        linelons[1] = clon.flatten('F')[index_nearest] + 0.03125
        linelons[2] = clon.flatten('F')[index_nearest] + 0.03125
        linelons[3] = clon.flatten('F')[index_nearest] - 0.03125
        linelons[4] = linelons[0]    # end point is start point

        polyline_res = Ngl.Resources()
        polyline_res.gsLineColor         = 'red'
        polyline_res.gsLineThicknessF    = 4.0
        Ngl.polyline(wks, plot, linelons, linelats, polyline_res)

    else:
        lat_near = list(np.where(abs(clat - point_grid['lat']) < filter_distance)[0])
        lon_near = list(np.where(abs(clon - point_grid['lon']) < filter_distance)[0])
        id_near = list(set(lat_near).intersection(lon_near))
        id_near.sort()
        distances = np.sqrt( np.square(abs(clat[id_near] - point_grid['lat']) * 111.2) \
                            + np.square(abs(clon[id_near] - point_grid['lon']) * 111.2 \
                                                     * np.cos(point_grid['lat']*np.pi/180)) )
        index_nearest = id_near[np.argmin(distances)]

        linelats = np.zeros(4)
        linelats[:3] = vlat[index_nearest]
        linelats[3] = vlat[index_nearest][0]    # end point is start point
        linelons = np.zeros(4)
        linelons[:3] = vlon[index_nearest]
        linelons[3] = vlon[index_nearest][0]

        polyline_res = Ngl.Resources()
        polyline_res.gsLineColor         = 'red'
        polyline_res.gsLineThicknessF    = 6.0
        Ngl.polyline(wks, plot, linelons, linelats, polyline_res)

    ########################################################################

    polymarker_res_1 = Ngl.Resources()
    polymarker_res_1.gsMarkerColor = 'black'
    polymarker_res_1.gsMarkerIndex = 16
    polymarker_res_1.gsMarkerSizeF = 0.015
    polymarker_res_1.gsMarkerThicknessF = 1
    Ngl.polymarker(wks, plot, point_city['lon'], point_city['lat'], polymarker_res_1)

    ########################################################################

    polymarker_res_2 = Ngl.Resources()
    polymarker_res_2.gsMarkerColor = 'white'
    polymarker_res_2.gsMarkerIndex = 16
    polymarker_res_2.gsMarkerSizeF = 0.010
    polymarker_res_2.gsMarkerThicknessF = 1
    Ngl.polymarker(wks, plot, point_city['lon'], point_city['lat'], polymarker_res_2)

    ########################################################################

    Ngl.frame(wks)

    del plot, wks_res, resources, polymarker_res_1, polymarker_res_2, text_res_1, text_res_2, clat, clon
    if model != 'icon-eu-det':
        del vlon, vlat, mpi_file
    Ngl.destroy(wks)

    plot_name += '.png'
    return plot_name

#######################################################################################################################
#######################################################################################################################
#######################################################################################################################
#######################################################################################################################
#######################################################################################################################
#######################################################################################################################
#######################################################################################################################
#######################################################################################################################

def plot_landsea(pointname, model):

    point_city = which_grid_point(pointname, 'city')
    point_grid = which_grid_point(pointname, model)

    plot_name = '{}_landsea_{}'.format(model, pointname)

    filenames = dict()
    path = dict(base = '/',
                plots = 'data/plots/point_information/')

    path['data'] = 'data/model_data/{}/invariant/'.format(model)
    path['grid'] = 'data/model_data/{}/grid/'.format(model)

    if model == 'icon-eu-eps':
        filenames['cells'] = 'icon_grid_0028_R02B07_N02.nc'
        filenames['landsea_fr'] = 'icon-eu-eps_europe_icosahedral_time-invariant_2018121312_fr_land.grib2'

    elif model == 'icon-global-eps':
        filenames['cells'] = 'icon_grid_0024_R02B06_G.nc'
        filenames['landsea_fr'] = 'icon-eps_global_icosahedral_time-invariant_2019010800_fr_land.grib2'

    elif model == 'icon-eu-det':
        filenames['lat'] = 'icon-eu_europe_regular-lat-lon_time-invariant_2019040800_RLAT.grib2'
        filenames['lon'] = 'icon-eu_europe_regular-lat-lon_time-invariant_2019040800_RLON.grib2'
        filenames['landsea_fr'] = 'icon-eu_europe_regular-lat-lon_time-invariant_2019061400_FR_LAND.grib2'

    elif model == 'icon-global-det':
        filenames['cells'] = 'icon_grid_0026_R03B07_G.nc'
        filenames['landsea_fr'] = 'icon_global_icosahedral_time-invariant_2019061400_FR_LAND.grib2'


    if model == 'icon-eu-det':
        with open(path['base'] + path['grid'] + filenames['lat'],'rb') as file:
            grib_id = eccodes.codes_grib_new_from_file(file)
            clat = eccodes.codes_get_array(grib_id, 'values')
            eccodes.codes_release(grib_id)
        with open(path['base'] + path['grid'] + filenames['lon'],'rb') as file:
            grib_id = eccodes.codes_grib_new_from_file(file)
            clon = eccodes.codes_get_array(grib_id, 'values')
            eccodes.codes_release(grib_id)
            #np.where(clon < 0.0, 360.0 - clon, clon)
    else:
        mpi_file = nc.Dataset(path['base'] + path['grid'] + filenames['cells'], 'r')
        vlat = mpi_file.variables['clat_vertices'][:].data * 180./np.pi
        vlon = mpi_file.variables['clon_vertices'][:].data * 180./np.pi
        clat = mpi_file.variables['clat'][:].data * 180./np.pi
        clon = mpi_file.variables['clon'][:].data * 180./np.pi
        mpi_file.close()

    with open(path['base'] + path['data'] + filenames['landsea_fr'],'rb') as file:
        grib_id = eccodes.codes_grib_new_from_file(file)
        fr_land = eccodes.codes_get_array(grib_id, 'values')
        eccodes.codes_release(grib_id)

    if model == 'icon-eu-det':
        clon = np.reshape(clon,(1097, 657),'F')
        clat = np.reshape(clat,(1097, 657),'F')
        fr_land = np.reshape(fr_land,(1097, 657),'F')

    ########################################################################

    x_resolution        = 770
    y_resolution        = 770
    wks_res             = Ngl.Resources()
    wks_res.wkWidth     = x_resolution
    wks_res.wkHeight    = y_resolution

    wks_type    = 'png'
    wks         = Ngl.open_wks(wks_type, path['base'] + path['plots'] + plot_name, wks_res)
    resources   = Ngl.Resources()

    resources.mpProjection = 'Hammer'
    resources.mpCenterLonF = point_grid['lon']
    resources.mpCenterLatF = point_grid['lat']

    if model == 'icon-eu-det' or model == 'icon-global-det':
        radius = 100    # image radius in km around centered point
    else:
        radius = 200    # image radius in km around centered point

    cutout_plot = dict(
                        lat_min = point_grid['lat'] - radius / 111.2,
                        lat_max = point_grid['lat'] + radius / 111.2,
                        lon_min = point_grid['lon'] - radius / (111.2 * np.cos(point_grid['lat']*np.pi/180)),
                        lon_max = point_grid['lon'] + radius / (111.2 * np.cos(point_grid['lat']*np.pi/180)),
                       )

    resources.mpLimitMode   = 'latlon'
    resources.mpMinLonF     = cutout_plot['lon_min']
    resources.mpMaxLonF     = cutout_plot['lon_max']
    resources.mpMinLatF     = cutout_plot['lat_min']
    resources.mpMaxLatF     = cutout_plot['lat_max']

    resources.nglMaximize   = False
    resources.vpXF          = 0.05
    resources.vpYF          = 0.95
    resources.vpWidthF      = 0.7
    resources.vpHeightF     = 0.7

    ########################################################################

    # Turn on filled map areas:
    resources.mpFillOn = True

    # Set colors for [FillValue, Ocean, Land , InlandWater]:
    resources.mpFillColors = ['pink','blue','white','blue']

    resources.mpDataBaseVersion         = 'MediumRes'
    resources.mpDataSetName             = 'Earth..4'
    resources.mpOutlineBoundarySets     = 'national'

    resources.mpGeophysicalLineThicknessF   = 7.0 * x_resolution / 1000
    resources.mpNationalLineThicknessF      = 7.0 * x_resolution / 1000
    #resources.mpGridAndLimbDrawOrder        = 'postdraw'

    resources.mpGridAndLimbOn               = False
    #resources.mpLimbLineColor               = 'black'
    #resources.mpLimbLineThicknessF          = 10
    #resources.mpGridLineColor               = 'black'
    #resources.mpGridLineThicknessF          = 1.0
    #resources.mpGridSpacingF                = 1

    resources.mpPerimOn                     = True
    resources.mpPerimLineColor              = 'black'
    resources.mpPerimLineThicknessF         = 8.0 * x_resolution / 1000

    resources.tmXBOn = False
    resources.tmXTOn = False
    resources.tmYLOn = False
    resources.tmYROn = False

    resources.sfDataArray       = 1.0 - fr_land
    resources.sfXArray          = clon
    resources.sfYArray          = clat
    resources.sfMissingValueV   = 9999
    if model != 'icon-eu-det':
        resources.sfXCellBounds     = vlon
        resources.sfYCellBounds     = vlat

    resources.cnFillOn              = True
    if model == 'icon-eu-det':
        resources.cnFillMode            = 'RasterFill'
        resources.cnRasterSampleFactorF = 0.0
    else:
        resources.cnFillMode            = 'CellFill'
        resources.cnCellFillEdgeColor   = 'black'

    resources.cnMissingValFillColor = 'black'
    resources.cnFillPalette         = 'MPL_GnBu'
    resources.cnLevelSelectionMode  = 'ManualLevels'

    minlevel                        = 0.0
    maxlevel                        = 1.0
    numberoflevels                  = 250
    resources.cnMinLevelValF        = minlevel
    resources.cnMaxLevelValF        = maxlevel
    resources.cnLevelSpacingF       = (maxlevel - minlevel) / numberoflevels

    # Turn off contour lines and labels:
    resources.cnLinesOn         = False
    resources.cnLineLabelsOn    = False

    # Set resources for a nice label bar
    resources.lbLabelBarOn          = True
    resources.lbAutoManage          = False
    resources.lbOrientation         = 'vertical'
    resources.lbLabelOffsetF        = 0.05
    #resources.lbBoxMinorExtentF     = 0.2

    resources.lbLabelStride         = 125
    resources.lbLabelFontHeightF    = 0.02
    resources.lbBoxSeparatorLinesOn = False
    resources.lbBoxLineThicknessF   = 4.0
    #resources.lbBoxEndCapStyle     = 'TriangleBothEnds'
    resources.lbLabelAlignment      = 'BoxCenters'

    resources.lbTitleString         = '0 = Land    1 = Sea'
    resources.lbTitleFontHeightF    = 0.02
    resources.lbTitlePosition       = 'Right'
    resources.lbTitleDirection      = 'Across'
    resources.lbTitleAngleF         = 90.0
    resources.lbTitleExtentF        = 0.1
    resources.lbTitleOffsetF        = 0.0

    resources.nglFrame = False
    plot = Ngl.contour_map(wks, 1.0-fr_land, resources)

    ########################################################################

    text = 'Ocean+Lake Fraction'
    x = 0.1
    y = 0.02

    text_res_1 = Ngl.Resources()
    text_res_1.txFontHeightF    = 0.03
    text_res_1.txJust           = 'BottomLeft'

    Ngl.text_ndc(wks, text, x, y, text_res_1)

    ########################################################################

    text = 'Point Information about {}'.format(pointname.replace('_', ' '))

    x = 0.02
    y = 0.14

    text_res_2 = Ngl.Resources()
    text_res_2.txFontHeightF    = 0.032
    text_res_2.txJust           = 'BottomLeft'

    Ngl.text_ndc(wks, text, x, y, text_res_2)

    ########################################################################

    filter_distance = get_latlon_filter_distance(model)

    if model == 'icon-eu-det':
        lat_near = list(np.where(abs(clat.flatten('F') - point_grid['lat']) < filter_distance)[0])
        lon_near = list(np.where(abs(clon.flatten('F') - point_grid['lon']) < filter_distance)[0])
        id_near = list(set(lat_near).intersection(lon_near))
        id_near.sort()
        distances = np.sqrt( np.square(abs(clat.flatten('F')[id_near] - point_grid['lat']) * 111.2) \
                            + np.square(abs(clon.flatten('F')[id_near] - point_grid['lon']) * 111.2 \
                                                     * np.cos(point_grid['lat']*np.pi/180)) )
        index_nearest = id_near[np.argmin(distances)]

        linelats = np.zeros(5)
        linelats[0] = clat.flatten('F')[index_nearest] + 0.03125
        linelats[1] = clat.flatten('F')[index_nearest] + 0.03125
        linelats[2] = clat.flatten('F')[index_nearest] - 0.03125
        linelats[3] = clat.flatten('F')[index_nearest] - 0.03125
        linelats[4] = linelats[0]    # end point is start point
        linelons = np.zeros(5)
        linelons[0] = clon.flatten('F')[index_nearest] - 0.03125
        linelons[1] = clon.flatten('F')[index_nearest] + 0.03125
        linelons[2] = clon.flatten('F')[index_nearest] + 0.03125
        linelons[3] = clon.flatten('F')[index_nearest] - 0.03125
        linelons[4] = linelons[0]    # end point is start point

        polyline_res = Ngl.Resources()
        polyline_res.gsLineColor         = 'red'
        polyline_res.gsLineThicknessF    = 4.0
        Ngl.polyline(wks, plot, linelons, linelats, polyline_res)

    else:
        lat_near = list(np.where(abs(clat - point_grid['lat']) < filter_distance)[0])
        lon_near = list(np.where(abs(clon - point_grid['lon']) < filter_distance)[0])
        id_near = list(set(lat_near).intersection(lon_near))
        id_near.sort()
        distances = np.sqrt( np.square(abs(clat[id_near] - point_grid['lat']) * 111.2) \
                            + np.square(abs(clon[id_near] - point_grid['lon']) * 111.2 \
                                                     * np.cos(point_grid['lat']*np.pi/180)) )
        index_nearest = id_near[np.argmin(distances)]

        linelats = np.zeros(4)
        linelats[:3] = vlat[index_nearest]
        linelats[3] = vlat[index_nearest][0]    # end point is start point
        linelons = np.zeros(4)
        linelons[:3] = vlon[index_nearest]
        linelons[3] = vlon[index_nearest][0]

        polyline_res = Ngl.Resources()
        polyline_res.gsLineColor         = 'red'
        polyline_res.gsLineThicknessF    = 6.0
        Ngl.polyline(wks, plot, linelons, linelats, polyline_res)

    ########################################################################

    polymarker_res_1 = Ngl.Resources()
    polymarker_res_1.gsMarkerColor = 'black'
    polymarker_res_1.gsMarkerIndex = 16
    polymarker_res_1.gsMarkerSizeF = 0.015
    polymarker_res_1.gsMarkerThicknessF = 1
    Ngl.polymarker(wks, plot, point_city['lon'], point_city['lat'], polymarker_res_1)

    ########################################################################

    polymarker_res_2 = Ngl.Resources()
    polymarker_res_2.gsMarkerColor = 'white'
    polymarker_res_2.gsMarkerIndex = 16
    polymarker_res_2.gsMarkerSizeF = 0.010
    polymarker_res_2.gsMarkerThicknessF = 1
    Ngl.polymarker(wks, plot, point_city['lon'], point_city['lat'], polymarker_res_2)

    ########################################################################

    Ngl.frame(wks)

    del plot, wks_res, resources, polymarker_res_1, polymarker_res_2, text_res_1, text_res_2, clat, clon
    if model != 'icon-eu-det':
        del vlon, vlat, mpi_file
    Ngl.destroy(wks)

    plot_name += '.png'
    return plot_name

########################################################################
########################################################################
########################################################################

