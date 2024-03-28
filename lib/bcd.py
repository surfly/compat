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
