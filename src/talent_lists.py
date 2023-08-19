from util import get_project_dir

holo_en: dict[int, str] = dict()
holo_id: dict[int, str] = dict()
niji_en: dict[int, str] = dict()
niji_exid: dict[int, str] = dict()
talents: dict[int, str] = dict()
talents_company: dict[int, str] = dict()
privated_accounts: dict[int, str] = dict()

test_talents = dict()

# TODO: talents(id) -> (name, company)
def __create_dict(file, _dict, company):
    print(f'Initializing talents\' account list from {file}...')
    global talents
    with open(file, 'r') as f:
        for line in f:
            words = line.split()
            if len(words) >= 2 and line[0] != '#':
                t = line.split()
                id, name = int(t[0]), t[1]
                # name = f'{util.get_username_online(id, default=name)}' # attempt to get updated name
                talents[id] = name
                _dict[id] = name
                talents_company[id] = company
                if len(words) > 2 and words[2] == 'p':
                    privated_accounts[id] = name
def init():
    global holo_en
    global holo_id
    global niji_en
    global niji_exid
    global test_talents

    # holoEN
    __create_dict(f'{get_project_dir()}/lists/holoen.txt', holo_en, 'holoEN')
    # holoID
    __create_dict(f'{get_project_dir()}/lists/holoid.txt', holo_id, 'holoID')
    # nijiEN
    __create_dict(f'{get_project_dir()}/lists/nijien.txt', niji_en, 'nijiEN')
    # nijiexID
    __create_dict(f'{get_project_dir()}/lists/nijiexid.txt', niji_exid, 'nijiex\'ID')
    # TODO: nijiex-KR

    test_talents = holo_en

def is_niji(id: int) -> bool:
    return id in niji_en or id in niji_exid

def is_holo(id: int) -> bool:
    return id in holo_en or id in holo_id

def is_cross_company(id1: int, id2: int):
    return (is_niji(id1) and is_holo(id2)) or (is_holo(id1) and is_niji(id2))

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
