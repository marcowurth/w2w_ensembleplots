#########################################
###  container for various functions  ###
#########################################


def get_domain(domain_name):

    if domain_name == 'europe':
        domain =   dict(name = domain_name, projection = 'Hammer', limits_type = 'radius',
                        centerlat = 48, centerlon = 9, radius = 1400)
    elif domain_name == 'europe_and_north_atlantic':
        domain =   dict(name = domain_name, projection = 'Hammer', limits_type = 'radius',
                        centerlat = 50, centerlon = -15, radius = 2400)
    elif domain_name == 'usa':
        domain =   dict(name = domain_name, projection = 'Hammer', limits_type = 'radius',
                        centerlat = 37, centerlon = -99, radius = 1900)
    elif domain_name == 'southern_south_america':
        domain =   dict(name = domain_name, projection = 'Hammer', limits_type = 'radius',
                        centerlat = -32, centerlon = -66, radius = 1900)
    elif domain_name == 'northern_pacific':
        domain =   dict(name = domain_name, projection = 'Hammer', limits_type = 'radius',
                        centerlat = 48, centerlon = -171, radius = 1400)
    elif domain_name == 'north_pole':
        domain =   dict(name = domain_name, projection = 'Stereographic', limits_type = 'angle',
                        centerlat = 90, centerlon = 0, angle = 60)
    elif domain_name == 'south_pole':
        domain =   dict(name = domain_name, projection = 'Stereographic', limits_type = 'angle',
                        centerlat = -90, centerlon = 0, angle = 60)
    elif domain_name == 'atlantic_hurricane_basin':
        domain =   dict(name = domain_name, projection = 'CylindricalEquidistant', limits_type = 'deltalatlon',
                        centerlat = 20, centerlon = -55, deltalat_deg = 20, deltalon_deg = 50)
    elif domain_name == 'gulf_of_mexico':
        domain =   dict(name = domain_name, projection = 'CylindricalEquidistant', limits_type = 'deltalatlon',
                        centerlat = 25, centerlon = -87, deltalat_deg = 8, deltalon_deg = 15)
    else:
        print('domain not known:', domain_name)
        exit()

    return domain

