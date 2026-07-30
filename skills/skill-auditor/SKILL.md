# Skill Auditor

## 用途
审计 `.qwen-agent/skills/` 下所有 skill 的完整性、触发词、描述质量。

## 触发条件
- 用户提到"审计 skills"、"检查 skill 配置"
- 项目初始化或迁移后

## 操作
- 扫描所有 skill 目录
- 检查 SKILL.md 是否存在且内容完整
- 验证 scripts 目录下的文件
- 报告问题并建议修复
