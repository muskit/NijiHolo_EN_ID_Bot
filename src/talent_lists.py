import util

holo_en = dict()
holo_id = dict()
niji_en = dict()
niji_exid = dict()
talents = dict()

def __create_dict(file, _dict):
    global talents
    with open(file, 'r') as f:
        for line in f:
            words = line.split()
            if len(words) == 2 and line[0] != '#':
                name, id = line.split()
                _dict[int(id)] = name
                talents[int(id)] = name
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

