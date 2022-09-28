import util

holo_en = dict()
holo_id = dict()
niji_en = dict()
niji_exid = dict()
talents = dict()

test_talents = dict()

def __create_dict(file, _dict):
    print(f'Initializing talents\' account list from {file}...')
    global talents
    with open(file, 'r') as f:
        for line in f:
            words = line.split()
            if len(words) == 2 and line[0] != '#':
                name, id = line.split()
                name = util.get_username_online(id, default=name) # attempt to get updated name
                talents[int(id)] = name
                _dict[int(id)] = name
def init():
    global holo_en
    global holo_id
    global niji_en
    global niji_exid
    global test_talents

    # holoEN
    __create_dict(f'{util.get_project_dir()}/lists/holoen.txt', holo_en)
    # holoID
    __create_dict(f'{util.get_project_dir()}/lists/holoid.txt', holo_id)
    # nijiEN
    __create_dict(f'{util.get_project_dir()}/lists/nijien.txt', niji_en)
    # nijiexID
    __create_dict(f'{util.get_project_dir()}/lists/nijiexid.txt', niji_exid)

    test_talents = holo_en

def get_twitter_rules():
    global talents
    rules = list()

    names = list(talents.values())
    curr_rule = f'from:{names[0]}'
    for name in list(talents.values())[1:]:
        test_rule = curr_rule +  f' OR from:{name}'
        if len(test_rule) > 512:
            rules.append(curr_rule)
            curr_rule = f'from:{name}'
        else:
            curr_rule = test_rule
    return rules