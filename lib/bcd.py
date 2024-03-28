#!/usr/bin/env python3

import requests


def download():
    return requests.get(
        "https://unpkg.com/@mdn/browser-compat-data@latest/data.json"
    ).json()


def get_features(data, prefix=""):
    for k, v in data.items():
        if not isinstance(v, dict):
            continue
        feature_id = f"{prefix}{k}"
        if "__compat" in v:
            yield (feature_id, v)
        yield from get_features(v, f"{feature_id}.")


def get_feature(data, feature_id):
    k, _, subfeature_id = feature_id.partition('.')
    return get_feature(data[k], subfeature_id) if subfeature_id else data[k]['__compat']
