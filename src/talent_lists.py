import util

holo_en = dict()
holo_id = dict()
niji_en = dict()
niji_exid = dict()
talents = dict()

def __create_dict(file, _dict):
    print(f'Initializing talents\' account list from {file}...')
    global talents
    with open(file, 'r') as f:
        for line in f:
            words = line.split()
            if len(words) == 2 and line[0] != '#':
                name, id = line.split()
                talents[int(id)] = name
                name = util.get_username_online(id) # attempt to get updated name
                talents[int(id)] = name
                _dict[int(id)] = name
def init():
    global holo_en
    global holo_id
    global niji_en
    global niji_exid

    # holoEN
    __create_dict(f'{util.get_project_dir()}/lists/holoen.txt', holo_en)
    # holoID
    __create_dict(f'{util.get_project_dir()}/lists/holoid.txt', holo_id)
    # nijiEN
    __create_dict(f'{util.get_project_dir()}/lists/nijien.txt', niji_en)
    # nijiexID
    __create_dict(f'{util.get_project_dir()}/lists/nijiexid.txt', niji_exid)

