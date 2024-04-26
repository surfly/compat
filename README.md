# surfly-compat-data

**surfly-compat-data** (_n_):

1. a project to discover how much of the Web (browser APIs, JS features, HTTP headers, etc.) will work under Surfly.
2. the data gathered from our investigations, stored under `features/`.
    - run `pipenv run ./populate.py` to create new features and remove old features as needed
3. a [nice interface](https://app.pagescms.org/surfly/compat) for devs to update Surfly compatibility data.
    - uses Pages CMS, which can be configured using `.pages.yml`
3. a [demo page](https://surfly.github.io/compat) which injects this data into browser compatibility tables on the MDN website.
    - the source of this demo page is stored under `docs/`[^1] and hosted by Github pages
    - run `pipenv run ./overlay.py` to create JSON files of browser compatibility data in the format used by MDN; generated data will be saved in the `data` branch of this repository

[^1]: The demo page source is stored in a directory named `docs` because this is the only non-root directory name that gh-pages can deploy from without creating a custom Github Actions workflow.

## Filling the data

### How to investigate a feature


- If there's a test for this feature, that's already enough evidence that it's supported. Mark the feature as "supported" and mention the path to the test source. You're done!
- If there's no test for this feature, write one in one of the Surfly suites:
  - if your test passes:
    - mark the feature as supported
    - create a PR to cobro with your new test
  - if your test fails:
    - mark the feature as TODO (or NEVER, or partial, etc.)
    - create an issue to add support for this feature
- If there's no way to test this currently, try testing manually in glitch.me or similar.
  - if the feature works under Surfly:
    - mark the feature as supported (or partial, etc.)
    - create an issue to add tests for this feature (and mention your manual testing strategy!)
  - if the feature doesn't work under Surfly:
    - mark the feature as TODO (or NEVER, or partial, etc.)
    - create an issue to add support and tests for this feature (and mention your manual testing strategy!)

### Grouping the changes

Each individual change from CMS results in a commit. Editing support for many features results in commit spam.

For multiple changes it's recommended to create a separate branch. It can be selected in the top left dropdown in the CMS.

Once the changes are ready - the PR based on the branch can be squashed and merged. All changes will be grouped in one commit.

<img src="https://github.com/surfly/compat/assets/11188888/c4a5c2ba-b94e-41b6-9b4f-cd521d533bed" width="400">
<img src="https://github.com/surfly/compat/assets/11188888/60296166-a441-4a44-8b02-9c7101b004e0" width="400">

## Known issues

- the search feature in the public instance of Pages CMS is not currently working
