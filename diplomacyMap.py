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
    def __init__(self, index, name, adjacent, supply, controller):
        self.index = index
        self.name = name
        self.adjacent = adjacent
        self.supply = supply
        self.controller = controller

tiles = {
    # (index, full name, [adjacent tiles], supply, controller)
    'NAO': Tile(4, None, ['NWG', 'IRI', 'MAO', 'CLY', 'LVP'], False, None),
    'NWG': Tile(5, None, ['NAO', 'CLY', 'EDL', 'NTH', 'NWY', 'BAR'], False, None),
    'BAR': Tile(6, None, ['NWG', 'NWY', 'STP'], False, None),
    'BOT': Tile(7, None, ['SWE', 'BAL', 'LVN', 'STP', 'FIN'], False, None),
    'NTH': Tile(8, None, ['NWG', 'EDL', 'YOR', 'LON', 'BEL', 'HOL', 'HEL', 'DEN', 'SKA', 'NWY'], False, None),
    'SKA': Tile(9, None, [], False, None),
    'IRI': Tile(10, None, [], False, None),
    'HEL': Tile(11, None, [], False, None),
    'BAL': Tile(12, None, [], False, None),
    'MAO': Tile(13, None, [], False, None),
    'BLA': Tile(15, None, [], False, None),
    'ADR': Tile(16, None, [], False, None),
    'LYO': Tile(17, None, [], False, None),
    'TYS': Tile(18, None, [], False, None),
    'WES': Tile(19, None, [], False, None),
    'ION': Tile(20, None, [], False, None),
    'AEG': Tile(21, None, [], False, None),
    'EAS': Tile(22, None, [], False, None),
    'STP': Tile(23, None, [], False, None),
    'FIN': Tile(24, None, [], False, None),
    'MOS': Tile(25, None, [], False, None),
    'LVN': Tile(26, None, [], False, None),
    'WAR': Tile(27, None, [], False, None),
    'SEV': Tile(28, None, [], False, None),
    'UKR': Tile(29, None, [], False, None),
    'CLY': Tile(30, None, [], False, None),
    'EDL': Tile(31, None, [], False, None),
    'LVP': Tile(32, None, [], False, None),
    'YOR': Tile(33, None, [], False, None),
    'WAL': Tile(34, None, [], False, None),
    'LON': Tile(35, None, [], False, None),
    'KIE': Tile(36, None, [], False, None),
    'BER': Tile(37, None, [], False, None),
    'PRU': Tile(38, None, [], False, None),
    'RUH': Tile(39, None, [], False, None),
    'MUN': Tile(40, None, [], False, None),
    'SIL': Tile(41, None, [], False, None),
    'BRE': Tile(42, None, [], False, None),
    'PIC': Tile(43, None, [], False, None),
    'PAR': Tile(44, None, [], False, None),
    'BUR': Tile(45, None, [], False, None),
    'GAS': Tile(46, None, [], False, None),
    'MAR': Tile(47, None, [], False, None),
    'BOH': Tile(48, None, [], False, None),
    'GAL': Tile(49, None, [], False, None),
    'TYR': Tile(50, None, [], False, None),
    'VIE': Tile(51, None, [], False, None),
    'BUD': Tile(52, None, [], False, None),
    'TRI': Tile(53, None, [], False, None),
    'PIE': Tile(54, None, [], False, None),
    'VEN': Tile(55, None, [], False, None),
    'TUS': Tile(56, None, [], False, None),
    'ROM': Tile(57, None, [], False, None),
    'APU': Tile(58, None, [], False, None),
    'NAP': Tile(59, None, [], False, None),
    'CON': Tile(60, None, [], False, None),

    'ANK': Tile(61, None, [], False, None),
    'ARM': Tile(62, None, [], False, None),
    'SMY': Tile(63, None, [], False, None),
    'SYR': Tile(64, None, [], False, None),
    'NWY': Tile(65, None, [], False, None),
    'SWE': Tile(66, None, [], False, None),
    'DEN': Tile(67, None, [], False, None),
    'HOL': Tile(68, None, [], False, None),
    'BEL': Tile(69, None, [], False, None),
    'SPA': Tile(70, None, [], False, None),
    'POR': Tile(71, None, [], False, None),
    'RUM': Tile(72, None, [], False, None),
    'SER': Tile(73, None, [], False, None),
    'BUL': Tile(74, None, [], False, None),
    'ALB': Tile(75, None, [], False, None),
    'GRE': Tile(76, None, [], False, None),
    'NAF': Tile(77, None, [], False, None),
    'TUN': Tile(78, None, [], False, None),
}

palette = np.zeros(256 * 3, dtype=np.uint8)
def setColor(index, color):
    palette[index], palette[index + 256], palette[index + 512] = color

def
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
# for i in range(4, 79):
#     x, y = coordinates[i]
#     # print('%i:(%f,%f)' % (i, x, y))
#     font = ImageFont.truetype("arial.ttf", 40)
#     draw.text((x, y), '%d' % i, (0,0,0), font=font)
for name, tile in tiles.items():
    (x, y) = coordinates[tile.index]
    font = ImageFont.truetype("arial.ttf", 40)
    draw.text((x, y), name, (0,0,0), font=font)

# font = ImageFont.truetype("arial.ttf", 40)
# draw.text((0,0), '', (0,0,0), font=font)

im_out.show()
# im_out.save('diplomacy_map_coordinates.png')
