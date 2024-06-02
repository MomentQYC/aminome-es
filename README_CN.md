# aminome-es
将所有 Misskey 帖文添加到 Elasticsearch 中

[English Version](README.md)

## 这是什么?

- 根据暂时关闭的重新支持 Elasticsearch 的 PR 编写的导入历史帖文的脚本。
- 您可以使用此脚本导入全部帖文。

## 目标版本

- 目前还没有支持此功能的正式版本，但您可以手动合并 PR misskey-dev/misskey#13166 中的更改。

## 系统要求

- Misskey 2023.12.2 或之后的版本 (aid)
- Postgresql 16
- Elasticsearch 8

## 使用方法

1. 安装 Python 包。

    ```sh
    pip3 install -r requirements.txt
    ```

3. 打开 `aminome-es.py` 并将 `postgresql config` 和 `elasticsearch config` 更改为正确的值。

4. 执行。

    ```sh
    python3 ./aminome.py
    ```

## 参考

- [dev-hato/aminome](https://github.com/dev-hato/aminome)
