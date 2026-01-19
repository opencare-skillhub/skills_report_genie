# ClinicalTrials.gov API v2 集成指南

## 概览

**ClinicalTrials.gov REST API v2** 是美国国立卫生研究院（NIH）提供的官方临床试验数据库API。Skill通过此API检索与患者基因、分期、病理相关的临床试验。

**API文档**：https://clinicaltrials.gov/data-api/api

---

## API基本信息

### Endpoint

```
https://clinicaltrials.gov/api/v2/studies
```

### 请求方法

```http
GET https://clinicaltrials.gov/api/v2/studies?query.cond=KRAS+G12D&pageSize=10
Accept: application/json
```

### 认证

- **无需API密钥**（公开API，无访问限制）
- **速率限制**：友好限制（建议每秒1-2个请求）
- **数据更新**：每周一至周五，一般在美国东部时间上午9点前更新

---

## 查询参数

### 1. 条件搜索（最常用）

**参数**：`query.cond`

用于搜索疾病、条件、基因突变。

```bash
# 搜索KRAS G12D相关试验
curl -X GET "https://clinicaltrials.gov/api/v2/studies?query.cond=KRAS+G12D&pageSize=20"

# 搜索胰腺癌相关试验
curl -X GET "https://clinicaltrials.gov/api/v2/studies?query.cond=pancreatic+cancer&pageSize=20"

# 组合搜索：胰腺癌 AND KRAS突变
curl -X GET "https://clinicaltrials.gov/api/v2/studies?query.cond=pancreatic+cancer+KRAS&pageSize=20"
```

### 2. 一般搜索词

**参数**：`query.term`

用于搜索试验标题、摘要、干预名称等。

```bash
# 搜索包含"immunotherapy"的试验
curl -X GET "https://clinicaltrials.gov/api/v2/studies?query.term=immunotherapy&pageSize=20"

# 组合搜索
curl -X GET "https://clinicaltrials.gov/api/v2/studies?query.cond=pancreatic+cancer&query.term=KRAS&pageSize=20"
```

### 3. 试验阶段过滤

**参数**：`filter.phase`

```
EARLY_PHASE1    - Early Phase 1
PHASE1          - Phase 1
PHASE2          - Phase 2
PHASE3          - Phase 3
PHASE4          - Phase 4
NOT_APPLICABLE  - Not Applicable
```

**示例**：
```bash
# 只搜索 Phase 2/3 试验
curl -X GET "https://clinicaltrials.gov/api/v2/studies?query.cond=pancreatic+cancer&filter.phase=PHASE2&filter.phase=PHASE3&pageSize=20"
```

### 4. 招募状态过滤

**参数**：`filter.status`

```
RECRUITING                  - 正在招募
ENROLLING_BY_INVITATION    - 邀请招募
ACTIVE_NOT_RECRUITING      - 进行中但不招募
COMPLETED                  - 已完成
TERMINATED                 - 已终止
SUSPENDED                  - 已暂停
WITHDRAWN                  - 已撤回
UNKNOWN                    - 未知
```

**示例**：
```bash
# 只搜索正在招募的试验
curl -X GET "https://clinicaltrials.gov/api/v2/studies?query.cond=pancreatic+cancer&filter.status=RECRUITING&pageSize=20"
```

### 5. 地理位置过滤

**参数**：`filter.locn`

```bash
# 搜索中国的试验
curl -X GET "https://clinicaltrials.gov/api/v2/studies?query.cond=pancreatic+cancer&filter.locn=China&pageSize=20"

# 搜索多个国家
curl -X GET "https://clinicaltrials.gov/api/v2/studies?query.cond=pancreatic+cancer&filter.locn=China&filter.locn=United+States&pageSize=20"
```

### 6. 分页参数

**参数**：`pageSize`, `pageNumber`

```bash
# pageSize: 1-100（默认10）
# pageNumber: 1, 2, 3...（默认1）

curl -X GET "https://clinicaltrials.gov/api/v2/studies?query.cond=pancreatic+cancer&pageSize=50&pageNumber=1"
```

---

## 完整查询示例

### 场景：胰腺癌患者，KRAS G12D突变，寻找Phase 2/3试验

```bash
curl -X GET "https://clinicaltrials.gov/api/v2/studies" \
  -H "accept: application/json" \
  -G \
  -d "query.cond=KRAS G12D" \
  -d "query.term=pancreatic cancer" \
  -d "filter.phase=PHASE2" \
  -d "filter.phase=PHASE3" \
  -d "filter.status=RECRUITING" \
  -d "filter.locn=China" \
  -d "pageSize=20" \
  -d "pageNumber=1"
```

### Python实现示例

```python
import requests

def search_clinical_trials(
    condition: str,
    mutations: list = None,
    phases: list = None,
    status: str = "RECRUITING",
    country: str = "China",
    page_size: int = 20,
    page_number: int = 1
):
    """
    搜索临床试验
    
    参数：
      - condition: 疾病/条件（如"pancreatic cancer"）
      - mutations: 基因突变列表（如["KRAS G12D", "TP53"]）
      - phases: 试验阶段列表（如["PHASE2", "PHASE3"]）
      - status: 招募状态（默认"RECRUITING"）
      - country: 国家（默认"China"）
      - page_size: 每页返回数量
      - page_number: 页码
    
    返回：
      - studies: 试验列表
      - totalCount: 总试验数
      - hasNextPage: 是否有下一页
    """
    
    url = "https://clinicaltrials.gov/api/v2/studies"
    
    params = {
        "query.cond": condition,
        "pageSize": page_size,
        "pageNumber": page_number
    }
    
    # 添加基因突变搜索
    if mutations:
        params["query.term"] = " ".join(mutations)
    
    # 添加试验阶段过滤
    if phases:
        params["filter.phase"] = phases
    
    # 添加招募状态过滤
    if status:
        params["filter.status"] = status
    
    # 添加地理位置过滤
    if country:
        params["filter.locn"] = country
    
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        return {
            "studies": data.get("studies", []),
            "total_count": data.get("totalCount", 0),
            "has_next_page": data.get("pageInfo", {}).get("hasNextPage", False),
            "page_number": data.get("pageInfo", {}).get("pageNumber", 1)
        }
    
    except requests.RequestException as e:
        return {
            "error": str(e),
            "studies": []
        }

# 使用示例
results = search_clinical_trials(
    condition="pancreatic cancer",
    mutations=["KRAS G12D"],
    phases=["PHASE2", "PHASE3"],
    status="RECRUITING",
    country="China",
    page_size=20
)

for study in results["studies"]:
    nct_id = study["protocolSection"]["identificationModule"]["nctId"]
    title = study["protocolSection"]["identificationModule"]["briefTitle"]
    status = study["protocolSection"]["statusModule"]["overallStatus"]
    print(f"{nct_id}: {title} ({status})")
```

---

## 响应数据结构

### 完整响应格式

```json
{
  "studies": [
    {
      "protocolSection": {
        "identificationModule": {
          "nctId": "NCT04123456",
          "orgStudyIdInfo": {
            "orgStudyId": "KRAS-2024-001"
          },
          "secondaryIdInfos": [...],
          "briefTitle": "KRAS G12D Inhibitor in Advanced Pancreatic Cancer",
          "officialTitle": "A Phase 2/3 Study of XXX in Patients with KRAS G12D-Mutant Advanced Pancreatic Cancer",
          "acronym": "KRAS-PC"
        },
        "statusModule": {
          "recordVerificationDate": "2024-01-15",
          "overallStatus": "RECRUITING",
          "expandedAccessInfo": null,
          "startDateStruct": {
            "date": "2023-06-01",
            "type": "ACTUAL"
          },
          "primaryCompletionDateStruct": {
            "date": "2025-12-31",
            "type": "ESTIMATED"
          },
          "completionDateStruct": {
            "date": "2026-06-30",
            "type": "ESTIMATED"
          },
          "studyFirstSubmitDate": "2023-04-15",
          "studyFirstPostDate": "2023-06-01",
          "lastUpdateSubmitDate": "2024-01-10",
          "lastUpdatePostDate": "2024-01-15"
        },
        "designModule": {
          "studyType": "INTERVENTIONAL",
          "phases": ["PHASE2", "PHASE3"],
          "designInfo": {
            "allocation": "RANDOMIZED",
            "interventionModel": "PARALLEL",
            "primaryPurpose": "TREATMENT",
            "masking": {
              "masking": "NONE"
            }
          },
          "enrollmentInfo": {
            "count": 300,
            "type": "ESTIMATED"
          }
        },
        "conditionsModule": {
          "conditions": ["Pancreatic Cancer", "Pancreatic Neoplasms"],
          "keywords": ["KRAS G12D", "Pancreatic Cancer", "Advanced Cancer"]
        },
        "interventionsModule": {
          "interventions": [
            {
              "type": "DRUG",
              "name": "KRAS Inhibitor",
              "description": "Direct KRAS G12D inhibitor",
              "armGroupLabels": ["Experimental: KRAS Inhibitor"]
            },
            {
              "type": "DRUG",
              "name": "Gemcitabine + Cisplatin",
              "description": "Standard chemotherapy",
              "armGroupLabels": ["Active Comparator: Standard Chemo"]
            }
          ]
        },
        "outcomesModule": {
          "primaryOutcomes": [
            {
              "measure": "Overall Survival",
              "timeFrame": "From date of randomization until death from any cause (up to 36 months)"
            }
          ],
          "secondaryOutcomes": [
            {
              "measure": "Progression-Free Survival",
              "timeFrame": "From date of randomization until documented progression (up to 36 months)"
            }
          ]
        },
        "eligibilityModule": {
          "eligibilityCriteria": "Inclusion Criteria:\n- Confirmed KRAS G12D mutation\n- Unresectable or metastatic pancreatic cancer\n- 18-75 years old\nExclusion Criteria:\n- Prior KRAS inhibitor therapy\n- Active secondary malignancy",
          "healthyVolunteers": false,
          "sex": "ALL",
          "genderBased": false,
          "minimumAge": "18 Years",
          "maximumAge": "75 Years",
          "stdAges": ["ADULT", "OLDER_ADULT"]
        },
        "contactsLocationsModule": {
          "centralContacts": [
            {
              "name": "Principal Investigator",
              "role": "PRINCIPAL_INVESTIGATOR",
              "email": "researcher@hospital.com",
              "phone": "+86-10-12345678"
            }
          ],
          "locations": [
            {
              "facility": "Shanghai Cancer Institute",
              "city": "Shanghai",
              "state": "Shanghai",
              "postalCode": "200032",
              "country": "China",
              "status": "RECRUITING",
              "contacts": [...]
            }
          ]
        },
        "referencesModule": {
          "references": [
            {
              "pmid": "PMID123456",
              "type": "BACKGROUND",
              "citation": "Authors et al. Journal 2023..."
            }
          ],
          "results": [
            {
              "url": "https://clinicaltrials.gov/show/NCT04123456"
            }
          ]
        }
      },
      "derivedSection": {
        "miscInfoModule": {
          "versionHolder": "2024-01-15",
          "submissionTrackerIds": []
        }
      }
    }
  ],
  "totalCount": 45,
  "pageInfo": {
    "pageNumber": 1,
    "pageSize": 20,
    "totalPages": 3,
    "hasNextPage": true
  }
}
```

### 关键字段提取

```python
def extract_trial_info(study):
    """从API响应中提取关键信息"""
    proto = study["protocolSection"]
    
    return {
        # 基本信息
        "nct_id": proto["identificationModule"]["nctId"],
        "brief_title": proto["identificationModule"]["briefTitle"],
        "official_title": proto["identificationModule"]["officialTitle"],
        
        # 状态信息
        "overall_status": proto["statusModule"]["overallStatus"],
        "start_date": proto["statusModule"]["startDateStruct"]["date"],
        "completion_date": proto["statusModule"]["completionDateStruct"]["date"],
        
        # 设计信息
        "study_type": proto["designModule"]["studyType"],
        "phases": proto["designModule"]["phases"],
        "enrollment": proto["designModule"]["enrollmentInfo"]["count"],
        
        # 条件和关键词
        "conditions": proto["conditionsModule"]["conditions"],
        "keywords": proto["conditionsModule"].get("keywords", []),
        
        # 干预措施
        "interventions": [
            {
                "type": i["type"],
                "name": i["name"],
                "description": i["description"]
            }
            for i in proto["interventionsModule"]["interventions"]
        ],
        
        # 纳入排斥标准
        "eligibility_criteria": proto["eligibilityModule"]["eligibilityCriteria"],
        "min_age": proto["eligibilityModule"]["minimumAge"],
        "max_age": proto["eligibilityModule"]["maximumAge"],
        "healthy_volunteers": proto["eligibilityModule"]["healthyVolunteers"],
        
        # 主要结果指标
        "primary_outcomes": [
            o["measure"] for o in proto["outcomesModule"].get("primaryOutcomes", [])
        ],
        
        # 地点信息
        "locations": [
            {
                "facility": l["facility"],
                "city": l["city"],
                "country": l["country"],
                "status": l["status"]
            }
            for l in proto.get("contactsLocationsModule", {}).get("locations", [])
        ]
    }
```

---

## Skill集成流程

### 1. 用户授权阶段

```
用户启动临床知识增强
  ↓
系统提示：将发送患者脱敏信息（分期、基因、病理）到ClinicalTrials.gov
  ↓
用户确认 ✓
  ↓
执行搜索
```

### 2. 敏感信息脱敏

```python
def prepare_search_query(patient_data):
    """准备搜索查询，进行敏感信息脱敏"""
    
    search_params = {
        "condition": patient_data["diagnosis"]["primary_cancer"],  # "pancreatic cancer"
        "mutations": patient_data["genetic_testing"]["mutations"],  # ["KRAS G12D"]
        "phases": ["PHASE2", "PHASE3"],  # 推荐阶段
        "status": "RECRUITING",  # 仅正在招募
        "country": "China"  # 患者所在国
    }
    
    # 不发送的信息：
    # - 患者姓名、ID
    # - 具体日期
    # - 医院信息
    # - 治疗细节
    
    return search_params
```

### 3. API调用和结果处理

```python
def enhance_with_clinical_trials(patient_id, patient_data):
    """为患者生成临床试验推荐"""
    
    # 1. 准备搜索参数
    search_params = prepare_search_query(patient_data)
    
    # 2. 调用API
    results = search_clinical_trials(**search_params)
    
    # 3. 处理结果
    if results.get("error"):
        return {"status": "failed", "error": results["error"]}
    
    # 4. 提取关键信息
    trials = []
    for study in results["studies"]:
        trial_info = extract_trial_info(study)
        trials.append(trial_info)
    
    # 5. 排序（中国优先，招募中优先）
    trials = sorted(
        trials,
        key=lambda t: (
            0 if any("China" in l["country"] for l in t["locations"]) else 1,
            0 if t["overall_status"] == "RECRUITING" else 1
        )
    )
    
    # 6. 保存结果到JSON
    save_to_json({
        "patient_id": patient_id,
        "search_time": datetime.now().isoformat(),
        "search_params": search_params,
        "total_results": results["total_count"],
        "trials": trials[:10]  # 保存前10条
    }, f"_reports/clinical_trials_{patient_id}.json")
    
    return {
        "status": "success",
        "total_count": results["total_count"],
        "trials": trials[:10]
    }
```

### 4. 报告生成

生成的临床试验推荐报告包含：

```markdown
## 临床试验推荐

基于您的基因检测结果（KRAS G12D + TP53），我们为您找到 45 项相关临床试验。

### 推荐试验（按优先级排序）

#### 1. NCT04123456 - KRAS G12D Inhibitor Study
**状态**: 正在招募 | **阶段**: II/III | **地点**: 上海，中国

**纳入条件**:
- KRAS G12D确认突变
- 不可切除或转移性胰腺癌
- 18-75岁

**主要终点**：
- 总体生存期 (OS)

**研究设计**：
- 随机对照试验
- 预计招募300人
- 预计完成时间：2026年6月

**主要干预措施**：
- KRAS抑制剂 vs 标准化疗

**联系方式**：
- 电话：+86-10-12345678
- 邮箱：researcher@hospital.com

[查看详细信息](https://clinicaltrials.gov/show/NCT04123456)
```

---

## 错误处理和降级方案

### 网络错误处理

```python
def search_with_retry(search_params, max_retries=3):
    """带重试的搜索"""
    for attempt in range(max_retries):
        try:
            results = search_clinical_trials(**search_params)
            if not results.get("error"):
                return results
        except requests.Timeout:
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)  # 指数退避
                continue
        except Exception as e:
            logger.error(f"Search error: {e}")
    
    # 降级方案：返回本地缓存或提示用户
    return {"error": "Cannot fetch trials, please try later"}
```

### 空结果处理

```python
if results["total_count"] == 0:
    message = """
    未找到与您的基因突变完全匹配的试验。
    建议：
    1. 查看相关基因变异的试验
    2. 扩大搜索范围（如全国或全球试验）
    3. 咨询医生关于其他治疗选项
    """
```

---

## 常见问题

**Q: API有使用限制吗？**
A: 没有严格的速率限制，但建议遵守友好限制（每秒1-2个请求）。

**Q: 数据多久更新一次？**
A: 每周一至周五更新，一般在美国东部时间上午9点前完成。

**Q: 如何搜索特定基因突变？**
A: 在 `query.cond` 中包含基因名称，如 "KRAS G12D" 或 "KRAS G12C"。

**Q: 能否按地点筛选？**
A: 可以，使用 `filter.locn` 参数，如 "China", "United States"。

**Q: 试验状态有哪些？**
A: 主要有RECRUITING(招募中)、ENROLLING_BY_INVITATION、ACTIVE_NOT_RECRUITING、COMPLETED等。

---

**最后更新**：2026-01-19  
**API版本**：v2  
**数据来源**：NIH Clinical Trials Database
