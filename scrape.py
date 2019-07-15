import requests
import shutil
import os
from bs4 import BeautifulSoup as BS
import sys
reload(sys)
sys.setdefaultencoding('utf-8')


BASE_PATH = "images/"

ALL_ITEM_NAMES = {}
DEBUG_LEVEL = 3

COMMON_PAINTED_KEYS = ['bodies', 'boosts', 'toppers', 'wheels']

def is_tradeable(key, name, rarity, platform):
    return (rarity != 'Premium' or name == 'Key') and platform == 'All' and (rarity != 'Common' or key in COMMON_PAINTED_KEYS)

def scrape(download=True, redownload=False, ambiguous=None):
    info('RL Garage Scrape Started')
    ITEM_NAMES = {}
    AMBIGUOUS_NAMES = {}
    items = {'bodies', 'wheels', 'boosts', 'antennas', 'decals', 'toppers', 'trails', 'explosions', 'paints',
             'banners', 'engines', 'borders', 'titles', 'crates'}

    new_ambiguous = []
    # iterate through each item in items
    for key in items:
        ALL_ITEM_NAMES[key] = []
        ITEM_NAMES[key] = []
        AMBIGUOUS_NAMES[key] = []
        # try to get the site tree until it returns properly
        while True:
            # tree is getting all the divs with the class 'rlg-items-item'
            tree = get_tree_rl(key).find_all('div', class_='rlg-items-item')
            if len(tree) > 0:
                break

        # iterate through each div in the tree
        for t in tree:
            # get the <img> tag
            img = t.img

            # get the imgae source from that <img> tag
            src = ("https://rocket-league.com" + img['src']).strip()

            # get the name of the item
            name = t.h2.get_text().strip().replace(" ", "_")

            if ambiguous and name in ambiguous[key]:
                try:
                    category = t.parent.find_previous_sibling('h2').get_text().strip()
                    cat = [x for x in ALL_ITEM_NAMES['bodies'] if x.replace("_", " ").lower() == category]

                    # Fix the name of the category
                    if len(cat) == 1:
                        category = cat[0].replace("_", " ")
                    else:
                        category = category.title()
                        warning("Guessing at name {0} ({1})".format(name, category))

                    name = '{0} ({1})'.format(name, category)
                    warning("Correcting ambiguous name {0}".format(name))
                except:
                    warning("Could not correct ambiguous name {0}".format(name))

            # get the rarity of the item
            rarity = t.div.get_text().strip()

            # get the platform
            platform = t.find_all('div', attrs={'data-platform': True})[0]['data-platform']

            #import pdb; pdb.set_trace()

            ALL_ITEM_NAMES[key].append(name)
            if is_tradeable(key, name, rarity, platform):
                if name in ITEM_NAMES[key] and name not in AMBIGUOUS_NAMES[key]:
                    AMBIGUOUS_NAMES[key].append(name)
                    if ambiguous and name not in ambiguous[key]:
                        new_ambiguous.append('{0} {1} {2}'.format(key, rarity, name))

                ITEM_NAMES[key].append(name)

                # set up the file path
                file_path = BASE_PATH + "{}/{}/{}.png".format(key, rarity, name)

                # shows the current object
                info('Detected {0} - {1} - {2}'.format(key, rarity, name))

                if download and (not os.path.exists(file_path) or redownload):
                    try:
                        # get the directory of the file path
                        directory = os.path.dirname(file_path)

                        # if the directory doesn't exist, create it
                        if not os.path.exists(directory):
                            os.makedirs(directory)

                        # request the image at the src, until the status code returned is 200 (successful)
                        while True:
                            r = requests.get(src, stream=True, headers={'User-agent': 'Mozilla/5.0'})
                            if r.status_code == 200:
                                break

                        # create/open the file, and write the contents of the image downloaded into it
                        with open(file_path, 'wb') as f:
                            r.raw.decode_content = True
                            shutil.copyfileobj(r.raw, f)

                        info('Downloaded {0} - {1} - {2}'.format(key, rarity, name))
                    except:
                        error('Failed to downloaded {0} - {1} - {2}'.format(key, rarity, name))
    # Completed!
    info('RL Garage Scrape Complete')
    info('{} unique items discovered'.format(count_values(ITEM_NAMES)))
    info('{} ambiguous item names discovered'.format(count_values(AMBIGUOUS_NAMES)))
    info(AMBIGUOUS_NAMES)
    if new_ambiguous:
        print('WARNING - Potential new ambiguous names detected.')
        print(new_ambiguous)
    return AMBIGUOUS_NAMES

def get_tree_rl(sub):
    return get_tree("https://rocket-league.com/items/" + sub)

def get_tree(url):
    # Requests the page located at the url
    page = requests.get(url)
    # Returns the Beatiful SouptTree
    return BS(page.content, 'html.parser')

def count_values(items):
    return sum(len(v) for v in items.itervalues())

def main():
    ambiguous = scrape(download=False)
    scrape(download=True, ambiguous=ambiguous)

def info(text):
    debugPrint(text, 3)

def warning(text):
    debugPrint(text, 2)

def error(text):
    debugPrint(text, 1)

def debugPrint(text, level):
    if level <= DEBUG_LEVEL:
        print(text)

main()
