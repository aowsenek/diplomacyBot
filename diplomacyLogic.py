from diplomacyData import ddata

class Command:
    def __init__(self):
        self.cmd = 'H'
        self.target = None
        self.atk = []
        self.sup = []

    def __repr__(self):
        return '%s (%s vs %s)' % (self.cmd, self.atk, self.sup)

class Game():
    def __init__(self):
        pass
    def move(self,ddata):
        orders = { n: Command() for n, p in ddata.map.provinces.items() if p.unit != None }
        ordrs = []
        for ctry in ddata.getPCountries():
            ordrs = ordrs + ddata.getOrdersbyCID(ctry)
        for command in ordrs:
            if command[2] == '-':
                _, attacker, _, target = command
                try:
                    orders[attacker].cmd = '-'
                    orders[attacker].target = target
                    if target in orders:
                        orders[target].atk.append(attacker)
                except KeyError: continue
            elif command[2] == 'S':
                try:
                    _, _, self.supporter, attacker, _, target = command
                except ValueError:
                    _, _, self.supporter, attacker, _ = command
                try:
                    orders[self.supporter].cmd = 'S'
                    orders[target].atk.append(self.supporter)
                    orders[attacker].sup.append(self.supporter)
                except KeyError: continue
            elif command[2] == 'H':
                pass
        success = []
        fails = []
        retreats = []
        for p in orders.keys():
            if self.succeeds(p,orders):
                success.append(p)
                if(orders[p].cmd == '-'):
                    try:
                        ddata.map.moveUnit(p,orders[p].target)
                    except AssertionError:
                        ddata.addRetreat(ddata.map.getUnitByProvince(orders[p].target),orders[p].target) #unit,prev location
                        ddata.map.deleteUnit(orders[p].target)
                        ddata.map.moveUnit(p,orders[p].target)
                else:
                    pass
            else:
                fails.append(p)

    def active(self,p,q):
        if p not in q:
            return False
        c = q[p]
        if c.cmd == 'S':
            if any([x for x in c.atk if self.active(x,q)]):
                return False
        return True

    def support(self,p,q):
        return sum([1 for x in q[p].sup if self.active(x,q)])

    def succeeds(self,p,q):
        c = q[p]
        if c.cmd == 'H':
            if not c.atk:
                return True
            return max([self.support(x,q) for x in c.atk]) <= self.support(p,q)
        if c.cmd == '-':
            if not self.active(c.target,q) or (q[c.target].cmd == '-' and self.succeeds(c.target,q)):
                return True
            return self.support(p,q) > self.support(c.target,q)
        if c.cmd == 'S':
            return not self.active(p,q)

    def retreat(self,ddata):
        ordrs = []
        for ctry in ddata.getPCountries():
            ordrs = ordrs + ddata.getOrdersbyCID(ctry)
        for u,loc in ddata.getRetreats():
            try:
                newLoc = None
                for i in ordrs:
                    if(i[1] == loc):
                        newLoc = i[3]
                if(newLoc):
                    if(ddata.map.isValidRetreat(u.type, loc, newLoc)):
                        ddata.map.placeUnit(u.type, u.controllerID, newLoc)
            except AssertionError: pass

    def build(self,ddata):
        for ctry in ddata.getPCountries():
            units = ddata.map.getUnitsByCountry(ctry)
            for loc,u in units:
                ddata.map.changeController(loc,ctry)
            supplyDepots =  len(ddata.map.getOwnedSupplyDepots(ctry))
            ddata.setNumBuild(ctry, supplyDepots - len(units))

    def resolveWinterOrders(self,ddata):
        for ctry in ddata.getPCountries():

            if(ddata.getNumBuild(ctry) > 0): #Build Units
                unitsBuilt = 0
                for i in ddata.getOrdersbyCID(ctry):
                    if(unitsBuilt < ddata.getNumBuild(ctry)):
                        ddata.map.placeUnit(i[0],ctry,i[1])
                        unitsBuilt += 1
            elif(ddata.getNumBuild(ctry) < 0): #Delete Units
                if(ddata.getOrdersbyCID(ctry) >= ddata.getNumBuild(ctry)):
                    unitsRemoved = 0
                    for i in ddata.getOrdersbyCID(ctry):
                        if(unitsRemoved < ddata.getNumBuild(ctry)):
                            ddata.map.deleteUnit(i[1])
                            unitsRemoved += 1
                else:
                    unitsRemoved = 0
                    units = ddata.map.getUnitsByCountry(ctry)
                    for i in ddata.getOrdersbyCID(ctry):
                        if(unitsRemoved < ddata.getNumBuild(ctry)):
                            ddata.map.deleteUnit(i[1])
                            unitsRemoved += 1
                    for i in units:
                        if(unitsRemoved < ddata.getNumBuild(ctry)):
                            ddata.map.deleteUnit(i[1])
                            unitsRemoved += 1
            else: pass #No units to remove or add

    def adjudicate(self,ddata):
        if(ddata.getSeason() in ["SPRING","FALL"]):
            if(ddata.getResolving() == True):
                self.retreat(ddata) #handles retreat orders
                ddata.setResolving(False)
            else:
                self.move(ddata)
                if(ddata.getRetreats() != []):
                    ddata.setResolving(True)
                    #self.springFall()
                    ddata.reset()
                    return

            if(ddata.getSeason() == "SPRING"):
                ddata.changeSeason()
                #self.springFall()
            else:
                ddata.changeSeason()
                #self.winter()
        elif(ddata.season == "WINTER"):
            self.resolveWinterOrders(ddata)
            ddata.changeSeason()
            ddata.incrementDate()
        ddata.reset()


