'''
Created on Jun 22, 2020

@author: Vasyalisk
'''
import db_setup

import string, enum, json



RESPONSE_TEXT_CONF = 'response_text.conf'

with open(RESPONSE_TEXT_CONF) as conf:
    RESPONSE_TEXT = json.load(conf)


@enum.unique
class ChatStatus(enum.Enum):
    IDLE = 'IDLE'
    RATES = 'RATES'
    EXCHANGE = 'EXCHANGE'
    

@enum.unique
class ChatPayload(enum.Enum):
    RATES = 'RATES'
    EXCHANGE = 'EXCHANGE'
    HELP = 'HELP'
    GET_STARTED = 'GET_STARTED'


@enum.unique
class EventType(enum.Enum):
    '''
    Basic event types from
    https://developers.facebook.com/docs/messenger-platform/reference/webhook-events/
    '''
    
    MESSAGES = 0
    MESSAGING_POSTBACKS = 1



class FacebookBot:
    '''
    Bot for processing Facebook Messenger requests using API.
    '''
    
    def __init__(self, db, data_in={}):
        self.db = db
        self.data_in = data_in
    
        
    def process_events(self, data_in=None):
        
        if data_in is None:
            data_in = self.data_in
        else:
            self.data_in = data_in
            
        data_out = []
        entries_in = [e['messaging'][0] for e in data_in['entry']]
        
        METHODS_MAP = {
                       EventType.MESSAGES:            self.process_message,
                       EventType.MESSAGING_POSTBACKS: self.process_postback
                       } 
        
        for entry_in in entries_in:
            e_type = self.get_event_type(entry_in)
            entry_out = METHODS_MAP[e_type](entry_in)
            data_out.append(entry_out)
            
        return data_out
    
    
    @staticmethod
    def get_event_type(entry):
        '''
        Returns EventType enum or None if event is not recognised.
        https://developers.facebook.com/docs/messenger-platform/reference/webhook-events/
        '''
        
        e_type = None
        
        if entry.get('message', ''):
            e_type = EventType.MESSAGES
        elif entry.get('postback', ''):
            e_type = EventType.MESSAGING_POSTBACKS
            
        return e_type
    
    
    def process_message(self, entry_in):
        '''
        Echoes message back to user.
        
        Incoming message JSON format:
        https://developers.facebook.com/docs/messenger-platform/reference/webhook-events/messages
        
        Sending API:
        https://developers.facebook.com/docs/messenger-platform/reference/send-api
        '''
        
        user_id = entry_in['sender']['id']
        text_in = entry_in['message']['text']
        text_out = ''
        
        if '?help' in text_in:
            text_out = RESPONSE_TEXT['t_help']
            self.update_chat_data(user_id, status=ChatStatus.IDLE.value)
        elif '?codes' in text_in:
            # to do
            self.update_chat_data(user_id, status=ChatStatus.IDLE.value)
        elif '?rates' in text_in:
            text_out = RESPONSE_TEXT['t_rates']
            self.update_chat_data(user_id, status=ChatStatus.RATES.value)
        elif '?exchange' in text_in:
            text_out = RESPONSE_TEXT['t_exchange']
            self.update_chat_data(user_id, status=ChatStatus.EXCHANGE.value)
        
        entry_out = {
                     'messaging_type': 'RESPONSE',
                     'recipient'     : {'id' : user_id},
                     'message'       : {'text': text_out}
                     }
        
        return entry_out
    
    
    def process_postback(self, entry_in):
        '''
        Sends message as a response to postback event. Also updates database's
        ChatData table.
        '''
        
        user_id = entry_in['sender']['id']
        payload = entry_in['postback']['payload']
        response_text = ''
        
        if payload == ChatPayload.RATES.value:
            response_text = RESPONSE_TEXT['t_rates']
            # Check the problem with user_id=user_id
            self.update_chat_data(user_id, status=ChatStatus.RATES.value)
        elif payload == ChatPayload.EXCHANGE.value:
            response_text = RESPONSE_TEXT['t_exchange']
            self.update_chat_data(user_id, status=ChatStatus.EXCHANGE.value)
        elif payload == ChatPayload.HELP.value:
            response_text = RESPONSE_TEXT['t_help']
            self.update_chat_data(user_id, status=ChatStatus.IDLE.value)
        elif payload == ChatPayload.GET_STARTED.value:
            # TO DO
            self.update_chat_data(user_id, status=ChatStatus.IDLE.value)
        
        entry_out = {
                     'messaging_type': 'RESPONSE',
                     'recipient'     : {'id' : user_id},
                     'message'       : {'text': response_text}
                     }
            
        return entry_out
    
    
    def update_chat_data(self, user_id, *, status, **kw):
        '''
        Updates entry for each user chat in the database or creates new.
        '''
        
        chat_metadata = '{}'
        if kw:
            chat_metadata = json.dumps(kw)
            
        entry = self.db.session.query(db_setup.ChatData).get(user_id)
        
        if entry is None:
            new_entry = db_setup.ChatData(user_id=user_id, chat_status=status,
                                          chat_metadata=chat_metadata)
            self.db.session.add(new_entry)
        else:
            entry.chat_status = status
            entry.chat_metadata = chat_metadata
            
        self.db.session.commit()
    
    
# Deprecated. To be transferred in FacebookBot class
def generate_response(text_in):
    '''
    Generates response based on the incoming text. Uses additional class for bug
    with duplicate event received from Messenger.
    '''
    
    
    def _split_number(text_in):
        number_s = ''
        end = ''
        for n, symbol in enumerate(text_in):
            if symbol.isdigit():
                number_s += symbol
            else:
                end = text_in[n:]
                break
        
        if number_s:
            number = int(number_s)
        else:
            number = 0
        
        return number, end
    
    
    def _split_curr_name(text_in):
        name = ''
        end = text_in
        
        for n, symbol in enumerate(text_in):
            if symbol in string.ascii_letters:
                name = text_in[n:n+3]
                end = text_in[n+3:]
                break
                
        return name, end
    
    
    number, end = _split_number(text_in)
    curr1, end = _split_curr_name(end)
    curr2, _ = _split_curr_name(end)
    
    if (number != 0) and all((curr1, curr2)):
        text_out = 'You asked to change {} units between {} and {}.'.format(number,
                                                                            curr1,
                                                                            curr2)
    else:
        text_out = 'Please, enter legal request.'
        
    return text_out