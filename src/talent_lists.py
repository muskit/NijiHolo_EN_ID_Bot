import util

niji_en = dict()
holo_en = dict()

def __create_dict(file, _dict):
    with open(file, 'r') as f:
        for line in f:
            words = line.split()
            if len(words) == 2 and line[0] != '#':
                name, id = line.split()
                _dict[int(id)] = name

def init():
    global niji_en
    global holo_en

    # holoEN
    __create_dict(f'{util.get_project_dir()}/lists/holoen.txt', holo_en)
    # nijiEN
    __create_dict(f'{util.get_project_dir()}/lists/nijien.txt', niji_en)
