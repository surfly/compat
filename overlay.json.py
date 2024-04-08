#!/usr/bin/env python3
"""
Determine which MDN pages should be altered to include data on Surfly support.

## How to modify tables

Surfly support                                       | limited  | how to modify table
--------------                                       | -------  | -------------------
Unknown                                              | (ignore) | {yes, partial, no} → unknown
Supported                                            | `false`  | no changes
Supported                                            | `true`   | yes → partial + note
Expected                                             | `false`  | yes → partial + note "not tested"
Expected                                             | `true`   | yes → partial + note "not tested"
No, not yet implemented                              | (ignore) | {yes, partial, unknown} → no
No, cannot implement due to a technical limitation   | (ignore) | {yes, partial, unknown} → no + note
"""

import json
import pathlib
import sys
import copy

import frontmatter

from lib import bcd
from lib.support import Support

root_path = pathlib.Path(__file__).parent
surfly_path = root_path / "features"
default_output_path = root_path / "scd"

supported_browser_ids = [
    'chrome',
    'chrome_android',
    'edge',
    'firefox',
    'firefox_android',
    'safari',
    'safari_ios',
]


def overlay(bcd_data, supported_browser_ids):
    for path in surfly_path.glob("**/*.html"):
        fm = frontmatter.load(path)
        feature_id = fm["id"]
        support = Support[fm["support"].upper()]
        icf_support_raw = fm.get("in_control_follower_support", "")
        limitations = fm.get("limitations", "")
        icf_limitations = fm.get("icf_limitations", "")
        note = str(fm)

        # handle empty support
        icf_support = Support[icf_support_raw.upper()] if icf_support_raw else support

        has_limitations = bool(limitations.strip())
        has_icf_limitations = bool(icf_limitations.strip())
        has_note = bool(note.strip())

        feature = bcd.get_feature(bcd_data, feature_id)
        native_browser_supports = feature['support']
        feature['support'] = {}

        for browser_id in supported_browser_ids:

            if browser_id not in native_browser_supports:
                continue

            # carry over original support data from native browser
            feature['support'][browser_id] = native_browser_supports[browser_id]

            # create "Surfly browser" column: start with a copy of the native browser support data
            surfly_support_entries = create_surfly_support_entries(
                support,
                has_limitations,
                icf_support,
                has_icf_limitations,
                native_browser_supports[browser_id],
            )
            feature['support'][f'surfly_{browser_id}'] = surfly_support_entries

            # always work with a list (simpler)
            if isinstance(surfly_support_entries, dict):
                surfly_support_entries = [surfly_support_entries]
            if not surfly_support_entries:
                continue

            if has_note:
                add_note(surfly_support_entries[0], note)

            icf_notes = []
            if support != icf_support:
                if icf_support == Support.UNKNOWN:
                    icf_notes.append('unknown support.')
                elif icf_support == Support.SUPPORTED:
                    icf_notes.append('supported.')
                elif icf_support == Support.EXPECTED:
                    icf_notes.append('expected to work.')
                elif icf_support == Support.TODO:
                    icf_notes.append('not yet supported.')
                elif icf_support == Support.NEVER:
                    icf_notes.append('cannot support.')
            if has_icf_limitations:
                icf_notes.append(icf_limitations)
            if icf_notes:
                icf_notes.insert(0, 'In-control followers:')
                add_note(surfly_support_entries[0], ' '.join(icf_notes))

            if has_limitations:
                add_note(surfly_support_entries[0], limitations)

            # prepend notes to the last entry
            if support == Support.EXPECTED:
                add_note(surfly_support_entries[0], 'Expected to work')
            elif support == Support.UNKNOWN:
                add_note(surfly_support_entries[0], 'Unknown Surfly support')
            elif support == Support.NEVER:
                add_note(surfly_support_entries[0], 'Surfly will not implement this feature due to technical limitations')


def create_surfly_support_entries(support, has_limitations, icf_support, has_icf_limitations, native_support_entries):
    if support == Support.UNKNOWN:
        return dict(version_added=None)

    if support in (Support.TODO, Support.NEVER):
        return dict(version_added=False)

    surfly_support_entries = copy.deepcopy(native_support_entries)

    if has_limitations or has_icf_limitations or icf_support not in (Support.SUPPORTED, Support.EXPECTED):
        xs = surfly_support_entries if isinstance(surfly_support_entries, list) else [surfly_support_entries]
        for support_entry in xs:
            if support_entry.get('version_added') and not support_entry.get('version_removed'):
                support_entry['partial_implementation'] = True

    return surfly_support_entries


def add_note(support_entry, new_note):
    try:
        notes = support_entry['notes']
    except KeyError:
        support_entry['notes'] = new_note
        return

    if isinstance(notes, str):
        support_entry['notes'] = [new_note, notes]
        return

    notes.insert(0, new_note)


def overlay_browsers(upstream_browsers, supported_browser_ids):
    for browser_id in supported_browser_ids:
        upstream_browser = upstream_browsers[browser_id]
        yield (browser_id, upstream_browser)

        surfly_browser = upstream_browser.copy()
        surfly_browser['name'] = f'Surfly on {upstream_browser["name"]}'
        yield (f'surfly_{browser_id}', surfly_browser)


def export(output_path, feature_data, browsers, feature_id=None):
    for k, subfeature_data in feature_data.items():
        if k == '__compat':
            out = dict(
                browsers=browsers,
                query=feature_id,
                data=feature_data,
            )
            feature_path = output_path / f'{feature_id}.json'
            print(feature_path.name, file=sys.stderr)
            with (output_path / f'{feature_id}.json').open('w') as f:
                json.dump(out, f, separators=",:")

        elif isinstance(subfeature_data, dict):
            export(output_path, subfeature_data, browsers, feature_id=k if feature_id is None else f'{feature_id}.{k}')


try:
    output_path = pathlib.Path(sys.argv[1])
except IndexError:
    output_path = default_output_path
output_path.mkdir(parents=True, exist_ok=True)

spec = bcd.download()
all_browsers = spec.pop('browsers')
browsers = dict(overlay_browsers(all_browsers, supported_browser_ids))
overlay(spec, supported_browser_ids)
export(output_path, spec, browsers)
