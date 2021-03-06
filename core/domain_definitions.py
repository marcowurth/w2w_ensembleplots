#########################################
###  container for various functions  ###
#########################################

# types of domain limit specifications:
#
# radius: define coordinates of domain center
#         + radius in km
# deltalatlon: define coordinates of domain center
#              + distance in lat degrees to the edges
#              + distance in lon degrees to the edges
# angle: define coordinates of domain center
#        + angle on earth with respect to the earth center
#
# in very rectangle and landscape-format domains you should raise the plot_width above the standard 800px
#

def get_domain(domain_name):

    if domain_name == 'EU-Nest':
        domain =   dict(name = domain_name, plot_width = 900, projection = 'Hammer', limits_type = 'radius',
                        centerlat = 50, centerlon = 13, radius = 2200)
    elif domain_name == 'EU-Nest_latlon':
        domain =   dict(name = domain_name, plot_width = 1200, projection = 'CylindricalEquidistant',
                        limits_type = 'deltalatlon',
                        centerlat = 50, centerlon = 19.5, deltalat_deg = 20.5, deltalon_deg = 43)
    elif domain_name == 'europe':
        domain =   dict(name = domain_name, plot_width = 800, projection = 'Hammer', limits_type = 'radius',
                        centerlat = 48, centerlon = 9, radius = 1400)
    elif domain_name == 'europe_and_north_atlantic':
        domain =   dict(name = domain_name, plot_width = 800, projection = 'Hammer', limits_type = 'radius',
                        centerlat = 50, centerlon = -15, radius = 2400)
    elif domain_name == 'mediterranean':
        domain =   dict(name = domain_name, plot_width = 1200, projection = 'CylindricalEquidistant',
                        limits_type = 'deltalatlon',
                        centerlat = 38.7, centerlon = 15, deltalat_deg = 8.5, deltalon_deg = 22)
    elif domain_name == 'ionian_sea':
        domain =   dict(name = domain_name, plot_width = 800, projection = 'CylindricalEquidistant',
                        limits_type = 'deltalatlon',
                        centerlat = 36, centerlon = 18.5, deltalat_deg = 6, deltalon_deg = 8)
    elif domain_name == 'north_atlantic_storm':
        domain =   dict(name = domain_name, plot_width = 800, projection = 'Hammer', limits_type = 'radius',
                        centerlat = 41.9, centerlon = -46.1, radius = 300)
    elif domain_name == 'usa':
        domain =   dict(name = domain_name, plot_width = 800, projection = 'Hammer', limits_type = 'radius',
                        centerlat = 37, centerlon = -99, radius = 1900)
    elif domain_name == 'southern_south_america':
        domain =   dict(name = domain_name, plot_width = 800, projection = 'Hammer', limits_type = 'radius',
                        centerlat = -32, centerlon = -66, radius = 1900)
    elif domain_name == 'north_argentina':
        domain =   dict(name = domain_name, plot_width = 800, projection = 'Hammer', limits_type = 'radius',
                        centerlat = -28.0, centerlon = -56.5, radius = 800)
    elif domain_name == 'central_argentina':
        domain =   dict(name = domain_name, plot_width = 800, projection = 'Hammer', limits_type = 'radius',
                        centerlat = -34.6, centerlon = -64.4, radius = 800)
    elif domain_name == 'northern_pacific':
        domain =   dict(name = domain_name, plot_width = 800, projection = 'Hammer', limits_type = 'radius',
                        centerlat = 48, centerlon = -171, radius = 1400)
    elif domain_name == 'north_pole':
        domain =   dict(name = domain_name, plot_width = 800, projection = 'Stereographic', limits_type = 'angle',
                        centerlat = 90, centerlon = 0, angle = 60)
    elif domain_name == 'south_pole':
        domain =   dict(name = domain_name, plot_width = 800, projection = 'Stereographic', limits_type = 'angle',
                        centerlat = -90, centerlon = 0, angle = 60)
    elif domain_name == 'atlantic_hurricane_basin':
        domain =   dict(name = domain_name, plot_width = 1200, projection = 'CylindricalEquidistant',
                        limits_type = 'deltalatlon',
                        centerlat = 20, centerlon = -55, deltalat_deg = 20, deltalon_deg = 50)
    elif domain_name == 'gulf_of_mexico':
        domain =   dict(name = domain_name, plot_width = 800, projection = 'CylindricalEquidistant',
                        limits_type = 'deltalatlon',
                        centerlat = 25, centerlon = -87, deltalat_deg = 8, deltalon_deg = 15)
    else:
        print('domain not known:', domain_name)
        exit()

    return domain

