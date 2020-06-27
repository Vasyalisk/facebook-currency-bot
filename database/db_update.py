'''
Created on Jun 19, 2020

@author: Vasyalisk
'''
import requests

import json, time, datetime

if __name__ == '__main__':
    import sys
    sys.path.append('/home/Vasyalisk/webhook/')

from database import db_setup
from database.db_setup import db, CurrencyExchangeRate, ChatData



# Contains the exchange rates from USD to all the other supported currencies
UPDATE_URL = 'https://open.exchangerate-api.com/v6/latest'

DATA_FILE = 'currency_rates.txt'
UPDATE_LOG = 'logs/UpdateLog.txt'

ENTRY_EXPIRE_TIME = 3600 * 24 # in seconds



def dump_to_file(json_data):
    with open(DATA_FILE, 'w+') as f:
        s = json.dumps(json_data, indent=4)
        f.write(s)


def update_db(data):
    for (name, rate) in data.items():
        entry = db.session.query(CurrencyExchangeRate).get(name)
        if entry is None:
            new_entry = CurrencyExchangeRate(name=name, ex_rate=rate)
            db.session.add(new_entry)
        else:
            entry.ex_rate = rate

    db.session.commit()


def update_from_file():
    with open(DATA_FILE, 'r') as f:
        data = json.load(f).get('rates', '')

    update_db(data)

    if db_setup.LOGGING:
        add_file_update_log_entry()


def add_file_update_log_entry():
    with open(UPDATE_LOG, 'a') as log:
        server_time = time.strftime('%H:%M, %d\%m\%Y')
        entry = '{} Updated database from file\n'.format(server_time)
        log.write(entry)

    return entry


def update_from_url():
    response = requests.get(UPDATE_URL)
    raw_data = response.json()
    dump_to_file(raw_data)
    data = raw_data.get('rates', '')
    update_db(data)

    if db_setup.LOGGING:
        add_url_update_log_entry()


def add_url_update_log_entry():
    with open(UPDATE_LOG, 'a') as log:
        server_time = time.strftime('%H:%M, %d\%m\%Y')
        entry = '{} Updated database from Exchangerate server\n'.format(server_time)
        log.write(entry)

    return entry


def remove_old_entries():
    now = datetime.datetime.now()
    entries = db.session.query(ChatData)

    for entry in entries:
        dt = now - entry.last_msg_date
        if dt.total_seconds() > ENTRY_EXPIRE_TIME:
            db.session.delete(entry)

    db.session.commit()


if __name__ == '__main__':
    update_from_url()
    remove_old_entries()