# Statistical Rethinking 中文化

《Statistical Rethinking》（第二版）的简体中文静态网页版项目。

当前采用 `~/Downloads/Statistical Rethinking 2nd Edition.pdf` 作为本地校对源。源 PDF、英文抽取文本和逐页渲染图不会进入版本库；仓库只保存转换工具、术语表、人工审校过的中文内容和可发布的中文静态站点。

## 当前进度

- 已确认源文件为 617 页、带文字层的 XeTeX PDF。
- 已建立 17 章及书后材料的 PDF 页码映射。
- 第 1 章 PDF 第 17–34 页（18/18 页）已完成翻译、逐页核对和全章桌面/移动端验收。
- 图 1.1、图 1.2 已重建为中文 SVG；图 1.3 从 PDF 原始嵌入对象提取；尾注 1–36 已译入章末。
- `config/chapter-contracts.json` 锁定第 1–2 章的页码、锚点、标题和组件数量；只有满足契约才能保持 `verified` 状态。
- 第 2 章 PDF 第 35–64 页（30/30 页）已完成整章翻译、逐页核对和桌面/移动端验收。
- 全书累计完成 2/17 章、验收 48/617 个 PDF 页面。
- 尚未完成的章节会在目录页明确标为“待翻译”，不会用低质量机翻冒充完成稿。

## 构建

```bash
python3 scripts/extract_source.py --chapter chapter-01
python3 scripts/build_site.py
python3 scripts/audit_site.py
python3 -m http.server 8877 --directory site
```

浏览器打开 `http://127.0.0.1:8877/`。

## 工作约定

1. `source/` 是本地、可再生、默认忽略的英文抽取物。
2. `translations/zh/chapters/` 只放已人工复核的中文章节片段。
3. `translations/zh/progress.json` 是唯一进度账本，以 PDF 页面为最小验收单位。
4. R、Stan、包名、函数名、变量名、代码和数学符号保持原样。
5. 每次修改后都要重新构建、运行静态审计，并对涉及页面做桌面与移动端视觉检查。
6. 未确认授权前，不公开源 PDF、英文抽取物或完整中文译本。

详细规范见 `docs/translation-guidelines.md`。
