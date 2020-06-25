'''
Created on Jun 22, 2020

@author: Vasyalisk
'''
import requests, os

if __name__ == '__main__':
    os.chdir('/home/Vasyalisk/webhook/')

from .facebook_bot import ChatStatus

from security import credentials

    
    
def set_messenger_profile():
    '''
    Sets pop-up menu and greeting screen. Also defines payload to appropriate
    actions.
    '''
    
    url = 'https://graph.facebook.com/v7.0/me/messenger_profile'
    data = {'get_started'    : {'payload': ChatStatus.GET_STARTED.value},
            'persistent_menu': [{
                                 'locale': 'default',
                                 'call_to_actions': [{'type': 'postback',
                                                      'title': 'Help',
                                                      'payload': ChatStatus.HELP.value},
                                                      
                                                     {'type': 'postback',
                                                      'title': 'Exchange currency',
                                                      'payload': ChatStatus.EXCHANGE.value},
                                                     
                                                     {'type': 'postback',
                                                      'title': 'Exchange rates',
                                                      'payload': ChatStatus.RATES.value}
                                                     ]
                                 }
                                ],
            'greeting'       : [{
                                 'locale': 'default',
                                 'text'  : ('Welcome! You can use this bot to '
                                            'obtain different exchange rates as '
                                            'well as convert currencies. To do '
                                            'that use the pop-up menu in the '
                                            'lower corner.')
                                 }]
            }
    token = {'access_token' : credentials.ACCESS_TOKEN}
    result = requests.post(url, json=data, params=token)
    print(result)


if __name__ == '__main__':
    set_messenger_profile()