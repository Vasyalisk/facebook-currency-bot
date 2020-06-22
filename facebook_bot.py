'''
Created on Jun 22, 2020

@author: Vasyalisk
'''
import string, enum



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
    
    def __init__(self, data_in):
        self.data_in = data_in
        self.METHODS_MAP = {
                            EventType.MESSAGES:            self.process_message,
                            EventType.MESSAGING_POSTBACKS: self.process_postback
                            } 
    
        
    def process_events(self):
        data_out = []
        entries_in = [e['messaging'][0] for e in self.data_in['entry'] if e]
        
        for entry_in in entries_in:
            e_type = self.get_event_type(entry_in)
            entry_out = self.METHODS_MAP[e_type](entry_in)
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
    
    
    @staticmethod
    def process_message(entry_in):
        '''
        Echoes message back to user.
        
        Incoming message JSON format:
        https://developers.facebook.com/docs/messenger-platform/reference/webhook-events/messages
        
        Sending API:
        https://developers.facebook.com/docs/messenger-platform/reference/send-api
        '''
        
        user_id = entry_in['sender']['id']
        text_in = entry_in['message']['text']
        
        entry_out = {
                     'messaging_type': 'RESPONSE',
                     'recipient'     : {'id' : user_id},
                     'message'       : {'text': text_in}
                     }
        
        return entry_out
    
    
    @staticmethod
    def process_postback(entry_in):
        entry_out = entry_in
        return entry_out
    

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