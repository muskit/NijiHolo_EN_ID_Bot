import util

holo_en = dict[int, str]
holo_id = dict[int, str]
niji_en = dict[int, str]
niji_exid = dict[int, str]
talents = dict[int, str]
talents_company = dict[int, str]

test_talents = dict()

# TODO: talents(id) -> (name, company)
def __create_dict(file, _dict, company):
    print(f'Initializing talents\' account list from {file}...')
    global talents
    with open(file, 'r') as f:
        for line in f:
            words = line.split()
            if len(words) == 2 and line[0] != '#':
                id, name = line.split()
                # name = f'{util.get_username_online(id, default=name)}' # attempt to get updated name
                talents[int(id)] = name
                _dict[int(id)] = name
                talents_company[int(id)] = company
def init():
    global holo_en
    global holo_id
    global niji_en
    global niji_exid
    global test_talents

    # holoEN
    __create_dict(f'{util.get_project_dir()}/lists/holoen.txt', holo_en, 'holoEN')
    # holoID
    __create_dict(f'{util.get_project_dir()}/lists/holoid.txt', holo_id, 'holoID')
    # nijiEN
    __create_dict(f'{util.get_project_dir()}/lists/nijien.txt', niji_en, 'nijiEN')
    # nijiexID
    __create_dict(f'{util.get_project_dir()}/lists/nijiexid.txt', niji_exid, 'nijiex-ID')
    # TODO: nijiex-KR

    test_talents = holo_en

def is_niji(id: int) -> bool:
    return id in niji_en or id in niji_exid

def is_holo(id: int) -> bool:
    return id in holo_en or id in holo_id

# For filtered stream
# DEPRECATED: thx elon
def get_twitter_rules():
    global talents
    rules = list()

    names = list(talents.values())
    curr_rule = f'from:{names}'
    for name in list(talents.values())[1:]:
        test_rule = curr_rule +  f' OR from:{name}'
        if len(test_rule) > 512:
            rules.append(curr_rule)
            curr_rule = f'from:{name}'
        else:
            curr_rule = test_rule
    rules.append(curr_rule)
    return rules
