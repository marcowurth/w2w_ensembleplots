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

    elif domain_name == 'europe':
        domain =   dict(name = domain_name, plot_width = 800, projection = 'Hammer', limits_type = 'radius',
                        centerlat = 48, centerlon = 9, radius = 1400, text_y = 0.865)

    elif domain_name == 'europe_and_north_atlantic':
        domain =   dict(name = domain_name, plot_width = 800, projection = 'Hammer', limits_type = 'radius',
                        centerlat = 50, centerlon = -15, radius = 2400, text_y = 0.83)

    elif domain_name == 'mediterranean':
        domain =   dict(name = domain_name, plot_width = 1200, projection = 'CylindricalEquidistant',
                        limits_type = 'deltalatlon',
                        centerlat = 37.2, centerlon = 15, deltalat_deg = 10, deltalon_deg = 22, text_y = 0.710)

    elif domain_name == 'conus':
        domain =   dict(name = domain_name, plot_width = 800, projection = 'Hammer', limits_type = 'radius',
                        centerlat = 37, centerlon = -96, radius = 2100, text_y = 0.870)

    elif domain_name == 'texas':
        domain =   dict(name = domain_name, plot_width = 800, projection = 'Hammer', limits_type = 'radius',
                        centerlat = 31, centerlon = -99, radius = 600, text_y = 0.880)

    elif domain_name == 'north_america':
        domain =   dict(name = domain_name, plot_width = 800, projection = 'Hammer', limits_type = 'radius',
                        centerlat = 42, centerlon = -96, radius = 2100, text_y = 0.860)

    elif domain_name == 'southern_south_america':
        domain =   dict(name = domain_name, plot_width = 800, projection = 'Hammer', limits_type = 'radius',
                        centerlat = -34, centerlon = -66, radius = 1900, text_y = 0.885)

    elif domain_name == 'patagonia_cyclone':
        domain =   dict(name = domain_name, plot_width = 800, projection = 'Hammer', limits_type = 'radius',
                        centerlat = -43, centerlon = -60, radius = 800, text_y = 0.885)

    elif domain_name == 'southern_south_america_old':
        domain =   dict(name = domain_name, plot_width = 800, projection = 'Hammer', limits_type = 'radius',
                        centerlat = -32, centerlon = -66, radius = 1900, text_y = 0.885)

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

    elif domain_name == 'argentina_central':
        domain =   dict(name = domain_name, plot_width = 800, projection = 'Hammer', limits_type = 'radius',
                        centerlat = -34.6, centerlon = -64.4, radius = 800, text_y = 0.905)

    elif domain_name == 'arg_uru_braz':
        domain =   dict(name = domain_name, plot_width = 800, projection = 'Hammer', limits_type = 'radius',
                        centerlat = -32.5, centerlon = -61.0, radius = 1000, text_y = 0.905)

    elif domain_name == 'argentina_central_cerca':
        domain =   dict(name = domain_name, plot_width = 800, projection = 'Hammer', limits_type = 'radius',
                        centerlat = -36.0, centerlon = -66.0, radius = 500, text_y = 0.905)

    elif domain_name == 'north_west_australia':
        domain =   dict(name = domain_name, plot_width = 800, projection = 'Hammer', limits_type = 'radius',
                        centerlat = -21.0, centerlon = 120.0, radius = 800, text_y = 0.905)

    else:
        print('domain not known:', domain_name)
        exit()

    return domain

