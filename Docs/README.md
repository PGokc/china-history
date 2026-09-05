# 史料目录

本目录保留能够支持当前内容核查与追溯的原始资料。

- `source-manifest.json` 记录来源名称、地址和对应主题。
- `226*.html` 与 `226*.txt` 是故宫公开人物资料的本地留存。
- `portrait-source.html`、`lineages.html` 与 `ewer.html` 用于画像、谱系和器物核查。
- `sheng-study.pdf` 用于相关专题研究。

应用运行数据统一以 `App/Resources/history.json` 为准。修改历史条目时，应同步维护条目中的来源 ID，并运行 `python3 scripts/validate_content.py`。
