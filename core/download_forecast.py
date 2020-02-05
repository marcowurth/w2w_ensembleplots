#########################################
###  container for various functions  ###
#########################################

import requests
import bz2
import os
import fnmatch
import datetime
import numpy as np
import xarray as xr


########################################################################
########################################################################
########################################################################

def download(url, filename, path):
    r = requests.get(url + filename, timeout=10)
    with open(path['base'] + path['subdir'] + filename, 'wb') as file:
        file.write(r.content)
    return 1

########################################################################
########################################################################
########################################################################

def unzip(path, filename):
    newfilename = filename[:-4]     # cut file ending
    with open(path['base'] + path['subdir'] + newfilename, 'wb') as unzippedfile:
        with open(path['base'] + path['subdir'] + filename, 'rb') as zippedfile:
            decompressor = bz2.BZ2Decompressor()
            for datapart in iter(lambda : zippedfile.read(100 * 1024), b''):
                try:
                    unzippedfile.write(decompressor.decompress(datapart))
                except OSError:
                    try:
                        unzippedfile.write(decompressor.decompress(datapart))
                    except OSError:
                        unzippedfile.write(decompressor.decompress(datapart))

    os.remove(path['base'] + path['subdir'] + filename)
    return newfilename

########################################################################
########################################################################
########################################################################

def convert_gribfiles_to_one_netcdf(path, grib_filename, netcdf_filename):
    ds = xr.open_mfdataset(path['base'] + path['subdir'] + grib_filename, engine='cfgrib',
                           combine='nested', concat_dim='step', parallel=False, backend_kwargs={'errors': 'ignore'})
    ds.to_netcdf(path['base'] + path['subdir'] + netcdf_filename)
    ds.close()
    del ds

    for idx_filename in fnmatch.filter(os.listdir(path['base'] + path['subdir']), '*.idx'):
        os.remove(path['base'] + path['subdir'] + idx_filename)
    return

########################################################################
########################################################################
########################################################################

def calc_latest_run_time(model):

    # keep always on track with dwd full update times #

    if model == 'icon-eu-eps':
        update_times_utc = [4+30/60, 9+49/60, 16+30/60, 21+49/60]
    elif model == 'icon-global-eps':
        update_times_utc = [4+24/60, 16+24/60]
    elif model == 'icon-eu-det':
        update_times_utc = [3+47/60, 9+41/60, 15+47/60, 21+41/60]
    elif model == 'icon-global-det':
        update_times_utc = [3+38/60, 15+38/60]


    datenow  = datetime.datetime.now().date()
    timenow  = datetime.datetime.now().time()
    run_year  = datenow.year
    run_month = datenow.month
    run_day   = datenow.day
    run_time_float = timenow.hour + timenow.minute / 60

    timeshift = get_timeshift()
    update_times_localtime = np.array(update_times_utc) + timeshift
    
    if len(update_times_utc) == 2:
        if   run_time_float >= update_times_localtime[0] and run_time_float < update_times_localtime[1]: run_hour = 0
        elif run_time_float >= update_times_localtime[1]  or run_time_float < update_times_localtime[0]: run_hour = 12
        else: exit()
    elif len(update_times_utc) == 4:
        if   run_time_float >= update_times_localtime[0] and run_time_float < update_times_localtime[1]: run_hour = 0
        elif run_time_float >= update_times_localtime[1] and run_time_float < update_times_localtime[2]: run_hour = 6
        elif run_time_float >= update_times_localtime[2] and run_time_float < update_times_localtime[3]: run_hour = 12
        elif run_time_float >= update_times_localtime[3]  or run_time_float < update_times_localtime[0]: run_hour = 18
        else: exit()

    if run_time_float < update_times_localtime[0]:
        run_year, run_month, run_day = go_back_one_day(run_year, run_month, run_day)

    date = dict(year = run_year, month = run_month, day = run_day, hour = run_hour)
    return date

########################################################################
########################################################################
########################################################################

def go_back_one_day(run_year, run_month, run_day):
    if run_day >= 2: run_day -= 1
    else:
        # run_day is 1
        if run_year % 4 == 0:
            # schaltjahre/leap years being considered
            days_of_month = [31,29,31,30,31,30,31,31,30,31,30,31]
        else:
            days_of_month = [31,28,31,30,31,30,31,31,30,31,30,31]
        if run_month >= 2:
            run_month -= 1
            run_day = days_of_month[run_month-1]
        else:
            # run_month is 1
            run_year -= 1
            run_month = 12
            run_day = days_of_month[run_month-1]

    return run_year, run_month, run_day
    
########################################################################
########################################################################
########################################################################

def get_timeshift():
    datenow  = datetime.datetime.now()
    dayofyear_now = (datenow-datetime.datetime(datenow.year,1,1)).days + 1

    #                     2019    2020    2021    2022    2023
    changedate_spring = [[3, 31],[3, 29],[3, 28],[3, 27],[3, 26]]
    changedate_autumn = [[10,27],[10,25],[10,31],[10,30],[10,29]]
    year_index = datenow.year - 2019
    date_spring = datetime.datetime(datenow.year, changedate_spring[year_index][0],
                                    changedate_spring[year_index][1], 0, 0)
    dayofyear_spring = (date_spring - datetime.datetime(datenow.year,1,1)).days + 1
    date_autumn = datetime.datetime(datenow.year, changedate_autumn[year_index][0],
                                    changedate_autumn[year_index][1], 0, 0)
    dayofyear_autumn = (date_autumn - datetime.datetime(datenow.year,1,1)).days + 1

    if dayofyear_now >= dayofyear_spring and dayofyear_now < dayofyear_autumn:
        timeshift = 2
    else:
        timeshift = 1

    return timeshift

########################################################################
########################################################################
########################################################################

