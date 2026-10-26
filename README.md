# Skill 发布 GitHub 助手

`skill-github-publish` 用中文陪伴零基础用户，将自制 AI Skill 从本地整理到 GitHub 上传，并验证远程文件。

## 能做什么

按「检查 → 补齐 → 复查 → 下一步」逐关处理用途、文件结构、实际试用、项目说明、隐私、仓库与许可、上传和远程验收。需要用户决定或登录时等待用户，自动保存工作目录中的进度文件以便继续。

这是一套由 AI 助手执行的工作指令，并非无人值守的上传程序。静态检查脚本不会替你登录、创建仓库或上传文件。GitHub 上传也不等同于在 AI 工具里安装。

## 环境与安装

主要面向 Codex；其他兼容 SKILL.md 的工具需要自行核实发现目录和执行能力。自动检查需要 Python 3.9 或更新版本，脚本不依赖第三方 Python 包。网页上传只需浏览器和 GitHub 账号；CLI 上传另需 Git 和相应认证。AI 助手必须具备读取文件和执行脚本的能力。

### 在 Codex 项目中使用

1. 下载本仓库的源文件并解压。
2. 将含有 SKILL.md 的完整文件夹命名为 `skill-github-publish`，放入目标项目的 `.agents/skills/` 下。
3. 确认入口位于 `.agents/skills/skill-github-publish/SKILL.md`，其他文件保持相对位置。
4. 在该项目的 Codex 中调用 `$skill-github-publish`。如果未出现，重启 Codex 后再试。

本地发现目录以 [OpenAI 官方说明](https://learn.chatgpt.com/docs/build-skills) 为准。本项目提供直接使用的 Skill 文件，不是已提交到插件目录的插件。

## 示例

对 Codex 说：

> 使用 $skill-github-publish，指导我把当前项目的 reading-notes Skill 上传到 GitHub。先检查准备情况，缺什么带我补齐，达标再继续。仓库公开范围和许可证请先询问我。

预期流程：找到目标 Skill → 输出当前关卡和证据 → 补齐文件或询问必要信息 → 上传 → 读取远程文件验证 → 返回实际仓库链接。若只有本地提交成功，不会报告上传完成。

## 单独执行检测

在本仓库目录中运行：

```bash
python3 scripts/check_skill.py /path/to/your-skill
```

将示例路径替换为实际 Skill 文件夹。脚本只读并输出 JSON：

- `needs_fix`：发现明确的结构错误，先修复；退出码为 1。
- `ready_for_review`：基础结构检查完成，仍需检查 findings 和人工关卡；退出码为 0。
- 参数错误：退出码为 2。

执行脚本自检：

```bash
python3 -B scripts/test_check_skill.py
```

## 限制

检测脚本仅做轻量文本检查，不完整解析 YAML；不能保证发现所有凭据，也不检查 Git 历史或证明 Skill 行为正确。真实任务试用、素材权属、许可决定和远程验收由 AI 助手结合用户信息完成。无关请求不应触发发布。没有登录或网络能力时会记录阻塞原因和下一步，不虚报成功。

进度文件 `skill-publish-progress.md` 应保存在待发布 Skill 外部。聊天记录、真实配置和测试输出不应随项目上传。

## 许可证

[MIT License](LICENSE)，Copyright (c) 2026 Mushiliuliugou。
