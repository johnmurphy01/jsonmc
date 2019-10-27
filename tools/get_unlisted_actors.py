# a tool to generate a list of actors credited in movies that do not have a
# json file in /actors (hereby referred to as 'unlisted actors')
# 
# made by themousery :)

# Imports 
import glob, os # for various file related functions
import json # for reading .json files

unlisted_actors = [] # soon-to-be list of unlisted actors

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

# recursively loop through /movies
for filename in glob.iglob(ROOT+"/movies/**", recursive=True):
    # only look at the json files, not the directories
    if os.path.isfile(filename):
        # read each movie json file
        with open(filename, 'r', encoding='utf-8') as read_file:
            data = json.load(read_file)
            # loop through each actor and check if they have a file
            for actor in data['actors']:
                if not os.path.exists(ROOT+"/actors/"+nameToFile(actor)):
                    # if they don't have a file, add them to the list
                    unlisted_actors.append(actor)

# sort the list alphabetically and remove duplicates
unlisted_actors = list(set(unlisted_actors))
unlisted_actors.sort()

# add them all to a .txt file
with open("tools/unlisted_actors.txt", 'w', encoding='utf-8') as write_file:
    for actor in unlisted_actors:
        write_file.write(actor + "\n")