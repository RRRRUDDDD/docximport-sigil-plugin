# Review

## 结论

本地审查未发现 Critical。普通上标及后续文字保留、EQ Ruby 叠加变体和 Word 字号识别均已实现并验证，可以交付。

## 根因

- 普通 `w:vertAlign="superscript"` 原有转换链路正常；回归测试确认其本身不会吞字。
- 可复现的空内容来自 EQ Ruby 使用 `\o\ac`、`\o\al`、`\o\ar` 等叠加对齐变体且 DOCX 未缓存字段显示结果时，旧解析器只识别 `\o\ad`，因此注音和基字均没有输出。
- 旧数据模型和转换器完全没有读取 `w:sz`/`w:szCs`，`styles.xml` 的默认、段落和字符样式字号也被忽略。

## Critical

- 无。

## Warning

- 外部 Codex 与 Claude 在分析、审查阶段均已按双模型并行模板调用，但供应商通道在模型产出报告前返回 403。Codex 通道拒绝当前 `codex_exec` 客户端；Claude 通道当前账号只允许 09:00–18:00 调用。未将失败调用冒充有效报告。

## Info

- EQ overlay 现支持 `\o`、`\o\ad`、`\o\ac`、`\o\al`、`\o\ar`，仍要求存在明确的 `\s\up` 注音表达式，避免把普通 EQ 公式误判为 Ruby。
- Word 半磅字号转换为 pt；优先使用 `w:sz`，缺失或无效时回退 `w:szCs`。
- 支持 `docDefaults`、段落样式和字符样式的字号，并对 `basedOn` 循环做了终止保护。
- 字符样式没有字号时继续继承段落字号，不错误回退并覆盖段落样式。
- 新增的 `Paragraph.font_size`、`Run.font_size` 和扩展 `Style` 均保留旧构造方式兼容性。

## 验证

- `python -m unittest discover -v`：19 项通过。
- 原始 `samples/sample.docx`：转换成功，输出包含字号样式。
- 内存构造真实 DOCX 包：同时验证 `\o\ac` Ruby、上标、后续正文、`w:sz`、`w:szCs` 和文档默认字号，输出符合预期且 0 条警告。
- `python -m compileall -q mmth tests`：通过。
- `python -m py_compile ...`：通过。
- `git diff --check`：通过。

## 变更范围

- `mmth/docx/complex_fields.py`：扩展 EQ overlay 对齐变体。
- `mmth/docx/styles_xml.py`：解析默认/样式字号及继承。
- `mmth/docx/body_xml.py`：读取 run、字符样式、段落样式和默认字号。
- `mmth/documents.py`：在 Paragraph/Run 模型中保存字号。
- `mmth/conversion.py`：输出段落和 run 的 pt 字号样式。
- `tests/test_word_alignment_and_ruby.py`：上标、字段边界、字号来源和回归测试。
