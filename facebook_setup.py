'''
Created on Jun 22, 2020

@author: Vasyalisk
'''
import requests

import credentials



def set_messenger_profile():
    url = 'https://graph.facebook.com/v7.0/me/messenger_profile'
    data = {'get_started'    : {'payload': 'GET_STARTED'},
            'persistent_menu': [{
                                 'locale': 'default',
                                 'call_to_actions': [{'type': 'postback', 'title': 'Help', 'payload': 'HELP'},
                                                     {'type': 'postback', 'title': 'Exchange currency', 'payload': 'CALC'},
                                                     {'type': 'postback', 'title': 'Exchange rates', 'payload': 'EXRATE'}
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