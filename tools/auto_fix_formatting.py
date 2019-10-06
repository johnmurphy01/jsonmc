# a tool to automatically fix the formatting of every single file in the repo
#
# made by themousery :)

# Imports
import glob, os # for various file-related functions
import json # for fixing the formatting
import codecs

# go to the root dir and store that to a var
os.chdir("..")
ROOT = os.getcwd()

# recursively loop through every single .json file
for filename in glob.iglob(ROOT+"/**", recursive=True):
    # only look at the json files
    if os.path.isfile(filename) and filename[-5:] == ".json":
        print(filename)
        
        folder = filename.split("\\")[-2]
        # get the data in json format
        with codecs.open(filename, 'r', encoding='utf-8') as read_file:
            data = json.load(read_file)
            
            # remove some trailing whitespace
            if folder == "movies" or folder == "directors":
                if data['name']: data['name'] = data['name'].strip()
                if 'birthname' in data.keys() and data['birthname']: data['birthname'] = data['birthname'].strip()
                if data['birthdate']: data['birthdate'] = data['birthdate'].strip()
                if data['birthplace']: data['birthplace'] = data['birthplace'].strip()
            
        # rewrite the file with correct formatting
        with codecs.open(filename, 'w', encoding='utf-8') as write_file:
            json.dump(data, write_file, indent=2, ensure_ascii=False)
            write_file.write('\n')