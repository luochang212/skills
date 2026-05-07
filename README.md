# luochang212's skills

由 [luochang212](https://github.com/luochang212) 创造的 Agent 技能集合。

## 技能列表

| 技能 | 描述 |
| -- | -- |
| [github-research-assistant](skills/github-research-assistant/SKILL.md) | **GitHub 科研助理**：专为研究 GitHub 仓库设计，引导 Agent 分析代码仓库并生成详细的研究报告，涵盖基础信息、用途、技术栈、使用方法和技术架构五个维度。 |
| [code-quality-reviewer](skills/code-quality-reviewer/SKILL.md) | **代码质量审查器**：系统性审查代码库质量问题，识别冗余代码、重复逻辑、命名问题等，基于"收益大于副作用"原则评估每个修复是否值得进行，避免过度工程化。 |
| [deepsec](skills/deepsec/SKILL.md) | **AI 安全漏洞扫描**：基于 Agent 的深度安全审计工具，通过正则匹配 + AI 调查两阶段流程发现传统静态分析难以捕获的漏洞，支持完整审计和 PR 审查两种模式。 |
| [semgrep](skills/semgrep/SKILL.md) | **Semgrep 静态分析**：快速开源静态分析工具，支持 30+ 语言。查找 bug、安全漏洞并强制执行编码规范，支持社区规则库和自定义规则。 |
| [md-to-pdf-macos](skills/md-to-pdf-macos/SKILL.md) | **Markdown 转 PDF（macOS）**：双后端方案——Playwright/Chromium 默认（语法高亮、LaTeX 公式、CSS 主题），reportlab 轻量回退（纯 Python）。CJK 完美支持。 |

## 安装方法

以安装 `github-research-assistant` 为例：

### npx skills

索引：[skills.sh/](https://skills.sh/)

```bash
# 安装单个技能
npx skills add https://github.com/luochang212/skills --skill github-research-assistant

# 安装全部技能
npx skills add https://github.com/luochang212/skills --skill '*' -g -y

# 升级所有技能到最新版本
npx skills update
```

### OpenClaw

索引：[clawhub.ai](https://clawhub.ai/)

```bash
# 登录 OpenClaw，用你的 token 替换 clh_xxxxx
npx clawhub@latest auth login --token clh_xxxxx --no-browser

# 安装技能
npx clawhub@latest install github-research-assistant

# 升级所有已安装技能到最新版本
npx clawhub@latest update --all
```
