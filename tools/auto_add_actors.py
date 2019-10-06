# a tool automatically add actors to the database based on the 'unlisted_actors'
# list. It uses tMDB api.
#
# made by themousery :)

# Imports
import os # for various file related functions
import json # for .json files
import requests # for api requests
import sys # for exit
import unicodedata as ud # for is_latin and only_roman_chars
import re # for finding birthname

# Variables

# if you want to use this, you can get an api key from tMDB
# https://developers.themoviedb.org/3/getting-started/authentication
api_key = "<< Your Api Key Here >>" 

latin_letters= {}

# go to the root dir and store that to a var
os.chdir("..")
ROOT = os.getcwd()

# function to convert an actor name to a file name
# ex: "Tom Cruise" becomes "tom-cruise.json"
def nameToFile(name):
    # replace space with - and make it lowercase
    filename = name.replace(" ", "-").lower()
    # remove any periods (for middle initials, suffixes, etc.)
    filename = filename.replace(".", "")
    # add file extension
    filename = filename + ".json"
    
    return filename
    
# gets details of actor from tMDB id
def getDetails(id):
    # api url
    url = "https://api.themoviedb.org/3/person/" + str(id)
    # parameters to give api
    params = {
        'api_key':api_key,
        'language':'en_US'
    }
    
    # get return data in json format
    r = requests.get(url = url, params = params)
    data = r.json()
    
    return data

# does a search in the Movie Database api for a given actor name
def search(name):
    # api url
    url = "https://api.themoviedb.org/3/search/person"
    # parameters to give to api
    params = {
        'api_key':api_key,
        'language':'en_US',
        'query':name,
        'page': 1,
        'include_adult':'false'
    }
    
    # get return data in json format
    r = requests.get(url = url, params = params)
    data = r.json()
    
    # return details about them if they exist, otherwise just quit
    if len(data['results'])>0 and data['results'][0]['name'] == name: 
        id = data['results'][0]['id']
        return getDetails(id)
    else: 
        return False

# function to get a person's birth name from the wikipedia api
def getBirthName(name):
    try:
        new_name = name
        while True:
            url = "https://en.wikipedia.org/w/api.php?"
            params = {
                'action':'query',
                'titles':new_name,
                'format':'json',
                'prop':'revisions',
                'rvsection':'0',
                'rvprop':'content'
            }
            # get page data
            r = requests.get(url=url, params=params)
            
            # if there's more than one guy with that name, go to the actor page
            if re.search('may refer to:', str(r.content)): new_name = name + " (actor)"
            else: break
        
        # parse the name out and make it look pretty
        # get the page id
        id = list(r.json()['query']['pages'])[0]
        # get the content of the page
        content = r.json()['query']['pages'][id]['revisions'][0]['*']
        # get the birth name using complicated regex
        birthname = re.search("birth_name.*= ({{nowrap\|)?(.*)(}})?", content).group(2)
        # chop of the }} if it's there
        if birthname[-2:] ==  "}}": birthname = birthname[:-2]
        
        # sometimes comments such as '<!-- only use if different from name -->'
        # are put in the birth_name place on wikipedia, so just return name
        if not birthname.replace(" ", "").isalpha(): return name
        
        return birthname
        
    # if all else fails, just set the birthname to name.
    except:
        return name
    
# function to skim data from tmdb api and change it to jsonmc format
def jsonmcify(data):
    # put in the name, birthdate, and birthplace
    new_data = {}
    
    # name
    new_data['name'] = name
    
    # birth name
    new_data['birthname'] = getBirthName(name)
    
    # birthdate
    new_data['birthdate'] = data['birthday']
    # strip whitespace
    if new_data['birthdate']: new_data['birthdate'] = new_data['birthdate'].strip()
    
    # birthplace
    new_data['birthplace'] = data['place_of_birth']
    # strip whitespace
    if new_data['birthplace']: new_data['birthplace'] = new_data['birthplace'].strip()
    
    # strip leading whitespace
    new_data['name'] = new_data['name'].strip()
    new_data['birthname'] = new_data['birthname'].strip()
    
    return new_data
    

# both functions below are for checking for roman chars in a string.
# this is for checking birthnames, as tmdb lists these in "also_known_as"
# along with translated versions of the name
#
# https://stackoverflow.com/questions/3094498/how-can-i-check-if-a-python-unicode-string-contains-non-western-letters
def is_latin(uchr):
    try: return latin_letters[uchr]
    except KeyError:
         return latin_letters.setdefault(uchr, 'LATIN' in ud.name(uchr))

def only_roman_chars(unistr):
    return all(is_latin(uchr)
           for uchr in unistr
           if uchr.isalpha()) # isalpha suggested by John Machin

# check if the user hasn't entered their own api key
if api_key == "<< Your Api Key Here >>":
    print("\nYou need to get an api key from tMDB and put it in the script.")
    sys.exit()

# get the list of unlisted actors
with open("tools/unlisted_actors.txt", 'r', encoding='utf-8') as read_file:
    # get the data and 'jsonmcify' it
    for name in read_file:
        name = name.rstrip()
        data = search(name)
        if not data: continue # if we can't find them, just continue to next person
        new_data = jsonmcify(data)
        print(name)

        # write the info to a new file
        with open("actors/"+nameToFile(name), 'w', encoding='utf-8') as write_file:
            json.dump(new_data, write_file, indent=2, ensure_ascii=False)