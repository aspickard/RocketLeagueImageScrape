import os
import json
import requests

BASE_DIR = "./images/"

blacklist = ['.git', '.DS_Store']
directories = [name for name in os.listdir(BASE_DIR) if os.path.isdir(BASE_DIR + name) and name not in blacklist]

schema = {}

for directory in directories:
    cur_type = schema[directory] = {}
    subdirs = [name for name in os.listdir(BASE_DIR + directory) if name not in blacklist]
    for subdir in subdirs:
        items = [name for name in os.listdir(BASE_DIR + directory + "/" + subdir) if name not in blacklist]
        for item in items:
            name = item[:-4]
            if '619' in name:
                name = name.replace('\xc3\xa4', 'a')
            if '_' in name:
                name = name.replace('_', ' ')
            if name:
                path = directory + "/" + subdir + "/" + item
                cur_type[name] = {
                    'quality': subdir,
                    'image': item,
                    'path': path
                }

del schema['crates']['Decryptor']
del schema['crates']['Key']

schema['credits'] = {'Credits': schema['crates']['Credits']}
schema['key'] = {'Key': schema['crates']['Credits']}
del schema['crates']['Credits']
schema['offers'] = {
    'Offers': {
        'path': 'offers/Common/Offers.png',
        'image': 'Offers.png',
        'quality': 'Common'
    }
}

with open('schema/schema.js', 'w') as schema_file:
    schema_file.write('/* eslint-disable */\n')
    schema_file.write('export default ')
    schema_file.write(json.dumps(schema, indent=4, sort_keys=True))

print("RLGarage schema generated.")

gf_schema = "https://gameflip.com/api/gameitem/inventory/812872018935"
r = requests.get(gf_schema, headers={'User-agent': 'Mozilla/5.0'})

with open('schema/rl-schema.json', 'w') as schema_file:
    schema_file.write(r.text)

print("GameFlip schema generated.")

# print json.dumps(schema, indent=4, sort_keys=True)
