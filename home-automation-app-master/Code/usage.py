import models
import datetime
import calendar
import json


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

#return total power usage, water usage, and cost from list of usage entries
def checkTotalUsage(app, usages):

    with app.app_context():
        #[powerUsage, waterUsage, totalCost]
        final = [0,0,0]

        #run cycle or calculate power usage
        for usage in usages:
            
            #Query item from database
            item = models.db.session.query(models.Item).filter_by(id = usage.item_id).first()
            name = item.name

            if item.type == "opening":
                continue
            #if a TV, check which room the TV is in
            if name == "TV":
                room_id = item.room_id
                roomName = models.db.session.query(models.Room).filter_by(id = room_id).first().name
                if roomName == "Living Room":
                    time = usage.usage/60/60
                    final[0] += time*wattages["Large TV"]
                else:
                    time = usage.usage/60/60
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
                final[1] += usage.usage/60*2
            elif name == "Sink":
                final[0] += usage.usage/60*300
                final[1] += usage.usage/60*2

            #calculate elec usage
            else:
                time = usage.usage/60/60
                final[0] += time*wattages[name]
        
        #convert to kWh
        final[0] = final[0]/1000

        #calculate cost of power + water
        final[2] = final[0]*0.12
        final[2] += final[1]/748*2.52
        
        return final



#function to generate estimated usage increase from given usage values
def estimateUsage(values, time):
    #index at which estimated usage starts
    estIndex = len(values)+1
    
    #remove duplicates
    last = values[-1]
    if last == 0:
        return values, 0
    nex = values[-2]
    if nex == last:
        while nex == last:
            values.pop()
            nex = values[-1]
            estIndex -= 1
        values.append(last)
    else:
        return values, estIndex

    #calculate average increase in values
    avgInc = values[-1]/(len(values)-1)

    if time == "day":
        while len(values) < 9:
            values.append(values[-1] + avgInc)
    elif time == "week":
        while len(values) < 8:
            values.append(values[-1] + avgInc)
    elif time == "month":
        while len(values) < 11:
            values.append(values[-1] + avgInc)
    return values, estIndex

#function to generate labels and values for a usage chart over the specified day
#
#Returns a tuple with four lists: labels, powerValues, waterValues, and costValues
def dayChartValues(app, month, day, year):

    with app.app_context():
        #query the database for all entries from specified day
        startDay = datetime.datetime(year, month, day, 0, 0, 0)
        endDay = startDay + datetime.timedelta(days=1)

        entries = iter(models.db.session.query(models.Usage).filter(models.Usage.start_time > startDay.strftime("%m/%d/%Y %H:%M:%S"), models.Usage.start_time < endDay.strftime("%m/%d/%Y %H:%M:%S"), models.Usage.usage > 0).order_by(models.Usage.start_time.asc()).all())

        #generate labels for each 3 hr section of the day
        labels = []
        time = startDay
        trigger = 0
        while len(labels) < 9:
            #the first label that is in the future is labeled as "Now"
            if time > datetime.datetime.now() and trigger == 0:
                labels.append("Now")
                trigger = 1
                time = time + datetime.timedelta(hours = 3)
                continue
            labels.append(time.strftime("%I %p"))
            time = time + datetime.timedelta(hours = 3)
        
        #calculate increases in usage totals over each 3 hr section of the day
        time = startDay + datetime.timedelta(hours = 3)
        chunk = []
        powerValues = [0]
        waterValues = [0]
        costValues = [0]
        new = next(entries, None)

        for i in range(7):
            while new != None and new.start_time < time.strftime("%m/%d/%Y %H:%M:%S"):
                chunk.append(new)
                new = next(entries, None)
            added = checkTotalUsage(app, chunk)
            powerValues.append(powerValues[-1] + added[0])
            waterValues.append(waterValues[-1] + added[1])
            costValues.append(costValues[-1] + added[2])
            time = time + datetime.timedelta(hours = 3)
            chunk = []
        while new != None:
            chunk.append(new)
            new = next(entries, None)
        added = checkTotalUsage(app, chunk)
        powerValues.append(powerValues[-1] + added[0])
        waterValues.append(waterValues[-1] + added[1])
        costValues.append(costValues[-1] + added[2])

        #calculate estimated usage increases
        powerValues, estIndex = estimateUsage(powerValues, "day")
        waterValues, estIndex = estimateUsage(waterValues, "day")
        costValues, estIndex = estimateUsage(costValues, "day")
        
        #round values for graph representation
        for i in range(len(powerValues)):
            powerValues[i] = round(powerValues[i], 2)
            waterValues[i] = round(waterValues[i], 2)
            costValues[i] = round(costValues[i], 2)
        estIndex -= 1

        #store values in DB for future use
        day = startDay.strftime("%m/%d/%Y")
        pow = json.dumps(powerValues)
        wat = json.dumps(waterValues)
        cos = json.dumps(costValues)

        #check if day already exists in database, ifso update values
        if models.db.session.query(models.History).filter_by(type="day", date=day).first() != None:
            models.db.session.query(models.History).filter_by(type="day", date=day).update({models.History.powervalues: pow, models.History.watervalues: wat, models.History.costvalues: cos})
        else:
            models.db.session.add(models.History("day", day, pow, wat, cos))
        models.db.session.commit()

        return labels, powerValues, waterValues, costValues, estIndex

#function to generate labels and values for a usage chart over the specified week
#
#Returns a tuple with four lists: labels, powerValues, waterValues, and costValues
def weekChartValues(app, month, startDay, year):
    
    with app.app_context():
        #query the database for all entries since the start of this week
        startWeek = datetime.datetime(year, month, startDay, 0, 0, 0)
        endWeek = startWeek + datetime.timedelta(days = 7)

        entries = iter(models.db.session.query(models.Usage).filter(models.Usage.start_time > startWeek.strftime("%m/%d/%Y %H:%M:%S"), models.Usage.start_time < endWeek.strftime("%m/%d/%Y %H:%M:%S"), models.Usage.usage > 0).order_by(models.Usage.start_time.asc()).all())

        #generate labels for each day from the past week till now
        labels = []
        time = startWeek
        trigger = 0
        while len(labels) < 7:
            #check if time is today
            if time.date() == datetime.datetime.now().date() and trigger == 0:
                labels.append("Today")
                trigger = 1
                time = time + datetime.timedelta(days = 1)
                continue
            labels.append(time.strftime("%a %m/%d"))
            time = time + datetime.timedelta(days = 1)

        #calculate increases in usage totals over each day section of the past week till now
        time = startWeek + datetime.timedelta(days = 1)
        chunk = []
        powerValues = [0]
        waterValues = [0]
        costValues = [0]
        new = next(entries, None)
        
        for i in range(6):
            while new != None and new.start_time < time.strftime("%m/%d/%Y %H:%M:%S"):
                chunk.append(new)
                new = next(entries, None)
            added = checkTotalUsage(app, chunk)
            powerValues.append(powerValues[-1] + added[0])
            waterValues.append(waterValues[-1] + added[1])
            costValues.append(costValues[-1] + added[2])
            time = time + datetime.timedelta(days = 1)
            chunk = []
        while new != None:
            chunk.append(new)
            new = next(entries, None)
        added = checkTotalUsage(app, chunk)
        powerValues.append(powerValues[-1] + added[0])
        waterValues.append(waterValues[-1] + added[1])
        costValues.append(costValues[-1] + added[2])

        #calculate estimated usage increases
        powerValues, estIndex = estimateUsage(powerValues, "week")
        waterValues, estIndex = estimateUsage(waterValues, "week")
        costValues, estIndex = estimateUsage(costValues, "week")
        estIndex -= 2 #adjust for removing the first 0 value from the list

        #round values for graph representation
        for i in range(len(powerValues)):
            powerValues[i] = round(powerValues[i], 2)
            waterValues[i] = round(waterValues[i], 2)
            costValues[i] = round(costValues[i], 2)

        #store values in DB for future use
        week = startWeek.strftime("%m/%d/%Y")
        pow = json.dumps(powerValues)
        wat = json.dumps(waterValues)
        cos = json.dumps(costValues)
        
        #check week already exists in the database, if so update the values
        if models.db.session.query(models.History).filter_by(type="week", date=week).first() != None:
            models.db.session.query(models.History).filter_by(type="week", date=week).update({models.History.powervalues: pow, models.History.watervalues: wat, models.History.costvalues: cos})
        else:
            models.db.session.add(models.History("week", week, pow, wat, cos))
        models.db.session.commit()

        return labels, powerValues[1:], waterValues[1:], costValues[1:], estIndex

#function to generate labels and values for a usage chart over the specified month
#
#Returns a tuple with four lists: labels, powerValues, waterValues, and costValues
def monthChartValues(app, month, year):
        
    with app.app_context():
        #datetime objects for the start and end of the specified month
        startMonth = datetime.datetime(year, month, 1)
        endMonth = datetime.datetime(year, month, calendar.monthrange(year, month)[1], hour=23, minute=59, second=59, microsecond=0)

        #query the database for all entries between the start and end of the specified month
        entries = iter(models.db.session.query(models.Usage).filter(models.Usage.start_time > startMonth.strftime("%m/%d/%Y %H:%M:%S"), models.Usage.start_time < endMonth.strftime("%m/%d/%Y %H:%M:%S"), models.Usage.usage > 0).order_by(models.Usage.start_time.asc()).all())

        #generate labels for each 3 day section of the specified month
        labels = []
        time = startMonth.replace(day=3)
        trigger = 0
        while len(labels) < 9:
            #check if time is today
            if time.date() >= datetime.datetime.now().date() and trigger == 0:
                labels.append("Today")
                trigger = 1
                time = time + datetime.timedelta(days = 3)
                continue
            labels.append(time.strftime("%m/%d"))
            time = time + datetime.timedelta(days = 3)
        labels.append(endMonth.strftime("%m/%d"))

        #calculate increases in usage totals over each 3 day section of the specified month
        time = startMonth.replace(day=3, hour=23, minute=59, second=59, microsecond=0)
        chunk = []
        powerValues = [0]
        waterValues = [0]
        costValues = [0]
        new = next(entries, None)

        for i in range(10):
            while new != None and new.start_time < time.strftime("%m/%d/%Y %H:%M:%S"):
                chunk.append(new)
                new = next(entries, None)
            added = checkTotalUsage(app, chunk)
            powerValues.append(powerValues[-1] + added[0])
            waterValues.append(waterValues[-1] + added[1])
            costValues.append(costValues[-1] + added[2])
            time = time + datetime.timedelta(days = 3)
            chunk = []
        while new != None:
            chunk.append(new)
            new = next(entries, None)
        added = checkTotalUsage(app, chunk)
        powerValues.append(powerValues[-1] + added[0])
        waterValues.append(waterValues[-1] + added[1])
        costValues.append(costValues[-1] + added[2])

        #calculate estimated usage increases
        powerValues, estIndex = estimateUsage(powerValues, "month")
        waterValues, estIndex = estimateUsage(waterValues, "month")
        costValues, estIndex = estimateUsage(costValues, "month")
        estIndex -= 2 #adjust for removing the first 0 value from the list

        #round values for graph representation
        for i in range(len(powerValues)):
            powerValues[i] = round(powerValues[i], 2)
            waterValues[i] = round(waterValues[i], 2)
            costValues[i] = round(costValues[i], 2)

        #store the values in DB for future use
        month = startMonth.strftime("%m/%Y")
        pow = json.dumps(powerValues)
        wat = json.dumps(waterValues)
        cos = json.dumps(costValues)

        #check if the month has already been stored in the database, if so update the values
        if models.db.session.query(models.History).filter_by(type="month", date=month).first() != None:
            models.db.session.query(models.History).filter_by(type="month", date=month).update({models.History.powervalues: pow, models.History.watervalues: wat, models.History.costvalues: cos})
        else:
            models.db.session.add(models.History("month", month, pow, wat, cos))
        models.db.session.commit()
    
        return labels, powerValues[1:], waterValues[1:], costValues[1:], estIndex
