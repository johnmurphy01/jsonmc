# a tool automatically add actors to the database based on the 'unlisted_actors'
# list. It uses tMDB api.
#
# made by themousery :)

# Imports
import os # for various file related functions
import json # for .json files
import requests # for api requests
import sys # for exit
import re # regex for finding birthname

# Variables

# if you want to use this, you can get an api key from tMDB
# https://developers.themoviedb.org/3/getting-started/authentication
api_key = "<< Your Api Key Here >>"

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
        
        # if the wikipedia page doesn't exist, just return the name
        if re.search(',"missing":""}}}}', str(r.content)): return name
        
        # if wikipedia redirects this page, go to the redirect
        redirect = re.search("#REDIRECT \[\[(.*)\]\]", str(r.content))
        if redirect: 
            new_name = redirect.group(1)
            continue
        
        # if there's more than one guy with that name, specify the actor page
        # ex: Tom Holland
        if re.search('may refer to:', str(r.content)): new_name = name + " (actor)"
        else: break
        
    # parse the name out and make it look pretty
    # get the page id
    id = list(r.json()['query']['pages'])[0]
    # get the content of the page
    content = r.json()['query']['pages'][id]['revisions'][0]['*']
    # get the birth name using complicated regex
    try: birthname = re.search("(birth_name|birthname).*= ({{nowrap\|)?(.*)(}})?", content).group(3)
    # if there's no specified birthname, their name is already their birthname
    except: return name
    # chop of the }} if it's there
    if birthname[-2:] ==  "}}": birthname = birthname[:-2]
    
    # sometimes comments such as '<!-- only use if different from name -->'
    # are put in the birth_name place on wikipedia, or the birth name is left 
    # blank. This means their name is the same as the birthname, so just return 
    # name. What i'm doing is making sure the info in the birthname section only
    # contains characters that belong in a name.
    if not birthname.replace(" ", "").replace(".", "").replace("-", "").isalpha():
        return name
            
    
    return birthname
    
# function to skim data from tmdb api and change it to jsonmc format
def jsonmcify(data):
    # make the new data
    new_data = {
        'name':name,
        'birthname':getBirthName(name),
        'birthdate':data['birthday'],
        'birthname':data['place_of_birth']
    }
    
    # strip leading whitespace
    new_data['name'] = new_data['name'].strip()
    new_data['birthname'] = new_data['birthname'].strip()
    if new_data['birthdate']: new_data['birthdate'] = new_data['birthdate'].strip()
    if new_data['birthplace']: new_data['birthplace'] = new_data['birthplace'].strip()
    
    return new_data
    

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