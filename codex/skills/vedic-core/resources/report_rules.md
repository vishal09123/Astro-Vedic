# Report Packaging Rules

> Purpose: Executed when user requests: "generate report", "package report", "export HTML".

---

## Script Location

`report_builder.py` resides in the skill's `scripts/` directory: `scripts/report_builder.py`.

If not found, resolve in order:
1. `scripts/report_builder.py` under the current skill directory.
2. `report_builder.py` in the workspace root.
3. If neither exists, notify user and prompt for confirmation.

## Packaging Command

Select `--lang` based on current `client_language`:
- English -> `--lang en`
- Japanese -> `--lang ja`
- Chinese -> `--lang cn`
- Other -> Select matching language; default HTML shell to `en` without altering the original prose language.

```bash
# Package all existing markdown files
python scripts/report_builder.py [workspace_dir] --lang [en|cn|ja]

# Package core analysis only
python scripts/report_builder.py [workspace_dir] --include core --lang [en|cn|ja]

# Package core + career
python scripts/report_builder.py [workspace_dir] --include core,career --lang [en|cn|ja]
```

`report_builder.py` automatically detects existing Markdown artifacts and compiles only present sections.
`--include` selectively packages specific modules.
`--lang` styles the cover, table of contents, section banners, and footers.

## ⚠️ Forbidden Actions

1. **No Automatic Browser Launch**: Do not open the browser with `open`, `start`, or `xdg-open`. State the absolute file path and let the user open it.
2. **No HTML Code Dumps in Chat**: Do not output raw HTML markup into the chat dialogue.
3. **Concise Confirmation**: State only the completed path upon generation: `"Report successfully generated: [absolute_file_path]"`.
