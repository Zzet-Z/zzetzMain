# Apple 风格设计系统参考

这个目录中的 [DESIGN.md](./DESIGN.md) 是从公开的 [Apple](https://apple.com/) 官网风格中提炼出的设计说明。它**不是 Apple 官方设计系统**。颜色、字体和间距不保证 100% 精确，但很适合作为构建相似视觉语言的起点。

## 文件说明

| 文件 | 说明 |
|------|------|
| `DESIGN.md` | 完整设计系统说明文档（9 个章节） |
| `preview.html` | 设计 token 交互预览（亮色） |
| `preview-dark.html` | 设计 token 交互预览（暗色） |

可以把 [DESIGN.md](./DESIGN.md) 当作 AI 代理或前端工程师的视觉参考，用来生成接近 Apple 网站语言的 UI。

## 预览说明

这里附带了一份基于 `DESIGN.md` 搭建的示例落地页，用于集中展示真实的：

- 颜色
- 字体层级
- 按钮样式
- 卡片样式
- 间距
- 层级与阴影

### 深色模式
![Apple Design System — Dark Mode](https://pub-2e4ecbcbc9b24e7b93f1a6ab5b2bc71f.r2.dev/designs/apple/preview-dark-screenshot.png)

### 亮色模式
![Apple Design System — Light Mode](https://pub-2e4ecbcbc9b24e7b93f1a6ab5b2bc71f.r2.dev/designs/apple/preview-screenshot.png)

## 中文界面使用建议

如果你的产品面向简体中文用户，建议在使用这套风格时做以下本地化处理：

- 字体回退链中加入 `PingFang SC`、`Noto Sans SC`、`Microsoft YaHei`
- 中文大标题不要机械照搬英文的极端负字距，需先以可读性为准
- 中文正文建议保持比英文略宽松的行高
- Apple Blue 仍然只作为交互强调色，不要把中文信息密度高的问题错误地用更多颜色去解决

这套风格最有价值的部分不是“像 Apple”，而是：

- 节制的配色
- 大量留白
- 强视觉层级
- 对结果内容的展品化呈现
