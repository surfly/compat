#!/usr/bin/env python3

import pathlib
import sys

import yaml

from lib import bcd
from lib import scd
from lib.featuretree import FeatureTree
from lib.support import Support

root_path = pathlib.Path(__file__).resolve().parent
features_path = root_path / "features"

did_something = False


def create_top_dir(feature_tree, name):
    subfeature_tree = feature_tree.get_node(name)
    for raw_path in subfeature_tree.dir(f"{name}."):
        create_feature_file(raw_path)


def create_feature_file(raw_path):
    global did_something
    _, _, feature_id = raw_path.rpartition("/")

    path = features_path / f"{raw_path}.html"
    if path.exists():
        return

    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w") as f:
        print("---", file=f)
        yaml.dump(dict(id=feature_id, support=Support.UNKNOWN.name.lower()), f)
        print("---", file=f)
        print(f"create {path.relative_to(features_path.parent)}", file=sys.stderr)
        did_something = True


def remove_outdated_feature_files(bcd_features_by_id, scd_paths_by_id):
    global did_something
    bcd_feature_ids = set(bcd_features_by_id.keys())
    scd_feature_ids = set(scd_paths_by_id.keys())
    removed_feature_ids = scd_feature_ids - bcd_feature_ids
    for fid in removed_feature_ids:
        path = scd_paths_by_id[fid]
        path.unlink()
        print(f"delete {path.relative_to(features_path.parent)}", file=sys.stderr)
        did_something = True


bcd_root = bcd.download()
bcd_features_by_id = dict(bcd.get_features(bcd_root))

remove_outdated_feature_files(bcd_features_by_id, dict(scd.get_features()))

feature_tree = FeatureTree()
for feature_id in bcd_features_by_id:
    feature_tree[feature_id] = Support.UNKNOWN

create_top_dir(feature_tree, "api")
create_top_dir(feature_tree, "html.elements")
create_top_dir(feature_tree, "html.global_attributes")
create_top_dir(feature_tree, "http.data-url")
create_top_dir(feature_tree, "http.headers")
create_top_dir(feature_tree, "javascript")

if not did_something:
    print("data was already up-to-date", file=sys.stderr)
