# Skill Report Genie - 详细开发方案

## 项目概览
**目标**：为肿瘤患者整理混乱病情资料，提取结构化信息，辅助准备问诊内容清单，生成标准化病情报告。

**主要用户**：胰腺癌患者及其家属（可扩展至其他实体瘤）

**核心价值**：
- 减少患者/家属信息整理负担
- 为医生提供标准化、可快速浏览的病情概览
- 生成结构化病情报告和问诊清单
- 关联最新临床试验和文献信息

---

## 一、核心确认点

### 1.1 患者ID管理
- **方案**：统一使用hash算法
- **组成**：`hash(姓名 + 出生年份 + 就诊医院 + 病例号)`
- **目的**：避免直接存储明文敏感信息，同时保持唯一性和稳定性

### 1.2 DICOM处理
- **定位**：额外可选工具能力
- **处理范围**：按系列处理，支持多序列
  - 强化期 (arterial phase)
  - 静脉期 (portal venous phase)
  - 退化期 (delayed phase)
- **输出**：DICOM序列 → JPG序列保存

### 1.3 肿瘤标志物缺失值处理
- **处理方法**：平滑均值补全
- **标注要求**：必须标注"**AI生成的补全值**，请用户注意"
- **应用场景**：CA19-9/CA50/CA125/CA72-4/CEA时间序列中缺失值

### 1.3.1 肿瘤标志物趋势图设计规范
基于ca_marker.png的标准化设计，包含四大主要标志物：

**主要肿瘤标志物**
- **CA19-9**：胰腺癌最灵敏的标志物，但可被炎症干扰
- **CA50**：与CA19-9同源，两者联合更可靠
- **CA125**：腹膜癌转移指示，用于评估腹膜播散
- **CA72-4**：胃肠肿瘤标志物，反映分化程度
- **CEA**（可选）：一般肿瘤标志物，特异性较低

**临床解读核心**：
- **关键原则**：多个标志物**同趋势变化**才能确认肿瘤异常
- **假阳性排除**：
  - 单个CA19-9升高 → 可能为炎症（胰炎、胆囊炎）、良性肿瘤
  - CA19-9+CA50同升高 → 肿瘤进展可能性↑↑
  - CA125同升高 → 腹膜转移信号↑↑↑
  - CA72-4同升高 → 分化程度下降/进展信号↑
- **临床判断标准**：
  - 2个以上标志物同升高+影像学恶化 → 肿瘤进展高可能性
  - CA19-9单独升高+其他标志物正常+无影像改变 → 可能为炎症，观察

**图表类型与布局**
- 多序列折线图（Line Chart）+ 数据点标记
- 白色背景 + 浅灰色网格线（水平/垂直方向）
- 结构：标题 → 绘图区 → 图例 → 临床判读提示 → 文字总结

**坐标轴设计**
- **Y轴**：数值轴
  - 底部刻度范围：0-100（默认），根据最大值动态调整
  - 刻度步长建议：10-20单位
  - 注：四个标志物单位不同，可能需要双Y轴或分开显示
    * CA19-9、CA50、CA125：U/mL
    * CA72-4：U/mL
    * CEA：ng/mL（可选图，单独或比例缩放）
- **X轴**：分类轴（时间/治疗阶段）
  - 标签示例：术前、C1-C12（化疗周期）、结疗1、结疗2
  - 刻度对齐垂直网格线

**数据序列配色**
- **CA19-9**：红色（#E54D42）- 实线折线 + 实心圆点
- **CA50**：深红色（#B71D3A）- 实线折线 + 实心方形（与CA19-9区分）
- **CA125**：绿色（#39B54A）- 实线折线 + 实心圆点
- **CA72-4**：橙色（#FF8811）- 实线折线 + 实心三角形
- **CEA**（可选）：蓝色（#0081FF）- 实线折线 + 实心圆点

**参考线**
- 与数据序列同色虚线，表示参考上限
- 标准参考值位置：
  - CA19-9：43 U/mL（虚线标注"参考上限(43)"）
  - CA50：20 U/mL（虚线标注"参考上限(20)"）
  - CA125：35 U/mL（虚线标注"参考上限(35)"）
  - CA72-4：10 U/mL（虚线标注"参考上限(10)"）
  - CEA：5 ng/mL（虚线标注"参考上限(5)"）

**图例**
- 位置：图表正下方，水平排列（或分两行）
- 两组内容：
  - 第一组：实心色块 + 指标名称（代表实际检测值）
  - 第二组：虚线线段 + 指标名称 + 参考值（代表参考上限）
- 示例：
  ```
  CA19-9  CA50  CA125  CA72-4
  ---- CA19-9参考(43)  ---- CA50参考(20)  ---- CA125参考(35)  ---- CA72-4参考(10)
  ```

**临床判读辅助区**
- 在图表下方显示趋势同步分析：
  ```
  【多标志物同趋势分析】
  ✓ CA19-9↑ + CA50↑ + CA125↑ → 肿瘤进展可能性高 🔴
  ✓ CA19-9↑ + 其他标志物正常 → 建议排除炎症 🟡
  ✓ 全部标志物↓ → 治疗有效，继续监测 🟢
  ```

**文本说明**
- **图注部分**：
  - 实线 = 实际检测值
  - 虚线 = 参考上限
  - 各指标单位和正常范围说明
  - **强调**：多标志物同升高更提示肿瘤异常，单一标志物升高需除外炎症
- **小结部分**：
  - 按指标分类阐述
  - 关键数值：初值、当前值、变化幅度、百分比变化
  - **多标志物同步分析**：
    * "CA19-9和CA50同时升高，CA125也升高，强烈提示肿瘤进展"
    * "CA19-9升高，但CA50、CA125、CA72-4均正常，可能为炎症反应"
  - 异常情况解释（如术后升高原因、胰漏等）
  - 临床意义说明

**示例数据呈现**
```
CA19-9：
  - 术前：245.5 U/mL（明显升高）
  - 化疗响应：C1后95.2 → C2后67.8 → C12结疗13.0（整体下降94%）
  - 当前：13.0 U/mL（正常范围）
  
CA50：
  - 术前：128.0 U/mL（明显升高）
  - 变化趋势：与CA19-9同步，同步下降，佐证CA19-9升高的肿瘤性质
  - 当前：8.5 U/mL（正常范围）

CA125：
  - 术前：35.8 U/mL（正常边界）
  - 术后升高：48.5 U/mL（胰漏相关，与CA19-9同升高）
  - 缓慢下降：经过3个月逐步恢复至17.4 U/mL
  - 当前：17.4 U/mL（正常范围）
  - 临床意义：腹膜反应已缓解，无腹膜播散迹象

CA72-4：
  - 全程轻度升高（5.6 → 12.1 → 7.2 U/mL）
  - 当前：5.1 U/mL（接近参考值）
  - 意义：分化程度信息，总体稳定

【多标志物同趋势结论】
✓ CA19-9 + CA50同步下降：肿瘤对化疗高度敏感
✓ CA125升高后逐步恢复：术后胰漏已控制，无腹膜播散
✓ CA72-4稳定：分化程度无明显变化
→ 整体评估：治疗有效，肿瘤缓解，继续监测
```

**交互建议**
- 数据点Tooltip：显示日期、周期、具体数值、参考范围、临床意义提示
- X轴缩放：长序列（C1-C12）支持水平滚动/缩放
- 数据对比：
  * 支持单指标vs多指标切换显示
  * 支持同趋势分析高亮（如CA19-9+CA50+CA125）
  * 支持移除某指标重新显示（排除某一指标后的趋势）

### 1.4 问诊清单格式
- **结构**：结构化列表 + 优先级 + 重点问题关注点提示
- **示例**：
  ```
  【高优先级】化疗方案调整
  - 问题：根据最新CA19-9(当前值: 85 U/mL)变化，是否需要调整化疗方案？
  - 关注点：对比上次检查(45 U/mL)，升高88%，请告知医生近期影像变化
  
  【中优先级】营养管理
  - 问题：当前体重下降5kg（3个月），是否需要营养干预？
  ```
- **图表实现**：quickchart-mcp 或 echart代码包生成可视化

### 1.5 临床试验搜索范围
- **逻辑**：根据患者本身病历癌肿类型
- **调用接口**：clinical_trials API 2.0
- **搜索条件**：
  - 癌肿类型（如胰腺癌）
  - 病理类型（如腺癌）
  - 基因突变（KRAS、TP53等）
  - TNM分期

### 1.6 月度定义
- **标准**：日历月（1月1日～1月31日）
- **生成内容**：月度摘要 + 当月新增治疗/检查事件

### 1.7 版本控制
- **需求**：完整的历史记录
- **实现**：
  - patient_master.json中记录版本时间戳
  - memos中为每个字段记录版本历史
  - 例：`基因检测_v1_2024-01-15`, `基因检测_v2_2024-06-20`

### 1.8 交互方式
- **UI形式**：不需要独立置信度面板
- **交互模式**：直接在对话中进行
- **示例**：
  ```
  系统："扫描完成！检测到50个文件，已分类如下：
  ✓ 医疗诊疗: 28个
  ✓ 营养管理: 8个
  ✓ 心理支持: 5个
  ✓ 并发症管理: 4个
  ✓ 待确认: 5个 (病历纲要.txt, 检查单_副本.pdf 等)
  
  请确认分类是否正确？需要调整哪些文件？"
  ```

---

## 二、核心技术要求：内容提取与智能分类

### 2.0 内容提取架构（必需功能）

**重要说明**：文件分类**必须基于内容提取**，而不仅仅是文件名。这是核心功能要求。

#### 2.0.1 为什么需要内容提取

**实际场景问题**：
- 患者上传的文件多为手机拍照：`IMG_0073.PNG`、`IMG_1104.JPG`
- 文件名无意义，无法通过文件名判断内容
- 扫描件、照片需要OCR识别文字
- PDF可能包含图片或文本，需要智能处理

**错误的做法**（仅基于文件名）：
```python
# ❌ 这样无法处理 IMG_0073.PNG（实际是病理报告）
if "病理" in filename:
    category = "病理报告"
```

**正确的做法**（基于内容）：
```python
# ✅ 读取文件内容，识别关键词
content = extract_content(file_path)  # OCR或文本提取
if "病理诊断" in content or "免疫组化" in content:
    category = "病理报告"
```

#### 2.0.2 内容提取模块设计

**模块1：内容提取器** (`src/file_handler/content_extractor.py`)

```python
class ContentExtractor:
    """统一的内容提取接口"""
    
    def extract(self, file_path: str) -> Dict[str, Any]:
        """
        提取文件内容
        
        Returns:
            {
                "text": "提取的文本内容",
                "metadata": {
                    "file_type": "pdf|image|word|excel",
                    "extraction_method": "ocr|text|parsing",
                    "confidence": 0.95,
                    "language": "zh"
                },
                "raw_data": {}  # 原始数据（如Excel的DataFrame）
            }
        """
        pass
    
    def extract_pdf(self, file_path: str) -> str:
        """PDF文本提取（pypdf + OCR fallback）"""
        pass
    
    def extract_image(self, file_path: str) -> str:
        """图片OCR识别（paddleOCR）"""
        pass
    
    def extract_word(self, file_path: str) -> str:
        """Word文档解析（python-docx）"""
        pass
    
    def extract_excel(self, file_path: str) -> Dict:
        """Excel数据读取（openpyxl）"""
        pass
```

**支持的文件类型**：
| 文件类型 | 提取方法 | 工具库 | 优先级 |
|---------|---------|--------|--------|
| PDF（文本） | 文本提取 | pypdf | ✅ 必需 |
| PDF（扫描件） | OCR | paddleOCR | ✅ 必需 |
| 图片（JPG/PNG/HEIC） | OCR | paddleOCR | ✅ 必需 |
| Word（.docx） | 文档解析 | python-docx | ✅ 必需 |
| Excel（.xlsx） | 数据读取 | openpyxl | ✅ 必需 |
| DICOM | 医学影像 | pydicom | ⭕ 可选 |

**模块2：内容分类器** (`src/file_handler/content_classifier.py`)

```python
class ContentClassifier:
    """基于内容的智能分类器"""
    
    def classify(self, content: str, filename: str) -> ClassificationResult:
        """
        综合内容和文件名进行分类
        
        Args:
            content: 提取的文本内容
            filename: 文件名（辅助判断）
        
        Returns:
            ClassificationResult(
                category=FileCategory.LAB_REPORTS,
                confidence=0.95,
                reasoning="检测到关键词：CA19-9、肿瘤标志物",
                keywords_found=["CA19-9", "肿瘤标志物", "检验报告"]
            )
        """
        pass
    
    def _extract_keywords(self, content: str) -> List[str]:
        """从内容中提取医疗关键词"""
        pass
    
    def _calculate_confidence(self, keywords: List[str], category: FileCategory) -> float:
        """计算分类置信度"""
        pass
```

**分类规则（基于内容关键词）**：

```python
CONTENT_CLASSIFICATION_RULES = {
    FileCategory.LAB_REPORTS: {
        "keywords": [
            "检验报告", "化验单", "血液检查", "肿瘤标志物",
            "CA19-9", "CA50", "CA125", "CEA",
            "白细胞", "血红蛋白", "血小板",
            "肝功能", "肾功能", "电解质"
        ],
        "weight": 1.0
    },
    FileCategory.IMAGING: {
        "keywords": [
            "影像报告", "CT", "MRI", "超声", "X光",
            "增强扫描", "平扫", "DICOM",
            "病灶", "肿块", "占位", "转移"
        ],
        "weight": 1.0
    },
    FileCategory.MEDICAL_RECORDS: {
        "keywords": [
            "病历", "病史", "主诉", "现病史", "既往史",
            "诊断", "医嘱", "查房记录", "出院小结"
        ],
        "weight": 0.9
    },
    # ... 其他分类
}
```

**模块3：文件类型JSON生成器**

```python
class FileTypeRecorder:
    """记录文件分类结果到JSON"""
    
    def save_classification(self, results: List[ClassificationResult]):
        """
        保存分类结果到 file_types.json
        
        格式：
        {
            "IMG_0073.PNG": {
                "category": "医疗诊疗/检查检测报告",
                "confidence": 0.95,
                "keywords_found": ["CA19-9", "肿瘤标志物"],
                "extraction_method": "ocr",
                "classified_at": "2026-01-19T15:30:00"
            },
            "病历.pdf": {
                "category": "医疗诊疗/病历",
                "confidence": 0.88,
                "keywords_found": ["主诉", "现病史"],
                "extraction_method": "text",
                "classified_at": "2026-01-19T15:30:05"
            }
        }
        """
        pass
```

#### 2.0.3 集成到现有扫描器

**更新 `scanner.py`**：

```python
class FileScanner:
    def __init__(self, base_path: str = "."):
        self.base_path = base_path
        self.content_extractor = ContentExtractor()  # 新增
        self.content_classifier = ContentClassifier()  # 新增
        self.file_type_recorder = FileTypeRecorder()  # 新增
    
    def _classify_file(self, file_path: str, file_name: str) -> Tuple[FileCategory, float]:
        """改进的分类方法：内容优先，文件名辅助"""
        
        # 1. 提取文件内容
        try:
            content_data = self.content_extractor.extract(file_path)
            content = content_data["text"]
        except Exception as e:
            print(f"⚠️  内容提取失败 {file_name}: {e}")
            # Fallback到文件名分类
            return self._classify_by_filename(file_path, file_name)
        
        # 2. 基于内容分类
        result = self.content_classifier.classify(content, file_name)
        
        # 3. 记录分类结果
        self.file_type_recorder.record(file_name, result)
        
        return (result.category, result.confidence)
```

#### 2.0.4 实现优先级

**Phase 1（必需）**：
1. ✅ 实现 `ContentExtractor` - PDF文本提取
2. ✅ 实现 `ContentExtractor` - 图片OCR（paddleOCR）
3. ✅ 实现 `ContentClassifier` - 基于关键词的分类
4. ✅ 生成 `file_types.json`

**Phase 2（必需）**：
5. ✅ 集成到 `scanner.py`
6. ✅ Word/Excel支持
7. ✅ 测试验证（使用 `/Users/qinxiaoqiang/Downloads/report_mess`）

**Phase 3（可选优化）**：
8. ⭕ LLM辅助分类（低置信度文件）
9. ⭕ DICOM支持
10. ⭕ 多语言支持

#### 2.0.5 依赖库安装

```bash
# 必需依赖
pip install pypdf python-docx openpyxl paddlepaddle paddleocr

# 可选依赖
pip install mineru pydicom pillow
```

---

## 三、完整工作流程

### 2.1 初诊流程

```
用户上传病例目录
  ↓
【第1步】文件扫描与分类
  - 扫描目录结构
  - 解析文件名、路径、内容（OCR/文本）
  - 自动分类至标准目录树：
    医疗诊疗/
    ├── 病历/
    ├── 影像/
    ├── 检查检测报告/
    └── 处方用药/
    营养管理/
    心理支持管理/
    并发症管理/
  - 对话中提示分类结果 + 待确认列表
  ↓
【用户确认】
  - 用户通过对话指定调整
  - 系统更新分类
  ↓
【第2步】信息提取与脱敏
  - 敏感字段检测（姓名、身份证号、电话、住址、详细住院号等）
  - 脱敏处理：生成patient_id，存储脱敏版本
  - 扫描医疗诊疗目录，调用3个子智能体：
    * 病情提取智能体 → 关键字段JSON
    * 病历整理智能体 → 病历结构化
    * 文件分类智能体 → 低置信度文件纠正
  - 去重处理（文件hash记录）
  - 增量识别（hash/mtime）
  - 失败记录：OCR失败、DICOM解析失败等
  ↓
【第3步】长期记忆存储
  - 调用memos MCP
  - 存储内容：病理结论、基因检测、诊断分期、版本历史
  - 主键：patient_id
  ↓
【第4步】报告生成
  a) 结构化病情报告
     - 时间线（诊断→治疗→复发节点）
     - 病情病历（历史摘要）
     - 病理与基因（特征+治疗implications）
     - 最新影像分析（增强CT/PET-CT）
       * 关键：复发/转移迹象
       * 并发症风险：胆管梗阻、肠道梗阻、门脉高压、血栓等
     - 肿瘤标志物（时间序列图表，缺失值平滑补全）
     - 并发症风险提示（预见性特征+预防原则）
  
  b) 问诊问题清单
     - 结构化列表 + 优先级 + 关注点
     - 调用echart/quickchart生成可视化
  
  c) 并发症风险预警
     - **检测项目**：
       * 胆管梗阻：胆管扩张、胆汁淤积、胆红素升高
       * 肠道梗阻：肠管扩张、粪便形成、腹胀
       * 门脉高压：脾大、腹水、静脉曲张（胃底静脉曲张）
       * 血栓：下肢肿胀、肺栓塞风险
       * 胰漏：淀粉酶升高、腹膜刺激症状
     - **预见性特征**（影像学&实验室）：
       * 胆管>3mm且无明确梗阻 → 胆管炎风险↑
       * 脾脏>4cm + 血小板<100 → 门脉高压信号
       * 术后淀粉酶升高2倍+腹痛 → 胰漏可能
     - **预防原则**：
       * 定期复查B超（3个月1次）
       * 监测肝功能（ALT/AST/TBIL）
       * 评估营养状况
     - **小红卡建议**：
       * 生成应急卡片链接(http://xhk.xiaoyibao.com.cn)
       * 包含患者基本信息、主要风险、应急联系方式
  
  d) 关键信息速览（2页纸模板）
    - 诊断/分期/治疗路径/当前状态/下一步问题
  
  e) 结构化数据表
    - JSON导出
    - 肿瘤标志物CSV/Excel时间序列
  ↓
【第5步】临床知识增强（可选，需用户授权）
  - 对话提示：
    "即将调用临床试验数据库，需要发送以下脱敏信息：
     - 分期：IIIB期
     - 基因：KRAS G12D突变
     - 病理：腺癌
    是否继续？(此操作涉及网络请求)"
  - 用户确认后：
    * 最终敏感字段检测
    * 脱敏处理
    * 调用clinical_trials API 2.0 → 搜索相关临床试验
    * 调用pubmed_llm_server（可选）→ 文献检索
  - 输出：临床方向建议 + 代表性试验概要 + 小胰宝社区引导链接
  ↓
输出完整报告包
  - 病情报告.md / .pdf
  - 问诊清单.md / .html(图表)
  - 2页速览.pdf
  - data.json (结构化数据)
  - 肿瘤标志物.csv
```

### 2.2 复诊更新流程

```
用户导入新增资料
  ↓
【增量识别】
  - 检查患者ID（基于memos记录）
  - 对比hash/mtime
  - 仅处理新增或变更文件
  ↓
【信息提取与更新】
  - 提取新增文件信息
  - 更新JSON（版本+时间戳）
  - 更新memos（新版本记录）
  ↓
【报告更新】
  - 生成增量更新报告
  - 月度摘要（如适用）
  - 总体进展分析
  ↓
输出增量报告
```

---

## 三、数据安全与隐私流程

### 3.1 敏感信息检测清单
```
高敏感：
  - 姓名、性别（可联合推断身份）
  - 身份证号、护照号
  - 电话、邮箱、微信、QQ
  - 详细住址、楼号房号
  - 详细住院号、病案号（可联合推断医院+日期）

中敏感（保存为脱敏版本）：
  - 年龄、性别（单独）
  - 就诊医院名称（可选脱敏为"医院A"）
  - 简化病例号（非详细住院号）

低敏感（可直接保存）：
  - 诊断、分期、TNM
  - 基因突变、病理结论
  - 治疗方案、用药名称
  - 检查结果（数值、影像描述）
```

### 3.2 隐私保护流程

#### 【分类阶段】
```
对话提示分类结果
└─ 系统仅提示："已识别50个医学文件，分类至对应目录"
   不涉及患者信息展示
```

#### 【提取阶段】
```
敏感字段检测 (regex + LLM)
  ↓
脱敏处理
  - 生成patient_id = hash(姓名+出生年份+就诊医院+病例号)
  - 姓名 → [患者]
  - 电话 → [已脱敏]
  - 详细住址 → [已脱敏]
  - 详细住院号 → [已脱敏]
  ↓
本地存储脱敏版本JSON
  ↓
日志记录：文件ID+分类+处理状态，不记录原始内容
```

#### 【长期记忆】
```
memos MCP存储
  - Key: patient_id
  - Value: 脱敏版本数据（病理、基因、诊断）
  - 版本记录：timestamp + 来源报告
```

#### 【对外API请求】
```
临床试验/文献检索前：
  
  1. 用户授权提示
     "即将调用外部API，数据将包括：
      - 分期信息
      - 基因突变（脱敏）
      - 病理类型（脱敏）
     是否继续？"
  
  2. 最终敏感字段检测
     检查待发送的JSON字段，确保无隐私信息
  
  3. 脱敏处理
     仅发送结构化字段：
     {
       "stage": "IIIB",
       "cancer_type": "pancreatic_cancer",
       "histology": "adenocarcinoma",
       "mutations": ["KRAS G12D", "TP53"],
       "therapy_response": "partial_response"
     }
  
  4. 发送请求
  
  5. 回显检测
     如果响应中包含患者姓名/身份等敏感信息
     → 立即停止处理
     → 用户提醒："检测到数据外漏风险，已停止处理。请联系开发者。"
     → 等待用户确认
```

---

## 四、技术栈与工具集成

### 4.0 MCP服务器配置

已配置的MCP服务器清单（mcp.json）：

| MCP服务器 | 类型 | 用途 | 配置状态 |
|-----------|------|------|--------|
| **Quickchart-MCP-Server** | SSE | 肿瘤标志物图表生成 | ✅ 已配置 |
| **metaso** | HTTP API | 知识补充搜索 | ✅ 已配置 (Bearer认证) |
| **mcp-pubmed-llm-server** | NPX命令 | PubMed文献检索 | ✅ 已配置 |
| **pubmed-data-server** | Node.js进程 | PubMed深度数据服务 | ✅ 已配置 (胰腺癌定制) |
| **memos-api-mcp** | NPX命令 | 长期记忆存储 | ✅ 已配置 (用户认证) |
| **searxng-simple-mcp** | UVX命令 | 网页搜索 | ✅ 已配置 |
| **clinical-trials** | NPX命令 | 临床试验检索 | ✅ 已配置 (xiaoyibao) |

**关键MCP服务细节**：

```json
{
  "mcpServers": {
    "Quickchart-MCP-Server": {
      "type": "sse",
      "url": "https://mcp-api.tencent-cloud.com/sse/d20f0f73a45f1bc6",
      "purpose": "图表生成：CA19-9/CA50/CA125/CA72-4折线图"
    },
    "metaso": {
      "url": "https://metaso.cn/api/mcp",
      "auth": "Bearer mk-8477E39D1CE97AAB3432EED9306E02F2",
      "purpose": "RAG搜索补充知识"
    },
    "pubmed-data-server": {
      "command": "node /Users/qinxiaoqiang/Downloads/mcp-pubmed-server-pancrpal/src/index.js",
      "env": {
        "ABSTRACT_MODE": "deep",
        "FULLTEXT_MODE": "enabled",
        "PUBMED_EMAIL": "qinxiaoqiang@gmail.com"
      },
      "purpose": "胰腺癌相关文献检索和全文获取"
    },
    "memos-api-mcp": {
      "command": "npx @memtensor/memos-api-mcp@latest",
      "env": {
        "MEMOS_API_KEY": "pg-XTF8X0lKOJVUpewkyvdL1GwR1T7MebYrgzJ3zhWo",
        "MEMOS_USER_ID": "sam.qin@xiaoyibao.com.cn"
      },
      "purpose": "患者长期记忆：病理、基因、诊断等变化小的信息"
    },
    "clinical-trials": {
      "command": "npx xiaoyibao-clinical-trials",
      "purpose": "临床试验检索（小胰宝社区API）"
    }
  }
}
```

### 4.1 文件处理工具

| 工具 | 用途 | 配置 |
|------|------|------|
| python-magic | 文件类型识别 | 本地 |
| glob | 文件模式匹配 | 本地 |
| mineru | PDF/图片OCR | 本地可选 |
| pypdf | PDF文本提取 | 本地 |
| paddleOCR | 通用OCR（中文友好） | 本地可选 |
| pydicom | DICOM解析 | 本地可选 |
| PIL/Pillow | DICOM→JPG转换 | 本地 |
| python-docx | DOC/DOCX解析 | 本地 |
| openpyxl | Excel解析 | 本地 |

### 4.2 数据存储与管理

| 工具 | 用途 | 配置 | 必需性 |
|------|------|------|--------|
| **JSON** | 本地结构化存储（主方案） | 本地文件系统 + 版本+日期 | ✅ 必需 |
| hashlib | 文件去重（hash） | 本地 | ✅ 必需 |
| memos MCP | 长期记忆存储（变化小的数据） | MCP已配置 | ✅ 必需 |
| sqlite3 | 增量识别索引 + 处理追踪（可选优化） | 自动化初始化脚本 | ⭕ 可选 |

**主方案：JSON + 版本控制**

为适配患者（非技术用户）和本地隐私优先的需求：
- 所有患者数据保存为JSON文件（本地文件系统）
- 每个JSON文件包含：版本号、时间戳、数据内容
- 支持多版本历史：`patient_master_v1_2024-01-15.json`, `patient_master_v2_2024-06-20.json`
- 增量识别：通过文件hash（md5/sha256）和修改时间（mtime）检测变化
- 数据追踪：在JSON中记录processing_log字段

**可选方案：SQLite数据库（高级用户）**

如需要性能优化和高级查询功能，可选择启用SQLite：
- 用途：快速查询、批量统计、复杂条件搜索
- 设计：6个核心表（file_index/patient_index/markers_history/processing_log/dedup_records/version_history）
- 启用方式：在config中设置 `enable_sqlite = true`，自动初始化

**SQLite初始化和自动化流程**：

```python
# init_database.py 初始化流程示例

class DatabaseInitializer:
    def __init__(self, db_path: str = "patient_case/skill.db"):
        self.db_path = db_path
        self.connection = None
    
    def initialize(self):
        """完整初始化流程"""
        # 1. 创建数据库文件和连接
        self.connection = sqlite3.connect(self.db_path)
        
        # 2. 创建所有表
        self._create_tables()
        
        # 3. 创建索引
        self._create_indexes()
        
        # 4. 初始化系统参数
        self._init_sys_params()
        
        # 5. 提交并关闭
        self.connection.commit()
        self.connection.close()
        
        return True
    
    def _create_tables(self):
        """创建6个核心表"""
        cursor = self.connection.cursor()
        
        # file_index - 文件扫描和处理记录
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS file_index (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                file_hash TEXT UNIQUE NOT NULL,
                file_path TEXT NOT NULL,
                file_size INTEGER,
                file_type TEXT,
                mtime REAL,
                status TEXT DEFAULT 'pending',  -- pending, processing, success, failed
                error_msg TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # patient_index - 患者记录索引
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS patient_index (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                patient_id TEXT UNIQUE NOT NULL,
                case_type TEXT NOT NULL,  -- pancreatic_cancer, etc
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                import_count INTEGER DEFAULT 1
            )
        ''')
        
        # markers_history - 肿瘤标志物历史追踪
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS markers_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                patient_id TEXT NOT NULL,
                marker_type TEXT NOT NULL,  -- CA19-9, CA50, CA125, CA72-4
                date DATE NOT NULL,
                value REAL,
                unit TEXT,
                source_file TEXT,
                imputed INTEGER DEFAULT 0,  -- 0=actual, 1=AI补全
                confidence TEXT,  -- high, medium, low
                recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(patient_id) REFERENCES patient_index(patient_id)
            )
        ''')
        
        # processing_log - 处理日志
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS processing_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                patient_id TEXT NOT NULL,
                import_id TEXT NOT NULL,
                step TEXT NOT NULL,  -- classification, extraction, dedup, storage, report
                status TEXT NOT NULL,  -- success, failed, skipped
                error_msg TEXT,
                duration_seconds REAL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(patient_id) REFERENCES patient_index(patient_id)
            )
        ''')
        
        # dedup_records - 文件去重记录
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS dedup_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                file_hash TEXT UNIQUE NOT NULL,
                file_count INTEGER,
                kept_file TEXT NOT NULL,
                duplicates_json TEXT,  -- JSON array of duplicate files
                recorded_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # version_history - 数据版本控制
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS version_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                patient_id TEXT NOT NULL,
                data_type TEXT NOT NULL,  -- genetics, pathology, diagnosis, markers
                version INTEGER NOT NULL,
                timestamp TIMESTAMP NOT NULL,
                source TEXT,  -- source file or report
                content_hash TEXT,  -- hash of the content
                metadata_json TEXT,  -- additional metadata
                recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(patient_id) REFERENCES patient_index(patient_id)
            )
        ''')
        
        # sys_params - 系统参数表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sys_params (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                param_key TEXT UNIQUE NOT NULL,
                param_value TEXT,
                param_type TEXT,  -- string, integer, json
                description TEXT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        self.connection.commit()
    
    def _create_indexes(self):
        """创建优化查询性能的索引"""
        cursor = self.connection.cursor()
        
        # file_index索引
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_file_hash ON file_index(file_hash)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_file_path ON file_index(file_path)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_file_status ON file_index(status)')
        
        # patient_index索引
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_patient_id ON patient_index(patient_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_case_type ON patient_index(case_type)')
        
        # markers_history索引
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_patient_marker ON markers_history(patient_id, marker_type)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_marker_date ON markers_history(date)')
        
        # processing_log索引
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_log_patient ON processing_log(patient_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_log_import ON processing_log(import_id)')
        
        self.connection.commit()
    
    def _init_sys_params(self):
        """初始化系统参数"""
        cursor = self.connection.cursor()
        
        params = [
            ('db_version', '1.0', 'string', '数据库schema版本'),
            ('db_created_at', datetime.now().isoformat(), 'string', '数据库创建时间'),
            ('last_maintenance', datetime.now().isoformat(), 'string', '最后维护时间'),
            ('enable_privacy_mode', '1', 'integer', '是否启用隐私模式'),
            ('default_patient_id_method', 'hash', 'string', '患者ID生成方法'),
        ]
        
        for param_key, param_value, param_type, description in params:
            cursor.execute('''
                INSERT OR REPLACE INTO sys_params 
                (param_key, param_value, param_type, description) 
                VALUES (?, ?, ?, ?)
            ''', (param_key, param_value, param_type, description))
        
        self.connection.commit()

# 自动化连接管理 - db_manager.py

class DatabaseManager:
    """单例模式的数据库连接管理器"""
    _instance = None
    _connection = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DatabaseManager, cls).__new__(cls)
        return cls._instance
    
    def __init__(self, db_path: str = "patient_case/skill.db"):
        self.db_path = db_path
        self._ensure_initialized()
    
    def _ensure_initialized(self):
        """确保数据库已初始化"""
        if not os.path.exists(self.db_path):
            initializer = DatabaseInitializer(self.db_path)
            initializer.initialize()
    
    def get_connection(self):
        """获取数据库连接（自动重连）"""
        try:
            if self._connection is None:
                self._connection = sqlite3.connect(self.db_path)
                self._connection.row_factory = sqlite3.Row
            # 测试连接
            self._connection.execute("SELECT 1")
            return self._connection
        except sqlite3.OperationalError:
            # 连接失败，重新连接
            self._connection = sqlite3.connect(self.db_path)
            self._connection.row_factory = sqlite3.Row
            return self._connection
    
    def execute(self, sql: str, params: tuple = None):
        """执行查询"""
        cursor = self.get_connection().cursor()
        if params:
            return cursor.execute(sql, params)
        else:
            return cursor.execute(sql)
    
    def commit(self):
        """提交事务"""
        if self._connection:
            self._connection.commit()
    
    def rollback(self):
        """回滚事务"""
        if self._connection:
            self._connection.rollback()
    
    def close(self):
        """关闭连接"""
        if self._connection:
            self._connection.close()
            self._connection = None

# 自动化CRUD操作 - db_operations.py

class FileIndexOps:
    def __init__(self, db: DatabaseManager):
        self.db = db
    
    def insert_file(self, file_hash, file_path, file_size, mtime):
        """插入文件记录"""
        self.db.execute('''
            INSERT INTO file_index (file_hash, file_path, file_size, mtime, status)
            VALUES (?, ?, ?, ?, 'pending')
        ''', (file_hash, file_path, file_size, mtime))
        self.db.commit()
    
    def query_by_hash(self, file_hash):
        """按hash查询文件"""
        cursor = self.db.execute(
            'SELECT * FROM file_index WHERE file_hash = ?',
            (file_hash,)
        )
        return cursor.fetchone()
    
    def update_status(self, file_hash, status, error_msg=None):
        """更新文件处理状态"""
        self.db.execute('''
            UPDATE file_index 
            SET status = ?, error_msg = ?, updated_at = CURRENT_TIMESTAMP
            WHERE file_hash = ?
        ''', (status, error_msg, file_hash))
        self.db.commit()
    
    def get_pending_files(self):
        """获取待处理文件列表"""
        cursor = self.db.execute(
            'SELECT * FROM file_index WHERE status = "pending" ORDER BY created_at'
        )
        return cursor.fetchall()

class MarkerOps:
    def __init__(self, db: DatabaseManager):
        self.db = db
    
    def insert_marker(self, patient_id, marker_type, date, value, source_file, imputed=0, confidence='high'):
        """插入标志物记录"""
        self.db.execute('''
            INSERT INTO markers_history 
            (patient_id, marker_type, date, value, source_file, imputed, confidence)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (patient_id, marker_type, date, value, source_file, imputed, confidence))
        self.db.commit()
    
    def get_marker_trend(self, patient_id, marker_type):
        """获取标志物趋势数据"""
        cursor = self.db.execute('''
            SELECT date, value, imputed FROM markers_history 
            WHERE patient_id = ? AND marker_type = ?
            ORDER BY date
        ''', (patient_id, marker_type))
        return cursor.fetchall()
```

**初始化调用方式**：
```python
# 在Skill启动时调用一次
from src.database.init_database import DatabaseInitializer
from src.database.db_manager import DatabaseManager

# 初始化数据库
initializer = DatabaseInitializer()
initializer.initialize()

# 获取连接管理器
db_manager = DatabaseManager()

# 使用自动化操作
from src.database.db_operations import FileIndexOps, MarkerOps
file_ops = FileIndexOps(db_manager)
marker_ops = MarkerOps(db_manager)
```

### 4.3 AI与智能体

| 工具 | 用途 | 配置 |
|------|------|------|
| Claude API | 子智能体调用 | 现有API |
| 病情提取智能体提示词 | 关键信息提取 | 自定义 |
| 病历整理智能体提示词 | 病历模版化 | 自定义 |
| 文件分类智能体提示词 | 低置信度纠正 | 自定义 |

### 4.3.1 肿瘤标志物图表生成指南

**使用工具选择**

方案1：**quickchart-mcp** (推荐)
- 集成度高，直接生成图片
- 支持Chart.js语法，丰富的配置选项
- 输出：PNG/SVG图片，可直接嵌入报告

方案2：**echart代码包** (高自定义度)
- JavaScript/Python库，完全自定义配置
- 生成HTML可视化，支持交互
- 输出：HTML文件，支持Tooltip、缩放、导出

**推荐使用quickchart-mcp生成CA19-9/CA125/CEA折线图**

**基本配置参数（包含CA19-9、CA50、CA125、CA72-4）**
```javascript
{
  type: "line",
  data: {
    labels: ["术前", "C1", "C2", ..., "C12", "结疗1", "结疗2"],
    datasets: [
      // CA19-9 - 红色实线 + 圆点
      {
        label: "CA19-9 (U/mL)",
        data: [245.5, 95.2, 67.8, ..., 13, 12],
        borderColor: "#E54D42",
        backgroundColor: "rgba(229, 77, 66, 0.1)",
        fill: false,
        tension: 0.4,
        pointRadius: 5,
        pointStyle: "circle",
        pointBackgroundColor: "#E54D42",
        borderWidth: 2
      },
      // CA50 - 深红色实线 + 方形
      {
        label: "CA50 (U/mL)",
        data: [128.0, 65.2, 48.5, ..., 8.5, 7.2],
        borderColor: "#B71D3A",
        backgroundColor: "rgba(183, 29, 58, 0.05)",
        fill: false,
        tension: 0.4,
        pointRadius: 5,
        pointStyle: "rect",
        pointBackgroundColor: "#B71D3A",
        borderWidth: 2
      },
      // CA125 - 绿色实线 + 圆点
      {
        label: "CA125 (U/mL)",
        data: [35.8, 45.3, 38.9, ..., 17.4, 16.2],
        borderColor: "#39B54A",
        backgroundColor: "rgba(57, 181, 74, 0.1)",
        fill: false,
        tension: 0.4,
        pointRadius: 5,
        pointStyle: "circle",
        pointBackgroundColor: "#39B54A",
        borderWidth: 2
      },
      // CA72-4 - 橙色实线 + 三角形
      {
        label: "CA72-4 (U/mL)",
        data: [5.6, 7.2, 6.5, ..., 5.1, 5.0],
        borderColor: "#FF8811",
        backgroundColor: "rgba(255, 136, 17, 0.05)",
        fill: false,
        tension: 0.4,
        pointRadius: 5,
        pointStyle: "triangle",
        pointBackgroundColor: "#FF8811",
        borderWidth: 2
      },
      // 参考线 - CA19-9上限43
      {
        label: "CA19-9参考上限(43)",
        data: [43, 43, 43, ...],
        borderColor: "#E54D42",
        borderDash: [5, 5],
        fill: false,
        pointRadius: 0,
        borderWidth: 1,
        spanGaps: true
      },
      // 参考线 - CA50上限20
      {
        label: "CA50参考上限(20)",
        data: [20, 20, 20, ...],
        borderColor: "#B71D3A",
        borderDash: [5, 5],
        fill: false,
        pointRadius: 0,
        borderWidth: 1,
        spanGaps: true
      },
      // 参考线 - CA125上限35
      {
        label: "CA125参考上限(35)",
        data: [35, 35, 35, ...],
        borderColor: "#39B54A",
        borderDash: [5, 5],
        fill: false,
        pointRadius: 0,
        borderWidth: 1,
        spanGaps: true
      },
      // 参考线 - CA72-4上限10
      {
        label: "CA72-4参考上限(10)",
        data: [10, 10, 10, ...],
        borderColor: "#FF8811",
        borderDash: [5, 5],
        fill: false,
        pointRadius: 0,
        borderWidth: 1,
        spanGaps: true
      }
    ]
  },
  options: {
    responsive: true,
    maintainAspectRatio: true,
    interaction: {
      mode: "index",
      intersect: false
    },
    plugins: {
      legend: {
        position: "bottom",
        labels: {
          usePointStyle: true,
          padding: 15,
          font: { size: 11 },
          boxWidth: 8
        }
      },
      title: {
        display: true,
        text: "肿瘤标志物趋势图（CA19-9、CA50、CA125、CA72-4）",
        font: { size: 16, weight: "bold" }
      },
      tooltip: {
        callbacks: {
          label: function(context) {
            let label = context.dataset.label || "";
            if (label) {
              label += ": " + context.parsed.y.toFixed(2);
              // 添加参考值判断
              if (label.includes("CA19-9") && context.parsed.y > 43) {
                label += " 🔴 高于参考";
              }
              if (label.includes("CA50") && context.parsed.y > 20) {
                label += " 🔴 高于参考";
              }
              if (label.includes("CA125") && context.parsed.y > 35) {
                label += " 🔴 高于参考";
              }
              if (label.includes("CA72-4") && context.parsed.y > 10) {
                label += " 🔴 高于参考";
              }
            }
            return label;
          }
        }
      }
    },
    scales: {
      y: {
        beginAtZero: true,
        max: 100,  // 动态调整为最大值+20%
        ticks: { stepSize: 20 },
        grid: { color: "rgba(0, 0, 0, 0.1)" },
        title: {
          display: true,
          text: "浓度 (U/mL)"
        }
      },
      x: {
        grid: { color: "rgba(0, 0, 0, 0.1)" }
      }
    }
  }
}
```

**多标志物同趋势分析逻辑**
```python
def analyze_trend_concordance(markers_data):
    """
    分析多个标志物的同趋势变化
    
    返回:
      - concordance_type: "progressive"(进展) / "response"(缓解) / "mixed"(混合) / "single"(单一异常)
      - risk_level: "🔴 high"(高危) / "🟡 medium"(中等) / "🟢 low"(低危)
      - analysis: 临床判读文字说明
    """
    # 计算各标志物趋势方向
    ca19_9_trend = calculate_trend(markers_data["CA19-9"])
    ca50_trend = calculate_trend(markers_data["CA50"])
    ca125_trend = calculate_trend(markers_data["CA125"])
    ca72_4_trend = calculate_trend(markers_data["CA72-4"])
    
    # 统计同向上升/下降
    upward_count = sum(1 for t in [ca19_9_trend, ca50_trend, ca125_trend, ca72_4_trend] if t > 0)
    downward_count = sum(1 for t in [ca19_9_trend, ca50_trend, ca125_trend, ca72_4_trend] if t < 0)
    
    # 判断
    if upward_count >= 2:
        return {
            "concordance": "progressive",
            "risk": "🔴 high",
            "analysis": f"{upward_count}个标志物同升高，强烈提示肿瘤进展"
        }
    elif downward_count >= 2:
        return {
            "concordance": "response",
            "risk": "🟢 low",
            "analysis": f"{downward_count}个标志物同下降，治疗有效"
        }
    elif ca19_9_trend > 0 and ca50_trend == 0 and ca125_trend == 0:
        return {
            "concordance": "single",
            "risk": "🟡 medium",
            "analysis": "仅CA19-9升高，CA50正常，建议除外炎症（胰炎/胆囊炎），观察CA50变化"
        }
    else:
        return {
            "concordance": "mixed",
            "risk": "🟡 medium",
            "analysis": "标志物变化不一致，需结合影像学评估"
        }
```

**缺失值处理**
- 用平滑均值算法补全
- 标注在图表上：`[补全值] ⚠️ AI生成，请用户注意`
- 在数据源JSON中记录补全信息（method, source, imputed=true）
- 在CSV中单独标注补全值所在行

**CSV/Excel导出格式**
```
日期,治疗周期,CA19-9(U/mL),CA50(U/mL),CA125(U/mL),CA72-4(U/mL),多标志物同趋势,临床判断,备注
2023-01-10,术前,245.5,128.0,35.8,5.6,全部升高,🔴 肿瘤进展,初诊检查
2023-02-15,C1,95.2,65.2,45.3,7.2,CA19-9↓CA50↓CA125↑,🟡 混合,化疗响应初期
2023-03-15,C2,67.8,48.5,38.9,6.5,全部下降,🟢 缓解,化疗有效
...
2023-04-15,C3,62.3,45.1,35.2,6.1,全部下降,🟢 缓解,[补全值]AI平滑填充
...
2024-06-15,复查,13.0,8.5,17.4,5.1,全部正常,🟢 缓解,缓解评估
```

### 4.4 图表与报告生成

| 工具 | 用途 | 配置 |
|------|------|------|
| **quickchart-mcp** | 肿瘤标志物时间序列图 | ✅ MCP已配置 (SSE) |
| echart (JavaScript) | 问诊清单可视化 | 代码包本地 |
| matplotlib/plotly | 本地补充图表生成 | 本地 |
| reportlab | PDF报告生成 | 本地 |
| weasyprint | HTML→PDF转换 | 本地 |

**Quickchart集成说明**：
- 用于生成四标志物趋势图（CA19-9/CA50/CA125/CA72-4）
- 已在mcp.json配置，URL: `https://mcp-api.tencent-cloud.com/sse/d20f0f73a45f1bc6`
- 调用方式：通过MCP协议发送Chart.js配置，返回PNG图片
- 输出：直接保存至 `questions/images/肿瘤标志物趋势图_[日期].png`

### 4.5 临床知识工具

| 工具 | 用途 | 配置 | 说明 |
|------|------|------|------|
| **ClinicalTrials.gov API v2** | 官方临床试验数据库 | ✅ 已配置 | REST API，支持基因、分期、条件查询 |
| **clinical-trials MCP** | 临床试验检索包装 | ✅ 已配置 | xiaoyibao API，基于官方API包装 |
| **pubmed-data-server MCP** | PubMed全文检索 | ✅ 已配置 | 胰腺癌定制，支持深度摘要+全文 |
| **mcp-pubmed-llm-server** | PubMed LLM处理 | ✅ 已配置 | 文献智能总结 |
| **metaso MCP** | 一般知识搜索 | ✅ 已配置 | RAG方式，补充临床常识 |
| **searxng-simple-mcp** | 网页搜索 | ✅ 已配置 | 最新指南和资讯 |

**ClinicalTrials.gov REST API v2 说明**：

```bash
# API Endpoint
https://clinicaltrials.gov/api/v2/studies

# 查询示例：搜索KRAS G12D相关临床试验
curl -X GET "https://clinicaltrials.gov/api/v2/studies?query.cond=KRAS+G12D&pageSize=10" \
  -H "accept: application/json"

# 查询示例：搜索胰腺癌 + KRAS + III期试验
curl -X GET "https://clinicaltrials.gov/api/v2/studies?query.cond=pancreatic+cancer&query.term=KRAS&filter.phase=PHASE3&pageSize=20" \
  -H "accept: application/json"
```

**查询参数说明**：
- `query.cond`：条件/疾病（如"KRAS G12D", "pancreatic cancer"）
- `query.term`：一般搜索词（如"KRAS", "immunotherapy"）
- `filter.phase`：试验阶段（PHASE1, PHASE2, PHASE3, PHASE4, EARLY_PHASE1, NOT_APPLICABLE）
- `filter.status`：招募状态（RECRUITING, ENROLLING_BY_INVITATION, ACTIVE_NOT_RECRUITING, COMPLETED）
- `filter.locn`：地点/国家（如"China", "United States"）
- `pageSize`：每页返回数量（1-100，默认10）
- `pageNumber`：页码（用于分页）

**响应字段**：
```json
{
  "studies": [
    {
      "protocolSection": {
        "identificationModule": {
          "nctId": "NCT04123456",
          "officialTitle": "A Study of XXX in KRAS Mutant Pancreatic Cancer",
          "briefTitle": "KRAS G12D Study"
        },
        "statusModule": {
          "recordVerificationDate": "2024-01-15",
          "overallStatus": "RECRUITING"
        },
        "designModule": {
          "studyType": "INTERVENTIONAL",
          "phases": ["PHASE2", "PHASE3"]
        },
        "conditionsModule": {
          "conditions": ["Pancreatic Cancer"]
        },
        "interventionsModule": {
          "interventions": [
            {
              "type": "DRUG",
              "name": "KRAS Inhibitor",
              "description": "Direct KRAS G12D inhibitor"
            }
          ]
        },
        "eligibilityModule": {
          "eligibilityCriteria": "Inclusion: KRAS G12D mutation...",
          "healthyVolunteers": false,
          "sex": "ALL",
          "minimumAge": "18 Years",
          "maximumAge": "75 Years"
        }
      }
    }
  ],
  "totalCount": 45,
  "pageInfo": {
    "pageNumber": 1,
    "pageSize": 10,
    "hasNextPage": true
  }
}
```

**临床知识增强流程（优化版）**：

**第1步：基因和病理特征自动提取**
```
患者基因检测报告（原始）
  ↓
自动化提取器：
  ├─ 基因突变名称：KRAS G12D
  ├─ 突变分类：驱动基因、原癌基因激活
  ├─ 临床意义：主要治疗靶点、预后指示
  ├─ 治疗方向：靶向治疗（KRAS抑制剂）、化疗
  └─ 相关文献和指南：最新治疗指南
  ↓
结构化特征JSON
```

**第2步：分别查询 + 匹配组合**
```
基因特征查询：
  KRAS G12D → ClinicalTrials API
           → 返回所有KRAS G12D相关试验
           → 按治疗方向分类

病理特征查询：
  腺癌 + Grade II → ClinicalTrials API
                  → 返回相应分化程度的试验
                  → 按化疗敏感性分类

匹配组合：
  (KRAS G12D试验) ∩ (腺癌试验) ∩ (中国试验)
  ↓
  最终推荐的临床试验清单
```

**第3步：生成科普型临床增强报告**

1. 调用 **基因科普模块**
   - 基因定义：简单介绍KRAS基因功能
   - 突变意义：G12D突变对患者意味着什么
   - 治疗指向：该突变可以怎样被治疗
   - 预后含义：对患者预后的影响

2. 调用 **病理科普模块**
   - 病理类型：腺癌的临床特征
   - 分化程度：Grade II的预后意义
   - 治疗敏感性：与化疗响应的关系

3. 调用 **ClinicalTrials.gov API** (优化查询)
   - 基因特征查询：KRAS G12D相关试验
   - 病理特征查询：腺癌相关试验
   - 返回：匹配的临床试验列表

4. 调用 **pubmed-data-server** 获取最新文献
   - 搜索：KRAS G12D + 胰腺癌腺癌 + 新治疗
   - 返回：摘要 + PMID + 全文链接

5. 调用 **metaso** 补充背景知识
   - 解释基因和病理的临床意义
   - 说明各试验的适应症和优劣

6. **生成科普型临床增强报告**
   - 包含：
     * 基因科普部分（患者易懂）
       - "KRAS是什么基因？"
       - "G12D是什么突变？对治疗有什么影响？"
       - "相关治疗方向有哪些？"
     * 病理科普部分
       - "腺癌意味着什么？"
       - "Grade II预后如何？"
     * 相关临床试验列表（按优先级排序）
     * 最新文献和治疗指南
     * 小胰宝公众号和临床微信群链接
     * 小胰宝助手和小绿卡工具链接

### 4.6 隐私保护工具

| 工具 | 用途 | 配置 |
|------|------|------|
| re (正则) | 敏感字段检测 | 本地 |
| LLM检测 | 上下文敏感信息 | Claude API |
| hashlib | patient_id生成 | 本地 |

---

## 五、数据结构设计

### 5.1 患者主JSON (`patient_master.json`)

```json
{
  "patient_id": "hash_xxx",
  "metadata": {
    "created_at": "2024-01-15T10:30:00Z",
    "last_updated": "2024-06-20T14:45:00Z",
    "import_count": 3,
    "case_type": "pancreatic_cancer"
  },
  "basic_info": {
    "age": 58,
    "gender": "M",
    "primary_diagnosis": "胰腺癌",
    "diagnosis_date": "2023-01-15"
  },
  "pathology": {
    "histology": "腺癌",
    "differentiation": "中分化",
    "special_markers": {
      "claudin18": "positive",
      "HER2": "negative"
    },
    "report_date": "2023-01-20",
    "confidence": "high",
    "version_history": [
      {
        "version": 1,
        "timestamp": "2024-01-15",
        "source_file": "病理报告_2023-01-20.pdf"
      }
    ]
  },
  "genetic_testing": {
    "mutations": ["KRAS G12D", "TP53"],
    "test_date": "2023-02-01",
    "test_method": "NGS",
    "version_history": [...]
  },
  "staging": {
    "TNM": "T3N1M0",
    "clinical_stage": "IIIB",
    "date": "2023-01-15"
  },
  "treatments": [
    {
      "type": "chemotherapy",
      "regimen": "gemcitabine+cisplatin",
      "start_date": "2023-02-15",
      "end_date": "2023-08-15",
      "cycles": 6,
      "response": "partial_response"
    },
    {
      "type": "surgery",
      "procedure": "pancreaticoduodenectomy",
      "date": "2023-09-10",
      "notes": "R0 resection"
    }
  ],
  "imaging_reports": [
    {
      "date": "2024-06-15",
      "modality": "enhanced_CT",
      "phases": ["arterial", "portal_venous", "delayed"],
      "key_findings": "无明显转移灶，胰体残余无明显增大",
      "file_references": ["imaging/CT_2024-06-15_*.jpg"]
    }
  ],
  "tumor_markers": [
    {
      "marker": "CA19-9",
      "unit": "U/mL",
      "reference_value": "< 43",
      "measurements": [
        {
          "date": "2023-01-10",
          "value": 245.5
        },
        {
          "date": "2023-02-15",
          "value": 95.2
        }
      ]
    }
  ],
  "complications": [
    {
      "type": "bile_duct_dilation",
      "status": "resolved",
      "notes": "术后缓解"
    }
  ],
  "nutrition_management": {
    "weight_trend": "下降3kg（3个月）",
    "notes": "建议营养干预"
  },
  "psychological_support": {
    "status": "evaluated",
    "last_assessment": "2024-06-01"
  },
  "file_processing": {
    "total_files": 50,
    "processed_files": 48,
    "failed_files": 2,
    "deduplication_records": [
      {
        "file_hash": "abc123def456",
        "count": 2,
        "kept": "file_v1.pdf",
        "duplicates": ["file_副本.pdf"]
      }
    ]
  }
}
```

### 5.2 肿瘤标志物JSON (`tumor_markers_detail.json`)

```json
{
  "patient_id": "hash_xxx",
  "markers": {
    "CA19-9": {
      "unit": "U/mL",
      "reference_value": "< 43",
      "measurements": [
        {"date": "2023-01-10", "value": 245.5, "source": "初诊检查"},
        {"date": "2023-02-15", "value": 95.2, "source": "C1化疗后"},
        {"date": "2023-03-15", "value": 67.8, "source": "C2化疗后"},
        {"date": "2024-06-15", "value": 38.5, "source": "复查"}
      ],
      "imputed_values": [
        {
          "date": "2023-04-15",
          "original_value": null,
          "imputed_value": 62.3,
          "method": "smooth_interpolation",
          "note": "**AI生成的补全值，请用户注意**"
        }
      ],
      "trend": "declining",
      "current_status": "normal"
    },
    "CA125": {...},
    "CEA": {...}
  }
}
```

### 5.3 问诊清单JSON (`consultation_questions.json`)

```json
{
  "patient_id": "hash_xxx",
  "generated_date": "2024-06-20",
  "questions": [
    {
      "priority": "high",
      "category": "treatment_plan",
      "question": "根据最新CA19-9(38.5 U/mL)和影像学变化，是否需要调整后续治疗方案？",
      "context": "对比上次检查(45 U/mL)，下降14%。影像学无新发转移灶。",
      "focus_points": [
        "对比基线CA19-9(245.5)，下降84%，说明化疗有效",
        "影像无进展，是否考虑maintenance治疗？",
        "下一步监测策略"
      ]
    },
    {
      "priority": "medium",
      "category": "nutrition",
      "question": "患者体重下降3kg（3个月），是否需要营养干预？",
      "context": "最近3个月体重趋势下降",
      "focus_points": [
        "营养补充建议",
        "肠内营养vs肠外营养",
        "定期复查营养指标"
      ]
    },
    {
      "priority": "medium",
      "category": "complications",
      "question": "术后是否存在胆管梗阻、肠道梗阻等并发症风险？",
      "context": "术后3个月，最新影像未见明显并发症迹象",
      "focus_points": [
        "长期胆管支架管理策略",
        "门脉高压预防措施",
        "定期复查B超、肝功能"
      ]
    }
  ]
}
```

### 5.4 处理日志JSON (`processing_log.json`)

```json
{
  "patient_id": "hash_xxx",
  "imports": [
    {
      "import_id": "import_001",
      "timestamp": "2024-01-15T10:30:00Z",
      "file_count": 50,
      "files_processed": 48,
      "files_failed": 2,
      "failed_files": [
        {
          "filename": "DICOM_series_001",
          "reason": "DICOM parse error",
          "retry_available": true
        }
      ],
      "classification_results": {
        "medical_diagnosis": 28,
        "nutrition_management": 8,
        "psychological_support": 5,
        "complication_management": 4,
        "unclassified": 5
      },
      "deduplication": {
        "duplicates_found": 2,
        "duplicates_removed": 2
      }
    }
  ]
}
```

---

## 六、目录树结构（最终）

基于病例模板标准目录树结构：

```
patient_case/
│
├── _metadata/                          # 系统元数据（自动生成）
│   ├── patient_master.json             # 患者主数据
│   ├── processing_log.json             # 处理日志
│   ├── extraction_log.json             # 文件hash + 去重记录
│   └── processing_status.json          # 增量更新标记
│
├── _reports/                           # AI生成的输出报告
│   ├── disease_report_comprehensive_2024-06-20.md
│   ├── disease_report_comprehensive_2024-06-20.pdf
│   ├── consultation_questions_2024-06-20.html    # 问诊清单（含echart可视化）
│   ├── key_points_summary_2024-06-20.pdf         # 2页速览
│   ├── tumor_markers_2024-06-20.csv              # 肿瘤标志物表
│   └── tumor_markers_trend_2024-06-20.html       # 趋势图（quickchart）
│
├── 00-项目主页/                        # 项目入口，可放置整体描述
│
├── 02-治疗时间表/                      # 治疗时间线总表
│
├── genetics/                           # 遗传学 & 分子检测
│   ├── 基因检测报告_NGS_2023-02-01.pdf
│   ├── KRAS_TP53_mutations.json        # 提取的基因数据JSON
│   └── 基因检测_结构化数据.json
│
├── imaging/                            # 影像检查
│   ├── CT_2024-06-15_arterial.jpg
│   ├── CT_2024-06-15_portal_venous.jpg
│   ├── CT_2024-06-15_delayed.jpg
│   ├── CT_2024-06-15_原始报告.pdf
│   ├── PET-CT_2024-03-27/
│   │   ├── PET-CT_arterial.jpg
│   │   ├── PET-CT_portal_venous.jpg
│   │   ├── PET-CT_delayed.jpg
│   │   └── PET-CT_原始报告.pdf
│   └── 影像_结构化数据.json
│
├── labs/                               # 实验室检查 & 血液生化
│   ├── images/                         # 检查单的图片/扫描件
│   │   ├── 血常规_2024-06-15.jpg
│   │   ├── 肿瘤标志物_2024-06-15.jpg
│   │   └── 肝肾生化_2024-06-15.jpg
│   │
│   ├── 便常规/
│   │   └── 便常规_2024-06-15.pdf
│   │
│   ├── 凝血功能/
│   │   └── 凝血功能_2024-06-15.pdf
│   │
│   ├── 尿常规/
│   │   └── 尿常规_2024-06-15.pdf
│   │
│   ├── 心肌损伤标志物/
│   │   └── 心肌损伤标志物_2024-06-15.pdf
│   │
│   ├── 维生素B12叶酸/
│   │   └── 维生素B12叶酸_2024-06-15.pdf
│   │
│   ├── 肝肾生化/
│   │   ├── 肝肾生化_2024-06-15.xlsx
│   │   └── 肝肾生化_2024-06-15.pdf
│   │
│   ├── 肿瘤标志物/
│   │   ├── 肿瘤标志物_2024-06-15.xlsx
│   │   ├── 肿瘤标志物_2024-06-15.pdf
│   │   └── 肿瘤标志物_结构化数据.json
│   │
│   ├── 血常规/
│   │   ├── 血常规_2024-06-15.xlsx
│   │   └── 血常规_2024-06-15.pdf
│   │
│   ├── 铁三项/
│   │   └── 铁三项_2024-06-15.pdf
│   │
│   └── labs_综合_结构化数据.json      # 所有检查的汇总JSON
│
├── pathology/                          # 病理
│   ├── 病理报告_2023-01-20.pdf
│   ├── 病理报告_扫描件.jpg
│   └── 病理_结构化数据.json
│
├── questions/                          # 问题/咨询 & AI生成内容
│   ├── images/
│   │   ├── 2026-01-18-影像科-病情介绍.jpg
│   │   └── 肿瘤标志物趋势图.png        # 生成的趋势图存放处
│   │
│   ├── 患者问诊清单.md
│   ├── 医学问题汇总.md
│   └── AI生成的咨询建议.md
│
├── records/                            # 各类医疗记录
│   ├── 初诊记录_2023-01-15.pdf
│   ├── 住院记录_2023-09-01.pdf
│   ├── 出院小结_2023-09-15.pdf
│   ├── 门诊随访记录_2024-06-15.pdf
│   └── records_结构化数据.json
│
├── scripts/                            # 辅助脚本/工具
│   ├── 营养评估脚本.py
│   ├── 风险预警规则.json
│   └── README.md
│
├── tasks/                              # 待办任务/后续建议
│   ├── 患者后续治疗计划.md
│   ├── 复查计划_按月.md
│   └── 临床试验推荐.md
│
├── treatment-history/                  # 治疗史
│   ├── 化疗/
│   │   ├── 化疗方案_gemcitabine+cisplatin.pdf
│   │   ├── C1_2023-02-15.pdf
│   │   ├── C2_2023-03-15.pdf
│   │   └── 化疗_结构化数据.json
│   │
│   ├── 手术/
│   │   ├── 手术记录_pancreaticoduodenectomy_2023-09-10.pdf
│   │   ├── 术前评估_2023-09-01.pdf
│   │   ├── 术后病理报告_2023-09-15.pdf
│   │   └── 手术_结构化数据.json
│   │
│   ├── 放疗/
│   │   ├── 放疗计划_2024-01-15.pdf
│   │   └── 放疗_结构化数据.json
│   │
│   ├── 靶向治疗/
│   │   └── 靶向治疗_结构化数据.json
│   │
│   ├── 免疫治疗/
│   │   └── 免疫治疗_结构化数据.json
│   │
│   └── treatment-history_综合.json    # 所有治疗汇总
│
├── trends/                             # 趋势分析 & 进度指标
│   ├── 00-项目主页/                    # 项目整体概览
│   │   └── 患者概览_2024-06-20.md
│   │
│   ├── 02-治疗时间表/                  # 治疗事件时间轴
│   │   └── 治疗时间表.csv
│   │
│   └── 肿瘤标志物趋势/
│       ├── CA19-9趋势.csv
│       ├── CA125趋势.csv
│       ├── CEA趋势.csv
│       └── trends_综合分析.json
│
└── 营养与心理支持/                     # 营养管理 & 心理支持
    ├── 营养评估记录_2024-06-01.pdf
    ├── 营养干预建议.md
    ├── 营养_结构化数据.json
    │
    ├── 心理评估记录_2024-06-01.pdf
    ├── 心理干预建议.md
    └── 心理_结构化数据.json
```

### 关键说明：

1. **顶级目录分类**
   - `genetics/` - 基因和分子生物学
   - `imaging/` - 影像检查
   - `labs/` - 实验室检查（细分11个检查类型）
   - `pathology/` - 病理
   - `questions/` - 问题/咨询与AI生成内容
   - `records/` - 医疗记录
   - `scripts/` - 辅助脚本
   - `tasks/` - 后续任务/建议
   - `treatment-history/` - 治疗史（分手术/化疗/放疗/靶向/免疫）
   - `trends/` - 趋势分析
   - `营养与心理支持/` - 营养和心理支持

2. **labs细分检查项目**（必须按此分类）
   - 便常规、凝血功能、尿常规、心肌损伤标志物
   - 维生素B12叶酸、肝肾生化、肿瘤标志物
   - 血常规、铁三项

3. **自动生成的JSON文件**
   - 每个一级目录对应一个`_结构化数据.json`
   - `patient_master.json` 在`_metadata/`中
   - 肿瘤标志物趋势数据存在`trends/肿瘤标志物趋势/`

4. **AI生成报告位置**
   - 存放在`_reports/`目录
   - 图表存放在`questions/images/`

---

## 七、Skill框架结构

```
skill-report-genie/
├── SKILL.md                            # Skill定义（自动生成）
├── DEVELOPMENT_PLAN.md                 # 本文档
│
├── src/
│   ├── core/
│   │   ├── __init__.py
│   │   ├── file_scanner.py             # 文件扫描+自动分类
│   │   ├── info_extractor.py           # 信息提取主流程
│   │   ├── data_manager.py             # JSON管理+memos集成
│   │   ├── report_generator.py         # 报告生成
│   │   └── clinical_enhancer.py        # 临床知识增强
│   │
│   ├── database/
│   │   ├── __init__.py
│   │   ├── init_database.py            # SQLite自动化初始化
│   │   ├── db_manager.py               # 数据库连接和事务管理
│   │   ├── db_operations.py            # 自动化CRUD操作
│   │   ├── db_schema.sql               # 数据库schema定义
│   │   └── migrations/                 # 数据库迁移脚本（可选）
│   │
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── classifier_agent.py         # 文件分类智能体
│   │   ├── extraction_agent.py         # 病情提取智能体
│   │   └── record_agent.py             # 病历整理智能体
│   │
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── ocr_handler.py              # OCR处理
│   │   ├── dicom_converter.py          # DICOM→JPG转换
│   │   ├── privacy_guard.py            # 敏感信息脱敏
│   │   ├── dedup.py                    # 文件去重（hash）
│   │   ├── text_processor.py           # 文本处理
│   │   └── chart_generator.py          # 图表生成
│   │
│   ├── templates/
│   │   ├── disease_report_template.md
│   │   ├── consultation_questions_template.html
│   │   ├── key_points_template.md
│   │   ├── 病历模版.md
│   │   └── 病例模板_打印版.md
│   │
│   ├── prompts/
│   │   ├── classifier_system_prompt.md
│   │   ├── extraction_system_prompt.md
│   │   ├── record_system_prompt.md
│   │   └── privacy_check_prompt.md
│   │
│   └── config/
│       ├── default_config.yaml
│       ├── mcp_config.yaml
│       └── sensitive_keywords.json
│
├── tests/
│   ├── __init__.py
│   ├── test_file_scanner.py
│   ├── test_info_extractor.py
│   ├── test_privacy_guard.py
│   ├── test_data_manager.py
│   └── test_integration.py
│
├── docs/
│   ├── API.md
│   ├── TROUBLESHOOTING.md
│   └── EXAMPLES.md
│
├── requirements.txt
├── setup.py
├── README.md
└── .gitignore
```

---

## 八、实现路线图

### Phase 1: 基础框架（Week 1）
- [ ] 使用building-skills创建Skill框架
- [ ] 设置项目结构和dependencies
- [ ] 实现文件扫描模块（file_scanner.py）
- [ ] 实现隐私保护模块（privacy_guard.py）

### Phase 2: 核心提取与可选数据库（Week 2）
- [ ] 实现3个子智能体（提示词 + agent代码）
- [ ] 实现信息提取主流程（info_extractor.py）
- [ ] **实现JSON数据管理**（data_manager.py - 主方案）
  - [ ] JSON文件读写（patient_master.json、markers_history.json等）
  - [ ] 版本控制（v1、v2、v3等）
  - [ ] 时间戳管理（日期后缀）
  - [ ] 增量识别（hash+mtime）
  - [ ] 版本历史追踪
- [ ] 实现文件去重（dedup.py）
  - [ ] hash计算和比对
  - [ ] 去重记录保存（在JSON中）
- [ ] **可选：SQLite自动化部署**（enable_sqlite=true时）
  - [ ] 编写init_database.py
    * 创建6个核心表（file_index/patient_index/markers_history/processing_log/dedup_records/version_history）
    * 创建索引（patient_id/file_hash/marker_type等）
    * 创建sys_params表存储系统参数
  - [ ] 编写db_manager.py
    * 数据库连接管理（单例模式）
    * 自动重连机制
    * 事务处理和错误恢复
  - [ ] 编写db_operations.py
    * 文件索引操作（insert_file_index/update_file_index/query_by_hash等）
    * 患者索引操作（get_patient_by_id/update_last_modified等）
    * 标志物历史操作（insert_marker_record/get_marker_trend等）
    * 去重操作（record_dedup/get_duplicate_files等）

### Phase 3: 报告生成（Week 3）
- [ ] 实现报告生成模块（report_generator.py）
- [ ] 集成肿瘤标志物图表生成（quickchart-mcp）
- [ ] 实现问诊清单生成（echart可视化）
- [ ] PDF导出（reportlab/weasyprint）

### Phase 4: 科普教育与医学可视化（Week 4）

**核心原则：LLM + 智能体 + 结构化数据**

```
结构化数据 (Phase 1-3输出)
    ↓
[智能体 + 系统提示词]
    ↓
Claude API调用
    ↓
患者友好的Markdown文本 (科普+可视化)
```

实现：
- [ ] **PopularScienceAgent**：LLM驱动的科普教育
  - [ ] 系统提示词定义（医学科普专家角色）
  - [ ] 基因科普：generate_genetic_education()
  - [ ] 病理科普：generate_pathology_education()
  - [ ] 治疗科普：generate_treatment_education()
  - [ ] 预后科普：generate_prognosis_education()
  - [ ] 试验科普：generate_clinical_trial_education()
  - [ ] 自我管理：generate_patient_self_care()
  - [ ] 完整报告：generate_comprehensive_education_report()

- [ ] **VisualizationAgent**：LLM驱动的医学可视化
  - [ ] 系统提示词定义（医学信息设计师角色）
  - [ ] 风险可视化：design_risk_profile_visualization()
  - [ ] 基因表格：design_genetic_features_table()
  - [ ] 时间线：design_treatment_timeline()
  - [ ] 趋势叙述：design_marker_trend_narrative()
  - [ ] 速览卡：design_patient_summary_card()
  - [ ] 问诊清单：design_consultation_checklist()
  - [ ] 并发症表：design_complication_risk_table()
  - [ ] 完整报告：generate_comprehensive_visualization_report()

- [ ] 输出格式规范（Markdown）
- [ ] 集成quickchart-mcp生成图表
- [ ] 缓存机制避免重复调用

### Phase 5: Web展示与隐私保护（Week 5）

**核心需求**：通过Web UI安全展示病情报告，并提供密码保护

```
报告生成 (Phase 1-4)
    ↓
[Web发布模块 - Phase 5]
├─ edgeone-pages-mcp集成
├─ 密码/身份验证层
├─ 响应式Web UI设计
└─ 隐私数据脱敏处理
    ↓
患者可访问的Web报告
└─ 安全、易读、隐私保护
```

实现清单：
- [ ] **edgeone-pages-mcp集成**
  - [ ] 将报告部署到Tencent EdgeOne Pages
  - [ ] 生成患者专属的访问URL
  - [ ] 自动部署流程

- [ ] **密码/身份认证**
  - [ ] 为每个患者生成随机密码（可自定义）
  - [ ] 前端密码验证页面（不涉及后端存储）
  - [ ] 密码安全传递机制（建议邮件/SMS）
  - [ ] Session管理（24小时过期）

- [ ] **Web UI设计**
  - [ ] 响应式布局（支持手机/平板/桌面）
  - [ ] 病情报告完整版渲染（Markdown转HTML）
  - [ ] 问诊清单交互式展示
  - [ ] 科普报告和可视化作为选项卡
  - [ ] 打印友好的样式

- [ ] **隐私保护**
  - [ ] 脱敏数据展示（patient_id而非真实姓名）
  - [ ] 不记录访问日志（或加密存储）
  - [ ] 支持导出PDF（带密码保护）
  - [ ] 自动过期机制（可配置的有效期）

- [ ] **部署与配置**
  - [ ] mcp.json中配置edgeone-pages-mcp
  - [ ] 环境变量配置（API密钥、部署路径）
  - [ ] 自动化部署脚本

### Phase 6: 可选增强（Week 6）
- [ ] DICOM处理（pydicom + PIL）
- [ ] OCR集成（paddleOCR/mineru）
- [ ] pubmed_llm_server集成
- [ ] metaso知识补充集成

### Phase 7: 测试与文档（Week 7）
- [ ] 单元测试
- [ ] 集成测试
- [ ] 隐私安全审计
- [ ] 文档完善
- [ ] 示例和用例

---

## 九、提示词框架（待编写）

### 文件分类智能体
```
系统角色：医疗文件分类专家
输入：文件名、文件路径、文件内容摘要（OCR/文本前100行）
输出：
  - 推荐分类：[顶级目录]/[二级目录]
  - 置信度：high/medium/low
  - 理由
```

### 病情提取智能体
```
系统角色：医学记录提取专家
输入：脱敏版本的病历、报告、检查单
输出：结构化JSON，包含：
  - 诊断、分期、TNM
  - 病理类型、特殊标志物
  - 基因突变、检测方法
  - 治疗方案、周期、疗效
  - 影像描述、关键发现
  - 肿瘤标志物、实验室结果
  - 并发症、营养、心理状态
注意：
  - 标注置信度
  - 标注数据来源
  - 不确定的信息标记为"待人工确认"
```

### 病历整理智能体
```
系统角色：临床医学记录员
输入：患者master JSON + 相关医学文件
输出：结构化病历，按模版组织：
  - 基本信息
  - 主诉与现病史
  - 诊断依据
  - 治疗经过
  - 随访情况
  - 总结评估
  - 后续建议
```

### 隐私检查智能体
```
系统角色：数据安全审查员
输入：待发送的JSON对象
输出：
  - 是否包含敏感信息：yes/no
  - 检测到的字段：[列表]
  - 脱敏建议
  - 是否安全发送：yes/no
```

---

## 十、关键设计决策

| 决策 | 选择 | 理由 |
|------|------|------|
| **主要数据存储** | **JSON + 版本控制** | 非技术患者友好、完全本地、隐私安全 |
| 患者ID | 哈希值 | 隐私保护，避免明文敏感信息 |
| 本地优先 | 默认本地处理 | 隐私安全，仅选择性上传 |
| 版本控制 | 完整历史（JSON文件+时间戳） | 支持复诊更新，追踪信息演变 |
| 增量识别 | hash+mtime | 提高效率，避免重复处理 |
| 敏感字段脱敏 | 自定义词表+LLM | 准确识别上下文中的敏感信息 |
| 外漏处理 | 立即停止+用户确认 | 隐私风险最小化 |
| memos存储 | 脱敏版本 | 支持长期记忆，保护隐私 |
| 图表生成 | quickchart+echart | 支持多种可视化，易于集成 |
| **可选数据库** | **SQLite（可选，enable_sqlite=true）** | 高级用户性能优化，非必需 |

---

## 十一、集成清单

### MCP工具 ✅ 已配置清单（mcp.json）
- [x] **memos-api-mcp**：长期记忆存储 (API Key已配置)
- [x] **metaso**：知识补充搜索 (Bearer Token已配置)
- [x] **clinical-trials**：临床试验检索 (xiaoyibao API)
- [x] **pubmed-data-server**：PubMed胰腺癌定制库 (ABSTRACT_MODE: deep)
- [x] **mcp-pubmed-llm-server**：PubMed LLM智能处理
- [x] **Quickchart-MCP-Server**：图表生成 (SSE)
- [x] **searxng-simple-mcp**：网页搜索

### SQLite（可选高级功能）⭕
- [x] **sqlite3**：Python内置库
- [ ] 自动化初始化脚本 (init_database.py) - 可选
  - 创建6个核心表
  - 创建索引优化查询
  - 初始化系统参数表
  - **启用方式**：在config中设置 `enable_sqlite = true`
- [ ] 数据库连接管理器 (db_manager.py) - 可选
  - 连接池管理
  - 自动重连机制
  - 事务处理
- [ ] 自动化读写操作 (db_operations.py) - 可选
  - 文件索引增删改查
  - 患者记录查询
  - 标志物历史查询
  - 日志记录
  - 去重记录管理

### JSON数据管理（必需主方案）✅
- [x] **JSON文件存储**（本地文件系统）
- [ ] 版本控制实现
  - 版本号管理（v1, v2, v3...）
  - 日期后缀保存（_2024-01-15.json）
  - 历史版本追踪
- [ ] 增量识别实现
  - 文件hash计算（md5/sha256）
  - 修改时间（mtime）检测
  - 变化检测和记录
- [ ] JSON结构化管理
  - patient_master.json
  - 各类型数据文件（markers_history.json、processing_log.json等）
  - 版本历史记录

### Python依赖
- [ ] python-magic：文件识别
- [ ] pypdf：PDF提取
- [ ] python-docx：DOC/DOCX解析
- [ ] openpyxl：Excel解析
- [ ] paddleOCR：OCR（可选）
- [ ] mineru：高级OCR（可选）
- [ ] pydicom：DICOM解析（可选）
- [ ] pillow：图像处理
- [ ] matplotlib/plotly：本地图表
- [ ] reportlab：PDF生成
- [ ] weasyprint：HTML→PDF
- [ ] requests：HTTP请求
- [ ] pydantic：数据验证
- [ ] pyyaml：配置管理
- [ ] **sqlite3**：数据库（Python内置）

### 外部服务
- [ ] Claude API（现有）
- [ ] clinical_trials API 2.0
- [ ] PubMed API（可选）

---

## 十之一、报告输出优先级与结构定义

### 优先级定义

**最高优先级（必须输出）**：
1. **病情报告_完整版.md** (Phase 2)
   - 医学专业版，遵循标准病例模板（8部分）
   - 目标用户：医疗专业人士、医生
   - 内容：诊断、基因、病理、治疗、影像、标志物、风险、随访
   - 部署：Web展示（带密码保护）+ PDF导出

2. **问诊清单.md** (Phase 2)
   - 结构化问题列表，按优先级分类
   - 目标用户：患者、医生
   - 内容：高/中/低优先级问题 + 关注点
   - 部署：Web展示 + 打印友好的PDF

**次要优先级（作为附件）**：
3. **患者科普版报告.md** (Phase 4)
   - 科普教育版，用简单语言解释
   - 目标用户：患者、患者家属
   - 内容：基因、病理、治疗、预后、临床试验、自我管理
   - 部署：Web展示（作为可选项卡）

4. **医学可视化报告.md** (Phase 4)
   - 可视化展示，包含emoji和表格
   - 目标用户：患者、医生（快速浏览）
   - 内容：速览卡、风险可视化、基因表格、时间线、清单
   - 部署：Web展示（作为可选项卡）

5. **肿瘤标志物趋势图.html** (Phase 3/5)
   - quickchart生成的交互式图表
   - 部署：Web展示 + 嵌入在完整报告中

### 报告包最终结构

```
_reports/
├── 【优先级1】病情报告_完整版_2026-01-19.md
│   └─ 内容：医学专业版（8部分）
│   └─ 用途：医生决策、医学记录
│   └─ 部署：Web主体 + PDF导出
│
├── 【优先级1】问诊清单_2026-01-19.md
│   └─ 内容：结构化问题清单
│   └─ 用途：患者准备、医患沟通
│   └─ 部署：Web主体 + 打印
│
├── 【优先级2】患者科普版报告_2026-01-19.md
│   └─ 内容：科普教育版
│   └─ 用途：患者教育、家属理解
│   └─ 部署：Web附件选项卡
│
├── 【优先级2】医学可视化报告_2026-01-19.md
│   └─ 内容：可视化快速浏览
│   └─ 用途：信息速览、视觉理解
│   └─ 部署：Web附件选项卡
│
├── 【优先级3】肿瘤标志物趋势_2026-01-19.html
│   └─ 内容：交互式图表
│   └─ 部署：嵌入报告 + 单独链接
│
└── index.md
    └─ 报告导航和目录
```

---

## 十一之一、关键架构原则：LLM + 智能体 + 结构化数据

### 原则定义

Skill Report Genie采用以下**核心架构原则**来处理内容生成：

```
【数据层】
结构化病情数据
├─ Phase 1: JSON存储 (patient_master.json)
├─ Phase 2: 病理特征 (pathology_features)
├─ Phase 2: 标志物数据 (marker_data)
├─ Phase 3: 基因特征 (genetic_features)
├─ Phase 3: 临床试验 (matched_trials)
└─ Phase 3: 风险评级 (risk_profile)
    ↓
【智能体层】
Agent = 系统提示词 + 数据 + Claude API
├─ PopularScienceAgent (科普专家)
│  └─ 输出：患者友好的Markdown科普内容
├─ VisualizationAgent (设计师)
│  └─ 输出：患者友好的可视化Markdown
├─ 其他Agent (可扩展)
│  └─ 输出：其他形式的内容
    ↓
【输出层】
Markdown格式的内容
├─ .md 文件（文本）
├─ .html 文件（网页）
├─ .pdf 文件（打印）
└─ JSON导出（数据）
```

### 为什么采用这个原则

| 问题 | 方案A：硬编码词汇表 | 方案B：LLM驱动（✅选择） |
|------|-------------------|----------------------|
| 灵活性 | ❌ 词汇表固定，难以扩展 | ✅ LLM可根据上下文生成 |
| 个性化 | ❌ 所有患者收到相同内容 | ✅ 可针对患者特征调整 |
| 维护性 | ❌ 增加新术语需要代码改动 | ✅ 只需更新提示词 |
| 质量 | ❌ 机械、单调 | ✅ 自然、生动 |
| 成本 | ✅ 无API成本 | ⚠️ 需要API调用 |
| 可控性 | ✅ 完全可控 | ⚠️ 需要提示词工程 |

**结论**：采用LLM驱动方案，原因是：
1. 医学知识不断更新，LLM自动适应
2. 患者背景各异，LLM可个性化
3. 科普的语气和例子需要灵活调整
4. 长期维护成本更低

### 实现细节

#### 1. 系统提示词（System Prompt）
定义智能体的**角色**和**约束**：

```python
# PopularScienceAgent
SYSTEM_PROMPT = """你是一位资深的医学科普专家...
- 用简单易懂的语言解释医学术语
- 避免复杂医学专业术语
- 使用类比和比喻帮助患者理解
- 提供积极且现实的信息
- 强调治疗的可能性和希望
"""

# VisualizationAgent  
SYSTEM_PROMPT = """你是一位资深的医学信息设计师...
- 将复杂数据转化为清晰的可视化
- 使用emoji和符号帮助理解
- 强调关键信息，简化复杂内容
- 创建易于阅读的信息层级
"""
```

#### 2. 用户提示词（User Prompt）
包含**具体数据**和**任务指示**：

```python
# 模板
user_prompt = f"""请根据以下基因检测结果，生成一份患者友好的科普说明：

基因检测结果：
{json.dumps(genetic_features, ensure_ascii=False, indent=2)}

请生成一份科普文本，包含：
1. 发现的关键基因突变及其含义
2. 这些突变对治疗有什么影响
3. 对预后的含义
4. 是否有可靶向的突变
5. 后续建议

格式要求：
- 使用## 作为主标题
- 使用### 作为副标题
- 包含相关emoji
- 控制在800-1200字"""

response = client.messages.create(
    model="claude-3-5-sonnet-20241022",
    max_tokens=2000,
    system=SYSTEM_PROMPT,
    messages=[{"role": "user", "content": user_prompt}]
)
```

#### 3. 结构化数据格式
所有数据必须是JSON序列化的结构：

```python
genetic_features = {
    'driver_genes': [
        {'gene': 'KRAS', 'mutation': 'G12C', 'actionable': True}
    ],
    'tumor_suppressor_genes': [
        {'gene': 'TP53', 'mutation': 'R248Q'}
    ],
    'actionable_mutations': ['KRAS-G12C'],
    'risk_profile': '高危'
}

# 传递给智能体
content = agent.generate_genetic_education(genetic_features)
```

### 关键约束

1. **不要硬编码内容**：所有文本都应通过LLM生成
2. **结构化输入**：数据必须是JSON格式，不是文本
3. **明确的系统提示词**：定义角色和约束，确保输出质量
4. **输出验证**：检查LLM输出是否包含敏感信息或错误
5. **缓存机制**：相同数据不重复调用LLM（成本考虑）

---

## 十二、注意事项

1. **隐私第一（本地优先）**
   - ✅ 所有数据本地存储（JSON文件系统）
   - ✅ 所有敏感处理优先本地处理
   - 对外请求前必须用户授权
   - 外漏风险即停止+提醒用户

2. **非技术患者友好**
   - ✅ 使用JSON文件存储，无需数据库维护
   - ✅ 版本+日期命名，便于用户理解
   - 完全本地，不依赖云端或复杂工具
   - 可选SQLite用于高级用户优化

3. **数据准确性**
   - 关键字段（诊断、分期、基因）置信度<high时标注"待人工确认"
   - 缺失值补全必须标注"AI生成"
   - 记录所有版本历史（JSON时间戳）

4. **用户体验**
   - 对话中直接交互，无需复杂UI
   - 进度提示、结果摘要、错误说明清晰
   - 分类纠正、授权确认流程简洁

5. **扩展性**
   - 支持多患者模式（每患者单独JSON目录）
   - 支持多癌肿类型
   - 支持定制化报告模板
   - 可选启用SQLite进行性能优化

6. **可靠性**
   - OCR/DICOM失败记录待重试
   - 增量识别避免重复处理（hash+mtime）
   - 文件去重保持信息完整
   - JSON文件自动备份版本历史

---

## 附录：MCP配置文件说明

**位置**：`/Users/qinxiaoqiang/Downloads/skill-report-genie/mcp.json`

**配置说明**：
该文件定义了Skill使用的所有外部MCP服务器，包括API接口、认证信息、命令行启动方式等。

**使用方式**：
1. 在Claude设置中导入该MCP配置
2. Skill运行时自动加载所有已配置的MCP服务
3. 通过MCP协议与这些服务进行交互

**关键API凭证**：
- memos-api-mcp：MEMOS_API_KEY
- metaso：Bearer Token
- pubmed-data-server：PUBMED_EMAIL + PUBMED_API_KEY
- clinical-trials：xiaoyibao官方API

**维护建议**：
- 定期检查API密钥是否过期
- 监控各MCP服务的可用性
- 更新服务器地址和参数配置

---

**文档更新日期**：2026-01-19
**版本**：1.5
**状态**：已确认完整，主方案为JSON+版本控制，基因病理科普+智能临床试验匹配，MCP+ClinicalTrials API完整配置，集成小胰宝工具，准备开发
