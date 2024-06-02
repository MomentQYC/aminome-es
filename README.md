# aminome-es
Add all misskey notes to Elasticsearch

[中文版本](README_CN.md)

## What's this?

- Script for importing historical notes based on the temporarily shut down PR for re-supporting Elasticsearch.
- You can import the entire notes with this script.

## Target Version

- There is currently no official version to support this, but you can manually merge the changes in PR misskey-dev/misskey#13166.

## System Requirements

- Misskey 2023.12.2 or later (aid)
- Postgresql 16
- Elasticsearch 8

## Usage

1. Install the python package.
    ```sh
    pip3 install -r requirements.txt
    ```

2. Open `aminome-es.py` and set `postgresql config` and `elasticsearch config`.

3. Execute.

    ```sh
    python3 ./aminome.py
    ```

## Reference

- [dev-hato/aminome](https://github.com/dev-hato/aminome)
