'''
Created on Jun 22, 2020

@author: Vasyalisk
'''
import requests, os

if __name__ == '__main__':
    os.chdir('/home/Vasyalisk/webhook/')

from bots.facebook_bot import ChatPayload, RESPONSE_TEXT

from security import credentials

    
    
def set_messenger_profile():
    '''
    Sets pop-up menu and greeting screen. Also defines payload to appropriate
    actions.
    '''
    
    url = 'https://graph.facebook.com/v7.0/me/messenger_profile'
    data = {'get_started'    : {'payload': ChatPayload.GET_STARTED.value},
            'persistent_menu': [{
                                 'locale': 'default',
                                 'call_to_actions': [{'type': 'postback',
                                                      'title': 'Help',
                                                      'payload': ChatPayload.HELP.value},
                                                      
                                                     {'type': 'postback',
                                                      'title': 'Exchange currency',
                                                      'payload': ChatPayload.EXCH.value},
                                                     
                                                     {'type': 'postback',
                                                      'title': 'Exchange rates',
                                                      'payload': ChatPayload.RATE.value}
                                                     ]
                                 }
                                ],
            'greeting'       : [{
                                 'locale': 'default',
                                 'text'  : (RESPONSE_TEXT['t_greeting'])
                                 }]
            }
    token = {'access_token' : credentials.ACCESS_TOKEN}
    result = requests.post(url, json=data, params=token)
    print(result)


if __name__ == '__main__':
    set_messenger_profile()