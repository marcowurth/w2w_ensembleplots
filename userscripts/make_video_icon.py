
import os
import fnmatch

import cv2


def main():

    # settings #

    path = dict(base = '/home/marcowurth/Documents/uni/hiwi/data/',
                plots = 'plots/experimental/deterministic_overview_maps/',
                video = 'videos/deterministic_overview_maps/')

    run = dict(year = 2021, month = 2, day = 24, hour = 0)
    fcst_hours_list = list(range(0,78+1,1))

    model = 'icon-global-det'

    domain_name = 'arg_uru_braz'

    #var1var2 = 'theta_e_850hPa_gph_850hPa'
    var1var2 = 'cape_ml_shear_0-6km'
    #var1var2 = 'prec_rate'


    fps = 6


    # create image array #

    path['plots'] += 'run_{:4d}{:02d}{:02d}{:02d}/{}'.format(
                      run['year'], run['month'], run['day'], run['hour'], var1var2)
    print('adding images...')
    file_list = os.listdir(path['base'] + path['plots'])
    size_taken = False
    img_array = []
    for hour in fcst_hours_list:
        match_string = '{}_{:4d}{:02d}{:02d}{:02d}_{}_{}_{:03d}h*'.format(
                        model, run['year'], run['month'], run['day'], run['hour'], var1var2, domain_name, hour)
        try:
            filename = fnmatch.filter(file_list, match_string)[0]
            print(filename)
            img = cv2.imread(path['base'] + path['plots'] + '/' + filename)
            img_array.append(img)

            if not size_taken:
                height, width, layers = img.shape
                size = (width,height)
                size_taken = True

        except IndexError:
            print('not found, match_string:', match_string)
            print(path['base'] + path['plots'])

    img_array_final = img_array


    # create gif video #

    print('making video...')
    print(len(img_array_final))
    videoname = '{}_{:4d}{:02d}{:02d}{:02d}_{}_{}_{:03d}h-{:03d}h_{:d}.mp4'.format(
                 model, run['year'], run['month'], run['day'], run['hour'], var1var2,
                 domain_name, fcst_hours_list[0], fcst_hours_list[-1], fps)
    fourcc = cv2.VideoWriter_fourcc(*'h264')
    video = cv2.VideoWriter(path['base'] + path['video'] + videoname, fourcc, fps, size)

    for i in range(len(img_array_final)):
        video.write(img_array_final[i])
    video.release()


    return

############################################################################
############################################################################

if __name__ == '__main__':
    import time
    t1 = time.time()
    main()
    t2 = time.time()
    print('total script time:  {:.1f}s'.format(t2-t1))