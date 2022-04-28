import models
import datetime

from webui import WebUI
from flask import Flask
app = Flask(__name__)
ui = WebUI(app, debug=True)
app.config['SECRET_KEY'] = '53cr37k3y'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://Team5:Team5@138.26.48.83:5432/Team5DB'
models.db.init_app(app)

#add test usage entries to DB
with app.app_context():
    #clear usage table
    models.db.session.query(models.Usage).delete()
    start = (datetime.datetime.now() - datetime.timedelta(days = 120))
    for i in range(120):
        new = models.Usage(start.strftime("%m/%d/%Y %H:%M:%S"), 3600, 1103)
        models.db.session.add(new)
        new = models.Usage(start.strftime("%m/%d/%Y %H:%M:%S"), 120, 1098)
        models.db.session.add(new)
        start = start + datetime.timedelta(days = 1)
    start = (datetime.datetime.now() - datetime.timedelta(hours = 48))
    for i in range(48):
        new = models.Usage(start.strftime("%m/%d/%Y %H:%M:%S"), 1800, 1103)
        models.db.session.add(new)
        new = models.Usage(start.strftime("%m/%d/%Y %H:%M:%S"), 120, 1098)
        models.db.session.add(new)
        start = start + datetime.timedelta(hours = 1)
    models.db.session.commit()

