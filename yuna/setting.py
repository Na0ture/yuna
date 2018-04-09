import os, json
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


def setup(**kwargs):
    for name, value in kwargs.items():
        name = name.upper()
        if name in config:
            config[name] = value
        else:
            raise SetiingError("没有该设定")

    with open(config_file, 'w') as json_config_file:
        json.dump(config, json_config_file, indent=2)

