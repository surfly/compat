#!/usr/bin/env python3

import pathlib
import sys

import requests
import yaml

script_path = pathlib.Path(__file__).resolve().parent
features_path = script_path / 'features'


def create_top_dir(root, name):
    name_parts = name.split('.')

    data = root
    for k in name_parts:
        data = data[k]

    create_dir(name, data)


def create_dir(name, data):
    '''search for a feature'''

    if '__compat' in data:
        name_path = name.replace('.', '/')
        dir_path = features_path / name_path
        dir_path.mkdir(parents=True, exist_ok=True)
        create_features(dir_path, name, data)
    else:
        for k, v in data.items():
            create_dir(f'{name}.{k}', v)


def create_features(dir_path, name, data):
    '''create empty (sub-)features'''

    if '__compat' in data:
        path = dir_path / f'{name}.html'
        if not path.exists():
            with path.open('w') as f:
                print('---', file=f)
                yaml.dump(dict(id=name, support='unknown'), f)
                print('---', file=f)
                print(path.relative_to(features_path.parent), file=sys.stderr)

    for k, v in data.items():
        if k != '__compat':
            create_features(dir_path, f'{name}.{k}', v)


root = requests.get('https://unpkg.com/@mdn/browser-compat-data@5.5.16/data.json').json()
create_top_dir(root, 'api')
create_top_dir(root, 'html.elements')
create_top_dir(root, 'html.global_attributes')
create_top_dir(root, 'http.data-url')
create_top_dir(root, 'http.headers')
create_top_dir(root, 'javascript')
