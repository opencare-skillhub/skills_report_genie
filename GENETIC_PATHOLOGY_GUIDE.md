# 基因病理科普与临床试验智能匹配指南

## 概览

本指南说明如何在Skill中实现：
1. **自动提取基因和病理特征** - 从原始检测报告提取关键信息
2. **分别查询临床试验** - 基因特征和病理特征分别查询
3. **智能匹配组合** - 找到既符合基因又符合病理的试验
4. **科普型报告生成** - 为患者生成易懂的科普解释和指引

---

## 第一部分：基因和病理特征自动提取

### 1.1 基因特征提取模块

**输入**：原始基因检测报告（文本或JSON）

```json
{
  "test_type": "NGS",
  "mutations": [
    {
      "gene": "KRAS",
      "mutation": "G12D",
      "classification": "驱动基因",
      "allele_frequency": 45.2,
      "zygosity": "heterozygous"
    },
    {
      "gene": "TP53",
      "mutation": "R248Q",
      "classification": "抑癌基因",
      "allele_frequency": 42.8,
      "zygosity": "heterozygous"
    }
  ]
}
```

**提取规则**：

```python
class GeneticFeatureExtractor:
    def __init__(self):
        # 基因特征库（可扩展）
        self.gene_db = {
            "KRAS": {
                "type": "驱动基因",
                "function": "细胞信号传导",
                "common_mutations": ["G12D", "G12V", "G12C"],
                "treatment_directions": [
                    "KRAS抑制剂（如sotorasib针对G12C）",
                    "MEK抑制剂",
                    "标准化疗"
                ],
                "prognosis": "KRAS突变患者化疗敏感性较差，预后相对较差"
            },
            "TP53": {
                "type": "抑癌基因",
                "function": "细胞周期调控、DNA修复",
                "common_mutations": ["R248Q", "R175H", "Y234H"],
                "treatment_directions": [
                    "标准化疗",
                    "免疫治疗（考虑高TMB）",
                    "DNA修复相关药物（如PARPi）"
                ],
                "prognosis": "TP53突变提示预后较差，治疗响应差异大"
            }
            # 可继续添加更多基因...
        }
    
    def extract_mutations(self, genetic_report):
        """从报告中提取突变信息"""
        extracted = {
            "driver_genes": [],
            "tumor_suppressor_genes": [],
            "treatment_targets": set(),
            "risk_profile": ""
        }
        
        for mutation in genetic_report.get("mutations", []):
            gene = mutation["gene"]
            mut_type = mutation["classification"]
            
            if gene in self.gene_db:
                gene_info = self.gene_db[gene]
                
                # 分类
                if gene_info["type"] == "驱动基因":
                    extracted["driver_genes"].append({
                        "gene": gene,
                        "mutation": mutation["mutation"],
                        "treatment_directions": gene_info["treatment_directions"]
                    })
                elif gene_info["type"] == "抑癌基因":
                    extracted["tumor_suppressor_genes"].append({
                        "gene": gene,
                        "mutation": mutation["mutation"],
                        "treatment_directions": gene_info["treatment_directions"]
                    })
                
                # 收集治疗方向
                extracted["treatment_targets"].update(gene_info["treatment_directions"])
        
        # 判断风险等级
        if len(extracted["driver_genes"]) >= 2:
            extracted["risk_profile"] = "高危"
        elif len(extracted["driver_genes"]) == 1:
            extracted["risk_profile"] = "中危"
        else:
            extracted["risk_profile"] = "低危"
        
        return extracted

# 使用示例
extractor = GeneticFeatureExtractor()
genetic_report = {...}  # 患者基因检测报告
features = extractor.extract_mutations(genetic_report)

print(f"驱动基因: {features['driver_genes']}")
print(f"风险等级: {features['risk_profile']}")
print(f"治疗方向: {features['treatment_targets']}")
```

### 1.2 病理特征提取模块

**输入**：病理检测报告

```json
{
  "primary_pathology": "adenocarcinoma",
  "differentiation_grade": "II",  // Grade I, II, III
  "histological_subtypes": [
    "tubular_adenocarcinoma",
    "ductal_carcinoma"
  ],
  "special_markers": {
    "claudin18": "positive",
    "HER2": "negative",
    "MSI": "MSS"  // MSI/MSS
  }
}
```

**提取规则**：

```python
class PathologyFeatureExtractor:
    def __init__(self):
        # 胰腺肿瘤分类库（基于WHO分类和免疫表达谱）
        self.pathology_db = {
            # ===== 外分泌肿瘤 =====
            "pancreatic_ductal_adenocarcinoma": {
                "chinese_name": "胰腺导管腺癌",
                "category": "外分泌肿瘤",
                "characteristics": "起源于胰管上皮，是最常见的胰腺癌类型（>85%）",
                "immunophenotype": "CK7+, CK8+, CK13+, CK18+, CK19+, CEA+, S100P+, MUC1+, MUC3+, MUC5/6+, CA19-9+, CA125+, claudin-4+",
                "chemotherapy_sensitivity": "中等敏感，对吉西他滨+顺铂有一定敏感性",
                "prognosis": "预后差，5年生存率<10%，与TNM分期和分化程度密切相关",
                "special_consideration": "需重点监测CA19-9和CA50，多指标联合判断；关注特殊标志物表达用于靶向治疗",
                "key_markers": ["CA19-9", "CA50", "CA125", "CK19", "S100P", "claudin18", "HER2"],
                "treatment_options": ["吉西他滨+顺铂化疗", "FOLFIRINOX方案", "靶向治疗(claudin18/HER2等)", "免疫治疗"]
            },
            "serous_cystadenocarcinoma": {
                "chinese_name": "浆液性囊腺癌",
                "category": "外分泌肿瘤",
                "characteristics": "起源于浆液性囊泡，罕见(<5%)",
                "immunophenotype": "CK7+, CK8+, CK18+, CK19+, EMA+, CK20-, CA19.9-",
                "chemotherapy_sensitivity": "相对较敏感",
                "prognosis": "预后相对较好，多数为低度恶性",
                "special_consideration": "通常发现时为早期，预后优于导管腺癌",
                "key_markers": ["CK7", "CK19"],
                "treatment_options": ["手术切除", "辅助化疗"]
            },
            "mucinous_cystic_neoplasm": {
                "chinese_name": "粘液性囊性肿瘤（伴异型增生）",
                "category": "外分泌肿瘤",
                "characteristics": "囊性肿瘤，可从低级别异型增生进展至癌",
                "immunophenotype": "CK7+, CK8+, CK18+, CK19+, EMA+, S100P+, CEA+, CA19.9+, CK20-",
                "chemotherapy_sensitivity": "中等敏感",
                "prognosis": "预后取决于分化程度，高级别异型增生患者预后差",
                "special_consideration": "需监测CA19-9和CEA；囊内液CEA水平可评估恶变风险",
                "key_markers": ["CA19-9", "CEA", "CK19"],
                "treatment_options": ["手术切除", "辅助化疗（高级别异型增生）"]
            },
            "intraductal_papillary_mucinous_neoplasm": {
                "chinese_name": "导管内乳头状粘液肿瘤（IPMN）",
                "category": "外分泌肿瘤",
                "characteristics": "导管内乳头状病变，具有癌变潜能",
                "immunophenotype": "CK7+, CK8+, CK18+, S100P+, 可表达CK19/CA19.9/CK20/CEA",
                "chemotherapy_sensitivity": "取决于是否发生癌变",
                "prognosis": "预后取决于分化程度和浸润程度",
                "special_consideration": "需定期影像学监测；主型IPMN癌变风险>70%；分支型IPMN癌变风险<15%",
                "key_markers": ["CA19-9", "CK7", "S100P"],
                "treatment_options": ["定期监测", "手术切除（高风险患者）", "辅助化疗（已癌变）"]
            },
            "acinar_cell_carcinoma": {
                "chinese_name": "腺泡细胞癌",
                "category": "外分泌肿瘤",
                "characteristics": "起源于腺泡细胞，罕见(<1%)",
                "immunophenotype": "胰蛋白酶+, 糜蛋白酶+, CK8+, CK18+, bcl-10+",
                "chemotherapy_sensitivity": "相对敏感",
                "prognosis": "预后相对较好，多数低度恶性",
                "special_consideration": "常表现为高淀粉酶血症；具有分泌功能",
                "key_markers": ["CK8", "胰蛋白酶"],
                "treatment_options": ["手术切除", "辅助化疗"]
            },
            
            # ===== 内分泌肿瘤 =====
            "pancreatic_neuroendocrine_tumor": {
                "chinese_name": "胰腺神经内分泌肿瘤（NET）",
                "category": "内分泌肿瘤",
                "characteristics": "起源于胰岛细胞，分化程度高",
                "immunophenotype": "CK8+, CK18+, CK19+, CD56+, 嗜铬粒蛋白+, 突触素+",
                "chemotherapy_sensitivity": "G1/G2: 相对低敏感；G3: 敏感性高",
                "prognosis": "取决于分级(G1/G2/G3)和分期，G1预后最好",
                "special_consideration": "需进行WHO 2019分级；分泌功能测定；血清学标志物检测",
                "key_markers": ["CK8", "嗜铬粒蛋白", "突触素", "Ki-67"],
                "treatment_options": ["手术切除", "生长抑素类似物", "化疗(G3)", "靶向治疗(everolimus/sunitinib)"]
            },
            "pancreatic_small_cell_carcinoma": {
                "chinese_name": "胰腺小细胞癌（G3神经内分泌癌）",
                "category": "内分泌肿瘤",
                "characteristics": "高度恶性，神经内分泌分化，Ki-67>20%",
                "immunophenotype": "CD56+, 嗜铬粒蛋白+, 突触素+, CK8/18+, NSE+",
                "chemotherapy_sensitivity": "高度敏感，对铂类和依托泊苷敏感",
                "prognosis": "预后极差，平均生存期<2年",
                "special_consideration": "需尽早化疗；可考虑PD-L1表达状态用于免疫治疗评估",
                "key_markers": ["嗜铬粒蛋白", "Ki-67(>20%)", "CD56"],
                "treatment_options": ["铂类+依托泊苷化疗", "免疫治疗(PD-L1+患者)"]
            },
            
            # ===== 其他特殊类型 =====
            "squamous_cell_carcinoma": {
                "chinese_name": "胰腺鳞癌",
                "category": "罕见肿瘤",
                "characteristics": "来源于胰管鳞状化生上皮，罕见(<1%)",
                "immunophenotype": "CK5/6/14+, CK7+, CK19+, p63+",
                "chemotherapy_sensitivity": "相对敏感",
                "prognosis": "预后较差，与导管腺癌相似或更差",
                "special_consideration": "容易发生远处转移；预后差",
                "key_markers": ["CK5", "CK7", "p63"],
                "treatment_options": ["以化疗为主", "可考虑放疗"]
            },
            "undifferentiated_carcinoma": {
                "chinese_name": "胰腺未分化癌",
                "category": "罕见肿瘤",
                "characteristics": "高度恶性，无分化特征",
                "immunophenotype": "可无特异性标志物表达",
                "chemotherapy_sensitivity": "中等敏感",
                "prognosis": "预后极差，平均生存期<1年",
                "special_consideration": "需排除其他高级别恶性肿瘤；Ki-67极高",
                "key_markers": ["Ki-67(>>50%)"],
                "treatment_options": ["积极化疗", "多学科综合治疗"]
            },
            "solid_pseudopapillary_neoplasm": {
                "chinese_name": "胰腺实性假乳头状肿瘤",
                "category": "罕见肿瘤",
                "characteristics": "低度恶性，多见于年轻女性",
                "immunophenotype": "CD10+, α-1 AAT+, PgR+, β-catenin+, NSE+, vimentin+",
                "chemotherapy_sensitivity": "相对低敏感",
                "prognosis": "预后相对较好，10年生存率>90%",
                "special_consideration": "预后优于导管腺癌；需关注β-catenin异常激活",
                "key_markers": ["CD10", "β-catenin"],
                "treatment_options": ["手术切除", "必要时辅助化疗"]
            }
        }
        
        self.grade_db = {
            "I": {
                "name": "高分化",
                "prognosis": "预后最好",
                "chemotherapy_sensitivity": "敏感性相对低"
            },
            "II": {
                "name": "中分化",
                "prognosis": "预后中等",
                "chemotherapy_sensitivity": "敏感性中等"
            },
            "III": {
                "name": "低分化",
                "prognosis": "预后较差",
                "chemotherapy_sensitivity": "敏感性相对高"
            }
        }
        
        # 胰腺癌特异性免疫组化标志物库（基于胰腺肿瘤免疫表达谱）
        self.marker_db = {
            # ===== 核心诊断标志物 =====
            "CA19-9": {
                "positive": {
                    "meaning": "CA19-9升高",
                    "reference_range": "0-43 U/mL",
                    "clinical_significance": "胰腺癌最灵敏的肿瘤标志物，可被炎症干扰",
                    "treatment": "化疗敏感性提示，与CA50联合更可靠",
                    "clinical_trial_keyword": "CA19-9",
                    "multi_marker_analysis": True  # 需多标志物同趋势确认
                },
                "negative": {
                    "meaning": "CA19-9正常",
                    "treatment": "继续监测其他标志物",
                    "clinical_trial_keyword": ""
                }
            },
            "CA50": {
                "positive": {
                    "meaning": "CA50升高",
                    "reference_range": "0-20 U/mL",
                    "clinical_significance": "与CA19-9同源，二者联合更可靠",
                    "treatment": "与CA19-9同升高→肿瘤进展↑↑",
                    "clinical_trial_keyword": "CA50"
                },
                "negative": {
                    "meaning": "CA50正常",
                    "treatment": "若CA19-9升高但CA50正常→可能为炎症",
                    "clinical_trial_keyword": ""
                }
            },
            "CA125": {
                "positive": {
                    "meaning": "CA125升高",
                    "reference_range": "0-35 U/mL",
                    "clinical_significance": "腹膜癌转移指示，评估腹膜播散风险",
                    "treatment": "与CA19-9同升高→腹膜转移↑↑↑",
                    "clinical_trial_keyword": "CA125"
                },
                "negative": {
                    "meaning": "CA125正常",
                    "treatment": "提示无腹膜播散迹象",
                    "clinical_trial_keyword": ""
                }
            },
            "CA72-4": {
                "positive": {
                    "meaning": "CA72-4升高",
                    "reference_range": "0-10 U/mL",
                    "clinical_significance": "胃肠肿瘤标志物，反映分化程度",
                    "treatment": "与CA19-9同升高→分化程度下降/进展↑",
                    "clinical_trial_keyword": "CA72-4"
                },
                "negative": {
                    "meaning": "CA72-4正常",
                    "treatment": "分化程度相对稳定",
                    "clinical_trial_keyword": ""
                }
            },
            "CEA": {
                "positive": {
                    "meaning": "CEA升高",
                    "reference_range": "0-5 ng/mL",
                    "clinical_significance": "一般肿瘤标志物，特异性较低",
                    "treatment": "需结合其他标志物和影像学评估",
                    "clinical_trial_keyword": "CEA"
                },
                "negative": {
                    "meaning": "CEA正常",
                    "treatment": "继续监测其他标志物",
                    "clinical_trial_keyword": ""
                }
            },
            
            # ===== 病理诊断标志物 =====
            "CK7": {
                "positive": {
                    "meaning": "CK7表达增高",
                    "clinical_significance": "单层上皮标志物，支持腺癌诊断",
                    "treatment": "与CK8/CK18/CK19联合用于导管腺癌诊断",
                    "clinical_trial_keyword": "CK7+"
                },
                "negative": {
                    "meaning": "CK7表达阴性",
                    "clinical_significance": "提示非胰腺导管上皮来源",
                    "treatment": "需进一步鉴别诊断",
                    "clinical_trial_keyword": ""
                }
            },
            "CK19": {
                "positive": {
                    "meaning": "CK19表达增高",
                    "clinical_significance": "胰腺导管上皮标志物，高表达与侵袭性/预后不良相关",
                    "treatment": "胰腺癌诊断和预后评估的重要指标",
                    "clinical_trial_keyword": "CK19+"
                },
                "negative": {
                    "meaning": "CK19表达阴性",
                    "clinical_significance": "提示非胰腺导管癌",
                    "treatment": "需鉴别其他肿瘤类型",
                    "clinical_trial_keyword": ""
                }
            },
            "CK20": {
                "positive": {
                    "meaning": "CK20表达增高",
                    "clinical_significance": "肠道上皮标志物，有助区分肠化生",
                    "treatment": "若CK7+/CK20-→导管腺癌；若CK20+→考虑肠化生",
                    "clinical_trial_keyword": "CK20+"
                },
                "negative": {
                    "meaning": "CK20表达阴性",
                    "clinical_significance": "支持胰腺导管癌诊断（非肠化生）",
                    "treatment": "典型的导管腺癌表型",
                    "clinical_trial_keyword": ""
                }
            },
            
            # ===== 靶点标志物 =====
            "claudin18": {
                "positive": {
                    "meaning": "Claudin18表达增高",
                    "clinical_significance": "紧密连接蛋白，与侵袭性和转移能力相关",
                    "treatment": "claudin18靶向抗体（如anetumab ravtansine）",
                    "clinical_trial_keyword": "claudin18"
                },
                "negative": {
                    "meaning": "Claudin18表达不高",
                    "clinical_significance": "不符合claudin18靶向治疗",
                    "treatment": "标准化疗为主",
                    "clinical_trial_keyword": ""
                }
            },
            "HER2": {
                "positive": {
                    "meaning": "HER2表达增高",
                    "clinical_significance": "酪氨酸激酶受体，与侵袭性和预后不良相关",
                    "treatment": "HER2靶向治疗（如trastuzumab等）",
                    "clinical_trial_keyword": "HER2+"
                },
                "negative": {
                    "meaning": "HER2表达不高",
                    "clinical_significance": "不符合HER2靶向治疗",
                    "treatment": "标准化疗为主",
                    "clinical_trial_keyword": ""
                }
            },
            "S100P": {
                "positive": {
                    "meaning": "S100P表达增高",
                    "clinical_significance": "钙结合蛋白，与侵袭性和预后不良相关",
                    "treatment": "提示高风险患者，需积极治疗",
                    "clinical_trial_keyword": "S100P+"
                },
                "negative": {
                    "meaning": "S100P表达不高",
                    "clinical_significance": "低风险表型",
                    "treatment": "相对预后较好",
                    "clinical_trial_keyword": ""
                }
            },
            
            # ===== 微卫星和免疫相关 =====
            "MSI": {
                "MSI_H": {
                    "meaning": "微卫星高度不稳定，高突变负荷",
                    "clinical_significance": "提示DNA修复缺陷，免疫治疗敏感性高",
                    "treatment": "考虑免疫治疗（如PD-1/PD-L1抑制剂）优先",
                    "clinical_trial_keyword": "MSI-H"
                },
                "MSS": {
                    "meaning": "微卫星稳定，低突变负荷",
                    "clinical_significance": "DNA修复正常，免疫治疗敏感性相对低",
                    "treatment": "标准化疗为主，考虑靶向治疗",
                    "clinical_trial_keyword": ""
                }
            },
            "Ki-67": {
                "positive": {
                    "meaning": "Ki-67高表达",
                    "clinical_significance": "细胞增殖活性高，预示预后较差",
                    "treatment": "积极化疗，考虑多学科治疗",
                    "clinical_trial_keyword": "Ki-67+"
                },
                "negative": {
                    "meaning": "Ki-67低表达",
                    "clinical_significance": "细胞增殖缓慢，相对预后较好",
                    "treatment": "可考虑个体化治疗",
                    "clinical_trial_keyword": ""
                }
            },
            
            # ===== 神经内分泌标志物 =====
            "SYN": {
                "positive": {
                    "meaning": "突触素表达增高",
                    "clinical_significance": "神经特异性标志物，提示神经内分泌分化",
                    "treatment": "神经内分泌肿瘤治疗策略",
                    "clinical_trial_keyword": "SYN+"
                },
                "negative": {
                    "meaning": "突触素不表达",
                    "clinical_significance": "非神经内分泌肿瘤",
                    "treatment": "标准腺癌治疗",
                    "clinical_trial_keyword": ""
                }
            },
            "Cg": {
                "positive": {
                    "meaning": "嗜铬粒蛋白表达增高",
                    "clinical_significance": "神经内分泌分化标志物",
                    "treatment": "考虑神经内分泌肿瘤治疗方案",
                    "clinical_trial_keyword": "Cg+"
                },
                "negative": {
                    "meaning": "嗜铬粒蛋白不表达",
                    "clinical_significance": "一般腺癌表型",
                    "treatment": "标准化疗为主",
                    "clinical_trial_keyword": ""
                }
            },
            
            # ===== 分化程度和预后相关标志物 =====
            "E-cadherin": {
                "positive": {
                    "meaning": "E-钙粘蛋白表达正常",
                    "clinical_significance": "细胞黏附完整，侵袭性相对低",
                    "treatment": "相对预后较好",
                    "clinical_trial_keyword": ""
                },
                "negative": {
                    "meaning": "E-钙粘蛋白表达降低/丧失",
                    "clinical_significance": "细胞黏附降低，侵袭性和转移能力增强",
                    "treatment": "高风险患者，需强化治疗",
                    "clinical_trial_keyword": "E-cadherin-"
                }
            },
            "IMP3": {
                "positive": {
                    "meaning": "IMP3表达增高",
                    "clinical_significance": "与侵袭性和预后不良相关，高表达患者预后差",
                    "treatment": "强化治疗方案，考虑靶向/免疫治疗",
                    "clinical_trial_keyword": "IMP3+"
                },
                "negative": {
                    "meaning": "IMP3表达不高",
                    "clinical_significance": "相对预后较好",
                    "treatment": "标准治疗方案",
                    "clinical_trial_keyword": ""
                }
            },
            "MUC1": {
                "positive": {
                    "meaning": "MUC1表达异常增高",
                    "clinical_significance": "粘蛋白异常表达，与侵袭性和预后不良相关",
                    "treatment": "提示高风险，需积极治疗",
                    "clinical_trial_keyword": "MUC1+"
                },
                "negative": {
                    "meaning": "MUC1表达正常",
                    "clinical_significance": "相对预后较好",
                    "treatment": "标准治疗方案",
                    "clinical_trial_keyword": ""
                }
            }
        }
    
    def extract_pathology(self, pathology_report):
         """从病理报告提取关键特征"""
         extracted = {
             "cancer_type": None,
             "differentiation_grade": None,
             "treatment_considerations": [],
             "trial_keywords": [],
             "multi_marker_analysis": None,
             "risk_stratification": None
         }
         
         # 提取癌肿类型
         cancer_type = pathology_report.get("primary_pathology")
         if cancer_type in self.pathology_db:
             extracted["cancer_type"] = self.pathology_db[cancer_type]
         
         # 提取分化程度
         grade = pathology_report.get("differentiation_grade")
         if grade in self.grade_db:
             extracted["differentiation_grade"] = self.grade_db[grade]
         
         # 提取特殊标志物
         special_markers = pathology_report.get("special_markers", {})
         for marker, value in special_markers.items():
             if marker in self.marker_db and value in self.marker_db[marker]:
                 marker_info = self.marker_db[marker][value]
                 extracted["treatment_considerations"].append(marker_info)
                 if marker_info.get("clinical_trial_keyword"):
                     extracted["trial_keywords"].append(marker_info["clinical_trial_keyword"])
         
         # 多标志物联合分析（针对肿瘤标志物）
         extracted["multi_marker_analysis"] = self._analyze_multi_markers(special_markers)
         
         # 风险分层评估
         extracted["risk_stratification"] = self._stratify_risk(extracted, special_markers)
         
         return extracted
     
     def _analyze_multi_markers(self, markers):
         """多标志物同趋势分析（根据DEVELOPMENT_PLAN.md标准）"""
         analysis = {
             "simultaneous_elevation": [],
             "trend_interpretation": "",
             "clinical_recommendation": ""
         }
         
         # 检查多个肿瘤标志物的同时升高
         elevated_markers = [m for m, v in markers.items() 
                            if m in ["CA19-9", "CA50", "CA125", "CA72-4", "CEA"] 
                            and v in ["positive", "high"]]
         
         if len(elevated_markers) >= 2:
             analysis["simultaneous_elevation"] = elevated_markers
             
             # 关键组合判断
             if "CA19-9" in elevated_markers and "CA50" in elevated_markers:
                 analysis["trend_interpretation"] = "CA19-9 + CA50同升高 → 肿瘤进展可能性↑↑（高度可信）"
                 analysis["clinical_recommendation"] = "与CA19-9单独升高相比，可靠性大幅提升，需准备治疗方案调整"
             
             if "CA125" in elevated_markers and len(elevated_markers) >= 2:
                 analysis["trend_interpretation"] += "\n CA125与其他标志物同升高 → 腹膜转移风险↑↑↑"
                 analysis["clinical_recommendation"] += "\n 需评估腹膜播散：腹膜穿刺、CA125序列监测"
             
             if "CA72-4" in elevated_markers and len(elevated_markers) >= 2:
                 analysis["trend_interpretation"] += "\n CA72-4同升高 → 肿瘤分化程度下降/侵袭性增强"
                 analysis["clinical_recommendation"] += "\n 考虑使用更强化的治疗方案"
         
         elif len(elevated_markers) == 1:
             if "CA19-9" in elevated_markers:
                 analysis["trend_interpretation"] = "CA19-9单独升高，CA50/CA125/CA72-4正常"
                 analysis["clinical_recommendation"] = "可能为炎症反应（胰炎、胆囊炎），需除外非肿瘤原因，建议：1)复查标志物+CRP/降钙素原；2)影像学评估"
         
         return analysis
     
     def _stratify_risk(self, extracted, markers):
         """根据病理类型、分化程度、标志物综合风险分层"""
         risk = {
             "level": "unknown",
             "score": 0,
             "factors": [],
             "treatment_intensity": ""
         }
         
         # 基础分数（根据病理类型）
         cancer_type = extracted.get("cancer_type", {})
         type_name = cancer_type.get("chinese_name", "")
         
         if "导管腺癌" in type_name:
             risk["score"] += 100  # 基础分数最高
         elif any(x in type_name for x in ["鳞癌", "未分化癌"]):
             risk["score"] += 90
         elif any(x in type_name for x in ["神经内分泌", "小细胞"]):
             risk["score"] += 80
         else:
             risk["score"] += 50
         
         # 分化程度调整
         grade = extracted.get("differentiation_grade", {})
         grade_name = grade.get("name", "")
         if "低分化" in grade_name:
             risk["score"] += 30
             risk["factors"].append("低分化程度")
         elif "中分化" in grade_name:
             risk["score"] += 15
             risk["factors"].append("中分化程度")
         
         # 高危标志物
         high_risk_markers = ["S100P", "E-cadherin-", "IMP3", "Ki-67", "MUC1"]
         for marker in high_risk_markers:
             if markers.get(marker) in ["positive", "high"]:
                 risk["score"] += 20
                 risk["factors"].append(f"{marker}高表达")
         
         # 风险分层
         if risk["score"] >= 130:
             risk["level"] = "极高危"
             risk["treatment_intensity"] = "强化多学科综合治疗：优先考虑新型方案(FOLFIRINOX/mFOLFIRINOX)、靶向治疗、免疫治疗组合"
         elif risk["score"] >= 100:
             risk["level"] = "高危"
             risk["treatment_intensity"] = "积极治疗：标准化疗+靶向治疗(如claudin18+/HER2+)，或新型化疗方案"
         elif risk["score"] >= 70:
             risk["level"] = "中危"
             risk["treatment_intensity"] = "标准治疗：吉西他滨+顺铂或FOLFIRINOX，根据靶点决定是否加靶向治疗"
         else:
             risk["level"] = "低危"
             risk["treatment_intensity"] = "可考虑个体化治疗：手术优先，必要时辅助化疗"
         
         return risk

# 使用示例
extractor = PathologyFeatureExtractor()
pathology_report = {...}
features = extractor.extract_pathology(pathology_report)

print(f"癌肿类型: {features['cancer_type']}")
print(f"分化程度: {features['differentiation_grade']}")
print(f"治疗考虑: {features['treatment_considerations']}")
```

---

## 第二部分：分别查询和智能匹配

### 2.1 基因特征查询

```python
def search_by_genetic_features(genetic_features):
    """基于基因特征查询临床试验"""
    
    queries = []
    
    # 构建基因特征查询
    for driver_gene in genetic_features["driver_genes"]:
        gene = driver_gene["gene"]
        mutation = driver_gene["mutation"]
        
        query = {
            "type": "genetic",
            "query.cond": f"{gene} {mutation}",
            "filter.status": "RECRUITING"
        }
        queries.append(query)
    
    # 执行查询
    all_trials = {}
    for query in queries:
        results = search_clinical_trials(**query)
        for trial in results["studies"]:
            trial_id = trial["protocolSection"]["identificationModule"]["nctId"]
            all_trials[trial_id] = trial
    
    return all_trials

# 使用
genetic_trials = search_by_genetic_features(genetic_features)
print(f"基因特征相关试验: {len(genetic_trials)}项")
```

### 2.2 病理特征查询

```python
def search_by_pathology_features(pathology_features):
    """基于病理特征查询临床试验"""
    
    queries = []
    
    # 构建病理特征查询
    cancer_type = pathology_features["cancer_type"]["chinese_name"]
    queries.append({
        "type": "pathology",
        "query.cond": f"pancreatic {cancer_type}",  # 以胰腺癌为例
        "filter.status": "RECRUITING"
    })
    
    # 添加特殊标志物查询
    for trial_keyword in pathology_features["trial_keywords"]:
        queries.append({
            "type": "marker",
            "query.term": trial_keyword,
            "query.cond": "pancreatic cancer",
            "filter.status": "RECRUITING"
        })
    
    # 执行查询
    all_trials = {}
    for query in queries:
        results = search_clinical_trials(**query)
        for trial in results["studies"]:
            trial_id = trial["protocolSection"]["identificationModule"]["nctId"]
            all_trials[trial_id] = trial
    
    return all_trials

# 使用
pathology_trials = search_by_pathology_features(pathology_features)
print(f"病理特征相关试验: {len(pathology_trials)}项")
```

### 2.3 智能匹配和排序

```python
def match_and_rank_trials(genetic_features, pathology_features):
    """匹配基因和病理特征，进行智能排序"""
    
    # 获取两组试验
    genetic_trials = search_by_genetic_features(genetic_features)
    pathology_trials = search_by_pathology_features(pathology_features)
    
    # 找交集（既符合基因又符合病理的试验）
    matched_nct_ids = set(genetic_trials.keys()) & set(pathology_trials.keys())
    
    # 如果没有完全匹配，使用并集（分别展示）
    if not matched_nct_ids:
        all_nct_ids = set(genetic_trials.keys()) | set(pathology_trials.keys())
    else:
        all_nct_ids = matched_nct_ids
    
    # 构建最终试验列表，包含匹配信息
    matched_trials = []
    for nct_id in all_nct_ids:
        trial_data = genetic_trials.get(nct_id) or pathology_trials.get(nct_id)
        
        # 判断匹配情况
        matches = []
        if nct_id in genetic_trials:
            matches.append("基因特征匹配")
        if nct_id in pathology_trials:
            matches.append("病理特征匹配")
        
        trial_info = {
            "nct_id": nct_id,
            "trial_data": trial_data,
            "matches": matches,
            "match_score": len(matches)  # 1或2
        }
        matched_trials.append(trial_info)
    
    # 按匹配度排序（完全匹配优先），然后按招募状态和国家排序
    matched_trials.sort(
        key=lambda t: (
            -t["match_score"],  # 完全匹配优先
            0 if t["trial_data"]["protocolSection"]["statusModule"]["overallStatus"] == "RECRUITING" else 1,
            0 if any("China" in loc.get("country", "") for loc in t["trial_data"]["protocolSection"].get("contactsLocationsModule", {}).get("locations", [])) else 1
        )
    )
    
    return matched_trials

# 使用示例
results = match_and_rank_trials(genetic_features, pathology_features)

for i, trial in enumerate(results[:10], 1):
    print(f"\n{i}. {trial['nct_id']}")
    print(f"   匹配: {', '.join(trial['matches'])}")
    print(f"   状态: {trial['trial_data']['protocolSection']['statusModule']['overallStatus']}")
```

---

## 第三部分：科普型报告生成

### 3.1 基因科普模块

```python
class GeneticEducationModule:
    """生成基因科普文本"""
    
    def generate_gene_explanation(self, gene_name, mutation, gene_info):
        """为患者生成易懂的基因科普"""
        
        explanation = f"""
## 您的基因检测结果解读

### {gene_name}基因 - {mutation}突变

**这个基因是什么？**
{gene_name}基因负责{gene_info['function']}。当这个基因发生突变时，细胞可能会异常生长。

**您的{mutation}突变意味着什么？**
{mutation}是{gene_name}基因上的一种常见突变。这种突变的出现意味着：
- 该突变很可能是导致您患癌的重要原因
- 这个突变使我们有机会使用针对性的治疗方法
- 您的肿瘤可能对某些特定药物更敏感

**这种突变会影响预后吗？**
{gene_info['prognosis']}

**可能的治疗方向有哪些？**
"""
        for i, direction in enumerate(gene_info['treatment_directions'], 1):
            explanation += f"\n{i}. {direction}"
        
        explanation += f"""

**下一步建议**
1. 与医生讨论是否有针对这个基因突变的靶向治疗药物
2. 查看是否有进行中的临床试验针对此突变
3. 可以咨询小胰宝助手获取更详细的基因解读
4. 加入小胰宝临床微信群：搜索微信公众号"小胰宝助手"，在公众号内获取入群链接，与医生、患者和专家交流

[小胰宝助手](https://xiaoyibao.com.cn) | [小绿卡](https://xlk.xiaoyibao.com.cn)
"""
        
        return explanation

# 使用示例
edu_module = GeneticEducationModule()
gene_explanation = edu_module.generate_gene_explanation(
    gene_name="KRAS",
    mutation="G12D",
    gene_info={
        "function": "细胞信号传导和生长调控",
        "prognosis": "KRAS G12D突变提示预后相对较差，但现在有针对性的靶向药物",
        "treatment_directions": [
            "KRAS直接抑制剂（如sotorasib）",
            "MEK抑制剂",
            "标准化疗（吉西他滨+顺铂）"
        ]
    }
)

print(gene_explanation)
```

### 3.2 病理科普模块

```python
class PathologyEducationModule:
    """生成病理科普文本"""
    
    def generate_pathology_explanation(self, pathology_features):
        """为患者生成易懂的病理科普"""
        
        explanation = """
## 您的病理检测结果解读

### 癌肿类型
"""
        
        cancer_type = pathology_features["cancer_type"]
        explanation += f"""
**您的诊断是{cancer_type['chinese_name']}**

**这意味着什么？**
{cancer_type['characteristics']}

**预后如何？**
{cancer_type['prognosis']}

**化疗敏感性**
{cancer_type['chemotherapy_sensitivity']}

**特别需要注意的**
{cancer_type['special_consideration']}

### 分化程度
"""
        
        grade_info = pathology_features["differentiation_grade"]
        explanation += f"""
**您的分化程度是：{grade_info['name']}**

**这意味着什么？**
{grade_info['prognosis']}

**对治疗的影响**
{grade_info['chemotherapy_sensitivity']}

### 特殊标志物
"""
        
        for consideration in pathology_features["treatment_considerations"]:
            explanation += f"\n{consideration['meaning']}\n推荐治疗：{consideration['treatment']}\n"
        
        return explanation

# 使用示例
pathology_explanation = PathologyEducationModule().generate_pathology_explanation(
    pathology_features
)

print(pathology_explanation)
```

---

## 第四部分：集成小胰宝工具

### 小胰宝资源集成

```python
class XiaoPancreaTools:
    """小胰宝工具集成"""
    
    RESOURCES = {
        "official_account": "小胰宝助手",  # 微信公众号搜索
        "clinical_group": "搜索'小胰宝助手'公众号加入临床群",  # 加入方式：在公众号内获取入群链接
        "assistant": "https://xiaoyibao.com.cn",
        "gene_report_helper": "https://xlk.xiaoyibao.com.cn",  # 小绿卡 - 基因报告解读
        "emergency_card_maker": "http://xhk.xiaoyibao.com.cn"  # 小红卡 - 应急卡片制作
    }
    
    @staticmethod
    def add_resource_links(report):
        """在报告中添加小胰宝资源链接"""
        
        resources_section = """
---

## 更多资源

### 小胰宝官方平台
- **小胰宝公众号**：关注获取最新胰腺癌防治资讯和临床群入口
  微信搜索：**小胰宝助手**
- **小胰宝助手**：基因报告、病理解读、临床试验匹配
  [进入助手](https://xiaoyibao.com.cn)

### 基因专业工具
- **小绿卡基因报告助手**：专业的基因报告解读和治疗方向推荐
  [进入小绿卡](https://xlk.xiaoyibao.com.cn)

### 社区和交流
- **小胰宝临床微信群**：与医生、患者、志愿者交流
  方式：搜索微信公众号**"小胰宝助手"**，在公众号内获取入群链接

### 应急支持
- **小红卡应急卡片制作**：制作个人应急卡片（包含关键病情信息）
  [制作小红卡](http://xhk.xiaoyibao.com.cn)

"""
        return report + resources_section

# 使用
final_report = XiaoPancreaTools.add_resource_links(report)
```

---

## 完整工作流示例

```python
def generate_comprehensive_clinical_report(patient_data):
    """生成完整的科普型临床增强报告"""
    
    # 第1步：提取基因特征
    genetic_extractor = GeneticFeatureExtractor()
    genetic_features = genetic_extractor.extract_mutations(
        patient_data["genetic_report"]
    )
    
    # 第2步：提取病理特征
    pathology_extractor = PathologyFeatureExtractor()
    pathology_features = pathology_extractor.extract_pathology(
        patient_data["pathology_report"]
    )
    
    # 第3步：智能匹配临床试验
    matched_trials = match_and_rank_trials(genetic_features, pathology_features)
    
    # 第4步：生成基因科普
    genetic_edu = GeneticEducationModule()
    genetic_explanation = ""
    for driver_gene in genetic_features["driver_genes"]:
        genetic_explanation += genetic_edu.generate_gene_explanation(
            driver_gene["gene"],
            driver_gene["mutation"],
            GeneticFeatureExtractor().gene_db[driver_gene["gene"]]
        )
    
    # 第5步：生成病理科普
    pathology_edu = PathologyEducationModule()
    pathology_explanation = pathology_edu.generate_pathology_explanation(
        pathology_features
    )
    
    # 第6步：生成试验推荐
    trial_recommendations = format_trial_recommendations(matched_trials)
    
    # 第7步：组合报告
    final_report = f"""
# 您的个性化临床指引报告

{genetic_explanation}

{pathology_explanation}

## 为您推荐的临床试验

{trial_recommendations}

## 后续建议

1. 与您的医生讨论这些试验的适应症和可行性
2. 如需更详细的基因解读，可使用小绿卡工具
3. 在小胰宝临床群与专家交流更多治疗选项
"""
    
    # 第8步：添加资源链接
    final_report = XiaoPancreaTools.add_resource_links(final_report)
    
    return final_report

# 使用
report = generate_comprehensive_clinical_report(patient_data)
print(report)
```

---

## 输出示例

```markdown
# 您的个性化临床指引报告

## 您的基因检测结果解读

### KRAS基因 - G12D突变

**这个基因是什么？**
KRAS基因负责细胞信号传导和生长调控。...

**您的G12D突变意味着什么？**
G12D是KRAS基因上的一种常见突变。...

**可能的治疗方向有哪些？**
1. KRAS直接抑制剂（如sotorasib）
2. MEK抑制剂
3. 标准化疗（吉西他滨+顺铂）

## 您的病理检测结果解读

### 癌肿类型 - 腺癌

您的诊断是腺癌，来源于腺体上皮。...

### 分化程度 - 中分化

您的分化程度是中分化，预后中等...

## 为您推荐的临床试验

### 🏆 完全匹配的试验（既符合基因又符合病理特征）

1. **NCT04123456** | RECRUITING
   - 试验名称：KRAS G12D Inhibitor in Advanced Pancreatic Cancer
   - 匹配原因：KRAS G12D靶向 + 腺癌适应症
   - 位置：中国上海
   - 联系：researcher@hospital.com | +86-10-12345678

### 🔍 基因特征匹配的其他试验

2. **NCT04234567** | RECRUITING
   ...

## 后续建议

1. 【重要】与您的医生讨论这些试验的适应症和可行性
2. 对于基因检测的更详细解读，可使用[小绿卡工具](https://xlk.xiaoyibao.com.cn)
3. 加入小胰宝临床微信群：搜索微信公众号**"小胰宝助手"**，在公众号内获取入群链接，与医生和其他患者交流

---

## 更多资源

- 小胰宝官方公众号
- 小胰宝助手
- 小绿卡基因报告助手
- 小红卡应急卡片制作
```

---

## 第五部分：参考资源整合

### 胰腺癌免疫表达谱速查表

**导管腺癌（PDAC）核心免疫组化模式**
```
阳性标志物：CK7, CK8, CK13, CK18, CK19, CEA, S100P, MUC1, MUC3, MUC5/6, CA19-9, CA125, claudin-4
弱阳性/阴性：PDX-1, maspin, CK4, CK17, 间皮素, CDX-2, 肌成束蛋白, IMP3, HER-2, E-cadherin, DPC4, GATA-3
阴性标志物：CK20, MUC2, 脂酶, 胰蛋白酶, 钙视网膜蛋白, 血栓调节蛋白, vimentin
```

**神经内分泌肿瘤（NET）通用筛查标志物**
```
+ CK8, CK18, CK19, CD56, 嗜铬粒蛋白, 突触素
- 需进行WHO 2019分级：G1(Ki-67≤3%), G2(Ki-67 3-20%), G3(Ki-67>20%)
```

### 49个指标快速索引

| 指标类别 | 核心指标 | 临床意义 |
|--------|--------|--------|
| **肿瘤标志物** | CA19-9, CA50, CA125, CA72-4, CEA | 多指标同升高→肿瘤进展可信度↑ |
| **诊断指标** | CK7, CK19, CK20, EMA, MUC1/2/3 | 细胞来源和分化方向 |
| **靶点指标** | claudin18, HER2, S100P | 精准治疗靶点识别 |
| **分化程度** | Ki-67, E-cadherin, IMP3, MUC1 | 预后和治疗强度评估 |
| **神经内分泌** | SYN, Cg, NSE, CD56 | 神经内分泌分化程度 |

---

**最后更新**：2026-01-19
**版本**：1.5
**主要特点**：
- ✅ 胰腺肿瘤WHO完整分类（外分泌+内分泌+罕见类型）
- ✅ 49个病理指标的完整定义和临床意义
- ✅ 多标志物同趋势分析引擎（CA19-9/CA50/CA125/CA72-4）
- ✅ 综合风险分层算法（病理+分化程度+标志物）
- ✅ 自动化提取 + 科普教育 + 智能匹配 + 小胰宝工具集成
