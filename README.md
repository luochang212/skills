# luochang212's skills

由 [luochang212](https://github.com/luochang212) 创造的 Agent 技能集合。

## 技能列表

| 技能 | 描述 |
| -- | -- |
| [github-research-assistant](skills/github-research-assistant/SKILL.md) | **GitHub 科研助理**：专为研究 GitHub 仓库设计，引导 Agent 分析代码仓库并生成详细的研究报告，涵盖基础信息、用途、技术栈、使用方法和技术架构五个维度。 |
| [code-quality](skills/code-quality/SKILL.md) | **代码质量审查器**：系统性审查代码库质量问题，识别冗余代码、重复逻辑、命名问题等，基于"收益大于副作用"原则评估每个修复是否值得进行，避免过度工程化。 |
| [code-audit](skills/code-audit/SKILL.md) | **代码安全审计**：双模式——快速模式（Semgrep）适合 CI 集成和模式搜索，深度模式（deepsec）通过 AI 调查进行可利用性判断。覆盖 30+ 语言，支持自定义规则和 PR Review。 |
| [html-report](skills/html-report/SKILL.md) | **HTML 精美报告**：将信息转化为自包含的纯 HTML 页面，适合项目报告、产品页、架构概览、仪表盘、代码审查总结等场景。6 套色板、SVG 内联图表、零依赖，打开即用。 |
| [md-to-pdf](skills/md-to-pdf/SKILL.md) | **Markdown 转 PDF**：跨平台双后端方案——Playwright/Chromium 默认（语法高亮、LaTeX 公式、CSS 主题），reportlab 轻量回退（纯 Python）。自动检测系统 CJK 字体，支持 macOS/Windows。 |

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
