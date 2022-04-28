import datetime, random, models, usage
import items_usage as iu

# create random index for random item usage.
def generateRandomID(list):
    return random.choice(list).id

# create all historical usage as defined by the project doc. Takes into account the time people are home/awake and randomly generates data for usage over a passed in range.
def historical_life(app, days):
    with app.app_context():
        power_items = models.db.session.query(models.Item).filter(models.Item.type == 'power').all()
        water_items = models.db.session.query(models.Item).filter(models.Item.type == 'water').all()
        light = models.db.session.query(models.Item).filter(models.Item.type == 'light').all()
        door = models.db.session.query(models.Item).filter(models.Item.type == 'opening', models.Item.name != 'Window').all()
        window = models.db.session.query(models.Item).filter(models.Item.type == 'opening', models.Item.name == 'Window').all()
        for item in power_items:
            if item.name == 'Microwave':
                microwave_id = item.id
            elif item.name == 'Stove':
                stove_id = item.id
            elif item.name == 'Oven':
                oven_id = item.id
            elif item.name == 'Dishwasher':
                dishwasher_id = item.id
            elif item.name == 'Washer':
                washer_id = item.id
            elif item.name == 'Dryer':
                dryer_id = item.id 
            elif item.name == 'TV':
                if item.room_id == models.db.session.query(models.Room).filter_by(name='Living Room').first().id:
                    lr_tv_id = item.id
                else:
                    br_tv_id = item.id
        shower = []
        for item in water_items:
            if item.name == 'Shower':
                shower.append(item)
            elif item.name == 'Bathtub':
                bath_id = item.id 
        lists = {'power': power_items, 'water': water_items, 'light': light, 'door': door, 'window': window, 'shower': shower}
        # loop over the passed in days. 
        for i in range(days):
            print('Day' + ' ' + str(i))
            day = datetime.datetime.today() - datetime.timedelta(days=days-i)
            # condition for weekdays
            if day.weekday() < 5:
                items_list = [
                    {'name': 'door', 'toggle': 0, 'uses': 16, 'item_id': generateRandomID(door), 'usage': 0.5}, 
                    {'name': 'window', 'toggle': 0, 'uses': 8, 'item_id': generateRandomID(window), 'usage': 10}, 
                    {'name': 'light', 'toggle': 0, 'uses': 32, 'item_id': generateRandomID(light), 'usage': 30}, 
                    {'name': 'microwave', 'toggle': 0, 'uses': 1, 'item_id': microwave_id, 'usage': 20}, 
                    {'name': 'stove', 'toggle': 0, 'uses': 1, 'item_id': stove_id, 'usage': 15}, 
                    {'name': 'oven', 'toggle': 0, 'uses': 1, 'item_id': oven_id, 'usage': 45}, 
                    {'name': 'lr_tv', 'toggle': 0, 'uses': 4, 'item_id': lr_tv_id, 'usage': 60}, 
                    {'name': 'br_tv', 'toggle': 0, 'uses': 2, 'item_id': br_tv_id, 'usage': 60}, 
                    {'name': 'shower', 'toggle': 0, 'uses': 2, 'item_id': generateRandomID(shower), 'usage': 15}, 
                    {'name': 'bath', 'toggle': 0, 'uses': 2, 'item_id': bath_id, 'usage': 30},
                    {'name': 'dishwasher', 'toggle': 0, 'uses': 4, 'item_id': dishwasher_id, 'usage': 45},
                    {'name': 'washer', 'toggle': 0, 'uses': 4, 'item_id': washer_id, 'usage': 30},
                    {'name': 'dryer', 'toggle': 0, 'uses': 4, 'item_id': dryer_id, 'usage': 30}]
                hour = 0
                minute = 0
                #condition for half hours of each day. 
                for i in range(47):
                    c_time = datetime.datetime(day.year, day.month, day.day, hour, minute)
                    # parents schedule
                    if ((c_time > datetime.datetime(day.year, day.month, day.day, 5, 0) and
                        c_time < datetime.datetime(day.year, day.month, day.day, 7, 30)) or
                        (c_time > datetime.datetime(day.year, day.month, day.day, 17, 30) and
                        c_time < datetime.datetime(day.year, day.month, day.day, 22, 30))):
                        # create data for each item in the list.
                        for item in items_list:
                            if item['name'] == 'door' or item['name'] == 'window' or item['name'] == 'light' or item['name'] == 'shower':
                                item['item_id'] = generateRandomID(lists[item['name']])
                            item['toggle'] = random.randint(0,1)
                            if item['toggle'] == 1:
                                if item['uses'] != 0:
                                    item['uses'] -= 1
                                    iu.setUsage(app, item['item_id'], 'Historical', c_time, item['usage'] * 60)
                            else:
                                pass    
                    else:
                        pass
                    # kids schedule
                    if ((c_time > datetime.datetime(day.year, day.month, day.day, 6, 0) and
                        c_time < datetime.datetime(day.year, day.month, day.day, 7, 30)) or
                        (c_time > datetime.datetime(day.year, day.month, day.day, 16, 0) and
                        c_time < datetime.datetime(day.year, day.month, day.day, 20, 30))):
                        
                        # create data for each item in the list.
                        for item in items_list:
                            if item['name'] == 'door' or item['name'] == 'window' or item['name'] == 'light' or item['name'] == 'shower':
                                item['item_id'] = generateRandomID(lists[item['name']])
                            item['toggle'] = random.randint(0,1)
                            if item['toggle'] == 1:
                                if item['uses'] != 0:
                                    item['uses'] -= 1
                                    iu.setUsage(app, item['item_id'], 'Historical', c_time, item['usage'] * 60)
                            else:
                                pass 
                    else:
                        pass
                    # adjust hour and minute variables for half hour increments.
                    if i == 0 or i % 2 == 0:
                        hour += 1
                        minute = 0
                    elif i % 2 != 0:
                        minute = 30
            # weekend schedule
            else:
                items_list = [
                    {'name': 'door', 'toggle': 0, 'uses': 32, 'item_id': generateRandomID(door), 'usage': 0.5}, 
                    {'name': 'window', 'toggle': 0, 'uses': 16, 'item_id': generateRandomID(window), 'usage': 10}, 
                    {'name': 'light', 'toggle': 0, 'uses': 64, 'item_id': generateRandomID(light), 'usage': 30}, 
                    {'name': 'microwave', 'toggle': 0, 'uses': 1, 'item_id': microwave_id, 'usage': 30}, 
                    {'name': 'stove', 'toggle': 0, 'uses': 1, 'item_id': stove_id, 'usage': 30}, 
                    {'name': 'oven', 'toggle': 0, 'uses': 1, 'item_id': oven_id, 'usage': 60}, 
                    {'name': 'lr_tv', 'toggle': 0, 'uses': 8, 'item_id': lr_tv_id, 'usage': 60}, 
                    {'name': 'br_tv', 'toggle': 0, 'uses': 4, 'item_id': br_tv_id, 'usage': 60}, 
                    {'name': 'shower', 'toggle': 0, 'uses': 3, 'item_id': generateRandomID(shower), 'usage': 15}, 
                    {'name': 'bath', 'toggle': 0, 'uses': 3, 'item_id': bath_id, 'usage': 30}]
                hour = 0
                minute = 0
                #condition for half hours of each day.
                for i in range(47):
                    c_time = datetime.datetime(day.year, day.month, day.day, hour, minute)
                    #parents schedule
                    if (c_time > datetime.datetime(day.year, day.month, day.day, 5, 0) and
                        c_time < datetime.datetime(day.year, day.month, day.day, 22, 30)):
                        # create data for each item in the list.
                        for item in items_list:
                            if item['name'] == 'door' or item['name'] == 'window' or item['name'] == 'light' or item['name'] == 'shower':
                                item['item_id'] = generateRandomID(lists[item['name']])
                            item['toggle'] = random.randint(0,1)
                            if item['toggle'] == 1:
                                if item['uses'] != 0:
                                    item['uses'] -= 1
                                    iu.setUsage(app, item['item_id'], 'Historical', c_time, item['usage'] * 60)
                            else:
                                pass
                    else:
                        pass
                    # kids schedule
                    if (c_time > datetime.datetime(day.year, day.month, day.day, 6, 0) and
                        c_time < datetime.datetime(day.year, day.month, day.day, 20, 30)):
                        # create data for each item in the list.
                        for item in items_list:
                            if item['name'] == 'door' or item['name'] == 'window' or item['name'] == 'light' or item['name'] == 'shower':
                                item['item_id'] = generateRandomID(lists[item['name']])
                            item['toggle'] = random.randint(0,1)
                            if item['toggle'] == 1:
                                if item['uses'] != 0:
                                    item['uses'] -= 1
                                    iu.setUsage(app, item['item_id'], 'Historical', c_time, item['usage'] * 60)
                            else:
                                pass
                    else:
                        pass
                    # adjust hour and minute variables for half hour increments.
                    if i == 0 or i % 2 == 0:
                        hour += 1
                        minute = 0
                    elif i % 2 != 0:
                        minute = 30
        #DB calls
        historical_usage = models.Usage.query.all()
        usageValues = usage.checkTotalUsage(app, historical_usage)
        print(usageValues)
        power_consumption = models.Sensor.query.filter_by(name="Power Consumption").first()
        print(power_consumption)
        water_consumption = models.Sensor.query.filter_by(name="Water Consumption").first()
        print(water_consumption)
        power_consumption.value = usageValues[0]
        models.db.session.commit()
        water_consumption.value = usageValues[1]
        models.db.session.commit()
        print(models.db.session.query(models.Sensor).filter_by(name="Power Consumption").first(), models.db.session.query(models.Sensor).filter_by(name="Water Consumption").first())

# function for shower scene
def takeShower(app):
    with app.app_context():
        shower = models.db.session.query(models.Item).filter(models.Item.type == 'water', models.Item.name == 'Shower').first()
        iu.setUsage(app, shower.id, 'Historical', datetime.datetime.now(), 1)
# function for dishwasher scene
def runDishwasher(app):
    with app.app_context():
        dishwasher = models.db.session.query(models.Item).filter(models.Item.type == 'power', models.Item.name == 'Dishwasher').first()
        iu.setUsage(app, dishwasher.id, 'Historical', datetime.datetime.now(), 1)
# function for party scene
def haveParty(app):
    with app.app_context():
        toilet = models.db.session.query(models.Item).filter(models.Item.type == 'water', models.Item.name == "toilet").all()
        light = models.db.session.query(models.Item).filter(models.Item.type == 'light').all()
        for t in toilet:
            for i in range(0,5):
                iu.setUsage(app, t.id, 'Historical', datetime.datetime.now(), 1)
        for l in light:
            iu.setUsage(app, l.id, 'Historical', datetime.datetime.now(), 4 * 60)

