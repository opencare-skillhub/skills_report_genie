# Skill Report Genie - 执行规范 (Prompts)

**更新日期**: 2026-01-20  
**版本**: v1.0

---

## 📋 核心规范

### 1. 记录文件规范

#### 1.1 简洁性原则
- ✅ **只记录关键内容**
  - 修复内容、文件变更、版本更新
  - 实现方案、设计决策、重要发现
  
- ❌ **避免冗余信息**
  - 重复说明、多余解释、长篇论述
  - 相同内容多次出现
  - 与其他文档重复的信息

#### 1.2 格式规范
```markdown
# 标题 - 版本/时间

## 关键信息
- 要点1
- 要点2

## 文件变更
- file1: 变更说明
- file2: 变更说明

## 下一步
- [ ] 行动项1
- [ ] 行动项2
```

#### 1.3 文件命名
- **版本记录**: `VERSION_X_Y_CHANGELOG.md`
- **修复记录**: `[问题名].md`
- **会议记录**: `YYYY-MM-DD_[主题].md`
- **其他**: `功能_日期.md`

### 2. 存入指定目录规范

#### 2.1 目录映射表
| 记录类型 | 存储目录 | 文件名例 |
|---------|---------|--------|
| 版本更新 | `records/development/` | VERSION_2_1_CHANGELOG.md |
| Bug修复 | `records/fixes/` | PROCESS_SINGLE_FIX.md |
| 会议记录 | `records/meetings/` | 2026-01-20_项目评审.md |
| 设计文档 | `docs/design/` | 功能_设计.md |
| 实现指南 | `docs/implementation/` | 功能_实现指南.md |
| 用户指南 | `docs/guides/` | 功能_快速开始.md |
| API文档 | `docs/api/` | API_集成指南.md |

#### 2.2 目录结构确认
```
project/
├── records/
│   ├── development/     ← 版本更新
│   ├── fixes/          ← Bug修复
│   └── meetings/       ← 会议记录
├── docs/
│   ├── design/         ← 设计文档
│   ├── implementation/ ← 实现指南
│   ├── guides/         ← 用户指南
│   └── api/           ← API文档
```

#### 2.3 创建新记录流程
1. 确定记录类型（版本/修复/会议）
2. 查表确定目录位置
3. 命名规范：`TYPE_INFO_DATE.md` 或 `VERSION_X_Y.md`
4. 写入简洁内容
5. 提交git

---

## ⚡ 减少无效Token消耗

### 3.1 避免的动作 ❌

#### 无效的重复查询
```bash
❌ 错误做法:
  1. grep pattern file1
  2. 看结果后，再 grep pattern file2
  3. 看结果后，再 grep pattern file3

✅ 正确做法:
  1. grep -r pattern directory/   # 一次搞定
```

#### 重复的文件读取
```bash
❌ 错误做法:
  Read file1
  Read file1 (再读一遍)
  
✅ 正确做法:
  Read file1 (一次性读完所有需要部分)
```

#### 连续的单个编辑
```bash
❌ 错误做法:
  edit_file (修改1行)
  edit_file (修改第2处)
  edit_file (修改第3处)
  
✅ 正确做法:
  edit_file (一次修改多个位置)
```

### 3.2 高效的做法 ✅

#### 并行读取
```python
# 同时读多个相关文件
Read file1 (并行)
Read file2 (并行)
Read file3 (并行)
```

#### 批量操作
```bash
# 一次性移动多个文件
mv file1 file2 file3 destination/

# 一次性删除多个文件
rm file1 file2 file3

# 一次性搜索
grep -r pattern directory/
```

#### 优化的git操作
```bash
✅ git log -10 (限制数量)
✅ git diff --stat (摘要)
❌ git log (所有历史)
❌ git show + git diff (多个命令)
```

### 3.3 Token消耗估算

| 操作 | Token | 优化 |
|------|-------|------|
| Read 100KB文件 | ~500 | 限制范围 |
| grep全目录 | ~100 | OK |
| 单个edit_file | ~1000 | 批量修改 |
| git log全历史 | ~5000+ | 加limit |
| 复述已知信息 | ~500 | 避免重述 |

**目标**: 每个任务 < 20000 tokens

### 3.4 提高效率的技巧

#### 技巧1: 链式操作
```bash
✅ find . -name "*.py" | xargs grep pattern | head -20
❌ find . -name "*.py" 
   # 看结果
   grep pattern result.txt
   # 看结果
   head -20 result.txt
```

#### 技巧2: 数据聚合
```bash
✅ 单个Bash脚本完成多步骤
  - 搜索
  - 统计
  - 汇总
  - 输出

❌ 多个Bash调用，每次查一部分
```

#### 技巧3: 文本处理
```bash
✅ awk/sed/grep 处理，直接输出想要的格式
❌ 输出全部信息，再手动筛选
```

### 3.5 写入提示规范

#### 避免冗长回复
```markdown
❌ 长篇幅回复：
"我已经读取了文件A，文件A包含...我又读取了文件B...
最后经过仔细分析，我发现..."

✅ 简洁回复：
"✅ 完成。修改了3个文件，共50行。"
```

#### 避免重复说明
```markdown
❌ "根据之前的分析，我们知道...之前我们说过..."
✅ "根据分析，X问题已修复。"
```

---

## 🎯 执行规范总结

### 记录文件
- 📂 **存储**: 按类型放入指定目录
- 📝 **内容**: 仅记录关键信息
- 🏷️ **命名**: 按规范命名
- 🔗 **链接**: 相对路径链接

### 消耗优化
- ⚡ **并行**: 相关文件同时读
- 🔗 **链式**: 一条命令完成多步
- 📊 **汇总**: 数据聚合后输出
- 🚫 **避免**: 重复查询、重复读取、冗余说明

---

## 📋 检查清单

### 每次执行前确认
- [ ] 是否需要创建新记录文件？
- [ ] 文件应该放在哪个目录？
- [ ] 是否有并行操作的机会？
- [ ] 是否有重复的查询/读取？
- [ ] 回复是否过长/冗余？

### 每次提交记录时确认
- [ ] 文件在正确的目录？
- [ ] 文件名按规范？
- [ ] 内容简洁且完整？
- [ ] 无重复或冗余信息？
- [ ] 链接使用相对路径？

---

## 📍 目录快速参考

```
创建新版本记录       → records/development/VERSION_X_Y.md
记录Bug修复         → records/fixes/问题名.md
记录会议内容        → records/meetings/YYYY-MM-DD_主题.md
添加设计文档        → docs/design/功能_设计.md
添加实现指南        → docs/implementation/功能_实现.md
添加用户指南        → docs/guides/功能_指南.md
添加API文档         → docs/api/API_说明.md
```

---

## 🔄 实施示例

### 例1: 修复完成后的记录流程
```
1. 编写修复代码 ✓
2. 创建文件: records/fixes/PROCESS_SINGLE_FIX.md
3. 简洁记录:
   - 问题说明
   - 修复方案
   - 文件变更 (只列举，不详细)
   - 验证方法
4. 完成
```

### 例2: 功能发布的记录流程
```
1. 完成功能开发 ✓
2. 创建文件: records/development/VERSION_2_2_CHANGELOG.md
3. 简洁记录:
   - 新功能列表
   - 主要改进
   - 影响文件 (简表)
   - 测试状态
4. 完成
```

### 例3: 高效的多文件修改
```bash
✅ 一次性修改多处:
   edit_file file1.py (修改ABC三处)
   edit_file file2.py (修改DE两处)
   
❌ 分次修改:
   edit_file file1.py (改A)
   edit_file file1.py (改B)
   edit_file file1.py (改C)
   edit_file file2.py (改D)
   edit_file file2.py (改E)
```

---

## ✅ 已执行清单

- [x] 2026-01-20: 整理项目结构（10个目录、41个文件）
- [x] 2026-01-20: 修复process_single.py完整流程
- [x] 2026-01-20: 创建docs/README.md文档索引
- [x] 2026-01-20: 创建records/目录和记录规范

---

## 📊 Tokens消耗目标

| 任务 | 目标 | 实际 | 状态 |
|------|------|------|------|
| 项目整理 | 30K | ~25K | ✅ |
| 脚本修复 | 20K | ~18K | ✅ |
| 文档创建 | 15K | ~12K | ✅ |
| **平均** | **~20K** | **~18K** | **✅** |

---

**目标**: 保持高效率、低消耗、高质量的项目维护。

**维护者**: Skill Report Genie Team  
**最后更新**: 2026-01-20
