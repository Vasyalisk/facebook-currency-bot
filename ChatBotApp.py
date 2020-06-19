'''
Created on Jun 16, 2020

@author: Vasyalisk
'''
from flask import request
import requests

import time

import db_setup, credentials



app = db_setup.app
db = db_setup.db

LOGGING = True
CONNECTION_LOG = 'ConnectionLog.txt'



@app.route('/', methods=['GET'])
def verify_token():
    '''
    The Messenger verifies webhook by sending GET request, which contains token
    value in hub.verify_token. It also generates expected response in hub.challenge,
    which should be returned if token is valid for this web app.
    '''
    
    DEFAULT_MODE = 'subscribe'
    MODE = 'hub.mode'
    STANDARD_QUESTION = 'hub.verify_token'
    GENERATED_RESPONSE = 'hub.challenge'
    
    mode = request.args.get(MODE, '')
    token = request.args.get(STANDARD_QUESTION, '')
    response = request.args.get(GENERATED_RESPONSE, '')
    
    if (token == credentials.VERIFY_TOKEN) and (mode == DEFAULT_MODE):
        
        if LOGGING:
            add_GET_log_entry()
            
        return response
    else:
        return 'Unable to authorise.'


def add_GET_log_entry():
    '''
    Adds basic GET request info to connection log.
    '''
    
    with open(CONNECTION_LOG, 'a') as log:
        server_time = time.strftime('%H:%M, %d\%m\%Y')
        entry = '{} GET from : {}\n'.format(server_time, request.url)
        log.write(entry)
    
    return entry
    
    
@app.route('/', methods=['POST'])
def handle_messages():
    '''
    After the user sends message in Messenger, webhook receives POST request.
    Processed request should always return 200 OK answer in 20 s.
    '''
    
    data_in = request.get_json()
    user_id, text_in = get_msg_data(data_in)
    text_out = generate_response(text_in)
    data_out = send_message(user_id, text_out)
    
    if LOGGING:
        add_POST_log_entry(data_in, data_out)
    
    return '200 OK'


def add_POST_log_entry(data_in, data_out):
    '''
    Adds basic POST request info to connection log.
    '''
    
    
    with open(CONNECTION_LOG, 'a') as log:
        server_time = time.strftime('%H:%M, %d\%m\%Y')
        entry = '{} POST; data_in: {}; data_out: {}\n'.format(server_time,
                                                              data_in,
                                                              data_out
                                                              )
        log.write(entry)
        
    return entry


def get_msg_data(data_in):
    '''
    https://developers.facebook.com/docs/messenger-platform/reference/webhook-events/messages
    Facebook message event API in JSON format:
    
    {
      "sender":{
        "id":"<PSID>"
      },
      "recipient":{
        "id":"<PAGE_ID>"
      },
      "timestamp":1458692752478,
      "message":{
        "mid":"<MSG_ID>",
        "text":"<TEXT>"
        }
      }
      ...
    }
    
    Function returns sender(user) ID and message text from incoming dictionary.
    '''
    
    user_id = ''
    text = ''
    msging_data = data_in['entry'][0].get('messaging', '')
    
    if msging_data:
        user_id = msging_data[0]['sender']['id']
        msg_data = msging_data[0]['message']
        text = msg_data['text']
        
    return user_id, text
    

def generate_response(text_in):
    '''
    Generates response based on the incoming text. Uses additional class for bug
    with duplicate event received from Messenger.
    '''
    
    text_out = text_in
    return text_out


def send_message(user_id, text, msg_type='RESPONSE'):
    '''
    https://developers.facebook.com/docs/messenger-platform/reference/send-api/
    Sends simple non-empty message to Messenger (of type RESPONSE by default)
    using requests library. Requires FB page access token.
    '''
    
    data_out = ''
    
    msg = {'messaging_type' :   msg_type,
           'recipient'      :   {'id' : user_id},
           'message'        :   {'text': text}
           }
    
    token = {'access_token' : credentials.ACCESS_TOKEN}
    
    if text:
        data_out = requests.post('https://graph.facebook.com/v7.0/me/messages', json=msg, params=token)
        
    return data_out


if __name__ == "__main__":
    app.run()