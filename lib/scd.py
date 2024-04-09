#!/usr/bin/env python3

import pathlib

import frontmatter

root_path = pathlib.Path(__file__).parent.parent
surfly_path = root_path / "features"


def get_features():
    for path in surfly_path.glob("**/*.html"):
        fm = frontmatter.load(path)
        yield (fm["id"], path)
