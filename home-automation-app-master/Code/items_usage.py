import datetime, models
from dateutil.parser import parse

# this function handles logging usage for all power and water happening in real time. 
def setUsage(app, item_id, cur_state, usage_start = None, usage_time = 0):
    start = datetime.datetime.now().strftime("%m/%d/%Y %H:%M:%S")
    with app.app_context():
        # create a usage entry with a 0 value 
        if cur_state == True:
            # ignore windows and doors for power and water, but adjust the open variable for HVAC. 
            if models.db.session.query(models.Item).filter_by(id=item_id).first().type == 'opening':
                if models.db.session.query(models.Item).filter_by(id=item_id).first().name == 'Window':
                    models.HVAC.openWindow += 1
                    print(models.HVAC.openWindow)
                    return
                else:
                    models.HVAC.openDoor += 1
                    print(models.HVAC.openDoor)
                    return
            usage = models.Usage(start, item_id)
            models.db.session.add(usage)
            models.db.session.commit()
        # this catches usage passed as historical and is used in the the manual creation such as the usage at first launch. 
        elif cur_state == 'Historical':
            if models.db.session.query(models.Item).filter_by(id=item_id).first().type == 'opening':
                if models.db.session.query(models.Item).filter_by(id=item_id).first().name == 'Window':
                    models.HVAC.openWindow += 1
                    models.HVAC.openWindow -= 1
                    return
                else:
                    models.HVAC.openDoor += 1
                    models.HVAC.openDoor -= 1
                    return
            s = models.db.session()
            s.expire_on_commit = False
            usage_start = usage_start.strftime("%m/%d/%Y %H:%M:%S")
            usage = models.Usage(usage_start, item_id, usage_time)
            this_usage = calcTotalUsage(app, item_id, usage_time)
            power_consumption = s.query(models.Sensor).filter_by(name="Power Consumption").first()
            water_consumption = s.query(models.Sensor).filter_by(name="Water Consumption").first()
            power_consumption.value += this_usage[0]
            water_consumption.value += this_usage[1]
            s.add(usage)
            s.commit()
            s.close()
        # if the item is toggled off, the usage entry is found, updated with the total amount of time it was on.
        else:
            usage = models.db.session.query(models.Usage).filter(models.Usage.item_id == item_id).all()
            for use in usage:
                if use.usage == 0:
                    if models.db.session.query(models.Item).filter_by(id=item_id).first().type == 'opening':
                        if models.db.session.query(models.Item).filter_by(id=item_id).first().name == 'Window':
                            models.HVAC.openWindow -= 1
                            print(models.HVAC.openWindow)
                            continue
                        else:
                            models.HVAC.openDoor -= 1
                            print(models.HVAC.openDoor)
                            continue
                    calc_usage = datetime.datetime.now() - parse(use.start_time)
                    use.usage = calc_usage.seconds
                    total_consumption = calcTotalUsage(app, item_id, calc_usage.seconds)
                    power_consumption = models.db.session.query(models.Sensor).filter_by(name="Power Consumption").first()
                    water_consumption = models.db.session.query(models.Sensor).filter_by(name="Water Consumption").first()
                    power_consumption.value += total_consumption[0]
                    water_consumption.value += total_consumption[1]
                    models.db.session.commit()

# this function calculates the usage and converts it to kwh and gal. This is the same as in the usage.py script with minor changes.        
def calcTotalUsage(app, item_id, usage):
    
    wattages = {
    "Overhead Light" : 60,
    "Lamp" : 60,
    "Exhaust Fan" : 30,
    "HVAC" : 3500,
    "Refrigerator" : 150,
    "Microwave" : 1100,
    "Stove" : 3500,
    "Oven" : 4000,
    "Small TV" : 100,
    "Large TV" : 636
    }

    with app.app_context():
        #[powerUsage, waterUsage, totalCost]
        final = [0,0,0]
            
        #Query item from database
        item = models.db.session.query(models.Item).filter_by(id = item_id).first()
        name = item.name

        if item.type == "opening":
            return
        #if a TV, check which room the TV is in
        if name == "TV":
            room_id = item.room_id
            roomName = models.db.session.query(models.Room).filter_by(id = room_id).first().name
            if roomName == "Living Room":
                time = usage/60/60
                final[0] += time*wattages["Large TV"]
            else:
                time = usage/60/60
                final[0] += time*wattages["Small TV"]
        elif name == "Bathtub":
            final[0] += 5850
            final[1] += 30
        elif name == "Shower":
            final[0] += 4875
            final[1] += 25
        elif name == "Toilet":
            final[1] += 1.6
        elif name == "Dishwasher":
            final[0] += 3150
            final[1] += 6
        elif name == "Washer":
            final[0] += 5350
            final[1] += 20
        elif name == "Dryer":
            final[0] += 1.5
            final[1] += 1
        elif name == "Outdoor faucet":
            final[1] += usage/60*2
        elif name == "Sink":
            final[0] += usage/60*300
            final[1] += usage/60*2

        #calculate elec usage
        else:
            time = usage/60/60
            final[0] += time*wattages[name]
        
        #convert to kWh
        final[0] = final[0]/1000

        #calculate cost of power + water
        final[2] = final[0]*0.12
        final[2] += final[1]/748*2.52
        
        return final
