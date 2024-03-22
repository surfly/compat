#!/usr/bin/env python3
"""Determine which MDN pages should be altered to include data on Surfly support."""

import json
import pathlib
import sys

import frontmatter

from .featuretree import FeatureTree
from .support import Support

root_path = pathlib.Path(__file__).parent.parent
mdn_path = root_path / "mdn/files/en-us/web"
surfly_path = root_path / "features"


def parse_mdn():
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


def parse_support():
    support_tree = FeatureTree()
    for path in surfly_path.glob("**/*.html"):
        fm = frontmatter.load(path)
        support_tree[fm["id"]] = Support[fm["support"].upper()]
    return support_tree


def gen_overlay(*, mdn, support_tree):
    for path, features in mdn:
        support_tables = []
        for feature in features:
            try:
                support_table = list(support_tree[feature])

            # error in mozilla site source; skip this table
            except KeyError:
                continue

            # sparse: if all rows are unknown, just say the whole table is unknown
            if all(support_row == Support.UNKNOWN for support_row in support_table):
                support_table = Support.UNKNOWN

            support_tables.append(support_table)

        # make sparse: if we don't support anything on this page, skip the page
        if all(support_table == Support.UNKNOWN for support_table in support_tables):
            continue

        yield (path, support_tables)


# FIXME: generate support tree from browser-compat-data directly (depth-first, preserving order), then add surfly data
mdn = parse_mdn()
support_tree = parse_support()
overlay = dict(gen_overlay(mdn=mdn, support_tree=support_tree))
json.dump(overlay, sys.stdout, separators=",:")
