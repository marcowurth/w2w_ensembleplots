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
                        centerlat = 50, centerlon = 13, radius = 2200, text_y = 0.837)

    elif domain_name == 'EU-Nest_latlon':
        domain =   dict(name = domain_name, plot_width = 1200, projection = 'CylindricalEquidistant',
                        limits_type = 'deltalatlon',
                        centerlat = 50, centerlon = 19.5, deltalat_deg = 20.5, deltalon_deg = 43, text_y = 0.837)

    elif domain_name == 'central_europe':
        domain =   dict(name = domain_name, plot_width = 800, projection = 'Hammer', limits_type = 'radius',
                        centerlat = 50, centerlon = 8, radius = 1000, text_y = 0.875)

    elif domain_name == 'europe':
        domain =   dict(name = domain_name, plot_width = 800, projection = 'Hammer', limits_type = 'radius',
                        centerlat = 48, centerlon = 9, radius = 1400, text_y = 0.865)

    elif domain_name == 'europe_and_north_atlantic':
        domain =   dict(name = domain_name, plot_width = 800, projection = 'Hammer', limits_type = 'radius',
                        centerlat = 50, centerlon = -15, radius = 2400, text_y = 0.83)

    elif domain_name == 'mediterranean':
        domain =   dict(name = domain_name, plot_width = 1200, projection = 'CylindricalEquidistant',
                        limits_type = 'deltalatlon',
                        centerlat = 37, centerlon = 13.5, deltalat_deg = 11, deltalon_deg = 24.5, text_y = 0.705)

    elif domain_name == 'north_america':
        domain =   dict(name = domain_name, plot_width = 800, projection = 'Hammer', limits_type = 'radius',
                        centerlat = 42, centerlon = -96, radius = 2100, text_y = 0.860)

    elif domain_name == 'southern_south_america':
        domain =   dict(name = domain_name, plot_width = 800, projection = 'Hammer', limits_type = 'radius',
                        centerlat = -34, centerlon = -66, radius = 1900, text_y = 0.885)

    elif domain_name == 'eastern_asia':
        domain =   dict(name = domain_name, plot_width = 800, projection = 'Hammer', limits_type = 'radius',
                        centerlat = 30, centerlon = 118, radius = 2100, text_y = 0.885)

    elif domain_name == 'west_africa':
        domain =   dict(name = domain_name, plot_width = 800, projection = 'Hammer', limits_type = 'radius',
                        centerlat = 9, centerlon = -4.5, radius = 2300, text_y = 0.925)

    elif domain_name == 'east_africa':
        domain =   dict(name = domain_name, plot_width = 800, projection = 'Hammer', limits_type = 'radius',
                        centerlat = 9, centerlon = 34.5, radius = 2300, text_y = 0.925)

    elif domain_name == 'southern_africa':
        domain =   dict(name = domain_name, plot_width = 800, projection = 'Hammer', limits_type = 'radius',
                        centerlat = -26, centerlon = 28, radius = 2300, text_y = 0.885)

    elif domain_name == 'northern_pacific':
        domain =   dict(name = domain_name, plot_width = 800, projection = 'Hammer', limits_type = 'radius',
                        centerlat = 48, centerlon = -171, radius = 1400)

    elif domain_name == 'north_pole':
        domain =   dict(name = domain_name, plot_width = 800, projection = 'Stereographic', limits_type = 'angle',
                        centerlat = 90, centerlon = 0, angle = 60, text_y = 0.93)

    elif domain_name == 'south_pole':
        domain =   dict(name = domain_name, plot_width = 800, projection = 'Stereographic', limits_type = 'angle',
                        centerlat = -90, centerlon = 0, angle = 60, text_y = 0.93)

    elif domain_name == 'atlantic_hurricane_basin':
        domain =   dict(name = domain_name, plot_width = 1200, projection = 'CylindricalEquidistant',
                        limits_type = 'deltalatlon',
                        centerlat = 20, centerlon = -55, deltalat_deg = 20, deltalon_deg = 50, text_y = 0.665)

    else:
        print('domain not known:', domain_name)
        exit()

    return domain

