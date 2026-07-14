# DOCXImport（Sigil 插件）

将 DOCX 文档导入 Sigil，并转换为可继续编辑的 EPUB。

本插件基于 Python 版 [Mammoth](https://github.com/mwilliamson/python-mammoth)，转换目标是生成结构清晰、便于编辑的 HTML，而不是逐像素复刻 Word 的页面排版。

## 主要功能

- 将 DOCX 转换为 EPUB2 或 EPUB3，并导入 Sigil。
- 支持自定义 Mammoth 样式映射和自定义 CSS。
- 保留常见的段落、标题、列表、表格、链接、图片、脚注及基础文字格式。
- 识别 Word 的显式右对齐，并输出对应的 HTML/CSS 对齐样式。
- 保留普通上标、下标及其前后正文。
- 识别 Word 字号：
  - 支持 run 中的 `w:sz` 和 `w:szCs`；
  - 支持文档默认字号；
  - 支持段落样式、字符样式及 `basedOn` 字号继承；
  - Word 的半磅值会转换为 CSS `pt`。
- 识别写在 Word 域中的 Ruby（拼音/注音），包括常见的 `EQ`、`\o`、`\o\ad`、`\o\ac`、`\o\al` 和 `\o\ar` 形式，并输出 HTML `ruby`/`rt` 标记。

复杂页面布局、浮动形状、特殊公式和部分 Word 专有对象可能需要在导入后手工调整。

## 相关链接

- [Sigil 官网](http://sigil-ebook.com)
- [Sigil MobileRead 支持论坛](http://www.mobileread.com/forums/forumdisplay.php?f=203)
- [DOCXImport MobileRead 支持主题](http://www.mobileread.com/forums/showthread.php?t=273966)
- [Mammoth 样式映射文档](https://github.com/mwilliamson/python-mammoth#writing-style-maps)

## 运行要求

- Sigil 0.9.8 或更高版本。
- Python 3；推荐使用 Sigil 自带的 Python 解释器。
- 插件界面依赖 Qt。使用 Sigil 自带解释器时，Windows、macOS 和常见 Linux 发行版通常无需另行安装依赖。
- 如果在 Linux 上使用外部 Python 环境，需要自行确保相应的 PyQt5 或 PySide6 组件可用。

> **注意：** 安装前不要重命名插件 ZIP 文件。

## 安装与使用

1. 在 Sigil 中选择 **插件 > 管理插件**（**Plugins > Manage Plugins**）。
2. 点击 **添加插件**（**Add Plugin**），选择构建或下载得到的 `DOCXImport_vX.X.X.zip`。
3. 通过 **插件 > 输入 > DOCXImport**（**Plugins > Input > DOCXImport**）启动插件。
4. 选择生成 EPUB2 或 EPUB3。
5. 使用第一个 **...** 按钮选择 DOCX 文件。
6. 如有需要，选择自定义样式映射文件和/或 CSS 文件。
7. 点击 **确定** 开始转换。

转换完成后得到的 EPUB 默认只有一个正文分区。如需拆分章节，可在 Sigil 中使用 **编辑 > 在光标处拆分**（**Edit > Split At Cursor**）或 **插入 > 拆分标记**（**Insert > Split Marker**）。

仓库的 [`samples`](samples) 目录包含示例 DOCX、样式映射和 CSS 文件。

## 自定义样式映射与 CSS

样式映射用于将 Word 样式映射为指定的 HTML 元素或 class；CSS 用于控制导入 EPUB 后的显示效果。

可从以下示例开始修改：

- [`samples/sample_style_map.txt`](samples/sample_style_map.txt)
- [`samples/sample_style_sheet.css`](samples/sample_style_sheet.css)

样式映射语法请参阅 Mammoth 的 [Writing Style Maps](https://github.com/mwilliamson/python-mammoth#writing-style-maps) 文档。

## 许可证

- DOCXImport：GPLv3。
- [Mammoth](https://github.com/mwilliamson/python-mammoth)：BSD 2-Clause License。
- [Cobble](https://github.com/mwilliamson/python-cobble)：BSD 2-Clause License。

完整许可证原文请参阅根目录的 [`LICENSE`](LICENSE)、[`mmth/LICENSE`](mmth/LICENSE) 和 [`cbbl/LICENSE`](cbbl/LICENSE)。
