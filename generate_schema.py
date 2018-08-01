import os
import json

blacklist = ['.git', '.DS_Store']
directories = [name for name in os.listdir(".") if os.path.isdir(name) and name not in blacklist]

schema = {}

for directory in directories:
    cur_type = schema[directory] = {}
    subdirs = [name for name in os.listdir("./" + directory) if name not in blacklist]
    for subdir in subdirs:
        items = [name for name in os.listdir("./" + directory + "/" + subdir) if name not in blacklist]
        for item in items:
            name = item[:-4]
            if '\xc2\xae' in name:
                name = name.replace('\xc2\xae', '')
            if '619' in name:
                name = name.replace('\xc3\xa4', '')
            if '_' in name:
                name = name.replace('_', ' ')
            if name:
                cur_type[name] = {
                    'quality': subdir,
                    'image': item,
                }


print json.dumps(schema, indent=4, sort_keys=True)
