import os, json, sys, glob, pickle
from yuna.exceptions import SetiingError


_yuna_base_dir = os.path.expanduser('~')
if not os.access(_yuna_base_dir, os.W_OK):
    _yuna_base_dir = '/temp'
_yuna_dir = os.path.join(_yuna_base_dir, 'yuna')
if not os.path.exists(_yuna_dir):
    try:
        os.makedirs(_yuna_dir)
    except OSError:
        raise SetiingError("无法创建文件目录")
config_file = os.path.join(_yuna_dir, "config.json")

if os.path.isfile(config_file):
    with open(config_file) as json_config_file:
        config = json.load(json_config_file)
    HOST = config['HOST']
    PORT = config['PORT']
    USER = config['USER']
    PASS_WD = config['PASS_WD']
    DB = config['DB']
    APP_CODE = config['APP_CODE']
    SOURCE = config['SOURCE']
    DESTINATION = config['DESTINATION']
else:
    config = {}
    config['HOST'] = HOST = ''
    config['PORT'] = PORT = 0
    config['USER'] = USER = ''
    config['PASS_WD'] = PASS_WD = ''
    config['DB'] = DB = ''
    config['APP_CODE'] = APP_CODE = ''
    config['SOURCE'] = SOURCE = ''
    config['DESTINATION'] = DESTINATION = ''

with open(config_file, 'w') as json_config_file:
    json.dump(config, json_config_file, indent=2)

_temp = os.getcwd()
os.chdir(os.path.join(os.path.expanduser('~'), 'yuna'))
os.makedirs('indicators', exist_ok=True)
os.makedirs('visual', exist_ok=True)
os.chdir(os.path.join(os.path.expanduser('~'), 'yuna/indicators'))

if glob.glob("[a-z]*.py"):
    with open('__init__.py', 'w') as i:
        i.write("from . import " + ','.join([f"{i.split('.')[0]}" for i in glob.glob("[a-z]*.py")]) + "\n"
                "\n"
                "_all_indicators = {\n" +
                ''.join([f"    '{i.split('.')[0]}': {i.split('.')[0]}.{i.split('.')[0].title()},\n"
                         for i in glob.glob("[a-z]*.py")]) +
                "}\n")
else:
    with open('__init__.py', 'w') as i:
        i.write("_all_indicators = {}\n")

os.chdir(os.path.join(os.path.expanduser('~'), 'yuna/visual'))

if glob.glob("[a-z]*.py"):
    with open('__init__.py', 'w') as i:
        i.write("from . import " + ','.join([f"{i.split('.')[0]}" for i in glob.glob("[a-z]*.py")]) + "\n"
                "\n"
                "_visual_indicators = {\n" +
                ''.join([f"    '{i.split('.')[0]}': {i.split('.')[0]}.{i.split('.')[0].title()},\n"
                         for i in glob.glob("[a-z]*.py")]) +
                "}\n")
else:
    with open('__init__.py', 'w') as i:
        i.write("_visual_indicators = {}\n")

sys.path.append(os.path.join(os.path.expanduser('~'), 'yuna'))
os.chdir(_temp)


def setup(**kwargs):
    for name, value in kwargs.items():
        name = name.upper()
        if name in config:
            config[name] = value
        else:
            raise SetiingError("没有该设定")

    with open(config_file, 'w') as json_config_file:
        json.dump(config, json_config_file, indent=2)


def set_stocks_list(all_stocks_list):
    with open(os.path.join(_yuna_dir + '/all_stock_lists.pkl'), 'wb') as i:
        pickle.dump(all_stocks_list, i)


def get_stocks_list():
    with open(os.path.join(_yuna_dir + '/all_stock_lists.pkl'), 'rb') as i:
        return pickle.load(i)
