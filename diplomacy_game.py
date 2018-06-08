from PIL import Image, ImagePalette, ImageFont, ImageDraw
import numpy as np

from coordinates import coordinates

WATER = (180, 180, 255)
NEUTRAL = (230, 230, 230)
IMPASSABLE = (50, 50, 50)
FRANCE = (180, 255, 255)
ITALY = (180, 255, 180)
GERMANY = (180, 180, 180)
POLAND = (255, 180, 180)
RUSSIA = (180, 180, 225)
TURKEY = (180, 255, 255)
BRITAIN = (255, 180, 255)
BORDER = (0, 0, 0)

class Tile:
    def __init__(self, index, adjacent, controller):
        self.index = index
        self.adjacent = adjacent
        self.controller = controller

tiles = {
    # (index, full name, [adjacent tiles], controller)
    'North Atlantic Ocean': Tile(1, ['Norweigan Sea', 'Irish Sea', 'Mid Atlantic', 'Clyde'], None),
    'Norweigan Sea': Tile(2, ['North Atlantic Sea', 'Barents Sea', 'North Sea', 'Norway'], None),
    'Barents Sea': Tile(3, ['Norweigan Sea', 'Norway', 'Saint Petersburg'], None),
    'Gulf of Bothnia': Tile(4, ['Sweden', 'Finland', 'Saint Petersburg', 'Baltic Sea', 'Livonia'], None),
    'North Sea': Tile(5, ['Norweigan Sea', 'Norway', 'Skagerrak', 'Denmark', 'Helgoland Bight', 'English Channel', 'Edinburgh', 'York', 'London', 'Holland', 'Belgium'], None),
}

palette = np.zeros(256 * 3, dtype=np.uint8)
def setColor(index, color):
    palette[index], palette[index + 256], palette[index + 512] = color

setColor(1, BORDER)
setColor(2, IMPASSABLE)
setColor(3, WATER)
for i in range(4, 24):
    setColor(i, WATER)
for i in range(23, 30):
    setColor(i, RUSSIA)
for i in range(30, 36):
    setColor(i, BRITAIN)
for i in range(36, 42):
    setColor(i, GERMANY)
for i in range(42, 48):
    setColor(i, FRANCE)
for i in range(48, 54):
    setColor(i, POLAND)
for i in range(54, 60):
    setColor(i, ITALY)
for i in range(60, 65):
    setColor(i, TURKEY)
for i in range(65, 79):
    setColor(i, NEUTRAL)
for i in range(65, 79):
    setColor(i, NEUTRAL)

im = Image.open('diplomacy_map.png')
pix = np.array(im)

# # Shift up over 46 (empty)
# for i in range(45, -1, -1):
#     pix[pix == i] += 1
# # Move 20 (now 21) and shift up to cover
# pix[pix == 21] = 100
# for i in range(20, 1, -1):
#     pix[pix == i] += 1
# # Shift up over 26 (now 27) (empty)
# for i in range(26, 2, -1):
#     pix[pix == i] += 1
# pix[pix == 100] = 3
# pix[pix == 79] = 2


def centerOfMass(index):
    y, x = np.where(np.any(pix == index, axis=()))
    if len(x) == 0 or len(y) == 0:
        return (0, 0)
    return (sum(x) / float(len(x)), sum(y) / float(len(y)))




im_out = Image.fromarray(pix)
im_out.putpalette(palette)
draw = ImageDraw.Draw(im_out)
for i in range(4, 79):
    x, y = coordinates[i]
    # print('%i:(%f,%f)' % (i, x, y))
    font = ImageFont.truetype("arial.ttf", 40)
    draw.text((x, y), '%d' % i, (0,0,0), font=font)
# font = ImageFont.truetype("arial.ttf", 40)
# draw.text((0,0), '', (0,0,0), font=font)

im_out.show()
im_out.save('diplomacy_map_coordinates.png')
