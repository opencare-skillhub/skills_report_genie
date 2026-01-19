"""
中国临床试验注册中心(chiCTR)检索客户端
支持中国国内临床试验检索
参考: https://www.chictr.org.cn/
"""

import requests
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from bs4 import BeautifulSoup
import logging
from urllib.parse import urlencode

logger = logging.getLogger(__name__)


@dataclass
class ChiCTRTrial:
    """chiCTR试验记录"""
    trial_id: str
    title: str
    condition: str  # 疾病
    phase: str  # 试验阶段
    status: str  # 招募状态
    institution: str  # 机构
    sponsor: str  # 赞助方
    recruit_status: str  # 招募状态（招募中/已完成等）
    start_date: Optional[str]
    country: str
    province: Optional[str]
    url: str


class ChiCTRClient:
    """
    中国临床试验注册中心客户端
    
    支持：
    - 基因特异性试验检索 (KRAS, BRCA等)
    - 肿瘤类型检索
    - 药物/治疗方式检索
    - 招募状态过滤
    """
    
    BASE_URL = "https://www.chictr.org.cn"
    SEARCH_URL = f"{BASE_URL}/searchproj.html"
    
    def __init__(self, timeout: int = 30):
        """
        初始化chiCTR客户端
        
        Args:
            timeout: 请求超时时间（秒）
        """
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        })
    
    def search(
        self,
        title: Optional[str] = None,
        condition: Optional[str] = None,
        recruit_status: Optional[str] = None,
        phase: Optional[str] = None,
        country: str = "China",
        **kwargs
    ) -> List[ChiCTRTrial]:
        """
        搜索chiCTR试验
        
        Args:
            title: 试验标题关键词 (如 "KRAS")
            condition: 疾病关键词 (如 "胰腺癌")
            recruit_status: 招募状态 (如 "招募中", "已完成")
            phase: 试验阶段 (如 "Phase 1/2", "Phase 2", "Phase 3")
            country: 国家 (默认"China")
            **kwargs: 其他搜索参数
        
        Returns:
            ChiCTRTrial列表
        """
        params = {
            'country': country,
        }
        
        if title:
            params['title'] = title
        if condition:
            params['studyailment'] = condition
        if recruit_status:
            params['recruitmentstatus'] = recruit_status
        if phase:
            params['studystage'] = phase
        
        # 合并其他参数
        params.update(kwargs)
        
        try:
            url = f"{self.SEARCH_URL}?{urlencode(params)}"
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()
            
            # 解析HTML
            trials = self._parse_trials(response.text)
            return trials
            
        except requests.exceptions.RequestException as e:
            logger.error(f"chiCTR搜索失败: {e}")
            return []
    
    def search_genetic_mutation(self, gene_name: str, mutation: str) -> List[ChiCTRTrial]:
        """
        搜索特定基因突变的试验
        
        Args:
            gene_name: 基因名称 (如 "KRAS")
            mutation: 突变 (如 "G12C")
        
        Returns:
            ChiCTRTrial列表
        """
        query = f"{gene_name} {mutation}"
        return self.search(title=query, condition="胰腺癌")
    
    def search_cancer_trials(
        self,
        cancer_type: str,
        treatment: Optional[str] = None,
        phase: Optional[str] = None
    ) -> List[ChiCTRTrial]:
        """
        搜索特定癌肿类型的试验
        
        Args:
            cancer_type: 癌肿类型 (如 "胰腺癌", "胰腺导管腺癌")
            treatment: 治疗方式 (如 "化疗", "靶向治疗", "免疫治疗")
            phase: 试验阶段
        
        Returns:
            ChiCTRTrial列表
        """
        keywords = [cancer_type]
        if treatment:
            keywords.append(treatment)
        
        return self.search(
            condition=cancer_type,
            title=" ".join(keywords),
            phase=phase
        )
    
    def _parse_trials(self, html_content: str) -> List[ChiCTRTrial]:
        """
        从HTML内容解析试验信息
        
        注：实际实现取决于网站的HTML结构
        当前为占位符实现
        """
        trials = []
        
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # 查找试验列表容器（需要根据实际网站结构调整）
            trial_rows = soup.find_all('tr', class_='trTr')
            
            for row in trial_rows:
                try:
                    # 提取字段（需要根据实际HTML结构调整）
                    cells = row.find_all('td')
                    
                    if len(cells) >= 6:
                        trial = ChiCTRTrial(
                            trial_id=cells[0].get_text(strip=True),
                            title=cells[1].get_text(strip=True),
                            condition=cells[2].get_text(strip=True),
                            phase=cells[3].get_text(strip=True),
                            status=cells[4].get_text(strip=True),
                            institution=cells[5].get_text(strip=True),
                            sponsor="",  # 需要从详情页获取
                            recruit_status=cells[4].get_text(strip=True),
                            start_date=None,
                            country="China",
                            province=None,
                            url=self._extract_trial_url(row)
                        )
                        trials.append(trial)
                        
                except (IndexError, AttributeError) as e:
                    logger.debug(f"解析试验行失败: {e}")
                    continue
                    
        except Exception as e:
            logger.error(f"解析HTML失败: {e}")
        
        return trials
    
    def _extract_trial_url(self, row) -> str:
        """从行元素提取试验URL"""
        link = row.find('a')
        if link and link.get('href'):
            url = link['href']
            if not url.startswith('http'):
                url = f"{self.BASE_URL}/{url}"
            return url
        return ""
    
    def get_trial_details(self, trial_id: str) -> Optional[Dict[str, Any]]:
        """
        获取试验详细信息
        
        Args:
            trial_id: 试验ID
        
        Returns:
            试验详细信息字典
        """
        try:
            url = f"{self.BASE_URL}/showproj.html?proj_id={trial_id}"
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()
            
            details = self._parse_trial_details(response.text)
            return details
            
        except Exception as e:
            logger.error(f"获取试验详情失败: {e}")
            return None
    
    def _parse_trial_details(self, html_content: str) -> Dict[str, Any]:
        """解析试验详细信息"""
        # 占位符实现，需要根据实际HTML结构调整
        return {
            "title": "",
            "description": "",
            "inclusion_criteria": "",
            "exclusion_criteria": "",
            "contact": "",
            "address": ""
        }


def create_chictr_client() -> ChiCTRClient:
    """创建chiCTR客户端"""
    return ChiCTRClient()
