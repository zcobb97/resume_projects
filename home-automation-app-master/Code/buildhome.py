import models

# Default Items to be generated upon home creation
master_bedroom_items = [{"name": "Overhead Light", "x_pos": 402, "y_pos": 513, "type": "light"}, 
                        {"name": "Lamp", "x_pos": 282, "y_pos": 451, "type": "light"}, 
                        {"name": "Lamp", "x_pos": 282, "y_pos": 563, "type": "light"}, 
                        {"name": "TV", "x_pos": 492, "y_pos": 509, "type": "power"}, 
                        {"name": "Window", "x_pos": 269, "y_pos": 483, "type": "opening"}, 
                        {"name": "Window", "x_pos": 269, "y_pos": 531, "type": "opening"}]
bedroom1_items = [{"name": "Overhead Light", "x_pos": 687, "y_pos": 228, "type": "light"}, 
                  {"name": "Lamp", "x_pos": 661, "y_pos": 105, "type": "light"}, 
                  {"name": "Lamp", "x_pos": 718, "y_pos": 105, "type": "light"}, 
                  {"name": "Window", "x_pos": 625, "y_pos": 93, "type": "opening"}, 
                  {"name": "Window", "x_pos": 751, "y_pos": 93, "type": "opening"}]
bedroom2_items = [{"name": "Overhead Light", "x_pos": 386, "y_pos": 213, "type": "light"}, 
                  {"name": "Lamp", "x_pos": 283, "y_pos": 187, "type": "light"}, 
                  {"name": "Lamp", "x_pos": 283, "y_pos": 244, "type": "light"}, 
                  {"name": "Window", "x_pos": 371, "y_pos": 93, "type": "opening"}, 
                  {"name": "Window", "x_pos": 269, "y_pos": 216, "type": "opening"}]
master_bathroom_items = [{"name": "Overhead Light", "x_pos": 600, "y_pos": 556, "type": "light"}, 
                         {"name": "Exhaust Fan", "x_pos": 651, "y_pos": 489, "type": "power"}, 
                         {"name": "Window", "x_pos": 585, "y_pos": 621, "type": "opening"}, 
                         {"name": "Sink", "x_pos": 584, "y_pos": 522, "type": "water"}, 
                         {"name": "Toilet", "x_pos": 652, "y_pos": 461, "type": "water"}, 
                         {"name": "Shower", "x_pos": 661, "y_pos": 604, "type": "water"}, 
                         {"name": "Bathtub", "x_pos": 586, "y_pos": 599, "type": "water"}]
bathroom_items = [{"name": "Overhead Light", "x_pos": 535, "y_pos": 170, "type": "light"}, 
                  {"name": "Exhaust Fan", "x_pos": 535, "y_pos": 129, "type": "power"}, 
                  {"name": "Window", "x_pos": 536, "y_pos": 93, "type": "opening"}, 
                  {"name": "Sink", "x_pos": 498, "y_pos": 173, "type": "water"}, 
                  {"name": "Toilet", "x_pos": 502, "y_pos": 122, "type": "water"}, 
                  {"name": "Shower", "x_pos": 573, "y_pos": 107, "type": "water"}]
kitchen_items = [{"name": "Overhead Light", "x_pos": 910, "y_pos": 505, "type": "light"}, 
                 {"name": "Stove", "x_pos": 859, "y_pos": 526, "type": "power"}, 
                 {"name": "Oven", "x_pos": 859, "y_pos": 540, "type": "power"}, 
                 {"name": "Microwave", "x_pos": 762, "y_pos": 458, "type": "power"}, 
                 {"name": "Refrigerator", "x_pos": 766, "y_pos": 491, "type": "power"}, 
                 {"name": "Dishwasher", "x_pos": 888, "y_pos": 606, "type": "power"}, 
                 {"name": "Window", "x_pos": 1090, "y_pos": 508, "type": "opening"}, 
                 {"name": "Window", "x_pos": 1029, "y_pos": 621, "type": "opening"},
                 {"name": "Sink", "x_pos": 840, "y_pos": 602, "type": "water"}]
laundary_items = [{"name": "Washer", "x_pos": 735, "y_pos": 606, "type": "power"}, 
                  {"name": "Dryer", "x_pos": 735, "y_pos": 580, "type": "power"}]
living_room_items = [{"name": "Overhead Light", "x_pos": 950, "y_pos": 220, "type": "light"}, 
                     {"name": "Lamp", "x_pos": 801, "y_pos": 155, "type": "light"}, 
                     {"name": "Lamp", "x_pos": 801, "y_pos": 310, "type": "light"}, 
                     {"name": "TV", "x_pos": 1073, "y_pos": 232, "type": "power"}, 
                     {"name": "Window", "x_pos": 879, "y_pos": 93, "type": "opening"}, 
                     {"name": "Window", "x_pos": 937, "y_pos": 93, "type": "opening"}, 
                     {"name": "Window", "x_pos": 994, "y_pos": 93, "type": "opening"}]
garage_items = [{"name": "Overhead Light", "x_pos": 831, "y_pos": 705, "type": "light"}, 
                {"name": "Garage Door", "x_pos": 769, "y_pos": 784, "type": "opening"}, 
                {"name": "Garage Door", "x_pos": 900, "y_pos": 784, "type": "opening"},
                {"name": "Hot Water Heater", "x_pos": 769, "y_pos": 638, "type": "power"},
                {"name": "HVAC", "x_pos": 800, "y_pos": 638, "type": "power"}]
exterior_items = [{"name": "Front Door", "x_pos": 1088, "y_pos": 357, "type": "opening"}, 
                  {"name": "Back Door", "x_pos": 272, "y_pos": 366, "type": "opening"}, 
                  {"name": "Garage Door", "x_pos": 972, "y_pos": 702, "type": "opening"}]

# this offest var fixes item position for 1920x1080 displays.
x_offset = 63
y_offset = 23

# This function builds the home out in the DB and creates all of the items in the above dict. 
def buildHome(app):
    with app.app_context():
        home_id = models.db.session.query(models.Home.id)

        # Master Bedroom
        room = models.Room(name="Master Bedroom", home_id=home_id)
        models.db.session.add(room)
        models.db.session.commit()
        room_id = models.db.session.query(models.Room.id).filter_by(name="Master Bedroom").first()[0]

        for item in master_bedroom_items:
            i = models.Item(name=item['name'], x_pos=item['x_pos'] - 13 + x_offset, y_pos=item['y_pos'] - 13 + y_offset, home_id=home_id, room_id=room_id, type = item['type'])
            models.db.session.add(i)
            models.db.session.commit()

        # Bedroom 1
        room = models.Room(name="Bedroom 1", home_id=home_id)
        models.db.session.add(room)
        models.db.session.commit()
        room_id = models.db.session.query(models.Room.id).filter_by(name="Bedroom 1").first()[0]

        for item in bedroom1_items:
            i = models.Item(name=item['name'], x_pos=item['x_pos'] - 13 + x_offset, y_pos=item['y_pos'] - 13 + y_offset, home_id=home_id, room_id=room_id, type = item['type'])
            models.db.session.add(i)
            models.db.session.commit()

        # Bedroom 2
        room = models.Room(name="Bedroom 2", home_id=home_id)
        models.db.session.add(room)
        models.db.session.commit()
        room_id = models.db.session.query(models.Room.id).filter_by(name="Bedroom 2").first()[0]

        for item in bedroom2_items:
            i = models.Item(name=item['name'], x_pos=item['x_pos'] - 13 + x_offset, y_pos=item['y_pos'] - 13 + y_offset, home_id=home_id, room_id=room_id, type = item['type'])
            models.db.session.add(i)
            models.db.session.commit()

        # Master Bathroom
        room = models.Room(name="Master Bathroom", home_id=home_id)
        models.db.session.add(room)
        models.db.session.commit()
        room_id = models.db.session.query(models.Room.id).filter_by(name="Master Bathroom").first()[0]

        for item in master_bathroom_items:
            i = models.Item(name=item['name'], x_pos=item['x_pos'] - 13 + x_offset, y_pos=item['y_pos'] - 13 + y_offset, home_id=home_id, room_id=room_id, type = item['type'])
            models.db.session.add(i)
            models.db.session.commit()

        # Bathroom
        room = models.Room(name="Bathroom", home_id=home_id)
        models.db.session.add(room)
        models.db.session.commit()
        room_id = models.db.session.query(models.Room.id).filter_by(name="Bathroom").first()[0]

        for item in bathroom_items:
            i = models.Item(name=item['name'], x_pos=item['x_pos'] - 13 + x_offset, y_pos=item['y_pos'] - 13 + y_offset, home_id=home_id, room_id=room_id, type = item['type'])
            models.db.session.add(i)
            models.db.session.commit()

        # Kitchen
        room = models.Room(name="Kitchen", home_id=home_id)
        models.db.session.add(room)
        models.db.session.commit()
        room_id = models.db.session.query(models.Room.id).filter_by(name="Kitchen").first()[0]

        for item in kitchen_items:
            i = models.Item(name=item['name'], x_pos=item['x_pos'] - 13 + x_offset, y_pos=item['y_pos'] - 13 + y_offset, home_id=home_id, room_id=room_id, type = item['type'])
            models.db.session.add(i)
            models.db.session.commit()
        
        # Laundary
        room = models.Room(name="Laundary", home_id=home_id)
        models.db.session.add(room)
        models.db.session.commit()
        room_id = models.db.session.query(models.Room.id).filter_by(name="Laundary").first()[0]

        for item in laundary_items:
            i = models.Item(name=item['name'], x_pos=item['x_pos'] - 13 + x_offset, y_pos=item['y_pos'] - 13 + y_offset, home_id=home_id, room_id=room_id, type = item['type'])
            models.db.session.add(i)
            models.db.session.commit()
        
        # Living Room
        room = models.Room(name="Living Room", home_id=home_id)
        models.db.session.add(room)
        models.db.session.commit()
        room_id = models.db.session.query(models.Room.id).filter_by(name="Living Room").first()[0]

        for item in living_room_items:
            i = models.Item(name=item['name'], x_pos=item['x_pos'] - 13 + x_offset, y_pos=item['y_pos'] - 13 + y_offset, home_id=home_id, room_id=room_id, type = item['type'])
            models.db.session.add(i)
            models.db.session.commit()

        # Garage
        room = models.Room(name="Garage", home_id=home_id)
        models.db.session.add(room)
        models.db.session.commit()
        room_id = models.db.session.query(models.Room.id).filter_by(name="Garage").first()[0]

        for item in garage_items:
            i = models.Item(name=item['name'], x_pos=item['x_pos'] - 13 + x_offset, y_pos=item['y_pos'] - 13 + y_offset, home_id=home_id, room_id=room_id, type = item['type'])
            models.db.session.add(i)
            models.db.session.commit()

        # Exterior
        room = models.Room(name="Exterior", home_id=home_id)
        models.db.session.add(room)
        models.db.session.commit()
        room_id = models.db.session.query(models.Room.id).filter_by(name="Exterior").first()[0]

        for item in exterior_items:
            i = models.Item(name=item['name'], x_pos=item['x_pos'] - 13 + x_offset, y_pos=item['y_pos'] - 13 + y_offset, home_id=home_id, room_id=room_id, type = item['type'])
            models.db.session.add(i)
            models.db.session.commit()
        
        # Sensors
        # Power
        sensor = models.Sensor(name="Power Consumption", home_id=home_id)
        models.db.session.add(sensor)
        models.db.session.commit()

        # Water
        sensor = models.Sensor(name="Water Consumption", home_id=home_id)
        models.db.session.add(sensor)
        models.db.session.commit()

        # Indoor Temperature
        sensor = models.Sensor(name="Indoor Temperature", value=60, home_id=home_id)
        models.db.session.add(sensor)
        models.db.session.commit()

        # Outdoor Temperature
        sensor = models.Sensor(name="Outdoor Temperature", home_id=home_id)
        models.db.session.add(sensor)
        models.db.session.commit()

        # HVAC 
        hvac = models.HVAC(name="HVAC", mode = "Off", home_id=home_id)
        models.db.session.add(hvac)
        models.db.session.commit()
        