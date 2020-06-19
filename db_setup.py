'''
Created on Jun 19, 2020

@author: Vasyalisk
'''
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

import credentials



app = Flask(__name__)

SQLALCHEMY_DATABASE_URI = "mysql+mysqlconnector://{username}:{password}@{hostname}/{databasename}".format(
    username=credentials.DB_USERNAME,
    password=credentials.DB_PASSWORD,
    hostname=credentials.DB_HOST_ADDRESS,
    databasename=credentials.DB_NAME,
)

# Custom configuration parameters for application
app.config["SQLALCHEMY_DATABASE_URI"] = SQLALCHEMY_DATABASE_URI
app.config["SQLALCHEMY_POOL_RECYCLE"] = 299 # Server-dependent timeout for each connection to DB
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)



class CurrencyExchangeRate (db.Model):
    
    __tablename__ = 'currency'
    
    name = db.Column(db.String(512), primary_key=True)
    ex_rate = db.Column(db.Float())