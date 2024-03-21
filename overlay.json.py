#!/usr/bin/env python3
'''
Determine which MDN pages should be altered to include data on Surfly support.
'''

# external
import frontmatter

# stdlib
import json
import pathlib
import sys

cwd = pathlib.Path(__file__).parent
mdn_path = cwd / 'content/files/en-us/web'
surfly_path = cwd / 'surfly.json'


def parse_mdn():
    for path in mdn_path.glob("**/index.md"):
        fm = frontmatter.load(path)

        try:
            features = fm['browser-compat']

        # skip pages without a compatibility table
        except KeyError:
            continue

        if type(features) != list:
            features = [features]

        path = fm['slug']
        yield (path, features)


def only_important(mdn):
    with surfly_path.open('r') as f:
        surfly = json.load(f)
        surfly_features = set(surfly.keys())

    for path, features in mdn:

        # if we have no data on this feature, skip
        if set(features).isdisjoint(surfly_features):
            continue

        yield path, [surfly.get(feature) for feature in features]


overlay = only_important(parse_mdn())
json.dump(dict(overlay), sys.stdout, separators=',:')
