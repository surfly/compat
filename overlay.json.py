#!/usr/bin/env python3
"""Generate browser compatibility API data to be requested from MDN pages."""

import copy
import json
import pathlib
import sys

import frontmatter

from lib import bcd
from lib.support import Support

root_path = pathlib.Path(__file__).parent
surfly_path = root_path / "features"
default_output_path = root_path / "scd"

supported_browser_ids = [
    "chrome",
    "chrome_android",
    "firefox",
    "firefox_android",
    "safari",
    "safari_ios",
]


def overlay(bcd_data, supported_browser_ids):
    for path in surfly_path.glob("**/*.html"):
        fm = frontmatter.load(path)
        feature_id = fm["id"]
        surfly_version_added = fm.get("version_added")
        support = Support[fm["support"].upper()]
        limitations = fm.get("limitations", "")
        icf_support_raw = fm.get("icf_support", "")
        icf_limitations = fm.get("icf_limitations", "")
        extra_note = str(fm)

        # handle empty support
        icf_support = Support[icf_support_raw.upper()] if icf_support_raw else support

        feature = bcd.get_feature(bcd_data, feature_id)
        native_browser_supports = feature["support"]
        feature["support"] = {}

        for browser_id in supported_browser_ids:
            try:
                native_support_entries = native_browser_supports[browser_id]
            except KeyError:
                continue

            # carry over original support data from native browser
            feature["support"][browser_id] = native_support_entries

            # we only care about the latest support entry
            latest_native_support_entry = get_latest_support_entry(
                native_support_entries
            )

            # create "Surfly browser" column: start with a copy of the native browser support data
            surfly_support_entry = create_surfly_support_entry(
                latest_native_support_entry,
                surfly_version_added,
                support,
                limitations,
                icf_support,
                icf_limitations,
                extra_note,
            )
            feature["support"][f"surfly_{browser_id}"] = surfly_support_entry


def capitalize(s):
    """capitalize first word without lowercasing subsequent words"""
    words = s.split(" ", maxsplit=1)
    words[0] = words[0].title()
    return " ".join(words)


def get_latest_support_entry(support_entries):
    return (
        support_entries[0]
        if isinstance(support_entries, list) and support_entries
        else support_entries
    )


def is_supported(support_entry):
    return support_entry.get("version_added") and not support_entry.get(
        "version_removed"
    )


def create_surfly_support_entry(
    latest_native_support_entry,
    surfly_version_added,
    support,
    limitations,
    icf_support,
    icf_limitations,
    extra_note,
):
    if not is_supported(latest_native_support_entry):
        return dict(version_added=False)

    if support == Support.UNKNOWN:
        surfly_support_entry = dict(version_added=None)

    elif support in (Support.TODO, Support.NEVER):
        surfly_support_entry = dict(version_added=False)

    else:
        surfly_support_entry = copy.deepcopy(latest_native_support_entry)

        if (
            limitations.strip()
            or icf_limitations.strip()
            or icf_support not in (Support.SUPPORTED, Support.EXPECTED)
        ):
            surfly_support_entry["partial_implementation"] = True

        surfly_support_entry["version_added"] = surfly_version_added or True

    for n in create_support_notes(
        support, limitations, icf_support, icf_limitations, extra_note
    ):
        add_note(surfly_support_entry, n)

    return surfly_support_entry


def create_support_notes(
    support, limitations, icf_support, icf_limitations, extra_note
):
    if extra_note.strip():
        yield extra_note

    icf_notes = []
    if support != icf_support:
        if icf_support == Support.UNKNOWN:
            icf_notes.append("unknown support.")
        elif icf_support == Support.SUPPORTED:
            icf_notes.append("supported.")
        elif icf_support == Support.EXPECTED:
            icf_notes.append("expected to work.")
        elif icf_support == Support.TODO:
            icf_notes.append("not yet supported.")
        elif icf_support == Support.NEVER:
            icf_notes.append("cannot support due to a browser limitation.")
    if icf_limitations.strip():
        icf_notes.append(icf_limitations)
    if icf_notes:
        icf_notes.insert(0, "<strong>Controlling another user's tab:</strong>")
        yield " ".join(icf_notes)

    notes = []
    if support == Support.NEVER:
        notes.append("cannot support due to a browser limitation.")
    elif support == Support.EXPECTED:
        notes.append("expected to work.")
    elif support == Support.UNKNOWN:
        notes.append("unknown Surfly support.")
    elif icf_notes and support == Support.SUPPORTED:
        notes.append("full Surfly support.")
    if limitations.strip():
        notes.append(limitations)
    if notes:
        if icf_notes:
            notes.insert(0, "<strong>Tab owner in control:</strong>")
            yield " ".join(notes)
        else:
            yield capitalize(" ".join(notes))


def add_note(support_entry, new_note):
    try:
        notes = support_entry["notes"]
    except KeyError:
        support_entry["notes"] = new_note
        return

    if isinstance(notes, str):
        support_entry["notes"] = [new_note, notes]
        return

    notes.insert(0, new_note)


def overlay_browsers(upstream_browsers, supported_browser_ids):
    for browser_id in supported_browser_ids:
        upstream_browser = upstream_browsers[browser_id]
        if browser_id == "chrome":
            upstream_browser["name"] = "Chrome/Edge"
        yield (browser_id, upstream_browser)

        surfly_browser = upstream_browser.copy()
        surfly_browser["name"] = f'Surfly on {upstream_browser["name"]}'
        yield (f"surfly_{browser_id}", surfly_browser)


def export(output_path, feature_data, browsers, feature_id=None):
    for k, subfeature_data in feature_data.items():
        if k == "__compat":
            out = dict(
                browsers=browsers,
                query=feature_id,
                data=feature_data,
            )
            feature_path = output_path / f"{feature_id}.json"
            print(feature_path.name, file=sys.stderr)
            with (output_path / f"{feature_id}.json").open("w") as f:
                json.dump(out, f, separators=",:")

        elif isinstance(subfeature_data, dict):
            export(
                output_path,
                subfeature_data,
                browsers,
                feature_id=k if feature_id is None else f"{feature_id}.{k}",
            )


try:
    output_path = pathlib.Path(sys.argv[1])
except IndexError:
    output_path = default_output_path
output_path.mkdir(parents=True, exist_ok=True)

spec = bcd.download()
all_browsers = spec.pop("browsers")
browsers = dict(overlay_browsers(all_browsers, supported_browser_ids))
overlay(spec, supported_browser_ids)
export(output_path, spec, browsers)
