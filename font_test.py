__author__ = 'bghende'

import os
from PIL import Image, ImageDraw, ImageFont

# get an image
base = Image.open('monkey.jpg').convert('RGBA')

# make a blank image for the text, initialized to transparent text color
txt = Image.new('RGBA', base.size, (255,255,255,0))

# get a font
fnt = ImageFont.truetype('Arial.ttf', 40)
# get a drawing context
d = ImageDraw.Draw(txt)

# draw text, half opacity
d.text
d.text((10,10), "Hello", font=fnt, fill=(0,0,0,128))
# draw text, full opacity
d.text((10,60), "World", font=fnt, fill=(255,255,255,255))

txt.save('out.jpg')


# out = Image.alpha_composite(base, txt)
#
# out.show()
