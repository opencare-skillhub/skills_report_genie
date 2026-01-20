# 文档组织指南

本目录组织了 Skill Report Genie 的所有文档。

## 📚 目录结构

### design/
**核心设计与规划文档**

- `skill_design.md` - Skill核心设计，包括流程、功能、需求
- `DEVELOPMENT_PLAN.md` - 详细开发方案，分模块说明
- `GENETIC_PATHOLOGY_GUIDE.md` - 遗传和病理诊断指南
- `PATHOLOGY_ANALYSIS_BEST_PRACTICES.md` - 病理分析最佳实践
- `JSON_STORAGE_GUIDE.md` - JSON数据存储规范
- `SQLITE_DEPLOYMENT.md` - SQLite数据库部署方案

### implementation/
**实现指南与技术文档**

- `DEVELOPMENT_PRINCIPLES.md` - 开发原则与规范
- `IMPLEMENTATION_SPEC.md` - 实现详细规范
- `WORKFLOW_IMPLEMENTATION.md` - 工作流实现
- `WORKFLOW_REDESIGN.md` - 工作流重设计
- `DESIGN_INTEGRATION_SUMMARY.md` - 设计集成总结
- `MULTI_SOURCE_ARCHITECTURE.md` - 多源架构设计
- `SYSTEM_SUMMARY.md` - 系统总结
- `ENVIRONMENT_SETUP.md` - 环境配置指南
- `PRIVACY_AND_WEB_DEPLOYMENT.md` - 隐私与Web部署
- `SECURITY_AUDIT_REPORT.md` - 安全审计报告
- `SECURITY_BEST_PRACTICES.md` - 安全最佳实践

### guides/
**用户指南与快速参考**

- `QUICK_REFERENCE.md` - 快速参考手册
- `SINGLE_IMAGE_PARSING_GUIDE.md` - 单图片解析指南
- `SINGLE_IMAGE_PROCESSING.md` - 单图片处理说明
- `STEPFUN_QUICK_START.md` - StepFun快速开始

### api/
**API文档与集成指南**

- `MCP_CONFIGURATION.md` - MCP配置说明
- `RAG_INTEGRATION_GUIDE.md` - RAG集成指南
- `CLINICALTRIALS_API_GUIDE.md` - 临床试验API指南

### archives/
**过期/历史文档**

包含所有历史版本的Phase文档和已完成的总结：
- PHASE2_SUMMARY.md - Phase 2 总结
- PHASE3_SUMMARY.md - Phase 3 总结
- PHASE4_SUMMARY.md - Phase 4 总结
- PHASE4_ARCHITECTURE.md - Phase 4 架构
- PHASE5_*.md - Phase 5 各周总结
- TEST_RESULTS.md - 测试结果
- CHANGELOG_STEPFUN.md - StepFun更新日志

## 🔍 如何使用

### 初次了解项目
1. 阅读根目录的 `README.md`
2. 查看 `docs/design/skill_design.md`
3. 参考 `docs/guides/QUICK_REFERENCE.md`

### 深入了解设计
1. `docs/design/DEVELOPMENT_PLAN.md` - 完整方案
2. `docs/design/GENETIC_PATHOLOGY_GUIDE.md` - 医学背景
3. `docs/design/JSON_STORAGE_GUIDE.md` - 数据格式

### 实施开发
1. `docs/implementation/DEVELOPMENT_PRINCIPLES.md` - 开发规范
2. `docs/implementation/IMPLEMENTATION_SPEC.md` - 详细规范
3. `docs/implementation/ENVIRONMENT_SETUP.md` - 环境配置

### 集成外部服务
1. `docs/api/MCP_CONFIGURATION.md` - MCP配置
2. `docs/api/RAG_INTEGRATION_GUIDE.md` - RAG集成
3. `docs/api/CLINICALTRIALS_API_GUIDE.md` - 临床试验

### 部署与安全
1. `docs/implementation/PRIVACY_AND_WEB_DEPLOYMENT.md` - 部署指南
2. `docs/implementation/SECURITY_BEST_PRACTICES.md` - 安全指南
3. `docs/design/SQLITE_DEPLOYMENT.md` - 数据库部署

## 📊 文件统计

| 目录 | 文件数 | 用途 |
|------|--------|------|
| design/ | 6 | 核心设计 |
| implementation/ | 11 | 实现指南 |
| guides/ | 4 | 用户指南 |
| api/ | 3 | API文档 |
| archives/ | 15 | 历史文档 |

**总计**: 39 个文档

## 🔗 相关文件位置

- **项目主文件**: `/process_single.py` (已修复, v2.1)
- **修复记录**: `/records/fixes/PROCESS_SINGLE_FIX.md`
- **版本记录**: `/records/development/VERSION_2_1_CHANGELOG.md`
- **废弃脚本**: `/scripts/legacy/` (8个历史脚本)
- **核心源代码**: `/src/` (处理、分析、报告模块)

## 📝 更新历史

### 2026-01-20
- ✅ 创建新文档组织结构
- ✅ 移动过期文档到archives/
- ✅ 分类活跃文档到对应目录
- ✅ 整理废弃脚本到scripts/legacy/
- ✅ 创建records/目录记录开发进度

## 💡 文档维护建议

1. **定期审查**: 每个Phase完成后，将相关文档归档
2. **版本控制**: 重要文档保留版本记录
3. **交叉引用**: 使用相对路径链接相关文档
4. **更新时间戳**: 文档修改时更新标题或日期
5. **清晰分类**: 新文档按类别放入合适目录

## 🚀 快速导航

- **我想快速开始** → `docs/guides/QUICK_REFERENCE.md`
- **我想理解设计** → `docs/design/skill_design.md`
- **我想部署系统** → `docs/implementation/PRIVACY_AND_WEB_DEPLOYMENT.md`
- **我想查找API** → `docs/api/MCP_CONFIGURATION.md`
- **我想了解历史** → `docs/archives/` 或 `records/`
