# luochang212's skills

由 [luochang212](https://github.com/luochang212) 创造的 skills，震撼首发！！！

## 🤓 技能列表

| 技能 | 描述 |
| -- | -- |
| [github-research-assistant](https://github.com/luochang212/skills/blob/main/skills/github-research-assistant/SKILL.md) | **GitHub 科研助理**：科研助理过去是公司 CEO 的标配。在高级认知可以被工业化生产的今天，它的供给几乎是无限的！本 skill 专为研究 GitHub 仓库设计，它能够引导你的 Agent 吃透代码仓库并生成详细的研究报告！ |
| [code-quality-reviewer](https://github.com/luochang212/skills/blob/main/skills/code-quality-reviewer/SKILL.md) | **代码质量审查器**：系统性审查代码库质量问题，识别冗余代码、重复逻辑、命名问题等，基于"收益大于副作用"原则评估每个修复是否值得进行，避免过度工程化。 |

## 🚀 安装方法

以安装 `github-research-assistant` 为例👇

### 📦 npx skills

索引：[skills.sh/](https://skills.sh/)

```bash
# 安装一个技能
npx skills \
  add https://github.com/luochang212/skills \
  --skill github-research-assistant

# 安装全部技能到 Claude Code
npx skills \
  add https://github.com/luochang212/skills \
  --skill '*' \
  --agent claude-code \
  -g -y

# 升级所有技能到最新版本
npx skills update
```

### 🦞 OpenClaw

索引：[clawhub.ai](https://clawhub.ai/)

```bash
# 登录 OpenClaw，用你的 token 替换 clh_xxxxx
npx clawhub@latest auth login --token clh_xxxxx --no-browser

# 安装技能
npx clawhub@latest install github-research-assistant

# 升级所有已安装技能到最新版本
npx clawhub@latest update --all
```
