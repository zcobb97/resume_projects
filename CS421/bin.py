from flask import Flask, render_template, request, g ,redirect, make_response
import sqlite3
import json
import hashlib

import datetime #what sadist made an object datetime in package datetime

import random
import os
from flask_sqlalchemy import SQLAlchemy



app = Flask (__name__)
basedir = os.path.abspath(os.path.dirname(__file__))

app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///'+os.path.join(basedir,'data.sqlite')
app.config['SQLALCHEMY_TRAC_MODIFICATIONS']=False
db=SQLAlchemy(app)


SESSIONS = {}

######################################################################################################
######################################Database Interaction############################################
DATABASE = 'data/datastore.db'

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)

    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def query_db(query, args=(), one=False):
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv

def insertQuery(insertQuery):
    #init_db()
    get_db().execute(insertQuery)
    get_db().commit()
######################################################################################################
######################################################################################################

###########################################################################
############################Authentication Routes##########################
@app.route('/newUser')
def newUser():
    return render_template('newUser.html',userAdded="")

@app.route('/newUserSubmit', methods=['POST'])
def newUserSubmit():
    name = request.form['name']
    newUserName = request.form['username']
    newUserPassword = request.form['password']
    newUserType = request.form['userType']

    newUserId = query_db("SELECT (max(userId) + 1) FROM users ")
    #newUserIdMadeIntoSomethingThatCanBeConcate
    newId = str(newUserId[0]).replace(',','',1).replace(')','',1).replace('(','',1)

    insertQuery("INSERT INTO users (userId, name, patientId, userName, password, userType) \
    VALUES ((SELECT (max(userId) + 1) FROM users), \
    '" + name + "', \
    '" + newId + "', \
    '" + newUserName + "', \
    '" + newUserPassword + "', \
    '" + newUserType + "' \
    )")

    insertQuery("INSERT INTO patientInformation (userId,orientation, dob) VALUES ((SELECT (max(userId)) FROM users),'','')")
    insertQuery("INSERT INTO patientHistory (userId) VALUES  ((SELECT (max(userId)) FROM users))")

    return render_template('newUser.html',userAdded="Added " + newUserName)

@app.route('/login')
def login():
    username = request.args.get('username')
    password = request.args.get('password')

    loginCheck = query_db("SELECT userId, userType, userId, name FROM users WHERE userName = '" + username + "' \
         AND password = '" + password + "'")

    if len(loginCheck) == 0:
        return ""

    omfgEncodingAreYouSerious = username + '|' +  password
    global SESSIONS

    sessionId = hashlib.md5(str(omfgEncodingAreYouSerious).encode('utf-8')).hexdigest() #python.org

    SESSIONS[sessionId] = SessionObject()

    SESSIONS[sessionId].sessionId = sessionId
    SESSIONS[sessionId].patient = None
    SESSIONS[sessionId].userType = loginCheck[0][1]
    SESSIONS[sessionId].loggedInName = loginCheck[0][3]
    SESSIONS[sessionId].loggedInUserId = loginCheck[0][2]

    if loginCheck[0][1] == "patient":
        SESSIONS[sessionId].patient = getPatientFromUserId(loginCheck[0][2])

    return sessionId

@app.route('/logout')
def logout():
    try:
        sessionId = request.cookies.get('sessionId') #request.args.get('sessionId')
        global SESSIONS
        del SESSIONS[sessionId]
    except:
        return render_template('index.html')

    response = make_response(render_template('index.html'))
    response.set_cookie('sessionId', '')

    return response

#instrospect is the endpoint that is used to validate tokens
@app.route('/introspect')
def introspect():
    try:
        sessionId = request.cookies.get('sessionId') #request.args.get('sessionId')
        global SESSIONS
        thisSession = SESSIONS[sessionId]
    except:
        return None

    if thisSession == None:
        return None

    return "GOOD"
###########################################################################
###########################################################################

@app.route('/defineTables')
def defineTables():

    insertQuery("CREATE TABLE IF NOT EXISTS intakeCalendar ( \
    id INTEGER PRIMARY KEY, \
    patientName TEXT, \
    providerName TEXT, \
    year INTEGER, \
    julianDay INTEGER, \
    hour INTEGER )")

    insertQuery("CREATE TABLE IF NOT EXISTS patientHistory ( \
    userId INTEGER PRIMARY KEY, \
    last_visit_before TEXT, \
    date_of_visit TEXT, \
    health_conditions TEXT, \
    medications TEXT)")

    insertQuery("CREATE TABLE IF NOT EXISTS patientInformation ( \
    userId INTEGER PRIMARY KEY, \
    address TEXT, \
    city TEXT, \
    state TEXT, \
    zip TEXT, \
    phoneH TEXT, \
    phoneCW TEXT, \
    dob TEXT, \
    SSN TEXT, \
    occupation TEXT, \
    employer TEXT, \
    email TEXT, \
    orientation TEXT, \
    relationshipStatus TEXT )")

    insertQuery("CREATE TABLE IF NOT EXISTS users ( userId INTEGER PRIMARY KEY, \
    name TEXT NOT NULL, patientId TEXT, userName TEXT NOT NULL, password TEXT NOT NULL, \
    userType TEXT NOT NULL )")

    insertQuery("CREATE TABLE IF NOT EXISTS insurance ( id INTEGER PRIMARY KEY, userId INTEGER NOT NULL, \
    type TEXT NOT NULL, provider TEXT NOT NULL, groupFamily TEXT NOT NULL)")



    return "GOOD"

###########################################################################
####################################Single Routes##########################
@app.route('/setUpUsers')
def setUpUsers():


    #insertQuery("drop table intakeCalendar")

    #insertQuery("CREATE TABLE IF NOT EXISTS intakeCalendar ( \
    #id INTEGER PRIMARY KEY, \
    #patientName TEXT, \
    #providerName TEXT, \
    #year INTEGER, \
    #julianDay INTEGER, \
    #hour INTEGER )")


    #insertQuery("CREATE TABLE IF NOT EXISTS patientHistory ( \
    #userId INTEGER PRIMARY KEY, \
    #last_visit_before TEXT, \
    #date_of_visit TEXT, \
    #health_conditions TEXT, \
    #medications TEXT)")


    #insertQuery("CREATE TABLE IF NOT EXISTS patientInformation ( \
    #userId INTEGER PRIMARY KEY, \
    #address TEXT, \
    #city TEXT, \
    #state TEXT, \
    #zip TEXT, \
    #phoneH TEXT, \
    #phoneCW TEXT, \
    #dob TEXT, \
    #SSN TEXT, \
    #occupation TEXT, \
    #employer TEXT, \
    #email TEXT, \
    #orientation TEXT, \
    #relationshipStatus TEXT )")

    #insertQuery("DROP TABLE patientInformation")
    #insertQuery("CREATE TABLE IF NOT EXISTS patientInformation ( \
    #userId INTEGER PRIMARY KEY, \
    #address TEXT, \
    #city TEXT, \
    #state TEXT, \
    #zip TEXT, \
    #phoneH TEXT, \
    #phoneCW TEXT, \
    #dob TEXT, \
    #SSN TEXT, \
    #occupation TEXT, \
    #employer TEXT, \
    #email TEXT, \
    #orientation TEXT, \
    #relationshipStatus TEXT )")

    #insertQuery("DROP TABLE users")
    #insertQuery("CREATE TABLE IF NOT EXISTS users ( userId INTEGER PRIMARY KEY, \
    #name TEXT NOT NULL, patientId TEXT, userName TEXT NOT NULL, password TEXT NOT NULL, \
    #userType TEXT NOT NULL )")
    #insertQuery("CREATE TABLE IF NOT EXISTS insurance ( id INTEGER PRIMARY KEY, userId INTEGER NOT NULL, \
    #type TEXT NOT NULL, provider TEXT NOT NULL, groupFamily TEXT NOT NULL)")
    #insertQuery("DROP TABLE insurance")
    #insertQuery("CREATE TABLE IF NOT EXISTS insurance ( id INTEGER PRIMARY KEY, userId INTEGER NOT NULL, \
    #type TEXT NOT NULL, provider TEXT NOT NULL, groupFamily TEXT NOT NULL)")
    #insertQuery("INSERT INTO insurance (id, userId, type, provider, groupFamily) VALUES \
    #(1,9, 'Dental','Delta','D234/F22')")
    #insertQuery("INSERT INTO insurance (id, userId, type, provider, groupFamily) VALUES \
    #(2,9, 'Health','BCBS PPO','J0812-UI121212')")
    #insertQuery("INSERT INTO insurance (id, userId, type, provider, groupFamily) VALUES \
    #(3,9, 'Medications','Quickscripts','D234/F22')")
    #insertQuery("INSERT INTO insurance (id, userId, type, provider, groupFamily) VALUES \
    #(4,9, 'Supplemental','AFLAC','QuackQuack Squaaaaack')")
    #insertQuery("INSERT INTO insurance (id, userId, type, provider, groupFamily) VALUES \
    #(5,9, 'Liability','GCL R Us','PP-2131ASD')")
    #insertQuery("INSERT INTO insurance (id, userId, type, provider, groupFamily) VALUES \
    #(6,9, 'Life','MetLife','MVMV/UWH')")
    #insertQuery("delete from users where userId >= 1")
    #insertQuery("INSERT INTO users (userId, name, patientId, userName, password, userType) VALUES (1,'firstUser', 'SUPERLONGPATIENTID1','user1','pass','provider')")
    #insertQuery("INSERT INTO users (userId, name, patientId, userName, password, userType) VALUES (2,'secondUser','SUPERLONGPATIENTID2','user2','pass','provider')")
    #insertQuery("INSERT INTO users (userId, name, patientId, userName, password, userType) VALUES (3,'thirdUser', 'SUPERLONGPATIENTID3','user3','pass','provider')")
    #insertQuery("INSERT INTO users (userId, name, patientId, userName, password, userType) VALUES (4,'fourthUser','SUPERLONGPATIENTID4','user4','pass','patient')")
    #insertQuery("INSERT INTO users (userId, name, patientId, userName, password, userType) VALUES (5,'fifthUser', 'SUPERLONGPATIENTID5','user5','pass','patient')")
    #insertQuery("INSERT INTO users (userId, name, patientId, userName, password, userType) VALUES ( 6,'User Six', 'SUPERLONGPATIENTID6','user5', 'pass','patient')")
    #insertQuery("INSERT INTO users (userId, name, patientId, userName, password, userType) VALUES ( 7,'Ultimate User', 'SUPERLONGPAID7','user6', 'pass','patient')")
    #insertQuery("INSERT INTO users (userId, name, patientId, userName, password, userType) VALUES ( 8,'Ocho Ba', 'SUPERLONGPATIENTI1D8','user7', 'pass','patient')")
    #insertQuery("INSERT INTO users (userId, name, patientId, userName, password, userType) VALUES ( 9,'Jiao Sher', 'SUPERLONGPATIENTD9','user8', 'pass','patient')")
    #insertQuery("INSERT INTO users (userId, name, patientId, userName, password, userType) VALUES (10,'Gelada Italiano', 'SUPERLONGP15','user9', 'pass','patient')")
    #insertQuery("INSERT INTO users (userId, name, patientId, userName, password, userType) VALUES (11,'Tira Misu', 'SUPERLONGPA2TID135','user10','pass','patient')")
    #insertQuery("INSERT INTO users (userId, name, patientId, userName, password, userType) VALUES (12,'Dolce de Leche', 'SUPERLOTID125','user11','pass','patient')")
    #insertQuery("INSERT INTO users (userId, name, patientId, userName, password, userType) VALUES (13,'Helado Deliciodo', 'ATIENTID115','user12','pass','patient')")
    #insertQuery("INSERT INTO users (userId, name, patientId, userName, password, userType) VALUES (14,'Legume Paste', 'SUPEaTIENTID165','user13','pass','patient')")
    #insertQuery("INSERT INTO users (userId, name, patientId, userName, password, userType) VALUES (15,'Cafe Blanco', 'SUPERLIENTID1115','user14','pass','patient')")
    #insertQuery("INSERT INTO users (userId, name, patientId, userName, password, userType) VALUES (16,'Delight Fully', 'GPATIENTID1335','user15','pass','patient')")
    #insertQuery("INSERT INTO users (userId, name, patientId, userName, password, userType) VALUES (17,'Iced Cream', 'ONGPATIENTID18885','user16','pass','patient')")
    #insertQuery("INSERT INTO users (userId, name, patientId, userName, password, userType) VALUES (18,'Home Made', 'RLONGPATIENTID5778','user17','pass','patient')")
    #insertQuery("INSERT INTO users (userId, name, patientId, userName, password, userType) VALUES (19,'Tasty Treat', 'LONGPATIENTID588','user18','pass','patient')")

    #global SESSIONS
    #SESSIONS['81538bb3bf61fa90eea389a130bf50f2'] = SessionObject()
    #thisSession = SESSIONS['81538bb3bf61fa90eea389a130bf50f2']
    #thisSession.sessionId = "81538bb3bf61fa90eea389a130bf50f2"
    #thisSession.patient = getPatientFromUserId(9)
    #thisSession.userType= "provider"
    #thisSession.loggedInName = ""
    #thisSession.loggedInUserId = 1

    return render_template('setUpUsers.html')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/getWelcomeMessage')
def getWelcomeMessage():
    try:
        sessionId = request.cookies.get('sessionId') #request.args.get('sessionId')
        global SESSIONS
        thisSession = SESSIONS[sessionId]
    except:
        return "Select Patient To Proceed"

    thisSession.patientName = getPatientFromUserId(thisSession.loggedInUserId).name

    if thisSession.patient == None:
        return "Select Patient To Proceed"

    if thisSession.userType == "provider":
        return "Patient Selected " + thisSession.patient.name

    return "Welcome " + thisSession.patientName

@app.route('/getUserType')
def getUserType():
    try:
        sessionId = request.cookies.get('sessionId') #request.args.get('sessionId')
        global SESSIONS
        thisSession = SESSIONS[sessionId]
    except:
        return ""

    return thisSession.userType

###########################################################################
###########################################################################


###########################################################################
############################Patient Select Routes##########################

#This is initial landing to page with no submitted data
@app.route('/patientSelect')
def patientSelect():
    try:
        sessionId = request.cookies.get('sessionId') #request.args.get('sessionId')
        allowAccess = verifyProviderAccess(sessionId)
        if allowAccess == False:
            return render_template('notAllowed.html')
    except:
        return render_template('index.html')

    return render_template('patientSelect.html')


@app.route('/patientSearchCriteria', methods=['POST'])
def patientSearchCriteria():
    try:
        sessionId = request.cookies.get('sessionId') #request.args.get('sessionId')
        allowAccess = verifyProviderAccess(sessionId)
        if allowAccess == False:
            return render_template('notAllowed.html')
    except:
        return render_template('index.html')


    searchCriteria = request.form['searchText']
    searchDob = request.form['searchDob']
    searchGender = request.form['searchGender']

    if(searchGender == "any"):
        searchGender = ""

    queryText = "SELECT pi.userId, u.name, pi.dob FROM patientInformation pi \
    , users u WHERE u.userId = pi.userId AND userType = 'patient' \
    AND lower(name) LIKE '%" + searchCriteria.lower() + "%' \
    AND lower(dob) LIKE '%" + searchDob.lower() + "%' \
    AND lower(orientation) LIKE '%" + searchGender.lower() + "%' \
    order by pi.userId desc limit 10"
    if searchGender == "male":
        queryText = "SELECT pi.userId, u.name, pi.dob FROM patientInformation pi \
        , users u WHERE u.userId = pi.userId AND userType = 'patient' \
        AND lower(name) LIKE '%" + searchCriteria.lower() + "%' \
        AND lower(dob) LIKE '%" + searchDob.lower() + "%' \
        AND lower(orientation) NOT LIKE '%" + "fe" + "%' \
        order by pi.userId desc limit 10"

    searchResults = query_db(queryText)

    return render_template('patientSelect.html',searchResults=searchResults)


@app.route('/patientSelectSubmit', methods=['POST'])
def patientSelectSubmit():
    try:
        sessionId = request.cookies.get('sessionId') #request.args.get('sessionId')
        allowAccess = verifyProviderAccess(sessionId)
        if allowAccess == False:
            return render_template('notAllowed.html')
    except:
        return render_template('index.html')


    patientUserId = request.form['patientId']

    global sessions
    thisSession = SESSIONS[sessionId]
    thisSession.patient = getPatientFromUserId(patientUserId)

    return redirect('/')
###########################################################################
###########################################################################




###########################################################################
############################Insurance Routes###############################

@app.route('/intakeCalendar')
def intakeCalendar():
    try:
        sessionId = request.cookies.get('sessionId') #request.args.get('sessionId')
        global SESSIONS
        thisSession = SESSIONS[sessionId]
    except:
        return render_template('index.html')

    try:
        whichCalendar = request.args.get('calendar')
        newDate = request.args.get('newDate')
    except:
        whichCalendar = ""
        if newDate == None:
            newDate = datetime.date.today().strftime("%j")

    if newDate == None:
        newDate = datetime.date.today().strftime("%j")

    datetime_object = datetime.datetime.strptime(newDate + ' 2021', '%j %Y')
    weekday = datetime_object.strftime("%A")
    nextDay = (datetime_object + datetime.timedelta(days=1)).strftime("%j")
    previousDay = (datetime_object + datetime.timedelta(days=-1)).strftime("%j")

    retCalendar = query_db("SELECT hour, patientName,providerName \
    FROM \
    intakeCalendar \
    WHERE \
    julianDay = '" + str(newDate) + "' ")

    return render_template('intakeCalendarDaily.html', schedule=retCalendar, weekday=weekday, currentJulian=newDate, previousDay=previousDay, nextDay=nextDay)

@app.route('/addAppointment')
def addAppointment():
    try:
        sessionId = request.cookies.get('sessionId') #request.args.get('sessionId')
        global SESSIONS
        thisSession = SESSIONS[sessionId]
    except:
        return render_template('index.html')

    today = datetime.date.today()
    julianDate = today.strftime("%j")

    return render_template('addAppointment.html',julianDate=julianDate)

@app.route('/addAppointmentSubmit', methods=['POST'])
def addAppointmentSubmit():
    try:
        sessionId = request.cookies.get('sessionId') #request.args.get('sessionId')
        global SESSIONS
        thisSession = SESSIONS[sessionId]
    except:
        return render_template('index.html')

    patientName = request.form['patientName']
    providerName = request.form['providerName']
    appointmentDate = request.form['appointmentDate']
    appointmentTime = request.form['appointmentTime']

    insertQueryString = "insert into intakeCalendar (id, patientName, providerName, \
     year, julianDay, hour) VALUES ((select max(id) + 1 from intakeCalendar), \
    '" + patientName + "', \
    '" + providerName + "', \
    '2021', \
    '" + appointmentDate + "', \
    '" + appointmentTime + "')"

    insertQuery(insertQueryString)

    today = datetime.date.today()
    julianDate = today.strftime("%j")

    return render_template('addAppointment.html',julianDate=julianDate)


###########################################################################
###########################################################################








###########################################################################
############################Insurance Routes###############################

@app.route('/insurance')
def insurance():
    try:
        sessionId = request.cookies.get('sessionId') #request.args.get('sessionId')
        global SESSIONS
        thisSession = SESSIONS[sessionId]
    except:
        return render_template('index.html')

    userId = thisSession.patient.userId

    retInsurance = query_db("SELECT type, provider, groupFamily, id FROM insurance \
    WHERE userId = '" + str(userId) + "'")

    return render_template('insurance.html',insurances=retInsurance)


@app.route('/deleteInsurance', methods=['POST'])
def deleteInsurance():
    try:
        sessionId = request.cookies.get('sessionId') #request.args.get('sessionId')
        global SESSIONS
        thisSession = SESSIONS[sessionId]
    except:
        return render_template('index.html')

    insuranceId = request.form['insuranceId']

    insertQuery("delete from insurance where id = '" + insuranceId + "'")

    return redirect('insurance')


@app.route('/insuranceAdd', methods=['POST'])
def insuranceAdd():
    try:
        sessionId = request.cookies.get('sessionId') #request.args.get('sessionId')
        global SESSIONS
        thisSession = SESSIONS[sessionId]
    except:
        return render_template('index.html')

    userId = thisSession.patient.userId

    insuranceType = request.form['addType']
    insuranceProvider = request.form['addProvider']
    insuranceGroup = request.form['addGroup']

    currentMax = query_db("SELECT MAX(id) + 1  FROM insurance")

    nextInsuranceId = str(currentMax[0]).replace(',','',2).replace(')','',2).replace('(','',2)

    if nextInsuranceId == None:
        nextInsuranceId = "1"

    if nextInsuranceId == "None":
        nextInsuranceId = "1"

    insertQueryString = "INSERT INTO insurance (id, userId, type, provider, groupFamily) VALUES ('" + nextInsuranceId + "'," + userId + ", '" + insuranceType + "','" + insuranceProvider + "','" + insuranceGroup + "')"

    insertQuery(insertQueryString)

    return redirect('/insurance')


###########################################################################
###########################################################################


def verifyProviderAccess(sessionId):
    try:
        global SESSIONS
        thisSession = SESSIONS[sessionId]
    except:
        return False

    if thisSession == None:
        return False
    if thisSession.userType == "provider":
        return True

    return False

def getPatientFromUserId(userId):
    thisPatientQueryResult = query_db("SELECT name, patientId, userId, userType FROM users WHERE userId = '" + str(userId) + "'")
    retPatient = PatientObject()
    retPatient.name = str(thisPatientQueryResult[0][0])
    retPatient.patientId = str(thisPatientQueryResult[0][1])
    retPatient.userId = str(thisPatientQueryResult[0][2])
    retPatient.userTYpe = str(thisPatientQueryResult[0][3])
    return retPatient

###########################################################################
############################Object Library#################################
class SessionObject:
    def __init__(self):
        self.sessionId = ""
        self.patient = None
        self.userType = ""
        self.loggedInName = ""
        self.loggedInUserId = ""

        #self.expiration ... dont feel like fooling with timestamp manipulation
        #odd that time is the most predictable thing in the universe yet somehow
        #   its still a PITA for us to program around


class PatientObject:
    def __init__(self):
        self.name = ""
        self.patientId = ""
        self.userId = ""



















###########################################################################
############################ Patient History and Forms#####################




# c.execute("""CREATE TABLE patients (
#    first_name TEXT,
#    middle_name TEXT,
#    last_name TEXT,
#    address TEXT,
#    city TEXT,
#    state TEXT,
#    zip TEXT,
#    phone_h TEXT,
#    phone_c_w TEXT,
#    dob TEXT,
#    ssn TEXT,
#    occupation TEXT,
#    employer TEXT,
#    email TEXT,
#    insurance_provider TEXT,
#    sexual_orientation TEXT,
#    relationship_status TEXT,
#    last_visit_before TEXT,
#    date_of_visit TEXT,
#    health_conditions TEXT,
#    medications TEXT
#    )""")

@app.route('/patientInformation', methods = ['POST', 'GET'])
def patientInformation():
    try:
        sessionId = request.cookies.get('sessionId') #request.args.get('sessionId')
        global SESSIONS
        thisSession = SESSIONS[sessionId]
    except:
        return render_template('index.html')

    userId = thisSession.patient.userId

    selectQuery = "SELECT * FROM patientInformation WHERE userId = '" + userId + "'"

    patientInformation = query_db(selectQuery)

    return render_template('patientInformation.html',patientInformation=patientInformation[0])

@app.route('/patientInformationUpdate', methods = ['POST', 'GET'])
def patientInformationUpdate():
    try:
        sessionId = request.cookies.get('sessionId') #request.args.get('sessionId')
        global SESSIONS
        thisSession = SESSIONS[sessionId]
    except:
        return render_template('index.html')

    userId = thisSession.patient.userId

    address = request.form['address']
    city = request.form['city']
    state = request.form['state']
    zip = request.form['zip']

    phoneH = request.form['phoneH']
    phoneCW = request.form['phoneCW']
    dob = request.form['dob']
    ssn = request.form['ssn']

    occupation = request.form['occupation']
    employer = request.form['employer']
    email = request.form['email']

    gender = request.form['gender']
    status = request.form['status']

    insertQueryString = "UPDATE patientInformation SET \
    zip = '" + zip + "', \
    address = '" + address + "', \
    city = '" + city + "', \
    state = '" + state + "', \
    zip = '" + zip + "', \
    phoneH = '" + phoneH + "', \
    phoneCW = '" + phoneCW + "', \
    dob = '" + dob + "', \
    ssn = '" + ssn + "', \
    occupation = '" + occupation + "', \
    employer = '" + employer + "', \
    email = '" + email + "', \
    orientation = '" + gender + "', \
    relationshipStatus = '" + status + "' WHERE \
    userId = '" + userId + "'"


    insertQuery(insertQueryString)

    return redirect('patientInformation')

@app.route('/patientHistory', methods = ['POST', 'GET'])
def patientHistory():
    try:
        sessionId = request.cookies.get('sessionId') #request.args.get('sessionId')
        global SESSIONS
        thisSession = SESSIONS[sessionId]
    except:
        return render_template('index.html')
    userId = thisSession.patient.userId
    patientHistoryTuples = query_db("select * from patientHistory where userid = '" + userId + "'")

    print("patientHistoryTuples " + str(len(patientHistoryTuples)))
    print("patientHistoryTuples " + str(len(patientHistoryTuples)))
    print("patientHistoryTuples " + str(len(patientHistoryTuples)))
    print("patientHistoryTuples " + str(len(patientHistoryTuples)))
    print("patientHistoryTuples " + str(len(patientHistoryTuples)))

    if len(patientHistoryTuples) > 0:
        retPatientHistory = patientHistoryTuples[0]
    if len(patientHistoryTuples) == 0:
        retPatientHistory = None



    return render_template('patientHistory.html', patientHistory = retPatientHistory)

@app.route('/patientHistoryUpdate', methods = ['POST', 'GET'])
def patientHistoryUpdate():
    return render_template('patientHistoryUpdate.html')

@app.route('/patientHistoryRetrieve', methods = ['POST', 'GET'])
def patientHistoryRetrieve():
    return render_template('enterSSN.html')

@app.route('/formProcess', methods = ['POST', 'GET'])
def formProcess():
    try:
        sessionId = request.cookies.get('sessionId') #request.args.get('sessionId')
        global SESSIONS
        thisSession = SESSIONS[sessionId]
    except:
        return render_template('index.html')
    userId = thisSession.patient.userId

    if request.method == 'POST':
        try:
            last_visit_before = request.form.get('visit')
            date_of_visit = request.form.get('lastvisit')
            health_conditions = request.form.get('health-conditions')
            medications = request.form.get('medication')
        except:
            if last_visit_before == None:
                last_visit_before = ""
            if date_of_visit == None:
                date_of_visit = ""
            if health_conditions == None:
                health_conditions = ""
            if medications == None:
                medications = ""


        insertQuery("delete from patientHistory where userid = '" + userId + "'")
        insertQuery("insert into patientHistory (userId, last_visit_before,date_of_visit, \
        health_conditions,medications) VALUES ( \
        '" + userId + "', \
        '" + last_visit_before + "', \
        '" + date_of_visit + "', \
        '" + health_conditions + "', \
        '" + medications + "')")

        result = 'You have submitted your form successfully'

        return redirect('patientHistory')

@app.route('/formUpdate', methods = ['POST', 'GET'])
def formUpdate():
    if request.method == 'POST':
        try:
            first_name = request.form.get('fname')
            middle_name = request.form.get('mname')
            last_name = request.form.get('lname')
            address = request.form.get('address')
            city = request.form.get('city')
            state = request.form.get('state')
            zip_code = request.form.get('zip')
            phone_h = request.form.get('home_phone')
            phone_c_w = request.form.get('cell_work_phone')
            dob = request.form.get('dob')
            ssn = request.form.get('ss#')
            occupation = request.form.get('occupation')
            employer = request.form.get('employer')
            email = request.form.get('email')
            insurance_provider = request.form.get('insurance-provider')
            sexual_orientation = request.form.get('gender')
            relationship_status = request.form.get('status')
            last_visit_before = request.form.get('visit')
            date_of_visit = request.form.get('lastvisit')
            health_conditions = request.form.get('health-conditions')
            medications = request.form.get('medication')

            with sqlite3.connect('patient.db') as conn:
                c = conn.cursor()

                c.execute("""UPDATE patients SET first_name=?,middle_name=?,last_name=?,address=?,city=?,state=?,zip=?,phone_h=?,phone_c_w=?,dob=?,occupation=?,employer=?,email=?,insurance_provider=?,sexual_orientation=?,relationship_status=?,last_visit_before=?,date_of_visit=?,health_conditions=?,medications=? 
                          WHERE ssn = ?""",(first_name,middle_name,last_name,address,city,state,zip_code,phone_h,phone_c_w,dob,occupation,employer,email,insurance_provider,sexual_orientation,relationship_status,last_visit_before,date_of_visit,health_conditions,medications,ssn))

                conn.commit()
                result = 'Your form was updated successfully'

        except:
            conn.rollback()
            result = 'Something went wrong with updating your form'

        finally:
            return render_template('feedback.html', result = result)
            conn.close()

@app.route('/historyDisplay', methods = ['POST', 'GET'])
def historyDisplay():
    if request.method == 'GET':
        social = request.values.get('social-security')

        with sqlite3.connect('patient.db') as conn:
            c = conn.cursor()

            c.execute("SELECT * FROM patients WHERE ssn = ?",(social,))
            items = c.fetchall()

            conn.commit()

            return render_template('historyDisplay.html', items = items)
            conn.close()

    return render_template('patientHistory.html')




###########################################################################
############################/ Messaging \#################################
## Create a Model for User and Departments

class Employee(db.Model):
    __tablename__="employee"
    eID = db.Column(db.Text, primary_key=True)
    name = db.Column(db.Text)
    pos = db.Column(db.Text) ## position
    dpt = db.Column(db.Text) ## department


    def __init__(self, eID, name, pos, dpt):
        self.eID  = eID
        self.name = name
        self.pos  = pos
        self.dpt  = dpt


## Create a Model for Messages
class Message(db.Model):
    __tablename__="message"
    mID = db.Column(db.Text, primary_key=True)
    rName = db.Column(db.Text)
    mes= db.Column(db.Text)
    subj = db.Column(db.Text)

    def __init__(self, mID, rName, subj, mes):
        self.mID = mID      ## message ID
        self.rName = rName  ## recipiant name
        self.subj = subj    ## subject
        self.mes = mes      ## message





@app.route('/messaging', methods = ["POST", "GET"])
def messaging ():
    all_messages = Message. query.all()
    return render_template ('messaging.html',all_messages=all_messages)

@app.route('/employeeForm', methods = ["POST", "GET"])
def employeeForm ():
    db.create_all()
    db.session.commit()
    if request.method == 'POST':
        eData = request.form
        idsuffix = random.randint(1111,9999)
        idprefix = "HC"
        eID = idprefix + str(idsuffix)

        name = eData["name"]
        pos = eData["pos"]
        dpt = eData["dpt"]

        emp_data = Employee(eID, name, pos, dpt)
        db.session.add(emp_data)
        db.session.commit()
        all_employees = Employee.query.all()
        return render_template('employeeList.html', all_employees = all_employees)

    return render_template ('employeeForm.html')

@app.route('/newMessage', methods = ["POST", "GET"])
def newMessage ():
    db.create_all()
    db.session.commit()

    if request.method == 'POST':
        data = request.form
        mprefix = "MS"
        mSuffix = random. randint(1000,9999)
        mID = mprefix + str(mSuffix)
        rName = data["rName"]
        subj = data["subj"]
        mes = data["mes"]

        new_data = Message(mID, rName, subj, mes)
        db.session.add(new_data)
        db.session.commit()
        all_messages = Message.query.all()
        return render_template('messaging.html', all_messages = all_messages)
    return render_template ('newMessage.html')



@app.route('/recipiant1', methods = ["POST", "GET"])
def recipiant1 ():
    all_employees = Employee.query.all()
    all_messages = Message. query.all()
    return render_template ('recipiant1.html',all_employees=all_employees, all_messages=all_messages)


@app.route('/rec1-Message', methods = ["POST", "GET"])
def rec1Message ():
    if request.method == "POST":
        select_recipiant =request.form.get("message.rName")
        Message.query.filter(Message.rName == select_recipiant)
        db.session.commit()
    all_messages = Message.query.all()
    return render_template ('rec1-Message.html',all_messages = all_messages)

## List All Employees
@app.route('/list_all', methods = ['POST', 'GET'])
def list_all ():
    all_employees = Employee.query.all()
    return render_template ('employeeList.html',all_employees = all_employees)

@app.route('/convList', methods = ['POST', 'GET'])
def results ():

    return render_template('convList.html')





@app.route('/recipiant2', methods = ["POST", "GET"])
def recipiant2 ():
    return render_template ('recipiant2.html')

@app.route('/recipiant3', methods = ["POST", "GET"])
def recipiant3 ():
    return render_template ('recipiant3.html')



















###########################################################################
########################### Main App ######################################

if __name__ == '__main__':
    app.run(debug=True)

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'),404

