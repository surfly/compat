#!/usr/bin/env python3

import pathlib
import sys

import yaml

from lib import bcd
from lib.featuretree import FeatureTree
from lib.support import Support

root_path = pathlib.Path(__file__).resolve().parent
features_path = root_path / "features"


def create_top_dir(feature_tree, name):
    subfeature_tree = feature_tree.get_node(name)
    for raw_path in subfeature_tree.dir(name):
        create_feature_file(raw_path)


def create_feature_file(raw_path):
    _, _, feature_id = raw_path.rpartition("/")

    path = features_path / f"{raw_path}.html"
    if path.exists():
        return

    with path.open("w") as f:
        print("---", file=f)
        yaml.dump(dict(id=feature_id, support=Support.UNKNOWN.name.lower()), f)
        print("---", file=f)
        print(path.relative_to(features_path.parent), file=sys.stderr)


bcd_data = bcd.download()
feature_tree = FeatureTree()
for feature_id in bcd.get_feature_ids(bcd_data):
    feature_tree[feature_id] = Support.UNKNOWN

create_top_dir(feature_tree, "api")
create_top_dir(feature_tree, "html.elements")
create_top_dir(feature_tree, "html.global_attributes")
create_top_dir(feature_tree, "http.data-url")
create_top_dir(feature_tree, "http.headers")
create_top_dir(feature_tree, "javascript")
