from PIL import Image, ImagePalette, ImageFont, ImageDraw
# import Image
import numpy as np

WATER = (0, 0, 255)
NEUTRAL = (180, 180, 180)
IMPASSABLE = (50, 50, 50)
FRANCE = (0, 255, 255)
ITALY = (0, 255, 0)
GERMANY = (50, 50, 50)
POLAND = (255, 60, 60)
RUSSIA = (0, 0, 100)
TURKEY = (0, 255, 255)
BRITAIN = (255, 0, 255)
BORDER = (0, 0, 0)

tiles = {
    # (index, adjacent, controller)
    'North Atlantic Ocean': (1, ['Norweigan Sea', 'Irish Sea', 'Mid Atlantic', 'Clyde'], None),
    'Norweigan Sea': (2, ['North Atlantic Sea', 'Barents Sea', 'North Sea', 'Norway'], None),
    'Barents Sea': (3, ['Norweigan Sea', 'Norway', 'Saint Petersburg'], None),
    'Gulf of Bothnia': (4, ['Sweden', 'Finland', 'Saint Petersburg', 'Baltic Sea', 'Livonia'], None),
    'North Sea': (5, ['Norweigan Sea', 'Norway', 'Skagerrak', 'Denmark', 'Helgoland Bight', 'English Channel', 'Edinburgh', 'York', 'London', 'Holland', 'Belgium'], None),
}

palette = np.zeros(256 * 3, dtype=np.uint8)
def setColor(index, color):
    palette[index], palette[index + 256], palette[index + 512] = color

for i in range(1, 21):
    setColor(i, WATER)
for i in range(21, 28):
    setColor(i, RUSSIA)
for i in range(28, 34):
    setColor(i, BRITAIN)
for i in range(34, 41):
    setColor(i, GERMANY)
for i in range(41, 48):
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
setColor(79, IMPASSABLE)

im = Image.open('diplomacy_map.png')
output_map.putpalette(palette)

draw = ImageDraw.Draw(output_map)
draw.text((0, 0),"Diplomacy Map Test",(0,0,0))

output_map.show()
