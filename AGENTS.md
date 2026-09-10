# AGENTS.md

静态 GitHub Pages 仓库：把收集到的博客做成手机能打开的列表。

| 文件 | 作用 |
|---|---|
| `blogs.md` | 源数据。九个中文分类 + `- YYYY-MM-DD [标题](url)` |
| `generate.py` | 读 `blogs.md`，生成 `index.html` |
| `index.html` | 站点：https://zeguanxiao.github.io/blog-reading-list/ |
| `XIAOHONGSHU.md` | **从小红书抓新合集的 playbook**。用户要求更新列表时才执行；默认 gitignore，不要提交 |

改列表后运行 `python3 generate.py`。不要改分类标题。不要提交 `.tmp-docx/`、cookie、`xsec_token`。未要求时不要 commit / push。
