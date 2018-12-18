import pandas as pd
import numpy as np
import string
import re
import emoji
from time import time
from unicodedata import normalize, combining
from requests import post

def get_json(df, normalization):
    items_list = []
    for idx in range(df.shape[0]):   
        obj = {}
        obj['configuration'] = {
            'unicodeNormalization': normalization,
            'toLower': True,
            'informationLevel': 3
        }
        obj['text'] = df.loc[idx,'Processed Content']
        obj['dateCheck'] = False
        items_list.append(obj)        
    return items_list

def remove_emojis(message):
    emoji_pattern = re.compile('['
        u'\U0001F600-\U0001F64F'  # emoticons
        u'\U0001F300-\U0001F5FF'  # symbols & pictographs
        u'\U0001F680-\U0001F6FF'  # transport & map symbols
        u'\U0001F1E0-\U0001F1FF'  # flags (iOS)
                           ']+', flags=re.UNICODE)
    new_message = emoji_pattern.sub(r'', message)    
    return new_message

def remove_accentuation(message):
    nfkd = normalize('NFKD', message)
    word_without_accentuation = u''.join([c for c in nfkd if not combining(c)])
    return word_without_accentuation.strip()

def remove_punctuation(message):
    pattern = '[{}]'.format(string.punctuation.replace('@',''))
    new_message = re.sub(pattern, ' ', message)
    return new_message

def use_dictonary_from_file(message, file_name):
    abreviations_dict = {}
    with open(file_name,'r',encoding='utf-8') as file:
        for relation in file.read().split('\n'):
            k, v = relation.split(',')
            abreviations_dict[k] = v
    
    correct_message = []
    for word in message.split():
        if word in abreviations_dict.keys():
            correct_message.append(abreviations_dict[word])
        else:
            correct_message.append(word)        
    return ' '.join(correct_message)
    
def remove_abbreviations(message): 
    return use_dictonary_from_file(message, 'abbreviations.txt')

def remove_portuguese_errors(message):
    return use_dictonary_from_file(message, 'portuguese_errors.txt' )

def smalltalk_requests(data, api_small_talks, number_of_batches, request_id, normalization):
    
    #Spliting the data into feasible lenght to use in smalltalk api
    data_splitted = np.array_split(data, number_of_batches)
    
    #Calling the API
    r = []
    for idx, dataframe in enumerate(data_splitted):
        dataframe = dataframe.reset_index()
        items_list = get_json(dataframe, normalization)
        
        begin = time()
        obj = {'id': str(request_id) + '_' + ('with' if normalization else 'without') + '_norm_' + str(idx) , 'items': items_list}
        
        r.append(post(api_small_talks, json=obj))

        end = time()
        print('Process finished! Time elapsed = ' + str((end - begin)) +' seconds')
    return r

def converting_response_from_API(r):
    columns = 'Input CleanedInput RelevantInput MarkedInput'.split()
    api_response_data = pd.DataFrame(data = None)

    for message in r['items']:
        Input = message['analysis']['input']
        CleanedInput = message['analysis']['cleanedInput']  
        RelevantInput = message['analysis']['relevantInput']
        MarkedInput = message['analysis']['markedInput']
        
        matches = message['analysis']['matches']
        if len(matches) > 0:
            for match in matches:

                lenght = match['lenght']
                
                if match['smallTalk'] == 'Negation':
                    value = match['value']
                    index = match['index']
                    MarkedInput = MarkedInput[:index] + value + MarkedInput[index + lenght:]
                    RelevantInput = RelevantInput[:index] + value + RelevantInput[index + lenght:]
                else:
                    MarkedInput = MarkedInput.replace('_' * lenght, '')
                    RelevantInput = RelevantInput.replace('_' * lenght, '')
        line = [Input, CleanedInput, RelevantInput, MarkedInput]
        line_dataframe = pd.DataFrame(data = line)
        api_response_data = api_response_data.append(line_dataframe.T).reset_index(drop = True)

    api_response_data.reset_index()
    api_response_data.columns = columns
    return api_response_data

def remove_whatsapp_emojis(message):
    new_message = [character for character in message if character not in emoji.EMOJI_UNICODE.values()]
    return ''.join(new_message)

def remove_numbers(message):
    new_message = re.sub(r'[-+]?\d*\.\d+|\d+', ' ', message)
    return new_message

def remove_spaces(message):
    new_message = re.sub('\s\s+' , ' ', message)
    return new_message

class PreProcessing:
    
    def __init__(self, input_file, api_small_talks = None, content_column = 'Content', encoding = 'utf-8', sep = ';', batch = 4):
        data = pd.read_csv(input_file, encoding = encoding, sep = sep)
        self.data = data
        self.input_file = input_file
        self.batch = batch
        self.api_small_talks = api_small_talks
        if type(content_column) == str: 
            self.text = data.loc[:, content_column]
        elif type(content_column) == int:
            self.text = data.loc[:, content_column]
        
    def process(self, output_file, lower = True, punctuation = True, abbreviation = True, typo = True, small_talk = True, emojis = True, wa_emojis = True, accentuation = True, number = True, relevant = False):
        
        data_processed = pd.DataFrame(data = self.text)
        data_processed.columns = ['Content']
        data_processed['Processed Content'] = self.text
        
        if emojis: data_processed['Processed Content'] = data_processed['Processed Content'].apply(remove_emojis)
        if wa_emojis: data_processed['Processed Content'] = data_processed['Processed Content'].apply(remove_whatsapp_emojis)
        if lower:  data_processed['Processed Content'] = data_processed['Processed Content'].str.lower()
        if punctuation: data_processed['Processed Content'] = data_processed['Processed Content'].apply(remove_punctuation)
        if abbreviation: data_processed['Processed Content'] = data_processed['Processed Content'].apply(remove_abbreviations)
        if typo: data_processed['Processed Content'] = data_processed['Processed Content'].apply(remove_portuguese_errors)
        if accentuation: data_processed['Processed Content'] = data_processed['Processed Content'].apply(remove_accentuation)
        if number: data_processed['Processed Content'] = data_processed['Processed Content'].apply(remove_numbers)
        data_processed['Processed Content'] = data_processed['Processed Content'].apply(remove_spaces)
        
        if small_talk and self.api_small_talks is not None:
            responses = smalltalk_requests(data_processed, self.api_small_talks, self.batch, self.input_file, True)
            without_small_talks = [converting_response_from_API(response.json()) for response in responses]
            without_small_talks = pd.concat(without_small_talks).reset_index()
            if relevant:
                data_processed['Processed Content'] = without_small_talks.loc[:,'RelevantInput']
            else:
                data_processed['Processed Content'] = without_small_talks.loc[:,'MarkedInput']
            
        data_processed.to_csv(output_file,sep=';',encoding='utf-8',index=False)