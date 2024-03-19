#!/usr/bin/env python3

import pathlib
import sys

import requests
import yaml

script_path = pathlib.Path(__file__).resolve().parent
features_path = script_path / 'features'

def create_features_dir(root, name):
    name_parts = name.split('.')

    data = root
    for k in name_parts:
        data = data[k]

    parent_path = features_path / '/'.join(name_parts)
    parent_path.mkdir(parents=True, exist_ok=True)

    create_features(parent_path, name, data)


def create_features(parent_path, name, data):
    if '__compat' in data:
        path = parent_path / f'{name}.html'
        if not path.exists():
            with path.open('w') as f:
                print('---', file=f)
                yaml.dump(dict(id=name, support='unknown'), f)
                print('---', file=f)
                print(path.relative_to(features_path.parent), file=sys.stderr)

    for k, v in data.items():
        if k != '__compat':
            create_features(parent_path, f'{name}.{k}', v)


root = requests.get('https://unpkg.com/@mdn/browser-compat-data@5.5.16/data.json').json()
create_features_dir(root, 'api')
create_features_dir(root, 'html.elements')
create_features_dir(root, 'html.global_attributes')
create_features_dir(root, 'http.data-url')
create_features_dir(root, 'http.headers')
create_features_dir(root, 'javascript')
