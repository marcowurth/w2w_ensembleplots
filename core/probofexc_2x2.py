
import os
from PIL import Image

import sys
current_path = sys.path[0]
ex_op_str = current_path[current_path.index('scripts')+8 : current_path.index('w2w_ensembleplots')-1]
sys.path.append('/lsdfos/kit/imk-tro/projects/MOD/Gruppe_Knippertz/nw5893/scripts/{}'.format(ex_op_str))
from w2w_ensembleplots.core.download_forecast import calc_latest_run_time


def plot_prob_of_exc_2x2_pointintime(variable, thresholds, title_pos, only_0utc_12utc_runs):

    # set basic paths #

    path = dict(base = '/lsdfos/kit/imk-tro/projects/MOD/Gruppe_Knippertz/nw5893/',
                scripts = 'scripts/operational/w2w_ensembleplots/cronscripts/',
                plots_general = 'plots/operational/prob_of_exc/{}/'.format(variable['name']))
    scriptname = 'callfile_probofexc_2x2_pointintime.py'
    #colormap_name = '_greenblackblue'
    colormap_name = ''


    # automatic time settings #

    run = calc_latest_run_time('icon-eu-eps')
    if only_0utc_12utc_runs:
        if run['hour'] == 6 or run['hour'] == 18:
            run['hour'] -= 6
    #hours = list(range(0, 120+1, 12))
    hours = list(range(0,72,3)) + list(range(72,120+1,6))


    # explicit time settings #

    #run = dict(year = 2019, month = 12, day = 5, hour = 0)

    #hours = list(range(24, 120+1, 24))       # 00Z run
    #hours = list(range(24+18, 120+1, 24))    # 06Z run
    #hours = list(range(24+12, 120+1, 24))    # 12Z run
    #hours = list(range(24+6, 120+1, 24))     # 18Z run
    #hours = [120]


    stat_processing_list = []
    stat_processing_list.append(dict(method = 'prob_of_exc', threshold = thresholds[0]))
    stat_processing_list.append(dict(method = 'prob_of_exc', threshold = thresholds[1]))
    stat_processing_list.append(dict(method = 'prob_of_exc', threshold = thresholds[2]))
    stat_processing_list.append(dict(method = 'prob_of_exc', threshold = thresholds[3]))
    label_text_value = thresholds[4]

    domains = []
    domains.append(dict(method = 'centerpoint', radius = 1400, deltalat =   0, deltalon =   0,
                  lat = 48.0, lon =  9.0, name = 'europe'))
    #domains.append(dict(method = 'deltalatlon', radius =    0, deltalat = 500, deltalon = 550,
    #              lat = 50.8, lon = 10.0, name = 'germany'))


    # make label bar plots #

    domain = dict(method = 'centerpoint', radius = 1400, deltalat =   0, deltalon =   0,
                  lat = 48.0, lon =  9.0, name = 'europe')
    stat_processing = dict(method = 'prob_of_exc', threshold = label_text_value)
    variable['hour'] = 0

    print('plot labelBar1')
    plot_type = 'labelBar1'
    command = 'python {}{}{} '.format(path['base'], path['scripts'], scriptname)
    arguments = '{} {} {:d} {:d} {:d} {:d} {:d} {} {:.2f} {:.2f} {:.2f} {:.2f} {:.2f} {} {} {:.2f} {}'.format(
                variable['name'], variable['unit'], variable['hour'],
                run['year'], run['month'], run['day'], run['hour'],
                domain['method'], domain['radius'], domain['deltalat'], domain['deltalon'],
                domain['lat'], domain['lon'], domain['name'],
                stat_processing['method'], stat_processing['threshold'], plot_type)
    os.system(command + arguments)

    print('plot labelBar2')
    plot_type = 'labelBar2'
    command = 'python {}{}{} '.format(path['base'], path['scripts'], scriptname)
    arguments = '{} {} {:d} {:d} {:d} {:d} {:d} {} {:.2f} {:.2f} {:.2f} {:.2f} {:.2f} {} {} {:.2f} {}'.format(
                variable['name'], variable['unit'], variable['hour'],
                run['year'], run['month'], run['day'], run['hour'],
                domain['method'], domain['radius'], domain['deltalat'], domain['deltalon'],
                domain['lat'], domain['lon'], domain['name'],
                stat_processing['method'], stat_processing['threshold'], plot_type)
    os.system(command + arguments)
    print('---------------------------------------------------')


    # make small map plots #

    for hour in hours:
        variable['hour'] = hour
        for stat_processing in stat_processing_list:
            for domain in domains:
                print('plot {}, {:2d}h, prob_of_exc, {}{}, {}'.format(
                       variable['name'], hour, stat_processing['threshold'], variable['unit'], domain['name']))

                plot_type = 'small_map_only'
                command = 'python {}{}{} '.format(path['base'], path['scripts'], scriptname)
                arguments = '{} {} {:d} {:d} {:d} {:d} {:d} {} {:.2f} {:.2f} {:.2f} {:.2f} {:.2f} {} {} {:.2f} {}'\
                            .format(variable['name'], variable['unit'], variable['hour'],
                            run['year'], run['month'], run['day'], run['hour'],
                            domain['method'], domain['radius'], domain['deltalat'], domain['deltalon'],
                            domain['lat'], domain['lon'], domain['name'],
                            stat_processing['method'], stat_processing['threshold'], plot_type)
                os.system(command + arguments)


        # make plots for time depending texts #

        print('plot text, {:2d}h'.format(hour))
        domain = dict(method = 'centerpoint', radius = 1400, deltalat =   0, deltalon =   0,
                      lat = 48.0, lon =  9.0, name = 'europe')
        stat_processing = dict(method = 'prob_of_exc', threshold = label_text_value)

        plot_type = 'text'
        command = 'python {}{}{} '.format(path['base'], path['scripts'], scriptname)
        arguments = '{} {} {:d} {:d} {:d} {:d} {:d} {} {:.2f} {:.2f} {:.2f} {:.2f} {:.2f} {} {} {:.2f} {}'.format(
                    variable['name'], variable['unit'], variable['hour'],
                    run['year'], run['month'], run['day'], run['hour'],
                    domain['method'], domain['radius'], domain['deltalat'], domain['deltalon'],
                    domain['lat'], domain['lon'], domain['name'],
                    stat_processing['method'], stat_processing['threshold'], plot_type)
        os.system(command + arguments)


        # put all plot parts together #

        path['plots_spec'] = 'run_{:4d}{:02d}{:02d}{:02d}/{}/'.format(run['year'], run['month'], run['day'],
                              run['hour'], domain['name'])
        filenames = dict()
        for i, stat_processing in enumerate(stat_processing_list):
            file_str = 'small_map_plot_{:d}'.format(i+1)
            filenames[file_str] = 'iconeueps_prob_of_exc_{}_{:.0f}{}_{:03d}h_{}_small_map_only.png'.format(
                                   variable['name'], stat_processing['threshold'], variable['unit'], variable['hour'],
                                   domain['name'])
        filenames['labelBar1']  = 'iconeueps_prob_of_exc_{}_{:.0f}{}_000h_europe_labelBar1.png'.format(
                                   variable['name'], label_text_value, variable['unit'])
        filenames['labelBar2']  = 'iconeueps_prob_of_exc_{}_{:.0f}{}_000h_europe_labelBar2.png'.format(
                                   variable['name'], label_text_value, variable['unit'])
        filenames['text']       = 'iconeueps_prob_of_exc_{}_{:.0f}{}_{:03d}h_europe_text.png'.format(
                                   variable['name'], label_text_value, variable['unit'], variable['hour'])
        filenames['finalplot']  = 'iconeueps_prob_of_exc_2x2_{}_{:03d}h_europe{}.png'.format(
                                   variable['name'], variable['hour'], colormap_name)


        img_combined = Image.new('RGB',(750, 935),(255,255,255))

        image_smallmap1 = Image.open(path['base'] + path['plots_general'] + path['plots_spec']\
                                     + filenames['small_map_plot_1'])
        img_combined.paste(image_smallmap1.crop((0, 0, 360, 360)), (10, 80))
        image_smallmap2 = Image.open(path['base'] + path['plots_general'] + path['plots_spec']\
                                     + filenames['small_map_plot_2'])
        img_combined.paste(image_smallmap2.crop((0, 0, 360, 360)), (10+360+10, 80))
        image_smallmap3 = Image.open(path['base'] + path['plots_general'] + path['plots_spec']\
                                     + filenames['small_map_plot_3'])
        img_combined.paste(image_smallmap3.crop((0, 0, 360, 360)), (10, 80+360-15))
        image_smallmap4 = Image.open(path['base'] + path['plots_general'] + path['plots_spec']\
                                     + filenames['small_map_plot_4'])
        img_combined.paste(image_smallmap4.crop((0, 0, 360, 360)), (10+360+10, 80+360-15))


        image_labelbar1a = Image.open(path['base'] + path['plots_general'] + path['plots_spec']\
                                     + filenames['labelBar1'])
        img_combined.paste(image_labelbar1a.crop((25, 610, 775, 630)), (3, 80+360-15+360+13))
        image_labelbar1b = Image.open(path['base'] + path['plots_general'] + path['plots_spec']\
                                     + filenames['labelBar1'])
        img_combined.paste(image_labelbar1b.crop((25, 630, 775, 650)), (3, 80+360-15+360-12))
        image_labelbar2 = Image.open(path['base'] + path['plots_general'] + path['plots_spec']\
                                     + filenames['labelBar2'])
        img_combined.paste(image_labelbar2.crop((25, 575, 775, 650)), (3, 80+360-15+360+29))


        image_title = Image.open(path['base'] + path['plots_general'] + path['plots_spec'] + filenames['text'])
        img_combined.paste(image_title.crop((50, 0, 750, 30)), (title_pos, 0))
        image_text1 = Image.open(path['base'] + path['plots_general'] + path['plots_spec'] + filenames['text'])
        img_combined.paste(image_text1.crop((5, 40, 300, 60)), (3, 45))
        image_text2 = Image.open(path['base'] + path['plots_general'] + path['plots_spec'] + filenames['text'])
        img_combined.paste(image_text2.crop((450, 40, 730, 60)), (460, 45))
        image_text3 = Image.open(path['base'] + path['plots_general'] + path['plots_spec'] + filenames['text'])
        img_combined.paste(image_text3.crop((5, 630, 450, 650)), (3, 80+360-15+360-20+75+70))

        img_combined.save(path['base'] + path['plots_general'] + path['plots_spec']\
                          + filenames['finalplot'],'png')
        print('---------------------------------------------------')


        for i in range(4):
            os.remove(path['base'] + path['plots_general'] + path['plots_spec']\
                      + filenames['small_map_plot_{:d}'.format(i+1)])
        os.remove(path['base'] + path['plots_general'] + path['plots_spec']\
                  + filenames['text'])
    os.remove(path['base'] + path['plots_general'] + path['plots_spec']\
              + filenames['labelBar1'])
    os.remove(path['base'] + path['plots_general'] + path['plots_spec']\
              + filenames['labelBar2'])

    return

#######################################################################################################################
#######################################################################################################################
#######################################################################################################################

def plot_prob_of_exc_2x2_timespan(variable, thresholds, title_pos, only_0utc_12utc_runs):

    # set basic paths #

    path = dict(base = '/lsdfos/kit/imk-tro/projects/MOD/Gruppe_Knippertz/nw5893/',
                scripts = 'scripts/operational/w2w_ensembleplots/cronscripts/',
                plots_general = 'plots/operational/prob_of_exc/{}/'.format(variable['name']))
    scriptname = 'callfile_probofexc_2x2_timespan.py'
    #colormap_name = '_greenblackblue'
    colormap_name = ''


    # automatic time settings #

    run = calc_latest_run_time('icon-eu-eps')
    if run['hour'] == 0:
        hours = list(range(24, 120+1, 24))
    else:
        hours = list(range(48 - run['hour'], 120+1, 24))


    # explicit time settings #

    #run = dict(year = 2019, month = 12, day = 5, hour = 0)

    #hours = list(range(24, 120+1, 24))       # 00Z run
    #hours = list(range(24+18, 120+1, 24))    # 06Z run
    #hours = list(range(24+12, 120+1, 24))    # 12Z run
    #hours = list(range(24+6, 120+1, 24))     # 18Z run
    #hours = [120]


    stat_processing_list = []
    stat_processing_list.append(dict(method = 'prob_of_exc', threshold = thresholds[0]))
    stat_processing_list.append(dict(method = 'prob_of_exc', threshold = thresholds[1]))
    stat_processing_list.append(dict(method = 'prob_of_exc', threshold = thresholds[2]))
    stat_processing_list.append(dict(method = 'prob_of_exc', threshold = thresholds[3]))
    label_text_value = thresholds[4]

    domains = []
    domains.append(dict(method = 'centerpoint', radius = 1400, deltalat =   0, deltalon =   0,
                  lat = 48.0, lon =  9.0, name = 'europe'))
    #domains.append(dict(method = 'deltalatlon', radius =    0, deltalat = 500, deltalon = 550,
    #              lat = 50.8, lon = 10.0, name = 'germany'))


    # make label bar plots #

    domain = dict(method = 'centerpoint', radius = 1400, deltalat =   0, deltalon =   0,
                  lat = 48.0, lon =  9.0, name = 'europe')
    stat_processing = dict(method = 'prob_of_exc', threshold = label_text_value)
    variable['hour_start'] = 0
    variable['hour_end'] = 24

    print('plot labelBar1')
    plot_type = 'labelBar1'
    command = 'python {}{}{} '.format(path['base'], path['scripts'], scriptname)
    arguments = '{} {} {:d} {:d} {:d} {:d} {:d} {:d} {} {:.2f} {:.2f} {:.2f} {:.2f} {:.2f} {} {} {:.2f} {}'.format(
                variable['name'], variable['unit'], variable['hour_start'], variable['hour_end'],
                run['year'], run['month'], run['day'], run['hour'],
                domain['method'], domain['radius'], domain['deltalat'], domain['deltalon'],
                domain['lat'], domain['lon'], domain['name'],
                stat_processing['method'], stat_processing['threshold'], plot_type)
    os.system(command + arguments)

    print('plot labelBar2')
    plot_type = 'labelBar2'
    command = 'python {}{}{} '.format(path['base'], path['scripts'], scriptname)
    arguments = '{} {} {:d} {:d} {:d} {:d} {:d} {:d} {} {:.2f} {:.2f} {:.2f} {:.2f} {:.2f} {} {} {:.2f} {}'.format(
                variable['name'], variable['unit'], variable['hour_start'], variable['hour_end'],
                run['year'], run['month'], run['day'], run['hour'],
                domain['method'], domain['radius'], domain['deltalat'], domain['deltalon'],
                domain['lat'], domain['lon'], domain['name'],
                stat_processing['method'], stat_processing['threshold'], plot_type)
    os.system(command + arguments)
    print('---------------------------------------------------')


    # make small map plots #

    for hour in hours:
        variable['hour_start'] = hour - 24
        variable['hour_end'] = hour
        for stat_processing in stat_processing_list:
            for domain in domains:
                print('plot {}, {:2d}-{:2d}h, prob_of_exc, {}{}, {}'.format(
                       variable['name'], variable['hour_start'], variable['hour_end'],
                       stat_processing['threshold'], variable['unit'], domain['name']))

                plot_type = 'small_map_only'
                command = 'python {}{}{} '.format(path['base'], path['scripts'], scriptname)
                arguments = '{} {} {:d} {:d} {:d} {:d} {:d} {:d} {} {:.2f} {:.2f} {:.2f} {:.2f} {:.2f} {} {} {:.2f} {}'\
                            .format(variable['name'], variable['unit'], variable['hour_start'], variable['hour_end'],
                            run['year'], run['month'], run['day'], run['hour'],
                            domain['method'], domain['radius'], domain['deltalat'], domain['deltalon'],
                            domain['lat'], domain['lon'], domain['name'],
                            stat_processing['method'], stat_processing['threshold'], plot_type)
                os.system(command + arguments)


        # make plots for time depending texts #

        print('plot text, {:2d}h'.format(hour))
        domain = dict(method = 'centerpoint', radius = 1400, deltalat =   0, deltalon =   0,
                      lat = 48.0, lon =  9.0, name = 'europe')
        stat_processing = dict(method = 'prob_of_exc', threshold = label_text_value)

        plot_type = 'text'
        command = 'python {}{}{} '.format(path['base'], path['scripts'], scriptname)
        arguments = '{} {} {:d} {:d} {:d} {:d} {:d} {:d} {} {:.2f} {:.2f} {:.2f} {:.2f} {:.2f} {} {} {:.2f} {}'.format(
                    variable['name'], variable['unit'], variable['hour_start'], variable['hour_end'],
                    run['year'], run['month'], run['day'], run['hour'],
                    domain['method'], domain['radius'], domain['deltalat'], domain['deltalon'],
                    domain['lat'], domain['lon'], domain['name'],
                    stat_processing['method'], stat_processing['threshold'], plot_type)
        os.system(command + arguments)


        # put all plot parts together #

        path['plots_spec'] = 'run_{:4d}{:02d}{:02d}{:02d}/{}/'.format(run['year'], run['month'], run['day'],
                              run['hour'], domain['name'])
        filenames = dict()
        for i, stat_processing in enumerate(stat_processing_list):
            if stat_processing['threshold'] >= 1.0:
                threshold_str = '{:03d}'.format(int(stat_processing['threshold']))
            else:
                threshold_str = '{:.1f}'.format(stat_processing['threshold'])
            file_str = 'small_map_plot_{:d}'.format(i+1)
            filenames[file_str] = 'iconeueps_prob_of_exc_{}_{}{}_{:03d}-{:03d}h_{}_small_map_only.png'.format(
                                   variable['name'], threshold_str, variable['unit'],
                                   variable['hour_start'], variable['hour_end'], domain['name'])
        filenames['labelBar1']  = 'iconeueps_prob_of_exc_{}_{:.1f}{}_000-024h_europe_labelBar1.png'.format(
                                   variable['name'], label_text_value, variable['unit'])
        filenames['labelBar2']  = 'iconeueps_prob_of_exc_{}_{:.1f}{}_000-024h_europe_labelBar2.png'.format(
                                   variable['name'], label_text_value, variable['unit'])
        filenames['text']       = 'iconeueps_prob_of_exc_{}_{:.1f}{}_{:03d}-{:03d}h_europe_text.png'.format(
                                   variable['name'], label_text_value, variable['unit'],
                                   variable['hour_start'], variable['hour_end'])
        filenames['finalplot']  = 'iconeueps_prob_of_exc_2x2_{}_{:03d}-{:03d}h_europe{}.png'.format(
                                   variable['name'], variable['hour_start'], variable['hour_end'], colormap_name)


        img_combined = Image.new('RGB',(750, 935),(255,255,255))

        image_smallmap1 = Image.open(path['base'] + path['plots_general'] + path['plots_spec']\
                                     + filenames['small_map_plot_1'])
        img_combined.paste(image_smallmap1.crop((0, 0, 360, 360)), (10, 80))
        image_smallmap2 = Image.open(path['base'] + path['plots_general'] + path['plots_spec']\
                                     + filenames['small_map_plot_2'])
        img_combined.paste(image_smallmap2.crop((0, 0, 360, 360)), (10+360+10, 80))
        image_smallmap3 = Image.open(path['base'] + path['plots_general'] + path['plots_spec']\
                                     + filenames['small_map_plot_3'])
        img_combined.paste(image_smallmap3.crop((0, 0, 360, 360)), (10, 80+360-15))
        image_smallmap4 = Image.open(path['base'] + path['plots_general'] + path['plots_spec']\
                                     + filenames['small_map_plot_4'])
        img_combined.paste(image_smallmap4.crop((0, 0, 360, 360)), (10+360+10, 80+360-15))


        image_labelbar1a = Image.open(path['base'] + path['plots_general'] + path['plots_spec']\
                                     + filenames['labelBar1'])
        img_combined.paste(image_labelbar1a.crop((25, 610, 775, 630)), (3, 80+360-15+360+13))
        image_labelbar1b = Image.open(path['base'] + path['plots_general'] + path['plots_spec']\
                                     + filenames['labelBar1'])
        img_combined.paste(image_labelbar1b.crop((25, 630, 775, 650)), (3, 80+360-15+360-12))
        image_labelbar2 = Image.open(path['base'] + path['plots_general'] + path['plots_spec']\
                                     + filenames['labelBar2'])
        img_combined.paste(image_labelbar2.crop((25, 575, 775, 650)), (3, 80+360-15+360+29))


        image_title = Image.open(path['base'] + path['plots_general'] + path['plots_spec'] + filenames['text'])
        img_combined.paste(image_title.crop((50, 0, 750, 30)), (title_pos, 0))
        image_text1 = Image.open(path['base'] + path['plots_general'] + path['plots_spec'] + filenames['text'])
        img_combined.paste(image_text1.crop((5, 40, 300, 60)), (3, 45))
        image_text2 = Image.open(path['base'] + path['plots_general'] + path['plots_spec'] + filenames['text'])
        img_combined.paste(image_text2.crop((450, 40, 730, 60)), (460, 45))
        image_text3 = Image.open(path['base'] + path['plots_general'] + path['plots_spec'] + filenames['text'])
        img_combined.paste(image_text3.crop((5, 630, 450, 650)), (3, 80+360-15+360-20+75+70))

        img_combined.save(path['base'] + path['plots_general'] + path['plots_spec']\
                          + filenames['finalplot'],'png')
        print('---------------------------------------------------')


        for i in range(4):
            os.remove(path['base'] + path['plots_general'] + path['plots_spec']\
                      + filenames['small_map_plot_{:d}'.format(i+1)])
        os.remove(path['base'] + path['plots_general'] + path['plots_spec']\
                  + filenames['text'])
    os.remove(path['base'] + path['plots_general'] + path['plots_spec']\
              + filenames['labelBar1'])
    os.remove(path['base'] + path['plots_general'] + path['plots_spec']\
              + filenames['labelBar2'])

    return
