'''
Created on Jun 22, 2020

@author: Vasyalisk
'''
from database import db_setup

import string, enum, json, datetime



RESPONSE_TEXT_CONF = 'response_text.conf'

with open(RESPONSE_TEXT_CONF) as conf:
    RESPONSE_TEXT = json.load(conf)


@enum.unique
class ChatStatus(enum.Enum):
    IDLE = 'IDLE'
    RATES = 'RATES'
    EXCHANGE = 'EXCHANGE'
    CODE = 'CODE'
    

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
        '''
        Process supported events from single POST request.
        '''
        
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
        text_out = self._process_commands(user_id, text_in)
        
        if not text_out:
            METHODS_MAP = {ChatStatus.IDLE    : self._process_idle,
                           ChatStatus.RATES   : self._process_rates,
                           ChatStatus.EXCHANGE: self._process_exchange,
                           ChatStatus.CODE    : self._process_code}
            
            
            chat_status = self._get_chat_status(user_id)
            text_out = METHODS_MAP[chat_status](user_id, text_in)
        
        entry_out = {
                     'messaging_type': 'RESPONSE',
                     'recipient'     : {'id' : user_id},
                     'message'       : {'text': text_out}
                     }
        
        return entry_out
    
    
    def _process_commands(self, user_id, text_in):
        '''
        Generates response to predefined chat commands. 
        '''
        
        text_out = ''
        
        if '?help' in text_in:
            text_out = RESPONSE_TEXT['t_help']
            self.update_chat_data(user_id, status=ChatStatus.IDLE)
        elif '?code' in text_in:
            code = self._strip_code(text_in)
            if code:
                text_out = self._process_code(user_id, text_in)
            else:
                text_out = RESPONSE_TEXT['t_code']
                self.update_chat_data(user_id, status=ChatStatus.CODE)
        elif '?rates' in text_in:
            codes = self._strip_codes(text_in)
            if all(codes):
                text_out = self._process_rates(user_id, text_in)
            else:
                text_out = RESPONSE_TEXT['t_rates']
                self.update_chat_data(user_id, status=ChatStatus.RATES)
        elif '?exchange' in text_in:
            codes = self._strip_codes(text_in)
            amount = self._strip_number(text_in)
            if all(codes) and (amount is not None):
                text_out = self._process_exchange(user_id, text_in)
            else:
                text_out = RESPONSE_TEXT['t_exchange']
                self.update_chat_data(user_id, status=ChatStatus.EXCHANGE)
        elif '?start' in text_in:
            # to do
            self.update_chat_data(user_id, status=ChatStatus.IDLE)
            
        return text_out
    
    
    def _process_code(self, user_id, text_in):
        '''
        Processes user input if current chat status is CODE and generates
        response.
        '''
        
        code = self._strip_code(text_in)
        if self._get_code_rate(code):
            text_out = RESPONSE_TEXT['t_code_resp'].format(code)
        else:
            text_out = RESPONSE_TEXT['t_code_err'].format(code)
        self.update_chat_data(user_id, status=ChatStatus.IDLE)
        
        return text_out
    
    
    def _process_idle(self, user_id, text_in):
        '''
        Processes user input if current chat status is IDLE and generates
        response.
        '''
        
        text_out = RESPONSE_TEXT['t_idle_err']
        self.update_chat_data(user_id, status=ChatStatus.IDLE)
            
        return text_out
    
    
    def _process_rates(self, user_id, text_in):
        '''
        Processes user input if current chat status is RATES and generates
        response.
        '''
        
        code1, code2 = self._strip_codes(text_in)
        rate1, rate2 = self._get_code_rate(code1), self._get_code_rate(code2) 
        
        if rate1 and rate2:
            am1 = '{:.2f}'.format(rate2 / rate1)
            am2 = '{:.2f}'.format(rate1 / rate2)
            params = code1, am1, code2, code2, am2, code1
            text_out = RESPONSE_TEXT['t_rates_resp'].format(*params)
            self.update_chat_data(user_id, status=ChatStatus.IDLE)
        else:
            text_out = RESPONSE_TEXT['t_rates_err']
        
        return text_out
            
    
    def _process_exchange(self, user_id, text_in):
        '''
        Processes user input if current chat status is EXCHANGE and generates
        response.
        '''
        
        code1, code2 = self._strip_codes(text_in)
        am0 = self._strip_number(text_in)
        rate1, rate2 = self._get_code_rate(code1), self._get_code_rate(code2)
        
        if rate1 and rate2 and (am0 is not None):
            am1 = '{:.2f}'.format(rate2 * am0 / rate1)
            am2 = '{:.2f}'.format(rate1 * am0 / rate2)
            params = am0, code1, am1, code2, am0, code2, am2, code1
            text_out = RESPONSE_TEXT['t_exchange_resp'].format(*params)
            self.update_chat_data(user_id, status=ChatStatus.IDLE)
        else:
            text_out = RESPONSE_TEXT['t_exchange_err']
            
        return text_out
    
    
    def _strip_code(self,text):
        '''
        Returns first 3-letter substring from text, which is separated by
        non-letter from both sides.
        '''
        
        code = ''
        code_length = 3
        n = 0
        
        for n, symbol in enumerate(text):
            if symbol in string.ascii_letters:
                code += symbol
                if len(code) == code_length:
                    break
            else:
                code = ''
        else:
            code = code if len(code) == code_length else ''
        
        try:
            suff = text[n+1]
        except IndexError:
            suff = ' '
        
        if suff in string.ascii_letters:
            code = self._strip_code(text[n+1:])
            
        return code.upper()
    
    
    def _strip_codes(self, text):
        '''
        Returns first two 3-letter substrings from text, which are separated by
        non-letter from both sides each.
        '''
        
        code1 = self._strip_code(text)
        sep = text.upper().find(code1) + len(code1)
        
        if code1 and sep < len(text):
            code2 = self._strip_code(text[sep:])
        else:
            code2 = ''
            
        return code1.upper(), code2.upper()
    
    
    def _strip_number(self, text):
        '''
        Returns first integer in text.
        '''
        
        digits = '0123456789'
        number = ''
        
        for symbol in text:
            if symbol in digits:
                number += symbol
            elif number:
                break
        
        return int(number) if number else None
    
    
    def process_postback(self, entry_in):
        '''
        Sends message as a response to postback event. Also updates database's
        ChatData table.
        '''
        
        user_id = entry_in['sender']['id']
        payload = entry_in['postback']['payload']
        text_out = ''
        
        if payload == ChatPayload.RATES.value:
            text_out = self._process_commands(user_id, '?rates')
        elif payload == ChatPayload.EXCHANGE.value:
            text_out = self._process_commands(user_id, '?exchange')
        elif payload == ChatPayload.HELP.value:
            text_out = self._process_commands(user_id, '?help')
        elif payload == ChatPayload.GET_STARTED.value:
            # TO DO
            text_out = self._process_commands(user_id, '?start')
        
        entry_out = {
                     'messaging_type': 'RESPONSE',
                     'recipient'     : {'id' : user_id},
                     'message'       : {'text': text_out}
                     }
            
        return entry_out
    
    
    def update_chat_data(self, user_id, *, status):
        '''
        Updates entry for each user chat in the database or creates new.
        '''
        
        entry = self.db.session.query(db_setup.ChatData).get(user_id)
        now = datetime.datetime.now()
        
        if entry is None:
            new_entry = db_setup.ChatData(user_id=user_id,
                                          chat_status=status.value,
                                          last_msg_date=now)
            self.db.session.add(new_entry)
        else:
            entry.chat_status = status.value
            entry.last_msg_date = now
            
        self.db.session.commit()
        
    
    def _get_chat_status(self, user_id):
        '''
        Returns ChatStatus enum for current user. If entry does not exist
        returns ChatStatus.IDLE.
        '''
        
        entry = self.db.session.query(db_setup.ChatData).get(user_id)
        
        if entry is None:
            status = ChatStatus.IDLE
        else:
            status = ChatStatus[entry.chat_status]
            
        self.db.session.expire_all()
        return status
    
    
    def _get_code_rate(self, code):
        '''
        Returns currency rate for the code if it is in the database. Returns 0
        otherwise.
        '''
        
        entry = self.db.session.query(db_setup.CurrencyExchangeRate).get(code)
        
        if entry is None:
            rate = 0
        else:
            rate = entry.ex_rate
            
        self.db.session.expire_all()
        return rate