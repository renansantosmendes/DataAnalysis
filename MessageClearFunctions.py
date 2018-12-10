import pandas as pd
import numpy as np
import requests, emoji
import time
import re, string
import unicodedata
import six

def get_json_without_normalization(df):
    items_list = []
    for i in range(df.shape[0]):   
        obj = {}
        obj["configuration"] = {
            "unicodeNormalization": False,
            "toLower": True,
            "informationLevel": 3
        }
        obj["id"] = str(df.iloc[i,0])
        obj["text"] = df.iloc[i,9]
        obj["dateCheck"] = False
        items_list.append(obj)
        
    return items_list

def get_json_with_normalization(df):
    items_list = []
    for i in range(df.shape[0]):   
        obj = {}
        obj["configuration"] = {
            "unicodeNormalization": True,
            "toLower": True,
            "informationLevel": 3
        }
        obj["id"] = str(df.iloc[i,0])
        obj["text"] = df.iloc[i,9]
        obj["dateCheck"] = False
        items_list.append(obj)
        
    return items_list


def lower_case(message):
    return message.lower()

def remove_emojis(message):
    emoji_pattern = re.compile("["
        u"\U0001F600-\U0001F64F"  # emoticons
        u"\U0001F300-\U0001F5FF"  # symbols & pictographs
        u"\U0001F680-\U0001F6FF"  # transport & map symbols
        u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                           "]+", flags=re.UNICODE)
    emoji_pattern.sub(r'', message)    
    return message

def remove_accentuation(message):
    new_message = []
    for word in message.split():
        new_message.append(remove_accentuation_from_word(word))
    return ' '.join(new_message)

def remove_punctuation(text):
    text = np.array([text])
    pattern = "[{}]".format(string.punctuation.replace('@',''))
    text = [word.lower() for word in text]
    text = [[re.sub(pattern, ' ', word) for word in words.split()] for words in text]
    text = [[word for word in words if len(word) > 1] for words in text]
    text = [' '.join(words) for words in text]
    text = ' '.join(text)
    text = text.strip()
    return text

def remove_accentuation_from_word(word):
    import unicodedata
    nfkd = unicodedata.normalize('NFKD', word)
    word_without_accentuation = u"".join([c for c in nfkd if not unicodedata.combining(c)])

    # Usa expressão regular para retornar a palavra apenas com números, letras e espaço
    return re.sub('[^a-zA-Z0-9]', '', word_without_accentuation)


def convert_lists_in_dic(list_a,list_b):
    new_dict = {}
    for element_a,element_b in zip(list_a,list_b):
        new_dict[element_a] = element_b
    return new_dict

def remove_abreviations(message):
    file_name = 'abreviations.txt'
    abreviations = []
    correct_word = []
    with open(file_name,'r',encoding='utf-8') as file:
        for relation in file.read().split('\n'):
            abreviations.append(relation.split(',')[0])
            correct_word.append(relation.split(',')[1])
       
    abreviations_dict = convert_lists_in_dic(abreviations,correct_word)
    
    correct_message = []
    for word in message.split():
        #print(word)
        if word in abreviations_dict.keys():
            correct_message.append(abreviations_dict[word])
        else:
            correct_message.append(word)
        
    return ' '.join(correct_message)


def remove_portuguese_errors(message):
    file_name = 'portuguese_errors.txt'
    errors = []
    correct_word = []
    with open(file_name,'r',encoding='utf-8') as file:
        for relation in file.read().split('\n'):
            errors.append(relation.split(',')[0])
            correct_word.append(relation.split(',')[1])
       
    errors_dict = convert_lists_in_dic(errors,correct_word)
    
    correct_message = []
    for word in message.split():
        if word in errors_dict.keys():
            correct_message.append(errors_dict[word])
        else:
            correct_message.append(word)
        
    return ' '.join(correct_message)


def post_processing(message):
    if type(message) == str:
       
        #retirar emojis e emoticons
        message = remove_emojis(message)

        #remover acentos e pontuação
        message = remove_accentuation(message)
        
        #corrigir abreviações
        #message = remove_abreviations(message)

        #corrigir erros de digitação
        #message = remove_portuguese_errors(message)

        # refazer - remover acentos e pontuação
        #message = remove_accentuation(message)
        
        return message
    else:
        return message

def pre_processing(message):
    """ Pre processing function to prepare messages to SmallTalk API request """
    
    if type(message) == str:

        message = lower_case(message)
        message = remove_punctuation(message)
        message = remove_abreviations(message)
        message = remove_portuguese_errors(message)
        
        return message

    else:
        return message
    
    
def is_empty(message):
    return message.isna()  


def is_significant(msg):
    if type(msg) is str:
        return len(msg) > 2
    else:
        return False

    
def is_trash(msg):
    if type(msg) is str:
        if len(msg.split()) > 1:
            return True
        else:
            return False
    else:
        return False

    
def convert_to_int(msg):
    msg = remove_punctuation(msg)
    try:
        integer = int(msg)
        return True
    except:
        return False


def is_text_plain(content):
    if content == 'text/plain':
        return True
    else:
        return False


def message_is_empty(message):
    if type(message) is str:
        return len(message) == 0
    else:
        return True
    

def is_bot_test(message):
    word1 = ' teste '
    word2 = ' take '
    if type(message) is str:
        return word1 in message or word2 in message
    else:
        return False
    

def is_uri(message):
    word1 = ' uri '
    if type(message) is str:
        return word1 in message
    else:
        return False
    

def is_numeric(msg):
    msg = msg.replace('.','').replace('-','').replace('/','').replace(' ','')
    return msg.isnumeric()


def remove_punctuation(text):
    text = np.array([text])
    pattern = "[{}]".format(string.punctuation)
    text = [[re.sub(pattern, ' ', word) for word in words.split()] for words in text]
    text = [[word for word in words if len(word) > 1] for words in text]
    text = [' '.join(words) for words in text]
    text = ' '.join(text)
    return text


def is_number(msg):
    text = remove_punctuation(msg)
    return text.isalpha()


def smalltalk_requests_without_normalization(data, number_of_batches, request_id):
    
    #Spliting the data into feasible lenght to use in smalltalk api
    data_splitted = np.array_split(data, number_of_batches)
    
    #Calling the API
    r = []
    i = 0
    for dataframe in data_splitted:
        items_list = get_json_without_normalization(dataframe)
        
        begin = time.time()
        obj = {"id": request_id + '_without_norm_' +str(i) , "items": items_list}

        r.append(requests.post('http://hmg-az-infobots.take.net/smalltalks/api/Analysis/batch', json=obj))

        end = time.time()
        print('Process finished! Time elapsed = ' + str((end - begin)) +' seconds')
        i = i + 1

    return r


def smalltalk_requests_with_normalization(data, number_of_batches, request_id):
    #Spliting the data into feasible lenght to use in smalltalk api
    data_splitted = np.array_split(data, number_of_batches)
    
    #Calling the API
    r = []
    i = 0
    for dataframe in data_splitted:
        items_list = get_json_with_normalization(dataframe)
        
        begin = time.time()
        obj = {"id": request_id + '_with_norm_' +str(i) , "items": items_list}

        r.append(requests.post('http://hmg-az-infobots.take.net/smalltalks/api/Analysis/batch', json=obj))

        end = time.time()
        print('Process finished! Time elapsed = ' + str((end - begin)) +' seconds')
        i = i + 1

    return r


def remove_underscore(msg):
    while '_' in msg:
        msg = msg.replace('_','')
    return msg


def converting_response_from_API(r):
    columns = 'MessageId Input CleanedInput RelevantInput MarkedInput'.split()
    api_response_data = pd.DataFrame(data = None)

    for message in r.json()['items']:
        Id = message['id']
        Input = message['analysis']['input']
        CleanedInput = message['analysis']['cleanedInput'].lower()  
        RelevantInput = message['analysis']['relevantInput'].lower()
        MarkedInput = message['analysis']['markedInput'].lower()
        
        matches = message['analysis']['matches']
        if len(matches) > 0:
            for match in matches:
                if match['smallTalk'] == 'Negation':
                    value = match['value']
                    index = match['index']
                    lenght = match['lenght']
                    MarkedInput = MarkedInput[:index] + value + MarkedInput[index + lenght:] #MarkedInput.replace('_' * lenght, value)

                elif match['smallTalk'] == 'Confirmation':
                    value = match['value']
                    index = match['index']
                    lenght = match['lenght']
                    MarkedInput = MarkedInput[:index] + value + MarkedInput[index + lenght:]    
                    
                else:
                    value = match['value']
                    index = match['index']
                    lenght = match['lenght']
                    MarkedInput = MarkedInput.replace('_' * lenght, '')
            
        MarkedInput = remove_underscore(MarkedInput)        
        line = [Id, Input, CleanedInput, RelevantInput, MarkedInput]
        line_dataframe = pd.DataFrame(data = line)
        api_response_data = api_response_data.append(line_dataframe.T).reset_index(drop = True)

    api_response_data.reset_index()
    api_response_data.columns = columns
    
    return api_response_data


def remove_whatsapp_emojis(msg):
    if type(msg) is int or type(msg) is float:
        return msg
    message = []
    if len(msg.split()) == 1:
        msg = remove_emoji_from_word(msg)
        return msg
    for word in msg.split():
        word = remove_emoji_from_word(word)
        message.append(word)
    return ' '.join(message).strip()


def str_strip(msg):
    if type(msg) is float or type(msg) is int:
        return msg
    return msg.strip()


def remove_emoji_from_word(teste):
    word = []
    for i in range(len(teste)):
        character = teste[i]    
        if character in emoji.EMOJI_UNICODE.values():
            word.append(teste[i].replace(character,' '))
        else:
            word.append(character)

    new_word = []        
    for j in range(len(word)):
        if word[j] == ' ' or word[j].isalpha() or word[j].isnumeric():
            new_word.append(word[j])
    new_word = ''.join(new_word)
    return new_word