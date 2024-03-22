#!/usr/bin/env python3
"""Determine which MDN pages should be altered to include data on Surfly support."""

import json
import pathlib
import sys

import frontmatter

from lib import bcd
from lib.featuretree import FeatureTree
from lib.support import Support

root_path = pathlib.Path(__file__).parent
mdn_path = root_path / "mdn/files/en-us/web"
surfly_path = root_path / "features"


def get_mdn_page_feature_ids():
    for path in mdn_path.glob("**/index.md"):
        fm = frontmatter.load(path)

        try:
            features = fm["browser-compat"]

        # skip pages without a compatibility table
        except KeyError:
            continue

        if not isinstance(features, list):
            features = [features]

        path = fm["slug"]
        yield (path, features)


def parse_support(feature_tree):
    for path in surfly_path.glob("**/*.html"):
        fm = frontmatter.load(path)
        feature_tree[fm["id"]] = Support[fm["support"].upper()]


def unpad_right(xs):
    while xs:
        if xs[-1]:
            return
        xs.pop()


def gen_overlay(*, page_feature_ids, feature_tree):
    for path, features in page_feature_ids:
        support_tables = []
        for feature in features:
            try:
                subfeature_tree = feature_tree.get_node(feature_id)
                support_table = [support for _, support in subfeature_tree.descendent_items()]

            # error in mozilla site source; skip this table
            except KeyError:
                continue

            # sparse: remove unknown rows from the right
            unpad_right(support_table)

            # sparse: if all rows are unknown, just say the whole table is unknown
            if not support_table:
                support_table = Support.UNKNOWN

            support_tables.append(support_table)

        # make sparse: if we don't support anything on this page, skip the page
        unpad_right(support_tables)
        if not support_tables:
            continue

        yield (path, support_tables)


# set up a FeatureTree for the BCD data to preserve its original ordering
bcd_data = bcd.download()
feature_tree = FeatureTree()
for feature_id in bcd.get_feature_ids(bcd_data):
    feature_tree[feature_id] = Support.UNKNOWN

parse_support(feature_tree)

page_feature_ids = get_mdn_page_feature_ids()
overlay = dict(gen_overlay(page_feature_ids=page_feature_ids, feature_tree=feature_tree))
json.dump(overlay, sys.stdout, separators=",:")
