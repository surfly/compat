#!/usr/bin/env python3
'''
Determine which MDN pages should be altered to include data on Surfly support.
'''

import enum
import json
import pathlib
import sys

import frontmatter

cwd = pathlib.Path(__file__).parent
mdn_path = cwd / 'content/files/en-us/web'
surfly_path = cwd / 'pages-cms-test/features'


class Support(enum.IntEnum):
    UNKNOWN = 0
    TESTED = 1
    EXPECTED = 2
    PARTIAL = 3
    TODO = 4
    NEVER = 5


class Tree:
    def __init__(self, v=None):
        self.children = dict()
        self.value = v

    def __setitem__(self, path, v):
        k, _, path = path.partition('.')
        if not path:
            self.children[k] = Tree(v)
            return

        if k not in self.children:
            self.children[k] = Tree()
        self.children[k][path] = v

    def __getitem__(self, path):
        k, _, path = path.partition('.')
        if not path:
            return self.children[k]

        return self.children[k][path]

    def __iter__(self):
        if self.value is not None:
            yield self.value
        for child in self.children.values():
            yield from child


def parse_mdn():
    for path in mdn_path.glob("**/index.md"):
        fm = frontmatter.load(path)

        try:
            features = fm['browser-compat']

        # skip pages without a compatibility table
        except KeyError:
            continue

        if not isinstance(features, list):
            features = [features]

        path = fm['slug']
        yield (path, features)


def parse_support():
    support_tree = Tree()
    for path in surfly_path.glob("**/*.html"):
        fm = frontmatter.load(path)
        support_tree[fm['id']] = Support[fm['support'].upper()]
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
json.dump(overlay, sys.stdout, separators=',:')
