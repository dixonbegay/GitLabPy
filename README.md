# GitLabPy
A Python module to help sort GitLab's Webhooks

Some of the JSON data coming from GitLab's webhooks are set as attributes to the GitLab class. There are functions within the GitLab class that allow for easy handling of the JSON data.

## Requirements
* Python >= 3.9

## Install
* `pip install GitLabPy`

## How to use
Check out the [wiki](https://github.com/shadez95/GitLabPy/wiki) for information.

### Example
An example of how to utilize this can be found [here](https://github.com/shadez95/GitLabPy/tree/master/examples/Django-App)

## Development
This project uses [uv](https://docs.astral.sh/uv/) for dependency management, building, and publishing.

```bash
# Install dependencies (including dev dependencies)
uv sync

# Run the test suite
uv run pytest

# Build the sdist and wheel
uv build
```

## Releasing
Releases are published manually from a local machine (no CI publish step).

```bash
# 1. Bump the version in pyproject.toml, then build
uv build

# 2. Publish to PyPI
uv publish

# 3. Create the GitHub release (tags and publishes the release)
gh release create vX.Y.Z --generate-notes
```
