from PIL import Image, ImagePalette, ImageFont, ImageDraw

import numpy as np

from copy import deepcopy


from coordinates import coordinates

BORDER = (0, 0, 0)
WATER = (180, 180, 255)
NEUTRAL = (230, 230, 230)
IMPASSABLE = (50, 50, 50)
COUNTRY_COLORS = [
    (180, 180, 225), # RUSSIA
    (255, 180, 255), # BRITAIN
    (180, 255, 255), # FRANCE
    (180, 180, 180), # GERMANY
    (255, 180, 180), # AUSTRIA
    (180, 255, 180), # ITALY
    (180, 255, 255), # TURKEY
]
UNIT_SIZE = (50, 50)

class Province:
    def __init__(self, index, name, neighbors, isSupplyDepot, unit, controller):
        self.index = index
        self.name = name
        self.neighbors = neighbors
        self.isSupplyDepot = isSupplyDepot
        self.unit = unit
        self.controller = controller

class Country:
    def __init__(self, name, colorID):
        self.name = name

        baseArmy = np.array(Image.open('army.png'))
        baseNavy = np.array(Image.open('fleet.png'))
        for pix in [baseArmy, baseNavy]:
            pix[pix==1] = colorID
        self.armyIcon = Image.fromarray(baseArmy)
        self.fleetIcon = Image.fromarray(baseNavy)

class Unit:
    def __init__(self, type, countryID):
        self.type = type
        self.countryID = countryID

def centerOfMass(index):
    y, x = np.where(np.any(pix == index, axis=()))
    if len(x) == 0 or len(y) == 0:
        return (0, 0)
    return (sum(x) / float(len(x)), sum(y) / float(len(y)))

class Map:
    countries = [
        Country('Russia', 80),
        Country('Britain', 81),
        Country('Germany', 82),
        Country('France', 83),
        Country('Austria', 84),
        Country('Italy', 85),
        Country('Turkey', 86),
    ]

    provinces = {
        # (index, full name, [neighboring provinces], isSupplyDepot, unit, controller)
        # WATER
        'NAO': Province(4, None, ['NWG', 'IRI', 'MAO', 'CLY', 'LVP'], False, None, None),
        'NWG': Province(5, None, ['NAO', 'CLY', 'EDL', 'NTH', 'NWY', 'BAR'], False, None, None),
        'BAR': Province(6, None, ['NWG', 'NWY', 'STP'], False, None, None),
        'BOT': Province(7, None, ['SWE', 'BAL', 'LVN', 'STP', 'FIN'], False, None, None),
        'NTH': Province(8, None, ['NWG', 'EDL', 'YOR', 'LON', 'BEL', 'HOL', 'HEL', 'DEN', 'SKA', 'NWY'], False, None, None),
        'SKA': Province(9, None, [], False, None, None),
        'IRI': Province(10, None, [], False, None, None),
        'HEL': Province(11, None, [], False, None, None),
        'BAL': Province(12, None, [], False, None, None),
        'MAO': Province(13, None, [], False, None, None),
        'BLA': Province(15, None, [], False, None, None),
        'ADR': Province(16, None, [], False, None, None),
        'LYO': Province(17, None, [], False, None, None),
        'TYS': Province(18, None, [], False, None, None),
        'WES': Province(19, None, [], False, None, None),
        'ION': Province(20, None, [], False, None, None),
        'AEG': Province(21, None, [], False, None, None),
        'EAS': Province(22, None, [], False, None, None),
        # RUSSIA
        'STP': Province(23, None, [], True, Unit('F', 0), 0),
        'FIN': Province(24, None, [], False, None, 0),
        'MOS': Province(25, None, [], True, Unit('A', 0), 0),
        'LVN': Province(26, None, [], False, None, 0),
        'WAR': Province(27, None, [], True, Unit('A', 0), 0),
        'SEV': Province(28, None, [], True, Unit('F', 0), 0),
        'UKR': Province(29, None, [], False, None, 0),
        # BRITAIN
        'CLY': Province(30, None, [], False, None, 1),
        'EDL': Province(31, None, [], True, Unit('F', 1), 1),
        'LVP': Province(32, None, [], True, Unit('A', 1), 1),
        'YOR': Province(33, None, [], False, None, 1),
        'WAL': Province(34, None, [], False, None, 1),
        'LON': Province(35, None, [], True, Unit('F', 1), 1),
        # GERMANY
        'KIE': Province(36, None, [], True, Unit('F', 2), 2),
        'BER': Province(37, None, [], True, Unit('A', 2), 2),
        'PRU': Province(38, None, [], False, None, 2),
        'RUH': Province(39, None, [], False, None, 2),
        'MUN': Province(40, None, [], True, Unit('A', 2), 2),
        'SIL': Province(41, None, [], False, None, 2),
        # FRANCE
        'BRE': Province(42, None, [], True, Unit('F', 3), 3),
        'PIC': Province(43, None, [], False, None, 3),
        'PAR': Province(44, None, [], True, Unit('A', 3), 3),
        'BUR': Province(45, None, [], False, None, 3),
        'GAS': Province(46, None, [], False, None, 3),
        'MAR': Province(47, None, [], True, Unit('A', 3), 3),
        # AUSTRIA
        'BOH': Province(48, None, [], False, None, 4),
        'GAL': Province(49, None, [], False, None, 4),
        'TYR': Province(50, None, [], False, None, 4),
        'VIE': Province(51, None, [], True, Unit('A', 4), 4),
        'BUD': Province(52, None, [], True, Unit('A', 4), 4),
        'TRI': Province(53, None, [], True, Unit('F', 4), 4),
        # ITALY
        'PIE': Province(54, None, [], False, None, 5),
        'VEN': Province(55, None, [], True, Unit('A', 5), 5),
        'TUS': Province(56, None, [], False, None, 5),
        'ROM': Province(57, None, [], True, Unit('A', 5), 5),
        'APU': Province(58, None, [], False, None, 5),
        'NAP': Province(59, None, [], True, Unit('F', 5), 5),
        # TURKEY
        'CON': Province(60, None, [], True, Unit('A', 6), 6),
        'ANK': Province(61, None, [], True, Unit('F', 6), 6),
        'ARM': Province(62, None, [], False, None, 6),
        'SMY': Province(63, None, [], True, Unit('A', 6), 6),
        'SYR': Province(64, None, [], False, None, 6),
        # NEUTRAL
        'NWY': Province(65, None, [], False, None, None),
        'SWE': Province(66, None, [], False, None, None),
        'DEN': Province(67, None, [], False, None, None),
        'HOL': Province(68, None, [], False, None, None),
        'BEL': Province(69, None, [], False, None, None),
        'SPA': Province(70, None, [], False, None, None),
        'POR': Province(71, None, [], False, None, None),
        'RUM': Province(72, None, [], False, None, None),
        'SER': Province(73, None, [], False, None, None),
        'BUL': Province(74, None, [], False, None, None),
        'ALB': Province(75, None, [], False, None, None),
        'GRE': Province(76, None, [], False, None, None),
        'NAF': Province(77, None, [], False, None, None),
        'TUN': Province(78, None, [], False, None, None),
    }

    def __init__(self):
        self._baseMap = Image.open('diplomacyMap.png')
        self._draw = ImageDraw.Draw(self._baseMap)
        self._palette = np.zeros(256 * 3, dtype=np.uint8)

        for name, province in self.provinces.items():
            (x, y) = coordinates[name]
            font = ImageFont.truetype("arial.ttf", 40)
            self._draw.text((x, y), name, (0,0,0), font=font)

        self._setColor(1, BORDER)
        self._setColor(2, IMPASSABLE)
        self._setColor(3, WATER)
        for i in range(4, 24):
            self._setColor(i, WATER)
        for i in range(23, 30):
            self._setColor(i, COUNTRY_COLORS[0])
        for i in range(30, 36):
            self._setColor(i, COUNTRY_COLORS[1])
        for i in range(36, 42):
            self._setColor(i, COUNTRY_COLORS[2])
        for i in range(42, 48):
            self._setColor(i, COUNTRY_COLORS[3])
        for i in range(48, 54):
            self._setColor(i, COUNTRY_COLORS[4])
        for i in range(54, 60):
            self._setColor(i, COUNTRY_COLORS[5])
        for i in range(60, 65):
            self._setColor(i, COUNTRY_COLORS[6])
        for i in range(65, 79):
            self._setColor(i, NEUTRAL)
        self._setColor(80, COUNTRY_COLORS[0])
        self._setColor(81, COUNTRY_COLORS[1])
        self._setColor(82, COUNTRY_COLORS[2])
        self._setColor(83, COUNTRY_COLORS[3])
        self._setColor(84, COUNTRY_COLORS[4])
        self._setColor(85, COUNTRY_COLORS[5])
        self._setColor(86, COUNTRY_COLORS[6])

    def _drawUnit(self, map, icon, coordinates):
        x, y = coordinates
        map.paste(icon, (int(x), int(y)))

    def _setColor(self, tileID, color):
        # self._palette[tileID], self._palette[tileID + 256], self._palette[tileID + 512] = color
        self._palette[tileID * 3], self._palette[tileID * 3 + 1], self._palette[tileID * 3 + 2] = color

    def _isFleet(self, unit):
        return unit.type == 'F'

    def getMap(self):
        map = deepcopy(self._baseMap)
        map.putpalette(self._palette)
        for name, province in self.provinces.items():
            if province.unit:
                c = self.countries[province.unit.countryID]
                self._drawUnit(map, c.fleetIcon if self._isFleet(province.unit) else c.armyIcon, coordinates[name])

        return map

    def saveMap(self, filename):
        self.getMap().save(filename)

    def displayMap(self):
        self.getMap().show()

    def placeUnit(self, type, countryID, province):
        assert not self.provinces[province].unit

        self.provinces[province].unit = Unit(type, countryID)

    def moveUnit(self, start, end):
        assert self.getUnitByProvince(start)
        assert not self.getUnitByProvince(end)

        self.provinces[end].unit = self.provinces[start].unit
        self.provinces[start].unit = None


    def deleteUnit(self, province):
        assert self.provinces[province].unit

        self.provinces[province].unit = None

    def getUnitByProvince(self, province):
        return self.provinces[province].unit

    def getUnitsByCountry(self, countryID):
        return [(p.unit.type, name) for name, p in self.provinces.items()
                if p.unit and p.unit.countryID == countryID]

    def adjacent(self, province1, province2):
        return province2 in self.provinces[province1].neighbors

    def isSupplyDepot(self, province):
        return self.provinces[province].isSupplyDepot

    def changeController(self, province, countryID):
        p = self.provinces[province]
        p.controller = countryID
        if self.isLand(province):
            self._setColor(p.index, COUNTRY_COLORS[countryID])

    def isLand(self, province):
        return self.provinces[province].index > 22

    def isOcean(self, province):
        return not self.isLand(self.province)

# m = Map()
# m.displayMap()
# m.saveMap('maptest.png')
