#!/usr/bin/env python3

import requests


def get():
    return requests.get(
        "https://unpkg.com/@mdn/browser-compat-data@latest/data.json"
    ).json()
