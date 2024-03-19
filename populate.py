import requests
import yaml

import pathlib

script_path = pathlib.Path(__file__).resolve().parent
features_path = script_path / 'features'


def create_features(name, data):
    if '__compat' in data:
        path = (features_path / data['__compat']['source_file']).with_suffix('.yaml')
        if not path.exists():
            path.parent.mkdir(parents=True, exist_ok=True)
            with path.open('w') as f:
                yaml.dump(dict(id=name, support='unknown'), f)

    for k, v in data.items():
        if k != '__compat':
            create_features(f'{name}.{k}', v)

root = requests.get('https://unpkg.com/@mdn/browser-compat-data@5.5.16/data.json').json()
create_features('api', root['api'])
create_features('html.elements', root['html']['elements'])
create_features('html.global_attributes', root['html']['global_attributes'])
create_features('http.data-url', root['http']['data-url'])
create_features('http.headers', root['http']['headers'])
create_features('javascript', root['javascript'])
