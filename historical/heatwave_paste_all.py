
from PIL import Image


path = dict(base = '/lsdfos/kit/imk-tro/projects/MOD/Gruppe_Knippertz/nw5893/',
            plots = 'plots/heatwave_25.07.19/prob_of_exceedance/france-germany/wahrscheinlich_wetter/')

filenames = dict(map_36C = 'map_36C.png',
                 map_38C = 'map_38C.png',
                 map_40C = 'map_40C.png',
                 captiontext1 = 'captiontext1.png',
                 captiontext2 = 'captiontext2.png',
                 finalplot = 'heatwave_final.png')


img_combined = Image.new('RGB',(1200, 500),(255,255,255))

image_map_36C = Image.open(path['base'] + path['plots'] + filenames['map_36C'])
image_map_38C = Image.open(path['base'] + path['plots'] + filenames['map_38C'])
image_map_40C = Image.open(path['base'] + path['plots'] + filenames['map_40C'])
image_captiontext1 = Image.open(path['base'] + path['plots'] + filenames['captiontext1'])
image_captiontext2 = Image.open(path['base'] + path['plots'] + filenames['captiontext2'])

img_combined.paste(image_map_36C.crop((62, 10, 413, 435)), (30, 0))
img_combined.paste(image_map_38C.crop((62, 10, 413, 435)), (30+351+10, 0))
img_combined.paste(image_map_40C.crop((62, 10, 413, 435)), (30+351+10+351+10, 0))
img_combined.paste(image_map_36C.crop((415, 10, 478, 435)), (30+351+10+351+10+351+5, 0))
img_combined.paste(image_captiontext1.crop((5, 1170, 1100, 1200)), (25, 430))
img_combined.paste(image_captiontext2.crop((5, 1170, 1100, 1200)), (760, 472))


img_combined.save(path['base'] + path['plots'] + filenames['finalplot'],'png')
