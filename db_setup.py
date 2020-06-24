'''
Created on Jun 19, 2020

@author: Vasyalisk
'''
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

import credentials


LOGGING = True

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
    '''
    Table contains exchange rates of supported currencies compared to USD. E.g.
    'UAH 26' means that 1 USD costs 26 UAH.
    '''
    
    __tablename__ = 'currency'
    
    name = db.Column(db.String(512), primary_key=True)
    ex_rate = db.Column(db.Float)
    

class ChatData(db.Model):
    '''
    Table contains user ID, chat status (what to expect from input) and metadata
    arguments (if any) as JSON string.
    '''
    
    __tablename__ = 'chat_data'
    
    user_id = db.Column(db.String(512), primary_key=True)
    chat_status = db.Column(db.String(512))
    chat_metadata = db.Column(db.String(512))
    

if __name__ == '__main__':
    db.create_all()
    print('Created all tables in the database.')