from buildhome import buildHome
import meteostat_API as ms
import models, scenes
import items_usage as iu
import wtforms, datetime, re, threading, time
from flask import Flask, render_template, redirect, url_for, request, jsonify
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
from usage import dayChartValues, weekChartValues, monthChartValues

'''
This is the main Flask app. This application holds app routes and functions to carry out the front end and first start function calls. 
'''

# generate flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = '53cr37k3y'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://Team5:Team5@138.26.48.83:5432/Team5DB'

models.db.init_app(app)

# global variables
startTime = datetime.datetime.now()
sum_power = []
sum_water = []

#Flask form classes for home page
class AddHomeForm(FlaskForm):
    home_name = StringField('Home Name', validators=[DataRequired()])
    submit = SubmitField('Add Home')

class MainForm(FlaskForm):
    add_home = wtforms.FormField(AddHomeForm)

#usage generation app. Runs at first launch to generate historical usage data. 
def usage_gen():
    with app.app_context():
        if models.db.session.query(models.Home).count() != 0:
            scenes.historical_life(app, 60)

# Function to generate chart data
def chart(firstrun):
    while firstrun == True:
        time.sleep(60)
        firstrun = False
    while True:
        print('generating chart data')
        with app.app_context():    
            today = datetime.datetime.now()
            global dayUsage 
            dayUsage = dayChartValues(app, today.month, today.day, today.year)
            start_of_week = today - datetime.timedelta(days = today.weekday())
            global weekUsage 
            weekUsage = weekChartValues(app, start_of_week.month, start_of_week.day, start_of_week.year)
            global monthUsage 
            monthUsage = monthChartValues(app, today.month, today.year)
            global totalPower 
            totalPower = models.db.session.query(models.Sensor).filter_by(name = 'Power Consumption').first().value
            global totalWater 
            totalWater = models.db.session.query(models.Sensor).filter_by(name = 'Water Consumption').first().value
            month = (datetime.datetime.now() - datetime.timedelta(days=30)).strftime('%m/%Y')
            global historyMonth1 
            historyMonth1 = models.db.session.query(models.History).filter_by(type = "month", date = month).first().graphValues()
            month = (datetime.datetime.now() - datetime.timedelta(days=60)).strftime('%m/%Y')
            global historyMonth2 
            historyMonth2 = models.db.session.query(models.History).filter_by(type = "month", date = month).first().graphValues()
            month = (datetime.datetime.now() - datetime.timedelta(days=90)).strftime('%m/%Y')
            global historyMonth3 
            historyMonth3 = models.db.session.query(models.History).filter_by(type = "month", date = month).first().graphValues()
            print('chart data generated')
            time.sleep(60)

#route for first launch landing page. This allows the end user to create the new home. It will build out the DB contents and generate usage.
@app.route('/', methods=['GET', 'POST'])
def home():
    home_name = None
    form = MainForm()
    with app.app_context():
        if models.db.session.query(models.Home).count() == 0:
            if form.add_home.submit.data:
                if form.add_home.validate_on_submit():
                    home_name = form.add_home.home_name.data
                    new_home = models.Home(home_name)
                    models.db.session.add(new_home)
                    models.db.session.commit()
                    buildHome(app)
                    threading.Thread(target=usage_gen).start()
                    return redirect(url_for('dashboard'))
        else:
            return redirect(url_for('dashboard'))
    return render_template('home.html', form=form, home_name=home_name)

# used for the loading page while usage is being generated.
@app.route('/loading', methods=['GET', 'POST'])
def loading():
    return render_template('loading.html')

#main dashboard page. This page displays the floorplan and HVAC controls.
@app.route('/dashboard', methods=['GET','POST'])
def dashboard():
    item_icons = []
    open_doors = []
    open_windows = []
    curr = ms.getCurrentConditions()
    with app.app_context():
        home_name = models.db.session.query(models.Home).first().name
        indoor_temp = models.db.session.query(models.Sensor).filter_by(name='Indoor Temperature').first().value
        for item in models.db.session.query(models.Item).all():
            item_icons.append(item)
        hvac = models.db.session.query(models.HVAC).all()
        for item in models.db.session.query(models.Item).filter_by(type="opening").all():
            if item.name == "Window" and item.status == True:
                open_windows.append(item)
            elif item.status == True:
                open_doors.append(item)
            else:
                pass
        models.HVAC.openDoor = len(open_doors)
        models.HVAC.openWindow = len(open_windows)
    return render_template('dashboard.html', item_icons=item_icons, hvac=hvac[0], home_name = home_name, curr=curr, indoor_temp=indoor_temp)

# Route that handles AJAX method to update the HVAC Controls
@app.route('/dashboard/hvac', methods=['GET'])
def hvac():
    value = request.args.get('id')
    if value == 'increase':
        value = 1
    elif value == 'decrease':
        value = -1
    with app.app_context():
        setpoint = models.db.session.query(models.HVAC).first().setpoint + value
        if setpoint > models.db.session.query(models.Sensor).filter_by(name='Indoor Temperature').first().value + 2:
            mode = 'Heat'
        elif setpoint < models.db.session.query(models.Sensor).filter_by(name='Indoor Temperature').first().value - 2:
            mode = 'Cool'
        else: 
            mode = 'Off'
        hvac = models.db.session.query(models.HVAC).first()
        hvac.setpoint = setpoint
        hvac.mode = mode
        models.db.session.commit()
    return redirect(url_for('dashboard'))

# route that handles AJAX methods to toggle lights on the floorplan. writes usage data to the DB as well. 
@app.route('/dashboard/action', methods=['GET'])
def action():
    item_id = request.args.get('id')
    with app.app_context():
        item = models.db.session.query(models.Item).filter_by(id=item_id).first()
        if item.status == True:
            item.status = False
            iu.setUsage(app, item_id, False)
        elif item.status == False:
            item.status = True
            iu.setUsage(app, item_id, True)
        models.db.session.commit()
    return redirect(url_for('dashboard'))

# route that handles feeding the indoor temp value which is automatically updated with AJAX. 
@app.route('/dashboard/hvac_update', methods=['GET'])
def hvac_update():
    with app.app_context():
        temp = models.db.session.query(models.Sensor).filter_by(name='Indoor Temperature').first().value
        return str(temp)
# main usage page route. this page holds the Chart.js modules and pulls in globally defined variables from the chart() function.
@app.route('/usage', methods=['GET','POST'])
def usage():
    try:
        return render_template('usage.html', dayUsage=dayUsage, weekUsage=weekUsage, monthUsage=monthUsage, totalPower=totalPower, totalWater=totalWater, historyMonth1=historyMonth1, historyMonth2=historyMonth2, historyMonth3=historyMonth3)
    except: return redirect(url_for('loading'))

# route for the maintenance page. This page holds toggles and scenes to manually toggle items and run predefines scenes. 
@app.route('/maintenance', methods=['GET','POST'])
def maintenance():
    items_list = []
    rooms_list = []
    with app.app_context():
        for item in models.db.session.query(models.Item).order_by(models.Item.name).all():
            items_list.append(item)
        for room in models.db.session.query(models.Room).order_by(models.Room.name).all():
            rooms_list.append(room)
    return render_template('maintenance.html', items_list = items_list, rooms_list = rooms_list)

# this route handles the toggle methods being passed in by AJAX
@app.route('/maintenance/toggle', methods=['GET'])
def toggle_action():
    #strip the leading info to get the item id in the format needed using regex. 
    item_id = re.search('(?<=_)\w+', request.args.get('id'))
    item_id = item_id.group(0)
    item_state = request.args.get('state') == "true"
    iu.setUsage(app, item_id, item_state)
    with app.app_context():
        item = models.db.session.query(models.Item).filter_by(id=item_id).first()
        item.status = bool(item_state)
        models.db.session.commit()
    return redirect(url_for('maintenance'))

# this route handles running the scenes. They are triggered by passing a var with AJAX and returning a message to flash as a success after the usage has been logged. 
@app.route('/maintenance/scenes', methods=['GET'])
def scenes_action():
    scene = request.args.get('id')
    with app.app_context():
        if scene == 'shower':
            scenes.takeShower(app)
            msg = 'You just took a shower!'
        elif scene == 'dishwasher':
            scenes.runDishwasher(app)
            msg = 'You just cleaned your dishes!'
        elif scene == 'party':
            scenes.haveParty(app)
            msg = 'You just had a WILD party!'
    return msg

# this route is for the members/team page. This was made for Austin's minor Business Administration. 
@app.route('/members', methods=['GET','POST'])
def members():
    return render_template('members.html')

# This function loops the internal temp change function which is what is used to dynamically update the HVAC information.
def indoor_temp_update():
    with app.app_context():
        while True:
            if models.db.session.query(models.Home).count() != 0:
                internalTempChange()
            time.sleep(60)

# this method generates historical weather information in the DB
def weather():
    ms.getWeather(30)
    ms.storeWeather(app)

# using threads to handle time consuming tasks, this route forces the thread to call functions at first run. This triggers specific things so that the application runs a bit smoother.
@app.before_first_request
def thread_start():
    threading.Thread(target=indoor_temp_update).start()
    threading.Thread(target=weather).start()
    threading.Thread(target=chart, args=(True,)).start()

# this function controls the HVAC mode which is displayed on the thermostat. 
def hvacOperation(indoor_temp, setpoint, mode):
    if setpoint < int(indoor_temp) - 2:
        return 'Cool'
    elif setpoint > int(indoor_temp) + 2:
        return 'Heat'
    else:
        return 'Off'
 # this function controls the internal temp and holds the logic to do so according to the project docs.         
def internalTempChange():
    
    endTime = datetime.datetime.now()

    with app.app_context():
        s = models.db.session()
        s.expire_on_commit = False

        externalTemp = ms.getCurrentConditions()['temp']
        indoor_temp_sensor = s.query(models.Sensor).filter_by(name = 'Indoor Temperature').first()
        setpoint = s.query(models.HVAC).first().setpoint
        hvac = s.query(models.HVAC).first()
        hvac_item = s.query(models.Item).filter_by(name = 'HVAC').first()
        time = endTime - startTime
        hvac.mode = hvacOperation(indoor_temp_sensor.value, setpoint, hvac.mode)
        # log hvac power usage 
        if hvac.mode == 'Off':
            iu.setUsage(app, hvac_item.id, False)
        elif hvac.mode == 'Cool':
            if setpoint <= indoor_temp_sensor.value:
                indoor_temp_sensor.value -= 1
                iu.setUsage(app, hvac_item.id, True)
                s.commit()
        elif hvac.mode == 'Heat':
            if setpoint >= indoor_temp_sensor.value:
                indoor_temp_sensor.value += 1
                iu.setUsage(app, hvac_item.id, True)
                s.commit()
        #first condition passes if at least one door and one window are open. 
        if (models.HVAC.openDoor > 0) and (models.HVAC.openWindow > 0):
            indoor_temp_sensor = s.query(models.Sensor).filter_by(name = 'Indoor Temperature').first()
            indoor_temp_sensor.value = round(indoor_temp_sensor.value + (((( externalTemp - indoor_temp_sensor.value) / 10) * 2 *  models.HVAC.openDoor *(time.total_seconds()/ 300)) + ((( externalTemp - indoor_temp_sensor.value) / 10) * 1 *  models.HVAC.openWindow * (time.total_seconds()/ 300))), 1)
            s.commit()
        #condition passes if at least one door is open. 
        elif ( models.HVAC.openDoor > 0):
            indoor_temp_sensor = s.query(models.Sensor).filter_by(name = 'Indoor Temperature').first()
            indoor_temp_sensor.value = round(indoor_temp_sensor.value + ((( externalTemp - indoor_temp_sensor.value) / 10) * 2 *  models.HVAC.openDoor *(time.total_seconds()/ 300)), 1)
            s.commit()
        #condition passes if at least one window is open. 
        elif ( models.HVAC.openWindow > 0):
            indoor_temp_sensor = s.query(models.Sensor).filter_by(name = 'Indoor Temperature').first()
            indoor_temp_sensor.value = round(indoor_temp_sensor.value + ((( externalTemp - indoor_temp_sensor.value) / 10) * 1 *  models.HVAC.openWindow * (time.total_seconds()/ 300)), 1)
            s.commit()
        # catches all other scenarios where no windows or doors are open. 
        else:
            indoor_temp_sensor = s.query(models.Sensor).filter_by(name = 'Indoor Temperature').first()
            indoor_temp_sensor.value = round(indoor_temp_sensor.value + ((( externalTemp - indoor_temp_sensor.value) / 10) * 2 * (time.total_seconds()/ 3600)), 1)
            s.commit()
        print(indoor_temp_sensor.value)

if __name__ == '__main__':
    # start the main app/flask server. 
    app.run(debug=True)

    
    

