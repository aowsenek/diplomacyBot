
class Command:
    def __init__(self):
        self.cmd = 'H'
        self.target = None
        self.atk = []
        self.sup = []

    def __repr__(self):
        return '%s (%s vs %s)' % (self.cmd, self.atk, self.sup)

countries = {1: "Russia",
             2: "England",
             3: "Germany",
             4: "France",
             5: "Austria",
             6: "Italy",
             7: "Turkey"}

def move(map_,orders_):
    q = { n: Command() for n, p in map_.provinces.items() if p.unit != None }
    orders = []
    for i in countries:
        orders = orders + orders_[i]
    for command in orders:
     #   print(command)
        if command[2] == '-':
            _, f,a,t = command
            q[a].cmd = '-'
            q[f].target = t
            if t in q:
                q[t].atk.append(f)
        elif command[2] == 'S':
            try:
                _, lc1, s, f,a,t = command
            except ValueError:
                _, lc1, s, f,a = command

            q[s].cmd = 'S'
            q[t].atk.append(s)
            q[f].sup.append(s)
        elif command[2] == 'H':
            pass

    success = []
    fails = []
    retreats = []
    for p in q.keys():
        if succeeds(p,q):
            success.append(p)
            if(q[p].cmd == '-'):
                try:
                    map_.moveUnit(p,q[p].target)
                except AssertionError:
                    retreats.append((map_.getUnitByProvince(q[p].target),q[p].target)) #unit,prev location
                    map_.deleteUnit(q[p].target)
                    map_.moveUnit(p,q[p].target)
            else:
                pass
        else:
            fails.append(p)
    return retreats


def active(p,q):
    if p not in q:
        return False
    c = q[p]
    if c.cmd == 'S':
        if any([x for x in c.atk if active(x,q)]):
            return False
    return True

def support(p,q):
    return sum([1 for x in q[p].sup if active(x,q)])

def succeeds(p,q):
    c = q[p]
    if c.cmd == 'H':
        if not c.atk:
            return True
        return max([support(x,q) for x in c.atk]) <= support(p,q)
    if c.cmd == '-':
        if not active(c.target,q) or (q[c.target].cmd == '-' and succeeds(c.target,q)):
            return True
        return support(p,q) > support(c.target,q)
    if c.cmd == 'S':
        return not active(p,q)

def retreat(orders_,retreats):
    for u,loc in retreats:
        try:
            newLoc = None
            for i in orders_.values():
                if(i[1] == loc):
                    newLoc = i[3]
            if(newLoc):
                if(map_.isValidRetreat(u.type, loc, newLoc)):
                    map_.placeUnit(u.type, u.controllerID, newLoc)
        except AssertionError: pass

def build(players,map_):
    unitsToBuild = {1:0,2:0,3:0,4:0,5:0,6:0,7:0}
    for i in players:
        ctry = players[i][1]
        units = map_.getUnitsByCountry(ctry)
        for loc,u in units:
            map_.changeController(loc,ctry)
        supplyDepots =  len(map_.getOwnedSupplyDepots(ctry))
        unitsToBuild[ctry] =  supplyDepots - len(units)
    return unitsToBuild

def resolveWinterOrders(players, map_, orders, unitsToBuild):
    for i in players:
        ctry = players[i][1]
        if(unitsToBuild[ctry] > 0): #Build Units
            unitsBuilt = 0
            for i in orders[ctry]:
                if(unitsBuilt < unitsToBuild[ctry]):
                    map_.placeUnit(i[0],ctry,i[1])
                    unitsBuilt += 1
        elif(unitsToBuild[ctry] < 0): #Delete Units
            if(orders[ctry] >= unitsToBuild[ctry]):
                unitsRemoved = 0
                for i in orders[ctry]:
                    if(unitsRemoved < unitsToBuild[ctry]):
                        map_.deleteUnit(i[1])
                        unitsRemoved += 1
            else:
                unitsRemoved = 0
                units = map_.getUnitsByCountry(ctry)
                for i in orders[ctry]:
                    if(unitsRemoved < unitsToBuild[ctry]):
                        map_.deleteUnit(i[1])
                        unitsRemoved += 1
                for i in units:
                    if(unitsRemoved < unitsToBuild[ctry]):
                        map_.deleteUnit(i[1])
                        unitsRemoved += 1
        else: pass #No units to remove or add

