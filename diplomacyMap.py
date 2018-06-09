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
    (180, 180, 180), # GERMANY
    (180, 255, 255), # FRANCE
    (255, 180, 180), # AUSTRIA
    (180, 255, 180), # ITALY
    (180, 255, 255), # TURKEY
]
UNIT_SIZE = (50, 50)

class Province:
    def __init__(self, index, name, neighbors, supportsFleets=False, occupiedCoast=None, isSupplyDepot=False, unit=None, controller=None):
        self.index = index
        self.name = name
        self.neighbors = neighbors
        self.supportsFleets = supportsFleets
        self.occupiedCoast = occupiedCoast
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
        # (index, full name, [neighboring provinces])
        # WATER
        'NAO': Province(4, '', ['BAL', 'IRI', 'CLY', 'LVP', 'NWG'], supportsFleets=True),
        'NWG': Province(5, '', ['NAO', 'CLY', 'EDL', 'NTH', 'NWY', 'BAR'], supportsFleets=True),
        'BAR': Province(6, '', ['NWG', 'NWY', 'STP'], supportsFleets=True),
        'BOT': Province(7, '', ['SWE', 'SKA', 'LVN', 'STP', 'FIN'], supportsFleets=True),
        'NTH': Province(8, '', ['NWG', 'EDL', 'YOR', 'LON', 'BEL', 'HOL', 'HEL', 'DEN', 'SWE', 'NWY'], supportsFleets=True),
        'SKA': Province(9, '', ['BOT', 'SWE', 'DEN', 'KIE', 'BER', 'PRU', 'LVN'], supportsFleets=True),
        'IRI': Province(10, '', ['NAO', 'BAL', 'MAO', 'WAL', 'LVP'], supportsFleets=True),
        'HEL': Province(11, '', ['NTH', 'HOL', 'KIE', 'DEN'], supportsFleets=True),
        'BAL': Province(12, '', ['NAO', 'NAF', 'POR', 'SPA', 'GAS', 'BRE', 'MAO', 'IRI'], supportsFleets=True),
        'MAO': Province(13, '', ['WAL', 'IRI', 'BAL', 'BRE', 'PIC', 'BEL', 'LON'], supportsFleets=True),
        'BLA': Province(15, '', ['SEV', 'RUM', 'BUL', 'CON', 'AEG', 'ANK', 'ARM'], supportsFleets=True),
        'ADR': Province(16, '', ['VEN', 'APU', 'ION', 'ALB', 'TRI'], supportsFleets=True),
        'LYO': Province(17, '', ['MAR', 'SPA', 'WES', 'TYS', 'TUS', 'PIE'], supportsFleets=True),
        'TYS': Province(18, '', ['TUS', 'LYO', 'WES', 'TUN', 'ION', 'NAP', 'ROM'], supportsFleets=True),
        'WES': Province(19, '', ['LYO', 'SPA', 'NAF', 'TUN', 'TYS'], supportsFleets=True),
        'ION': Province(20, '', ['NAP', 'TYS', 'TUN', 'EAS', 'AEG', 'GRE', 'ALB', 'ADR', 'APU'], supportsFleets=True),
        'AEG': Province(21, '', ['BUL', 'GRE', 'ION', 'EAS', 'SMY', 'CON', 'BLA'], supportsFleets=True),
        'EAS': Province(22, '', ['SMY', 'AEG', 'ION', 'SYR'], supportsFleets=True),
        # RUSSIA
        'STP': Province(23, '', ['BAR', 'FIN', 'BOT', 'LVN', 'MOS'], supportsFleets=True, isSupplyDepot=True, unit=Unit('F', 0), controller=0),
        'FIN': Province(24, '', ['NWY', 'SWE', 'BOT', 'LVN', 'STP'], supportsFleets=True, controller=0),
        'MOS': Province(25, '', ['STP', 'LVN', 'WAR', 'UKR', 'SEV'], isSupplyDepot=True, unit=Unit('A', 0), controller=0),
        'LVN': Province(26, '', ['FIN', 'BOT', 'SKA', 'PRU', 'WAR', 'MOS', 'STP'], supportsFleets=True, controller=0),
        'WAR': Province(27, '', ['PRU', 'SIL', 'GAL', 'UKR', 'MOS', 'LVN'], isSupplyDepot=True, unit=Unit('A', 0), controller=0),
        'SEV': Province(28, '', ['MOS', 'UKR', 'RUM', 'BLA', 'ARM'], supportsFleets=True, isSupplyDepot=True, unit=Unit('F', 0), controller=0),
        'UKR': Province(29, '', ['MOS', 'WAR', 'GAL', 'RUM', 'SEV'], controller=0),
        # BRITAIN
        'CLY': Province(30, '', ['NAO', 'LVP', 'EDL', 'NWG'], supportsFleets=True, controller=1),
        'EDL': Province(31, '', ['NWG', 'CLY', 'LVP', 'YOR', 'NTH'], supportsFleets=True, isSupplyDepot=True, unit=Unit('F', 1), controller=1),
        'LVP': Province(32, '', ['CLY', 'NAO', 'IRI', 'WAL', 'YOR', 'EDL'], supportsFleets=True, isSupplyDepot=True, unit=Unit('A', 1), controller=1),
        'YOR': Province(33, '', ['EDL', 'LVP', 'WAL', 'LON', 'NTH'], supportsFleets=True, controller=1),
        'WAL': Province(34, '', ['LVP', 'IRI', 'MAO', 'LON', 'YOR'], supportsFleets=True, controller=1),
        'LON': Province(35, '', ['YOR', 'WAL', 'MAO', 'NTH'], supportsFleets=True, isSupplyDepot=True, unit=Unit('F', 1), controller=1),
        # GERMANY
        'KIE': Province(36, '', ['DEN', 'HEL', 'HOL', 'RUH', 'MUN', 'BER', 'SKA'], supportsFleets=True, isSupplyDepot=True, unit=Unit('F', 2), controller=2),
        'BER': Province(37, '', ['SKA', 'KIE', 'MUN', 'SIL', 'PRU'], supportsFleets=True, isSupplyDepot=True, unit=Unit('A', 2), controller=2),
        'PRU': Province(38, '', ['SKA', 'BER', 'SIL', 'WAR', 'LVN'], supportsFleets=True, controller=2),
        'RUH': Province(39, '', ['KIE', 'HOL', 'BEL', 'PAR', 'MUN'], controller=2),
        'MUN': Province(40, '', ['KIE', 'RUH', 'PAR', 'TYR', 'BOH', 'SIL', 'BER'], isSupplyDepot=True, unit=Unit('A', 2), controller=2),
        'SIL': Province(41, '', ['PRU', 'BER', 'MUN', 'BOH', 'GAL', 'WAR'], controller=2),
        # FRANCE
        'BRE': Province(42, '', ['MAO', 'BAL', 'GAS', 'BUR', 'PIC'], supportsFleets=True, isSupplyDepot=True, unit=Unit('F', 3), controller=3),
        'PIC': Province(43, '', ['MAO', 'BRE', 'BUR', 'PAR', 'BEL'], supportsFleets=True, controller=3),
        'PAR': Province(44, '', ['BEL', 'PIC', 'BUR', 'GAS', 'MAR', 'MUN', 'RUH'], isSupplyDepot=True, unit=Unit('A', 3), controller=3),
        'BUR': Province(45, '', ['PIC', 'BRE', 'GAS', 'PAR'], controller=3),
        'GAS': Province(46, '', ['BRE', 'BAL', 'SPA', 'MAR', 'PAR', 'BUR'], supportsFleets=True, controller=3),
        'MAR': Province(47, '', ['PAR', 'GAS', 'SPA', 'LYO', 'PIE'], supportsFleets=True, isSupplyDepot=True, unit=Unit('A', 3), controller=3),
        # AUSTRIA
        'BOH': Province(48, '', ['SIL', 'MUN', 'TYR', 'VIE', 'GAL'], controller=4),
        'GAL': Province(49, '', ['WAR', 'SIL', 'BOH', 'VIE', 'BUD', 'RUM', 'UKR'], controller=4),
        'TYR': Province(50, '', ['BOH', 'MUN', 'PIE', 'VEN', 'TRI', 'VIE'], controller=4),
        'VIE': Province(51, '', ['BOH', 'TYR', 'TRI', 'BUD', 'GAL'], isSupplyDepot=True, unit=Unit('A', 4), controller=4),
        'BUD': Province(52, '', ['GAL', 'VIE', 'TRI', 'SER', 'RUM'], isSupplyDepot=True, unit=Unit('A', 4), controller=4),
        'TRI': Province(53, '', ['VIE', 'TYR', 'VEN', 'ADR', 'ALB', 'SER', 'BUD'], supportsFleets=True, isSupplyDepot=True, unit=Unit('F', 4), controller=4),
        # ITALY
        'PIE': Province(54, '', ['MAR', 'LYO', 'TUS', 'VEN', 'TYR'], supportsFleets=True, controller=5),
        'VEN': Province(55, '', ['TYR', 'PIE', 'TUS', 'ROM', 'APU', 'ADR', 'TRI'], supportsFleets=True, isSupplyDepot=True, unit=Unit('A', 5), controller=5),
        'TUS': Province(56, '', ['VEN', 'PIE', 'LYO', 'TYS', 'ROM'], supportsFleets=True, controller=5),
        'ROM': Province(57, '', ['VEN', 'TUS', 'TYS', 'NAP', 'APU'], supportsFleets=True, isSupplyDepot=True, unit=Unit('A', 5), controller=5),
        'APU': Province(58, '', ['ADR', 'VEN', 'ROM', 'NAP', 'ION'], supportsFleets=True, controller=5),
        'NAP': Province(59, '', ['APU', 'ROM', 'TYS', 'ION'], supportsFleets=True, isSupplyDepot=True, unit=Unit('F', 5), controller=5),
        # TURKEY
        'CON': Province(60, '', ['BLA', 'BUL', 'AEG', 'SMY', 'ANK'], supportsFleets=True, isSupplyDepot=True, unit=Unit('A', 6), controller=6),
        'ANK': Province(61, '', ['BLA', 'CON', 'SMY', 'ARM'], supportsFleets=True, isSupplyDepot=True, unit=Unit('F', 6), controller=6),
        'ARM': Province(62, '', ['SEV', 'BLA', 'ANK', 'SMY', 'SYR'], supportsFleets=True, controller=6),
        'SMY': Province(63, '', ['ANK', 'CON', 'AEG', 'EAS', 'SYR', 'ARM'], supportsFleets=True, isSupplyDepot=True, unit=Unit('A', 6), controller=6),
        'SYR': Province(64, '', ['ARM', 'SMY', 'EAS'], supportsFleets=True, controller=6),
        # NEUTRAL
        'NWY': Province(65, '', ['NWG', 'NTH', 'SWE', 'FIN', 'BAR'], supportsFleets=True, isSupplyDepot=True),
        'SWE': Province(66, '', ['NWY', 'NTH', 'DEN', 'SKA', 'BOT', 'FIN'], supportsFleets=True, isSupplyDepot=True),
        'DEN': Province(67, '', ['NTH', 'HEL', 'KIE', 'SWE', 'SKA'], supportsFleets=True),
        'HOL': Province(68, '', ['NTH', 'BEL', 'RUH', 'KIE', 'HEL'], supportsFleets=True, isSupplyDepot=True),
        'BEL': Province(69, '', ['HOL', 'NTH', 'MAO', 'PIC', 'PAR', 'RUH'], supportsFleets=True, isSupplyDepot=True),
        'SPA': Province(70, '', ['BAL', 'POR', 'NAF', 'WES', 'LYO', 'MAR', 'GAS'], supportsFleets=True, isSupplyDepot=True),
        'POR': Province(71, '', ['BAL', 'SPA'], supportsFleets=True, isSupplyDepot=True),
        'RUM': Province(72, '', ['UKR', 'GAL', 'BUD', 'SER', 'BUL', 'BLA', 'SEV'], supportsFleets=True, isSupplyDepot=True),
        'SER': Province(73, '', ['BUD', 'TRI', 'ALB', 'GRE', 'BUL', 'RUM'], isSupplyDepot=True),
        'BUL': Province(74, '', ['RUM', 'SER', 'GRE', 'AEG', 'CON', 'BLA'], supportsFleets=True, isSupplyDepot=True),
        'ALB': Province(75, '', ['SER', 'TRI', 'ADR', 'ION', 'GRE'], supportsFleets=True),
        'GRE': Province(76, '', ['SER', 'ALB', 'ION', 'AEG', 'BUL'], supportsFleets=True, isSupplyDepot=True),
        'NAF': Province(77, '', ['BAL', 'WES', 'TUN', 'SPA'], supportsFleets=True),
        'TUN': Province(78, '', ['WES', 'NAF', 'ION', 'TYS'], supportsFleets=True, isSupplyDepot=True),
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
                # self._drawUnit(map, c.fleetIcon if self._isFleet(province.unit) else c.armyIcon, coordinates[name])

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

m = Map()
for p in m.provinces:
    for n in m.provinces[p].neighbors:
        if p not in m.provinces[n].neighbors:
            print "%s not in %s!" % (p, n)
m.displayMap()
# m.saveMap('maptest.png')
