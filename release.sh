#!/usr/bin/env bash
# Interactive release script: bumps the version, builds, publishes to PyPI,
# and creates the GitHub release.
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

PYPROJECT="pyproject.toml"

require_cmd() {
    if ! command -v "$1" >/dev/null 2>&1; then
        echo "Error: '$1' is required but not installed." >&2
        exit 1
    fi
}

require_cmd uv
require_cmd git
require_cmd gh

current_branch="$(git rev-parse --abbrev-ref HEAD)"
if [[ "$current_branch" != "master" ]]; then
    echo "Error: you're on branch '$current_branch', not 'master'. Switch to master first." >&2
    exit 1
fi

if [[ -n "$(git status --porcelain)" ]]; then
    echo "Error: working tree is not clean. Commit or stash your changes first." >&2
    exit 1
fi

git fetch origin
if [[ "$(git rev-parse HEAD)" != "$(git rev-parse origin/master)" ]]; then
    echo "Error: local master is not up to date with origin/master. Run 'git pull' first." >&2
    exit 1
fi

current_version="$(grep -m1 '^version' "$PYPROJECT" | sed -E 's/version = "(.*)"/\1/')"
echo "Current version: $current_version"
read -rp "New version (e.g. 1.2.3): " new_version

if [[ ! "$new_version" =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
    echo "Error: version must look like X.Y.Z" >&2
    exit 1
fi

tag="v$new_version"
if git rev-parse "$tag" >/dev/null 2>&1; then
    echo "Error: tag $tag already exists." >&2
    exit 1
fi

read -rp "Bump version $current_version -> $new_version, publish to PyPI, and create GitHub release $tag? [y/N] " confirm
if [[ "$confirm" != "y" && "$confirm" != "Y" ]]; then
    echo "Aborted."
    exit 1
fi

echo "==> Updating $PYPROJECT"
sed -i.bak -E "s/^version = \".*\"/version = \"$new_version\"/" "$PYPROJECT"
rm -f "$PYPROJECT.bak"

echo "==> Running tests"
uv run pytest

echo "==> Committing version bump"
git add "$PYPROJECT"
git commit -m "Bump version to $new_version"

echo "==> Building sdist and wheel"
rm -rf dist/
uv build

echo "==> Publishing to PyPI"
uv publish

echo "==> Pushing master and tag"
git tag "$tag"
git push origin master
git push origin "$tag"

echo "==> Creating GitHub release"
gh release create "$tag" dist/* --generate-notes

echo "Done. Released $tag."
