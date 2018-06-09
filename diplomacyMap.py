from PIL import Image, ImagePalette, ImageFont, ImageDraw

import numpy as np

from copy import deepcopy


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

UNIT_SIZE = (50, 50)

class Province:
    def __init__(self, index, name, adjacent, supply, controller):
        self.index = index
        self.name = name
        self.adjacent = adjacent
        self.supply = supply
        self.controller = controller

class Country:
    def __init__(self, name, startingUnits, colorID):
        self.name = name
        self.units = startingUnits

        baseArmy = np.array(Image.open('army.png'))
        baseNavy = np.array(Image.open('fleet.png'))
        for pix in [baseArmy, baseNavy]:
            pix[pix==1] = colorID
        self.armyIcon = Image.fromarray(baseArmy)
        self.fleetIcon = Image.fromarray(baseNavy)

def centerOfMass(index):
    y, x = np.where(np.any(pix == index, axis=()))
    if len(x) == 0 or len(y) == 0:
        return (0, 0)
    return (sum(x) / float(len(x)), sum(y) / float(len(y)))

class Board:
    countries = [
        Country('Russia', [('F', 'STP'), ('A', 'MOS'), ('F', 'SEV'), ('A', 'WAR')], 80),
        Country('Britain', [('F', 'EDL'), ('A', 'LVP'), ('F', 'LON')], 81),
        Country('Germany', [('F', 'KIE'), ('A', 'BER'), ('A', 'MUN')], 82),
        Country('France', [('F', 'BRE'), ('A', 'PAR'), ('A', 'MAR')], 83),
        Country('Austria', [('A', 'VIE'), ('A', 'BUD'), ('F', 'TRI')], 84),
        Country('Italy', [('A', 'VEN'), ('A', 'ROM'), ('F', 'NAP')], 85),
        Country('Turkey', [('A', 'CON'), ('F', 'ANK'), ('A', 'SMY')], 86),
    ]

    provinces = {
        # (index, full name, [adjacent provinces], supply, controller)
        # WATER
        'NAO': Province(4, None, ['NWG', 'IRI', 'MAO', 'CLY', 'LVP'], False, None),
        'NWG': Province(5, None, ['NAO', 'CLY', 'EDL', 'NTH', 'NWY', 'BAR'], False, None),
        'BAR': Province(6, None, ['NWG', 'NWY', 'STP'], False, None),
        'BOT': Province(7, None, ['SWE', 'BAL', 'LVN', 'STP', 'FIN'], False, None),
        'NTH': Province(8, None, ['NWG', 'EDL', 'YOR', 'LON', 'BEL', 'HOL', 'HEL', 'DEN', 'SKA', 'NWY'], False, None),
        'SKA': Province(9, None, [], False, None),
        'IRI': Province(10, None, [], False, None),
        'HEL': Province(11, None, [], False, None),
        'BAL': Province(12, None, [], False, None),
        'MAO': Province(13, None, [], False, None),
        'BLA': Province(15, None, [], False, None),
        'ADR': Province(16, None, [], False, None),
        'LYO': Province(17, None, [], False, None),
        'TYS': Province(18, None, [], False, None),
        'WES': Province(19, None, [], False, None),
        'ION': Province(20, None, [], False, None),
        'AEG': Province(21, None, [], False, None),
        'EAS': Province(22, None, [], False, None),
        # RUSSIA
        'STP': Province(23, None, [], False, None),
        'FIN': Province(24, None, [], False, None),
        'MOS': Province(25, None, [], False, None),
        'LVN': Province(26, None, [], False, None),
        'WAR': Province(27, None, [], False, None),
        'SEV': Province(28, None, [], False, None),
        'UKR': Province(29, None, [], False, None),
        # BRITAIN
        'CLY': Province(30, None, [], False, None),
        'EDL': Province(31, None, [], False, None),
        'LVP': Province(32, None, [], False, None),
        'YOR': Province(33, None, [], False, None),
        'WAL': Province(34, None, [], False, None),
        'LON': Province(35, None, [], False, None),
        # GERMANY
        'KIE': Province(36, None, [], False, None),
        'BER': Province(37, None, [], False, None),
        'PRU': Province(38, None, [], False, None),
        'RUH': Province(39, None, [], False, None),
        'MUN': Province(40, None, [], False, None),
        'SIL': Province(41, None, [], False, None),
        # FRANCE
        'BRE': Province(42, None, [], False, None),
        'PIC': Province(43, None, [], False, None),
        'PAR': Province(44, None, [], False, None),
        'BUR': Province(45, None, [], False, None),
        'GAS': Province(46, None, [], False, None),
        'MAR': Province(47, None, [], False, None),
        # AUSTRIA
        'BOH': Province(48, None, [], False, None),
        'GAL': Province(49, None, [], False, None),
        'TYR': Province(50, None, [], False, None),
        'VIE': Province(51, None, [], False, None),
        'BUD': Province(52, None, [], False, None),
        'TRI': Province(53, None, [], False, None),
        # ITALY
        'PIE': Province(54, None, [], False, None),
        'VEN': Province(55, None, [], False, None),
        'TUS': Province(56, None, [], False, None),
        'ROM': Province(57, None, [], False, None),
        'APU': Province(58, None, [], False, None),
        'NAP': Province(59, None, [], False, None),
        # TURKEY
        'CON': Province(60, None, [], False, None),
        'ANK': Province(61, None, [], False, None),
        'ARM': Province(62, None, [], False, None),
        'SMY': Province(63, None, [], False, None),
        'SYR': Province(64, None, [], False, None),
        # NEUTRAL
        'NWY': Province(65, None, [], False, None),
        'SWE': Province(66, None, [], False, None),
        'DEN': Province(67, None, [], False, None),
        'HOL': Province(68, None, [], False, None),
        'BEL': Province(69, None, [], False, None),
        'SPA': Province(70, None, [], False, None),
        'POR': Province(71, None, [], False, None),
        'RUM': Province(72, None, [], False, None),
        'SER': Province(73, None, [], False, None),
        'BUL': Province(74, None, [], False, None),
        'ALB': Province(75, None, [], False, None),
        'GRE': Province(76, None, [], False, None),
        'NAF': Province(77, None, [], False, None),
        'TUN': Province(78, None, [], False, None),
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
            self._setColor(i, RUSSIA)
        for i in range(30, 36):
            self._setColor(i, BRITAIN)
        for i in range(36, 42):
            self._setColor(i, GERMANY)
        for i in range(42, 48):
            self._setColor(i, FRANCE)
        for i in range(48, 54):
            self._setColor(i, POLAND)
        for i in range(54, 60):
            self._setColor(i, ITALY)
        for i in range(60, 65):
            self._setColor(i, TURKEY)
        for i in range(65, 79):
            self._setColor(i, NEUTRAL)
        for i in range(65, 79):
            self._setColor(i, NEUTRAL)
        self._setColor(80, RUSSIA)
        self._setColor(81, BRITAIN)
        self._setColor(82, GERMANY)
        self._setColor(83, FRANCE)
        self._setColor(84, POLAND)
        self._setColor(85, ITALY)
        self._setColor(86, TURKEY)

    def _drawUnit(self, map, icon, x, y):
        map.paste(icon, (int(x), int(y)))

    def _setColor(self, tileID, color):
        # self._palette[tileID], self._palette[tileID + 256], self._palette[tileID + 512] = color
        self._palette[tileID * 3], self._palette[tileID * 3 + 1], self._palette[tileID * 3 + 2] = color

    def _isFleet(self, unit):
        return unit[0] == 'F'

    def getMap(self):
        map = deepcopy(self._baseMap)
        map.putpalette(self._palette)
        for country in self.countries:
            for unit in country.units:
                x, y = coordinates[unit[1]]
                self._drawUnit(map, country.fleetIcon if self._isFleet(unit) else country.armyIcon, x, y)

        return map

    def saveMap(self, filename):
        self.getMap().save(filename)

    def displayMap(self):
        self.getMap().show()

    def placeArmy(self, country, location):
        pass

    def moveArmy(self, f, to):
        pass

    def deleteArmy(self, location):
        pass

    def getUnitByProvince(self, province):
        return ('F', 'NAO')

    def getUnitsByCountry(self, countryID):
        return [('F', 'NAO')]

    def adjacent(self, province1, province2):
        return True

    def isSupplyDepot(self, province):
        return False

    def changeOwner(self, province, country):
        return

m = Board()
m.displayMap()
# m.saveMap('maptest.png')
