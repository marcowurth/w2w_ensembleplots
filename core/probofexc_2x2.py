
import os
from PIL import Image

import sys
current_path = sys.path[0]
ex_op_str = current_path[current_path.index('scripts')+8 : current_path.index('w2w_ensembleplots')-1]
sys.path.append('/lsdfos/kit/imk-tro/projects/MOD/Gruppe_Knippertz/nw5893/scripts/{}'.format(ex_op_str))
from w2w_ensembleplots.core.download_forecast import calc_latest_run_time


def plot_prob_of_exc_2x2_pointintime(variable, thresholds, domains, model, title_pos, only_0utc_12utc_runs):

    # set basic paths #

    path = dict(base = '/lsdfos/kit/imk-tro/projects/MOD/Gruppe_Knippertz/nw5893/',
                scripts = 'scripts/operational/w2w_ensembleplots/cronscripts/',
                plots_general = 'plots/operational/prob_of_exc/{}/'.format(variable['name']))
    scriptname = 'callfile_probofexc_2x2_pointintime.py'
    #colormap_name = '_greenblackblue'
    colormap_name = ''

    if variable['name'] == 'acc_prec':
        if thresholds[0] < 30.0:
            colormap_name = '_low'
        else:
            colormap_name = '_high'

    # automatic time settings #

    run = calc_latest_run_time('icon-eu-eps')
    if only_0utc_12utc_runs:
        if run['hour'] == 6 or run['hour'] == 18:
            run['hour'] -= 6

    if model == 'icon-eu-eps':
        #hours = list(range(0, 120+1, 12))
        hours = list(range(0,72,3)) + list(range(72,120+1,6))
    elif model == 'icon-global-eps':
        #hours = list(range(0,72,3)) + list(range(72,120,6)) + list(range(120,180+1,12))
        if variable['name'] == 'acc_prec':
            hours = list(range(12,180+1,12))
        else:
            hours = list(range(0,180+1,12))


    # explicit time settings #

    #run = dict(year = 2019, month = 12, day = 25, hour = 0)

    #hours = list(range(24, 120+1, 24))       # 00Z run
    #hours = list(range(24+18, 120+1, 24))    # 06Z run
    #hours = list(range(24+12, 120+1, 24))    # 12Z run
    #hours = list(range(24+6, 120+1, 24))     # 18Z run
    #hours = [180]


    stat_processing_list = []
    stat_processing_list.append(dict(method = 'prob_of_exc', threshold = thresholds[0]))
    stat_processing_list.append(dict(method = 'prob_of_exc', threshold = thresholds[1]))
    stat_processing_list.append(dict(method = 'prob_of_exc', threshold = thresholds[2]))
    stat_processing_list.append(dict(method = 'prob_of_exc', threshold = thresholds[3]))
    label_text_value = thresholds[4]


    # make label bar plots #

    domain = domains[0]
    stat_processing = dict(method = 'prob_of_exc', threshold = label_text_value)
    variable['hour'] = 0

    print('plot labelBar1')
    plot_type = 'labelBar1'
    command = 'python {}{}{} '.format(path['base'], path['scripts'], scriptname)
    arguments = '{} {} {:d} {:d} {:d} {:d} {:d} {} {:.2f} {:.2f} {:.2f} {:.2f} {:.2f} {} {} {} {:.2f} {}'.format(
                variable['name'], variable['unit'], variable['hour'],
                run['year'], run['month'], run['day'], run['hour'],
                domain['method'], domain['radius'], domain['deltalat'], domain['deltalon'],
                domain['lat'], domain['lon'], domain['name'], model,
                stat_processing['method'], stat_processing['threshold'], plot_type)
    os.system(command + arguments)

    print('plot labelBar2')
    plot_type = 'labelBar2'
    command = 'python {}{}{} '.format(path['base'], path['scripts'], scriptname)
    arguments = '{} {} {:d} {:d} {:d} {:d} {:d} {} {:.2f} {:.2f} {:.2f} {:.2f} {:.2f} {} {} {} {:.2f} {}'.format(
                variable['name'], variable['unit'], variable['hour'],
                run['year'], run['month'], run['day'], run['hour'],
                domain['method'], domain['radius'], domain['deltalat'], domain['deltalon'],
                domain['lat'], domain['lon'], domain['name'], model,
                stat_processing['method'], stat_processing['threshold'], plot_type)
    os.system(command + arguments)
    print('---------------------------------------------------')


    # make small map plots #

    for hour in hours:
        variable['hour'] = hour
        for stat_processing in stat_processing_list:
            for domain in domains:
                print('plot {}, {:d}h, prob_of_exc, {}{}, {}'.format(
                       variable['name'], hour, stat_processing['threshold'], variable['unit'], domain['name']))

                plot_type = 'small_map_only'
                command = 'python {}{}{} '.format(path['base'], path['scripts'], scriptname)
                arguments = '{} {} {:d} {:d} {:d} {:d} {:d} {} {:.2f} {:.2f} {:.2f} {:.2f} {:.2f} {} {} {} {:.2f} {}'\
                            .format(variable['name'], variable['unit'], variable['hour'],
                            run['year'], run['month'], run['day'], run['hour'],
                            domain['method'], domain['radius'], domain['deltalat'], domain['deltalon'],
                            domain['lat'], domain['lon'], domain['name'], model,
                            stat_processing['method'], stat_processing['threshold'], plot_type)
                os.system(command + arguments)


        # make plots for time depending texts #

        print('plot text, {:d}h'.format(hour))
        domain = domains[0]
        stat_processing = dict(method = 'prob_of_exc', threshold = label_text_value)

        plot_type = 'text'
        command = 'python {}{}{} '.format(path['base'], path['scripts'], scriptname)
        arguments = '{} {} {:d} {:d} {:d} {:d} {:d} {} {:.2f} {:.2f} {:.2f} {:.2f} {:.2f} {} {} {} {:.2f} {}'.format(
                    variable['name'], variable['unit'], variable['hour'],
                    run['year'], run['month'], run['day'], run['hour'],
                    domain['method'], domain['radius'], domain['deltalat'], domain['deltalon'],
                    domain['lat'], domain['lon'], domain['name'], model,
                    stat_processing['method'], stat_processing['threshold'], plot_type)
        os.system(command + arguments)


        # put all plot parts together #

        if model == 'icon-eu-eps':
            model_acr = 'iconeueps'
        elif model == 'icon-global-eps':
            model_acr = 'iconglobaleps'

        for domain in domains:
            print('paste together {}, {:d}h, prob_of_exc, {}'.format(
                   variable['name'], variable['hour'], domain['name']))

            path['plots_maps'] = 'run_{:4d}{:02d}{:02d}{:02d}/{}/'.format(run['year'], run['month'], run['day'],
                                  run['hour'], domain['name'])
            path['plots_labelBar_text'] = 'run_{:4d}{:02d}{:02d}{:02d}/{}/'.format(run['year'], run['month'],
                                           run['day'], run['hour'], domains[0]['name'])

            filenames = dict()
            for i, stat_processing in enumerate(stat_processing_list):
                file_str = 'small_map_plot_{:d}'.format(i+1)
                filenames[file_str] = '{}_prob_of_exc_{}_{:.0f}{}_{:03d}h_{}_small_map_only.png'.format(
                                       model_acr, variable['name'], stat_processing['threshold'], variable['unit'],
                                       variable['hour'], domain['name'])
            filenames['labelBar1']  = '{}_prob_of_exc_{}_{:.0f}{}_000h_{}_labelBar1.png'.format(
                                       model_acr, variable['name'], label_text_value, variable['unit'],
                                       domain['name'])
            filenames['labelBar2']  = '{}_prob_of_exc_{}_{:.0f}{}_000h_{}_labelBar2.png'.format(
                                       model_acr, variable['name'], label_text_value, variable['unit'],
                                       domain['name'])
            filenames['text']       = '{}_prob_of_exc_{}_{:.0f}{}_{:03d}h_{}_text.png'.format(
                                       model_acr, variable['name'], label_text_value, variable['unit'],
                                       variable['hour'], domain['name'])
            filenames['finalplot']  = '{}_prob_of_exc_2x2_{}_{:03d}h_{}{}.png'.format(
                                       model_acr, variable['name'], variable['hour'], domain['name'],
                                       colormap_name)


            img_combined = Image.new('RGB',(750, 935),(255,255,255))

            image_smallmap1 = Image.open(path['base'] + path['plots_general'] + path['plots_maps']\
                                         + filenames['small_map_plot_1'])
            img_combined.paste(image_smallmap1.crop((0, 0, 360, 360)), (10, 80))
            image_smallmap2 = Image.open(path['base'] + path['plots_general'] + path['plots_maps']\
                                         + filenames['small_map_plot_2'])
            img_combined.paste(image_smallmap2.crop((0, 0, 360, 360)), (10+360+10, 80))
            image_smallmap3 = Image.open(path['base'] + path['plots_general'] + path['plots_maps']\
                                         + filenames['small_map_plot_3'])
            img_combined.paste(image_smallmap3.crop((0, 0, 360, 360)), (10, 80+360-15))
            image_smallmap4 = Image.open(path['base'] + path['plots_general'] + path['plots_maps']\
                                         + filenames['small_map_plot_4'])
            img_combined.paste(image_smallmap4.crop((0, 0, 360, 360)), (10+360+10, 80+360-15))


            image_labelbar1a = Image.open(path['base'] + path['plots_general'] + path['plots_labelBar_text']\
                                         + filenames['labelBar1'])
            img_combined.paste(image_labelbar1a.crop((25, 610, 775, 630)), (3, 80+360-15+360+13))
            image_labelbar1b = Image.open(path['base'] + path['plots_general'] + path['plots_labelBar_text']\
                                         + filenames['labelBar1'])
            img_combined.paste(image_labelbar1b.crop((25, 630, 775, 650)), (3, 80+360-15+360-12))
            image_labelbar2 = Image.open(path['base'] + path['plots_general'] + path['plots_labelBar_text']\
                                         + filenames['labelBar2'])
            img_combined.paste(image_labelbar2.crop((25, 575, 775, 650)), (3, 80+360-15+360+29))


            image_title = Image.open(path['base'] + path['plots_general'] + path['plots_labelBar_text']
                                     + filenames['text'])
            img_combined.paste(image_title.crop((50, 0, 750, 30)), (title_pos, 0))
            image_initial_time = Image.open(path['base'] + path['plots_general'] + path['plots_labelBar_text']
                                     + filenames['text'])
            img_combined.paste(image_initial_time.crop((5, 40, 300, 60)), (3, 45))
            image_valid_time = Image.open(path['base'] + path['plots_general'] + path['plots_labelBar_text']
                                     + filenames['text'])
            img_combined.paste(image_valid_time.crop((450, 40, 730, 60)), (460, 45))
            image_model = Image.open(path['base'] + path['plots_general'] + path['plots_labelBar_text']
                                     + filenames['text'])
            img_combined.paste(image_model.crop((5, 630, 550, 650)), (3, 80+360-15+360-20+75+70))

            img_combined.save(path['base'] + path['plots_general'] + path['plots_maps']\
                              + filenames['finalplot'],'png')
            print('---------------------------------------------------')


            for i in range(4):
                os.remove(path['base'] + path['plots_general'] + path['plots_maps']\
                          + filenames['small_map_plot_{:d}'.format(i+1)])
        os.remove(path['base'] + path['plots_general'] + path['plots_labelBar_text']\
                  + filenames['text'])
    os.remove(path['base'] + path['plots_general'] + path['plots_labelBar_text']\
              + filenames['labelBar1'])
    os.remove(path['base'] + path['plots_general'] + path['plots_labelBar_text']\
              + filenames['labelBar2'])

    return

#######################################################################################################################
#######################################################################################################################
#######################################################################################################################

def plot_prob_of_exc_2x2_timespan(variable, thresholds, domains, model, title_pos, only_0utc_12utc_runs):

    # set basic paths #

    path = dict(base = '/lsdfos/kit/imk-tro/projects/MOD/Gruppe_Knippertz/nw5893/',
                scripts = 'scripts/operational/w2w_ensembleplots/cronscripts/',
                plots_general = 'plots/operational/prob_of_exc/{}/'.format(variable['name']))
    scriptname = 'callfile_probofexc_2x2_timespan.py'
    #colormap_name = '_greenblackblue'
    colormap_name = ''


    # automatic time settings #

    run = calc_latest_run_time(model)

    if model == 'icon-eu-eps':
        max_hour = 120
    elif model == 'icon-global-eps':
        if variable['name'] == 'tot_prec_24h'\
         or variable['name'] == 'tot_prec_48h':
            max_hour = 180
        elif variable['name'] == 'tot_prec_06h':
            max_hour = 120
        elif variable['name'] == 'tot_prec_03h':
            max_hour = 72
        elif variable['name'] == 'tot_prec_01h':
            max_hour = 48

    timespan = int(variable['name'][-3:-1])

    if variable['name'] == 'tot_prec_24h'\
     or variable['name'] == 'tot_prec_48h':
        if run['hour'] == 0:
            hours = list(range(timespan, max_hour+1, 24))
        else:
            hours = list(range(timespan + 24 - run['hour'], max_hour+1, 24))
    else:
        hours = list(range(timespan, max_hour+1, timespan))


    # explicit time settings #

    #run = dict(year = 2019, month = 12, day = 28, hour = 0)

    #hours = list(range(24, 120+1, 24))       # 00Z run
    #hours = list(range(24+18, 120+1, 24))    # 06Z run
    #hours = list(range(24+12, 120+1, 24))    # 12Z run
    #hours = list(range(24+6, 120+1, 24))     # 18Z run
    #hours = list(range(30, 120+1, 6))
    #hours = [10]


    stat_processing_list = []
    stat_processing_list.append(dict(method = 'prob_of_exc', threshold = thresholds[0]))
    stat_processing_list.append(dict(method = 'prob_of_exc', threshold = thresholds[1]))
    stat_processing_list.append(dict(method = 'prob_of_exc', threshold = thresholds[2]))
    stat_processing_list.append(dict(method = 'prob_of_exc', threshold = thresholds[3]))
    label_text_value = thresholds[4]


    # make label bar plots #

    domain = domains[0]
    stat_processing = dict(method = 'prob_of_exc', threshold = label_text_value)
    variable['hour_start'] = 0
    variable['hour_end'] = timespan

    print('plot labelBar1')
    plot_type = 'labelBar1'
    command = 'python {}{}{} '.format(path['base'], path['scripts'], scriptname)
    arguments = '{} {} {:d} {:d} {:d} {:d} {:d} {:d} {} {:.2f} {:.2f} {:.2f} {:.2f} {:.2f} {} {} {} {:.2f} {}'.format(
                variable['name'], variable['unit'], variable['hour_start'], variable['hour_end'],
                run['year'], run['month'], run['day'], run['hour'],
                domain['method'], domain['radius'], domain['deltalat'], domain['deltalon'],
                domain['lat'], domain['lon'], domain['name'], model,
                stat_processing['method'], stat_processing['threshold'], plot_type)
    os.system(command + arguments)

    print('plot labelBar2')
    plot_type = 'labelBar2'
    command = 'python {}{}{} '.format(path['base'], path['scripts'], scriptname)
    arguments = '{} {} {:d} {:d} {:d} {:d} {:d} {:d} {} {:.2f} {:.2f} {:.2f} {:.2f} {:.2f} {} {} {} {:.2f} {}'.format(
                variable['name'], variable['unit'], variable['hour_start'], variable['hour_end'],
                run['year'], run['month'], run['day'], run['hour'],
                domain['method'], domain['radius'], domain['deltalat'], domain['deltalon'],
                domain['lat'], domain['lon'], domain['name'], model,
                stat_processing['method'], stat_processing['threshold'], plot_type)
    os.system(command + arguments)
    print('---------------------------------------------------')


    # make small map plots #

    for hour in hours:
        variable['hour_start'] = hour - timespan
        variable['hour_end'] = hour
        for stat_processing in stat_processing_list:
            for domain in domains:
                print('plot {}, {:2d}-{:2d}h, prob_of_exc, {}{}, {}'.format(
                       variable['name'], variable['hour_start'], variable['hour_end'],
                       stat_processing['threshold'], variable['unit'], domain['name']))

                plot_type = 'small_map_only'
                command = 'python {}{}{} '.format(path['base'], path['scripts'], scriptname)
                arguments_1 = '{} {} {:d} {:d} {:d} {:d} {:d} {:d} '.format(
                               variable['name'], variable['unit'], variable['hour_start'], variable['hour_end'],
                               run['year'], run['month'], run['day'], run['hour'])
                arguments_2 = '{} {:.2f} {:.2f} {:.2f} {:.2f} {:.2f} {} {} {} {:.2f} {}'.format(
                               domain['method'], domain['radius'], domain['deltalat'], domain['deltalon'],
                               domain['lat'], domain['lon'], domain['name'], model,
                               stat_processing['method'], stat_processing['threshold'], plot_type)
                os.system(command + arguments_1 + arguments_2)


        # make plots for time depending texts #

        print('plot text, {:2d}h'.format(hour))
        domain = domains[0]
        stat_processing = dict(method = 'prob_of_exc', threshold = label_text_value)

        plot_type = 'text'
        command = 'python {}{}{} '.format(path['base'], path['scripts'], scriptname)
        arguments_1 = '{} {} {:d} {:d} {:d} {:d} {:d} {:d} '.format(
                       variable['name'], variable['unit'], variable['hour_start'], variable['hour_end'],
                       run['year'], run['month'], run['day'], run['hour'])
        arguments_2 = '{} {:.2f} {:.2f} {:.2f} {:.2f} {:.2f} {} {} {} {:.2f} {}'.format(
                       domain['method'], domain['radius'], domain['deltalat'], domain['deltalon'],
                       domain['lat'], domain['lon'], domain['name'], model,
                       stat_processing['method'], stat_processing['threshold'], plot_type)
        os.system(command + arguments_1 + arguments_2)


        # put all plot parts together #

        if model == 'icon-eu-eps':
            model_acr = 'iconeueps'
        elif model == 'icon-global-eps':
            model_acr = 'iconglobaleps'

        for domain in domains:
            print('paste together {}, {:2d}-{:2d}h, prob_of_exc, {}'.format(
                   variable['name'], variable['hour_start'], variable['hour_end'], domain['name']))

            path['plots_maps'] = 'run_{:4d}{:02d}{:02d}{:02d}/{}/'.format(run['year'], run['month'], run['day'],
                                  run['hour'], domain['name'])
            path['plots_labelBar_text'] = 'run_{:4d}{:02d}{:02d}{:02d}/{}/'.format(run['year'], run['month'],
                                           run['day'], run['hour'], domains[0]['name'])
            filenames = dict()
            for i, stat_processing in enumerate(stat_processing_list):
                if stat_processing['threshold'] >= 1.0:
                    threshold_str = '{:03d}'.format(int(stat_processing['threshold']))
                else:
                    threshold_str = '{:.1f}'.format(stat_processing['threshold'])
                file_str = 'small_map_plot_{:d}'.format(i+1)
                filenames[file_str] = '{}_prob_of_exc_{}_{}{}_{:03d}-{:03d}h_{}_small_map_only.png'.format(
                                       model_acr, variable['name'], threshold_str, variable['unit'],
                                       variable['hour_start'], variable['hour_end'], domain['name'])
            filenames['labelBar1']  = '{}_prob_of_exc_{}_{:.1f}{}_000-{:03d}h_{}_labelBar1.png'.format(
                                       model_acr, variable['name'], label_text_value, variable['unit'],
                                       timespan, domains[0]['name'])
            filenames['labelBar2']  = '{}_prob_of_exc_{}_{:.1f}{}_000-{:03d}h_{}_labelBar2.png'.format(
                                       model_acr, variable['name'], label_text_value, variable['unit'],
                                       timespan, domains[0]['name'])
            filenames['text']       = '{}_prob_of_exc_{}_{:.1f}{}_{:03d}-{:03d}h_{}_text.png'.format(
                                       model_acr, variable['name'], label_text_value, variable['unit'],
                                       variable['hour_start'], variable['hour_end'], domains[0]['name'])
            filenames['finalplot']  = '{}_prob_of_exc_2x2_{}_{:03d}-{:03d}h_{}{}.png'.format(
                                       model_acr, variable['name'], variable['hour_start'], variable['hour_end'],
                                       domain['name'], colormap_name)


            img_combined = Image.new('RGB',(750, 950),(255,255,255))

            image_smallmap1 = Image.open(path['base'] + path['plots_general'] + path['plots_maps']\
                                         + filenames['small_map_plot_1'])
            img_combined.paste(image_smallmap1.crop((0, 0, 360, 360)), (10, 95))
            image_smallmap2 = Image.open(path['base'] + path['plots_general'] + path['plots_maps']\
                                         + filenames['small_map_plot_2'])
            img_combined.paste(image_smallmap2.crop((0, 0, 360, 360)), (10+360+10, 95))
            image_smallmap3 = Image.open(path['base'] + path['plots_general'] + path['plots_maps']\
                                         + filenames['small_map_plot_3'])
            img_combined.paste(image_smallmap3.crop((0, 0, 360, 360)), (10, 95+360-15))
            image_smallmap4 = Image.open(path['base'] + path['plots_general'] + path['plots_maps']\
                                         + filenames['small_map_plot_4'])
            img_combined.paste(image_smallmap4.crop((0, 0, 360, 360)), (10+360+10, 95+360-15))


            image_labelbar1a = Image.open(path['base'] + path['plots_general'] + path['plots_labelBar_text']\
                                         + filenames['labelBar1'])
            img_combined.paste(image_labelbar1a.crop((25, 610, 775, 630)), (3, 95+360-15+360+13))
            image_labelbar1b = Image.open(path['base'] + path['plots_general'] + path['plots_labelBar_text']\
                                         + filenames['labelBar1'])
            img_combined.paste(image_labelbar1b.crop((25, 630, 775, 650)), (3, 95+360-15+360-12))
            image_labelbar2 = Image.open(path['base'] + path['plots_general'] + path['plots_labelBar_text']\
                                         + filenames['labelBar2'])
            img_combined.paste(image_labelbar2.crop((25, 575, 775, 650)), (3, 95+360-15+360+29))


            image_title = Image.open(path['base'] + path['plots_general'] + path['plots_labelBar_text']
                                     + filenames['text'])
            img_combined.paste(image_title.crop((50, 0, 750, 30)), (title_pos, 0))
            image_initial_time = Image.open(path['base'] + path['plots_general'] + path['plots_labelBar_text']
                                            + filenames['text'])
            img_combined.paste(image_initial_time.crop((5, 40, 300, 60)), (3, 50))
            image_valid_time_start = Image.open(path['base'] + path['plots_general'] + path['plots_labelBar_text']
                                                + filenames['text'])
            img_combined.paste(image_valid_time_start.crop((450, 40, 740, 60)), (445, 45))
            image_valid_time_end = Image.open(path['base'] + path['plots_general'] + path['plots_labelBar_text']
                                              + filenames['text'])
            img_combined.paste(image_valid_time_end.crop((560, 630, 775, 650)), (525, 65))
            image_model = Image.open(path['base'] + path['plots_general'] + path['plots_labelBar_text']
                                     + filenames['text'])
            img_combined.paste(image_model.crop((5, 630, 550, 650)), (3, 95+360-15+360-20+75+70))

            img_combined.save(path['base'] + path['plots_general'] + path['plots_maps']\
                              + filenames['finalplot'],'png')
            print('---------------------------------------------------')


            for i in range(4):
                os.remove(path['base'] + path['plots_general'] + path['plots_maps']\
                          + filenames['small_map_plot_{:d}'.format(i+1)])
        os.remove(path['base'] + path['plots_general'] + path['plots_labelBar_text']\
                  + filenames['text'])
    os.remove(path['base'] + path['plots_general'] + path['plots_labelBar_text']\
              + filenames['labelBar1'])
    os.remove(path['base'] + path['plots_general'] + path['plots_labelBar_text']\
              + filenames['labelBar2'])

    return
