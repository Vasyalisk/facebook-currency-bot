'''
Created on Jun 16, 2020

@author: Vasyalisk
'''
from flask import request
import requests

import time

import db_setup, facebook_bot, credentials



app = db_setup.app
db = db_setup.db

CONNECTION_LOG = 'ConnectionLog.txt'


# Facebook specific API

@app.route('/facebook', methods=['GET'])
def verify_facebook_token():
    '''
    The Messenger verifies webhook by sending GET request, which contains token
    value in hub.verify_token. It also generates expected response in hub.challenge,
    which should be returned if token is valid for this web app.
    '''
    
    def _add_GET_log_entry():
        '''
        Adds basic GET request info to connection log.
        '''
        
        with open(CONNECTION_LOG, 'a') as log:
            server_time = time.strftime('%H:%M, %d\%m\%Y')
            entry = '{} GET from : {}\n'.format(server_time, request.url)
            log.write(entry)
        
        return entry


    DEFAULT_MODE = 'subscribe'
    MODE = 'hub.mode'
    STANDARD_QUESTION = 'hub.verify_token'
    GENERATED_RESPONSE = 'hub.challenge'
    
    mode = request.args.get(MODE, '')
    token = request.args.get(STANDARD_QUESTION, '')
    response = request.args.get(GENERATED_RESPONSE, '')
    
    if (token == credentials.VERIFY_TOKEN) and (mode == DEFAULT_MODE):
        
        if db_setup.LOGGING:
            _add_GET_log_entry()
            
        return response
    else:
        return 'Unable to authorise.'

    
@app.route('/facebook', methods=['POST'])
def handle_facebook_events():
    '''
    After the user sends message in Messenger, webhook receives POST request.
    Processed request should always return 200 OK answer in 20 s.
    '''
    
    def _add_POST_log_entry(data_in, data_out, results):
        '''Adds basic POST request info to connection log.'''
    
        with open(CONNECTION_LOG, 'a') as log:
            server_time = time.strftime('%H:%M, %d\%m\%Y')
            for (entry_out, result) in zip(data_out, results):
                log_entry = ('{t} POST; data_in: {i}; '
                             'data_out: {o}; result: {r}\n').format(
                             t=server_time, i=data_in, o=entry_out, r=result)
                log.write(log_entry)
            
            
    def _send_response(data_out):
        '''
        https://developers.facebook.com/docs/messenger-platform/reference/send-api/
        Sends various responses to Messenger (defined in data_out) using requests
        library. Requires FB page access token.
        '''
        
        results = []
        token = {'access_token' : credentials.ACCESS_TOKEN}
        
        for entry in data_out:
            result = requests.post('https://graph.facebook.com/v7.0/me/messages',
                                   json=entry, params=token)
            results.append(result)
            
        return results


    data_in = request.get_json()
    bot = facebook_bot.FacebookBot(data_in)
    data_out = bot.process_events()
    results = _send_response(data_out)
    
    if db_setup.LOGGING:
        _add_POST_log_entry(data_in, data_out, results)
    
    return '200 OK'


if __name__ == "__main__":
    app.run()