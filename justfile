test:
    uv run pytest

build:
    uv build

clean:
    find . -name '*~' -print0 | xargs -0 -r rm
    find . -name '__pycache__' -print0 | xargs -0 -r rm -r
