import re
import copy 
import locale
from datetime import datetime

# Locate the file path of the file to be read
file_path_visura = '/Users/giuls/Desktop/SBT 4/download-file-api_visura2.txt'

# Defines tag to be used from the file
tags = {
    'descrizione_attivita': 'attivita',   
    'ateco_code' : 'c-attivita'          
}

# Define a tag value
tags_types = {
    'descrizione_attivita' : 'str',
    'ateco_code'  : 'str'
}

# Function to extract the Company incorporation year and returns years of experience
def get_incorporation():
    # Open the file to read content
    with open(file_path_visura, 'r') as f:
        content = f.read()
    incorporation = {}
    match = re.search(r'dt-iscrizione-ri="([^"]+)"', content)
    if match:
        date_iscrizione = match.group(1)
        print(date_iscrizione)
        # Converts data string inot an data object
        incorporation = datetime.strptime(date_iscrizione, '%d/%m/%Y').date()
        # Calculates years of trading, since the Company was set up
        years_since_incorporation = (datetime.now().date() - incorporation).days // 365
        return years_since_incorporation
    else:
        print('No match found for date_iscrizione')
    return incorporation 
incorporation = get_incorporation()
print(incorporation, "years of experience in the market")    

# Function that extract the Company business description from Visura Camerale
def get_attivita():
    #Open file to read content
    with open(file_path_visura, 'r') as f:
        content = f.read()
    ateco_description = ''
    # regukar expreession to extract the type of business from xml file
    tag_matches = re.search(r'<classificazione-ateco[^>]* attivita="([^"]+)"', content)
    if tag_matches:
        attivita = tag_matches.group(1)
        ateco_description = attivita
    else:
        return "Attribute 'attivita' not found in the XML file."
    return ateco_description

# Function thatextracts the ATECO code from the Visura Camerale
def get_ateco_code():
    with open(file_path_visura, 'r') as f:
        content = f.read()
    # Regular expression to extract Ateco code ftorm xml file
    tag_matches = re.search(r'c-attivita="(\d+)"', content)
    if tag_matches:
        ateco_code = tag_matches.group(1)
    #If match is not found return error message 
    else:
        return "Ateco Code not found in the XML Visura file."
    return ateco_code


