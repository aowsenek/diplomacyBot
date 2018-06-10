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
    def __init__(self, type, controllerID):
        self.type = type
        self.controllerID = controllerID

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
        'NAO': Province(4, 'North Atlantic Ocean', set(['BAL', 'IRI', 'CLY', 'LVP', 'NWG']), supportsFleets=True),
        'NWG': Province(5, 'Norwegian Sea', set(['NAO', 'CLY', 'EDL', 'NTH', 'NWY', 'BAR']), supportsFleets=True),
        'BAR': Province(6, 'Barents Sea', set(['NWG', 'NWY', 'STP']), supportsFleets=True),
        'BOT': Province(7, 'Gulf of Bothnia', set(['SWE', 'SKA', 'LVN', 'STP', 'FIN']), supportsFleets=True),
        'NTH': Province(8, 'North Sea', set(['NWG', 'EDL', 'YOR', 'LON', 'BEL', 'HOL', 'HEL', 'DEN', 'SWE', 'NWY']), supportsFleets=True),
        'SKA': Province(9, 'Skagerrak', set(['BOT', 'SWE', 'DEN', 'KIE', 'BER', 'PRU', 'LVN']), supportsFleets=True),
        'IRI': Province(10, 'Irish Sea', set(['NAO', 'BAL', 'MAO', 'WAL', 'LVP']), supportsFleets=True),
        'HEL': Province(11, 'Heligoland Bight', set(['NTH', 'HOL', 'KIE', 'DEN']), supportsFleets=True),
        'BAL': Province(12, 'Baltic Sea', set(['NAO', 'NAF', 'POR', 'SPA', 'GAS', 'BRE', 'MAO', 'IRI']), supportsFleets=True),
        'MAO': Province(13, 'Mid Atlantic Ocean', set(['WAL', 'IRI', 'BAL', 'BRE', 'PIC', 'BEL', 'LON']), supportsFleets=True),
        'BLA': Province(15, 'Black Sea', set(['SEV', 'RUM', 'BUL', 'CON', 'AEG', 'ANK', 'ARM']), supportsFleets=True),
        'ADR': Province(16, 'Adriatic Sea', set(['VEN', 'APU', 'ION', 'ALB', 'TRI']), supportsFleets=True),
        'LYO': Province(17, 'Gulf of Lyons', set(['MAR', 'SPA', 'WES', 'TYS', 'TUS', 'PIE']), supportsFleets=True),
        'TYS': Province(18, 'Tyrbennian Sea', set(['TUS', 'LYO', 'WES', 'TUN', 'ION', 'NAP', 'ROM']), supportsFleets=True),
        'WES': Province(19, 'Western Mediterranean Sea', set(['LYO', 'SPA', 'NAF', 'TUN', 'TYS']), supportsFleets=True),
        'ION': Province(20, 'Ionian Sea', set(['NAP', 'TYS', 'TUN', 'EAS', 'AEG', 'GRE', 'ALB', 'ADR', 'APU']), supportsFleets=True),
        'AEG': Province(21, 'Aegean Sea', set(['BUL', 'GRE', 'ION', 'EAS', 'SMY', 'CON', 'BLA']), supportsFleets=True),
        'EAS': Province(22, 'Eastern Mediterranean Sea', set(['SMY', 'AEG', 'ION', 'SYR']), supportsFleets=True),
        # RUSSIA
        'STP': Province(23, 'Saint Petersburg', set(['BAR', 'FIN', 'BOT', 'LVN', 'MOS']), supportsFleets=True, isSupplyDepot=True, unit=Unit('F', 0), controller=0),
        'FIN': Province(24, 'Finland', set(['NWY', 'SWE', 'BOT', 'LVN', 'STP']), supportsFleets=True, controller=0),
        'MOS': Province(25, 'Moscow', set(['STP', 'LVN', 'WAR', 'UKR', 'SEV']), isSupplyDepot=True, unit=Unit('A', 0), controller=0),
        'LVN': Province(26, 'Livonia', set(['FIN', 'BOT', 'SKA', 'PRU', 'WAR', 'MOS', 'STP']), supportsFleets=True, controller=0),
        'WAR': Province(27, 'Warsaw', set(['PRU', 'SIL', 'GAL', 'UKR', 'MOS', 'LVN']), isSupplyDepot=True, unit=Unit('A', 0), controller=0),
        'SEV': Province(28, 'Sevastopol', set(['MOS', 'UKR', 'RUM', 'BLA', 'ARM']), supportsFleets=True, isSupplyDepot=True, unit=Unit('F', 0), controller=0),
        'UKR': Province(29, 'Ukraine', set(['MOS', 'WAR', 'GAL', 'RUM', 'SEV']), controller=0),
        # BRITAIN
        'CLY': Province(30, 'Clyde', set(['NAO', 'LVP', 'EDL', 'NWG']), supportsFleets=True, controller=1),
        'EDL': Province(31, 'None', set(['NWG', 'CLY', 'LVP', 'YOR', 'NTH']), supportsFleets=True, isSupplyDepot=True, unit=Unit('F', 1), controller=1),
        'LVP': Province(32, 'Liverpool', set(['CLY', 'NAO', 'IRI', 'WAL', 'YOR', 'EDL']), supportsFleets=True, isSupplyDepot=True, unit=Unit('A', 1), controller=1),
        'YOR': Province(33, 'Yorkshire', set(['EDL', 'LVP', 'WAL', 'LON', 'NTH']), supportsFleets=True, controller=1),
        'WAL': Province(34, 'Wales', set(['LVP', 'IRI', 'MAO', 'LON', 'YOR']), supportsFleets=True, controller=1),
        'LON': Province(35, 'London', set(['YOR', 'WAL', 'MAO', 'NTH']), supportsFleets=True, isSupplyDepot=True, unit=Unit('F', 1), controller=1),
        # GERMANY
        'KIE': Province(36, 'Kiel', set(['DEN', 'HEL', 'HOL', 'RUH', 'MUN', 'BER', 'SKA']), supportsFleets=True, isSupplyDepot=True, unit=Unit('F', 2), controller=2),
        'BER': Province(37, 'Berlin', set(['SKA', 'KIE', 'MUN', 'SIL', 'PRU']), supportsFleets=True, isSupplyDepot=True, unit=Unit('A', 2), controller=2),
        'PRU': Province(38, 'Prussia', set(['SKA', 'BER', 'SIL', 'WAR', 'LVN']), supportsFleets=True, controller=2),
        'RUH': Province(39, 'Ruhr', set(['KIE', 'HOL', 'BEL', 'PAR', 'MUN']), controller=2),
        'MUN': Province(40, 'Munich', set(['KIE', 'RUH', 'PAR', 'TYR', 'BOH', 'SIL', 'BER']), isSupplyDepot=True, unit=Unit('A', 2), controller=2),
        'SIL': Province(41, 'Silesia', set(['PRU', 'BER', 'MUN', 'BOH', 'GAL', 'WAR']), controller=2),
        # FRANCE
        'BRE': Province(42, 'Brest', set(['MAO', 'BAL', 'GAS', 'BUR', 'PIC']), supportsFleets=True, isSupplyDepot=True, unit=Unit('F', 3), controller=3),
        'PIC': Province(43, 'Picardy', set(['MAO', 'BRE', 'BUR', 'PAR', 'BEL']), supportsFleets=True, controller=3),
        'PAR': Province(44, 'Paris', set(['BEL', 'PIC', 'BUR', 'GAS', 'MAR', 'MUN', 'RUH']), isSupplyDepot=True, unit=Unit('A', 3), controller=3),
        'BUR': Province(45, 'Burgundy', set(['PIC', 'BRE', 'GAS', 'PAR']), controller=3),
        'GAS': Province(46, 'Gascony', set(['BRE', 'BAL', 'SPA', 'MAR', 'PAR', 'BUR']), supportsFleets=True, controller=3),
        'MAR': Province(47, 'Marseilles', set(['PAR', 'GAS', 'SPA', 'LYO', 'PIE']), supportsFleets=True, isSupplyDepot=True, unit=Unit('A', 3), controller=3),
        # AUSTRIA
        'BOH': Province(48, 'Bohemia', set(['SIL', 'MUN', 'TYR', 'VIE', 'GAL']), controller=4),
        'GAL': Province(49, 'Galacia', set(['WAR', 'SIL', 'BOH', 'VIE', 'BUD', 'RUM', 'UKR']), controller=4),
        'TYR': Province(50, 'Tyrolia', set(['BOH', 'MUN', 'PIE', 'VEN', 'TRI', 'VIE']), controller=4),
        'VIE': Province(51, 'Vienna', set(['BOH', 'TYR', 'TRI', 'BUD', 'GAL']), isSupplyDepot=True, unit=Unit('A', 4), controller=4),
        'BUD': Province(52, 'Budapest', set(['GAL', 'VIE', 'TRI', 'SER', 'RUM']), isSupplyDepot=True, unit=Unit('A', 4), controller=4),
        'TRI': Province(53, 'Trieste', set(['VIE', 'TYR', 'VEN', 'ADR', 'ALB', 'SER', 'BUD']), supportsFleets=True, isSupplyDepot=True, unit=Unit('F', 4), controller=4),
        # ITALY
        'PIE': Province(54, 'Piedmont', set(['MAR', 'LYO', 'TUS', 'VEN', 'TYR']), supportsFleets=True, controller=5),
        'VEN': Province(55, 'Venice', set(['TYR', 'PIE', 'TUS', 'ROM', 'APU', 'ADR', 'TRI']), supportsFleets=True, isSupplyDepot=True, unit=Unit('A', 5), controller=5),
        'TUS': Province(56, 'Tuscany', set(['VEN', 'PIE', 'LYO', 'TYS', 'ROM']), supportsFleets=True, controller=5),
        'ROM': Province(57, 'Rome', set(['VEN', 'TUS', 'TYS', 'NAP', 'APU']), supportsFleets=True, isSupplyDepot=True, unit=Unit('A', 5), controller=5),
        'APU': Province(58, 'Apulia', set(['ADR', 'VEN', 'ROM', 'NAP', 'ION']), supportsFleets=True, controller=5),
        'NAP': Province(59, 'Naples', set(['APU', 'ROM', 'TYS', 'ION']), supportsFleets=True, isSupplyDepot=True, unit=Unit('F', 5), controller=5),
        # TURKEY
        'CON': Province(60, 'Constantinople', set(['BLA', 'BUL', 'AEG', 'SMY', 'ANK']), supportsFleets=True, isSupplyDepot=True, unit=Unit('A', 6), controller=6),
        'ANK': Province(61, 'Ankara', set(['BLA', 'CON', 'SMY', 'ARM']), supportsFleets=True, isSupplyDepot=True, unit=Unit('F', 6), controller=6),
        'ARM': Province(62, 'Armenia', set(['SEV', 'BLA', 'ANK', 'SMY', 'SYR']), supportsFleets=True, controller=6),
        'SMY': Province(63, 'Smyrna', set(['ANK', 'CON', 'AEG', 'EAS', 'SYR', 'ARM']), supportsFleets=True, isSupplyDepot=True, unit=Unit('A', 6), controller=6),
        'SYR': Province(64, 'Syria', set(['ARM', 'SMY', 'EAS']), supportsFleets=True, controller=6),
        # NEUTRAL
        'NWY': Province(65, 'Norway', set(['NWG', 'NTH', 'SWE', 'FIN', 'BAR']), supportsFleets=True, isSupplyDepot=True),
        'SWE': Province(66, 'Sweden', set(['NWY', 'NTH', 'DEN', 'SKA', 'BOT', 'FIN']), supportsFleets=True, isSupplyDepot=True),
        'DEN': Province(67, 'Denmark', set(['NTH', 'HEL', 'KIE', 'SWE', 'SKA']), supportsFleets=True),
        'HOL': Province(68, 'Holland', set(['NTH', 'BEL', 'RUH', 'KIE', 'HEL']), supportsFleets=True, isSupplyDepot=True),
        'BEL': Province(69, 'Belgium', set(['HOL', 'NTH', 'MAO', 'PIC', 'PAR', 'RUH']), supportsFleets=True, isSupplyDepot=True),
        'SPA': Province(70, 'Spain', set(['BAL', 'POR', 'NAF', 'WES', 'LYO', 'MAR', 'GAS']), supportsFleets=True, isSupplyDepot=True),
        'POR': Province(71, 'Portugal', set(['BAL', 'SPA']), supportsFleets=True, isSupplyDepot=True),
        'RUM': Province(72, 'Rumania', set(['UKR', 'GAL', 'BUD', 'SER', 'BUL', 'BLA', 'SEV']), supportsFleets=True, isSupplyDepot=True),
        'SER': Province(73, 'Serbia', set(['BUD', 'TRI', 'ALB', 'GRE', 'BUL', 'RUM']), isSupplyDepot=True),
        'BUL': Province(74, 'Bulgaria', set(['RUM', 'SER', 'GRE', 'AEG', 'CON', 'BLA']), supportsFleets=True, isSupplyDepot=True),
        'ALB': Province(75, 'None', set(['SER', 'TRI', 'ADR', 'ION', 'GRE']), supportsFleets=True),
        'GRE': Province(76, 'Greece', set(['SER', 'ALB', 'ION', 'AEG', 'BUL']), supportsFleets=True, isSupplyDepot=True),
        'NAF': Province(77, 'North Africa', set(['BAL', 'WES', 'TUN', 'SPA']), supportsFleets=True),
        'TUN': Province(78, 'Tunis', set(['WES', 'NAF', 'ION', 'TYS']), supportsFleets=True, isSupplyDepot=True),
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

    def getMap(self):
        map = deepcopy(self._baseMap)
        map.putpalette(self._palette)
        for name, province in self.provinces.items():
            if province.unit:
                c = self.countries[province.unit.controllerID]
                self._drawUnit(map, c.fleetIcon if province.unit.type == 'F' else c.armyIcon, coordinates[name])

        return map

    def saveMap(self, filename):
        self.getMap().save(filename)

    def displayMap(self):
        self.getMap().show()

    def placeUnit(self, type, controllerID, province):
        assert not self.provinces[province].unit

        self.provinces[province].unit = Unit(type, controllerID)

    def moveUnit(self, start, end):
        assert self.provinces[start].unit
        assert not self.provinces[end].unit
        if self.provinces[start].unit.type == 'F':
            assert self.provinces[end].supportsFleets
            # If they're both land, do they share a coastline?
            if isLand(start) and isLand(end):
                assert [isOcean(p) for p in
                        self.provinces[end].neighbors &
                        self.provinces[start].neighbors]
            if end in ['SPA', 'STP', 'BUL']:
                end.occupiedCoast = start
            if start in ['SPA', 'STP', 'BUL']:
                pass

        self.provinces[end].unit = self.provinces[start].unit
        self.provinces[start].unit = None

    def deleteUnit(self, province):
        assert self.provinces[province].unit

        self.provinces[province].unit = None

    def getUnitByProvince(self, province):
        return self.provinces[province].unit

    def getUnitsByCountry(self, controllerID):
        return [(name, p.unit) for name, p in self.provinces.items()
                if p.unit and p.unit.controllerID == controllerID]

    def adjacent(self, province1, province2):
        return province2 in self.provinces[province1].neighbors

    def isSupplyDepot(self, province):
        return self.provinces[province].isSupplyDepot

    def changeController(self, province, controllerID):
        p = self.provinces[province]
        p.controller = controllerID
        if self.isLand(province):
            self._setColor(p.index, COUNTRY_COLORS[controllerID])

    def isLand(self, province):
        return self.provinces[province].index > 22

    def isOcean(self, province):
        return not self.isLand(self.province)

# Testing - too lazy to remove
# m = Map()
#
# m.placeUnit('A', 0, 'MUN')
# m.placeUnit('A', 0, 'KIE')
# m.placeUnit('A', 0, 'RUH')
# m.placeUnit('A', 0, 'TYR')
# m.placeUnit('A', 1, 'BOH')
# m.placeUnit('A', 1, 'VIE')
#
# commands = [
#     ('A', 'MUN', 'BOH'),
#     ('A', 'BOH', 'TYR'),
#     ('A', 'TYR', 'MUN'),
# ]
#
# class Command:
#     def __init__(self):
#         self.cmd = 'H'
#         self.target = None
#         self.atk = []
#         self.sup = []
#
#     def __repr__(self):
#         return '%s (%s vs %s)' % (self.cmd, self.atk, self.sup)
#
# q = { n: Command() for n, p in m.provinces.items() if p.unit != None }
#
# for command in commands:
#     if command[0] == 'A':
#         _, f, t = command
#         q[f].cmd = 'A'
#         q[f].target = t
#         if t in q:
#             q[t].atk.append(f)
#     elif command[0] == 'S':
#         _, s, f, t = command
#         q[s].cmd = 'S'
#         q[t].atk.append(s)
#         q[f].sup.append(s)
#     elif command[0] == 'H':
#         pass
#
# def active(p):
#     if p not in q:
#         return False
#     c = q[p]
#     if c.cmd == 'S':
#         if any([x for x in c.atk if active(x)]):
#             return False
#     return True
#
# def support(p):
#     return sum([1 for x in q[p].sup if active(x)])
#
# def succeeds(p):
#     c = q[p]
#     if c.cmd == 'H':
#         if not c.atk:
#             return True
#         return max([support(x) for x in c.atk]) <= support(p)
#     if c.cmd == 'A':
#         if not active(c.target) or (q[c.target].cmd == 'A' and succeeds(c.target)):
#             return True
#         return support(p) > support(c.target)
#     if c.cmd == 'S':
#         return not active(p)
#
# for p in q.keys():
#     # print("On: %s" % p)
#     print("%s: %s" % (p, "succeeds" if succeeds(p) else "fails"))
#
# start = q.keys()[0]
# solve(start)
#
# print(q)
# m.saveMap('maptest.png')
# m.displayMap()