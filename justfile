set ignore-comments := true

default:
  @just --list

test:
    uv run pytest

build:
    # This is ignored.
    rm -fr dist
    uv build

publish:
    # Publish on PyPI. Relies on UV_PUBLISH_TOKEN being set.
    uv publish

[working-directory: 'docs']
docs:
    uv run make html

clean:
    find . -name '*~' -print0 | xargs -0 -r rm
    find . -name '__pycache__' -print0 | xargs -0 -r rm -r
    rm -fr dist
