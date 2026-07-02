import os
import json
import sys
import glob
import shutil

from yuna.exceptions import SettingError


_CONFIG_DIR = os.path.join(os.path.expanduser('~'), '.yuna')
_CONFIG_FILE = os.path.join(_CONFIG_DIR, 'config.json')

_DEFAULT_CONFIG = {
    'HOST': '',
    'PORT': 0,
    'USER': '',
    'PASS_WD': '',
    'DB': '',
    'APP_CODE': '',
    'TUSHARE_TOKEN': '',
    'SOURCE': '',
    'DESTINATION': '',
}


def _ensure_config_dir():
    if not os.path.exists(_CONFIG_DIR):
        try:
            os.makedirs(_CONFIG_DIR)
        except OSError:
            raise SettingError('无法创建配置目录')


def _load_config():
    _ensure_config_dir()
    config = {}
    config.update(_DEFAULT_CONFIG)
    if os.path.isfile(_CONFIG_FILE):
        with open(_CONFIG_FILE) as f:
            stored = json.load(f)
            config.update(stored)
    with open(_CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=2)
    return config


config = _load_config()
HOST = config['HOST']
PORT = config['PORT']
USER = config['USER']
PASS_WD = config['PASS_WD']
DB = config['DB']
APP_CODE = config['APP_CODE']
TUSHARE_TOKEN = config['TUSHARE_TOKEN']
SOURCE = config['SOURCE']
DESTINATION = config['DESTINATION']

_init_workspace_called = False


def _seed_samples(workspace):
    """如果用户 indicators/visual 目录为空，从内置 sample 目录复制默认算法"""
    pkg_dir = os.path.dirname(os.path.abspath(__file__))
    sample_dir = os.path.join(pkg_dir, '..', 'sample')
    for subdir in ('indicators', 'visual'):
        user_dir = os.path.join(workspace, subdir)
        if not glob.glob(os.path.join(user_dir, '[a-z]*.py')):
            src = os.path.join(sample_dir, subdir)
            if os.path.isdir(src):
                for f in os.listdir(src):
                    if f.endswith('.py') and not f.startswith('_'):
                        shutil.copy2(os.path.join(src, f), os.path.join(user_dir, f))


def _init_workspace():
    global _init_workspace_called
    if _init_workspace_called:
        return
    _init_workspace_called = True

    workspace = os.path.join(os.path.expanduser('~'), 'yuna')
    os.makedirs(os.path.join(workspace, 'indicators'), exist_ok=True)
    os.makedirs(os.path.join(workspace, 'visual'), exist_ok=True)

    if workspace not in sys.path:
        sys.path.insert(0, workspace)

    # 如果用户目录为空，从内置 sample 复制默认文件
    _seed_samples(workspace)

    for subdir in ('indicators', 'visual'):
        target = os.path.join(workspace, subdir)
        py_files = sorted(glob.glob(os.path.join(target, '[a-z]*.py')))
        init_path = os.path.join(target, '__init__.py')
        mod_names = [os.path.splitext(os.path.basename(f))[0] for f in py_files]

        if subdir == 'indicators':
            if mod_names:
                content = (
                    'from . import ' + ','.join(mod_names) + '\n'
                    '\n'
                    '_all_indicators = {\n'
                    + ''.join(f"    '{m}': {m}.{m.title()},\n" for m in mod_names)
                    + '}\n'
                )
            else:
                content = '_all_indicators = {}\n'
        else:
            if mod_names:
                content = (
                    'from . import ' + ','.join(mod_names) + '\n'
                    '\n'
                    '_visual_indicators = {\n'
                    + ''.join(f"    '{m}': {m}.{m.title()},\n" for m in mod_names)
                    + '}\n'
                )
            else:
                content = '_visual_indicators = {}\n'

        with open(init_path, 'w') as f:
            f.write(content)


def setup(**kwargs):
    _init_workspace()
    for name, value in kwargs.items():
        key = name.upper()
        if key in config:
            config[key] = value
        else:
            raise SettingError(f'没有该设定: {key}')

    with open(_CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=2)

    globals().update(config)


_init_workspace()

