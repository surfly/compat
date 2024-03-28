#!/usr/bin/env python3
"""
Determine which MDN pages should be altered to include data on Surfly support.

## Data format

- keys are page paths
    - page paths can be absent, meaning that all rows in all tables have unknown support in Surfly
- values are lists of tables
- a table is either:
    - a Support value as an integer, meaning that all rows in this table have this much support in Surfly
    - a list of rows
- a row is a Support value as an integer, meaning that this row's feature has this much support in Surfly

## How to modify tables

Surfly support                                       | how to modify table
--------------                                       | -------------------
Unknown                                              | {yes, partial, no} → unknown
Yes (tested, no known issues)                        | no changes
Partial implementation (tested, has bugs or caveats) | yes → partial + note
Expected to work (not tested)                        | yes → partial + note "not tested"
No, not yet implemented                              | {yes, partial, unknown} → no
No, cannot implement due to a technical limitation   | {yes, partial, unknown} → no + note
"""

import json
import pathlib

import frontmatter

from lib import bcd
from lib.support import Support

root_path = pathlib.Path(__file__).parent
surfly_path = root_path / "features"
output_path = root_path / "scd"

browser_names = {
    'chrome',
    'chrome_android',
    'edge',
    'firefox',
    'firefox_android',
    'safari',
    'safari_ios',
}


def overlay(bcd_data):
    for path in surfly_path.glob("**/*.html"):
        fm = frontmatter.load(path)
        feature_id = fm["id"]
        support = Support[fm["support"].upper()]
        notes = str(fm).strip()

        browser_supports = bcd.get_feature(bcd_data, feature_id)['support']
        for browser_id, support_entries in browser_supports.items():
            if not browser_id.startswith('surfly_'):
                continue
            if not isinstance(support_entries, list):
                support_entries = [support_entries]
            for support_entry in support_entries:
                if notes:
                    add_note(support_entry, notes)
                overlay_one(support_entry, support)


def overlay_one(support_entry, support):

    if support in (Support.NEVER, Support.TODO):
        if not support_entry.get('version_removed'):
            support_entry['version_added'] = False

    elif support == Support.PARTIAL:
        if support_entry.get('version_added') and not support_entry.get('version_removed'):
            support_entry['partial_implementation'] = True

    elif support == Support.EXPECTED:
        add_note(support_entry, 'Expected to work, but not tested under Surfly.')

    elif support == Support.UNKNOWN:
        if not support_entry.get('version_removed'):
            support_entry['version_added'] = None


def add_note(support_entry, new_note):
    try:
        notes = support_entry['notes']
    except KeyError:
        support_entry['notes'] = new_note
        return

    if isinstance(notes, str):
        support_entry['notes'] = [notes, new_note]
        return

    notes.insert(0, new_note)


def supported_browsers(upstream_browsers):
    for browser_id in browser_names:
        upstream_browser = upstream_browsers[browser_id]
        yield (browser_id, upstream_browser)

        surfly_browser = upstream_browser.copy()
        surfly_browser['name'] = f'Surfly on {upstream_browser["name"]}'
        yield (f'surfly_{browser_id}', surfly_browser)


def export(feature_data, browsers, feature_id=None):
    for k, subfeature_data in feature_data.items():
        if k == '__compat':
            out = dict(
                browsers=browsers,
                query=feature_id,
                data=subfeature_data,
            )
            with (output_path / f'{feature_id}.json').open('w') as f:
                json.dump(out, f, separators=",:")

        else:
            export(subfeature_data, browsers, feature_id=k if feature_id is None else f'{feature_id}.{k}')


output_path.mkdir(parents=True, exist_ok=True)
spec = bcd.download()
all_browsers = spec.pop('browsers')
browsers = dict(supported_browsers(spec.pop('browsers')))
overlay(spec)
export(spec, browsers, feature_id='')
