"""
Web UI HTML渲染模块

功能：
- Markdown转HTML
- 报告页面框架生成
- 选项卡导航
- 响应式设计
"""

from typing import Dict, Optional
import json


class ReportHTMLRenderer:
    """报告HTML渲染"""
    
    def __init__(self):
        """初始化渲染器"""
        self.style = self._get_default_styles()
    
    def render_password_page(self, password: str) -> str:
        """
        生成密码输入页面
        
        Args:
            password: 正确的密码（嵌入到HTML中）
            
        Returns:
            str: 完整的HTML页面
        """
        html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>患者病情报告</title>
    <style>
        {self.style}
    </style>
</head>
<body>
    <!-- 密码保护面板 -->
    <div id="passwordPanel" class="password-container">
        <div class="password-box">
            <div class="lock-icon">🔒</div>
            <h1>患者病情报告</h1>
            <p class="subtitle">请输入访问密码</p>
            
            <div class="input-group">
                <input 
                    type="password" 
                    id="passwordInput" 
                    class="password-input"
                    placeholder="输入访问密码"
                    onkeypress="if(event.key==='Enter') verifyPassword()"
                >
                <button class="btn-primary" onclick="verifyPassword()">访问报告</button>
            </div>
            
            <div id="errorMessage" class="error-message"></div>
            
            <div class="password-tips">
                <p>⏰ 此链接有效期：24小时</p>
                <p>🔐 密码仅在您的浏览器本地验证</p>
            </div>
        </div>
    </div>
    
    <!-- 报告内容（初始隐藏） -->
    <div id="reportContent" class="report-container" style="display: none;">
        <!-- 顶部导航 -->
        <div class="top-nav">
            <div class="nav-title">
                <h1>患者病情报告</h1>
            </div>
            <button class="btn-logout" onclick="logout()">🚪 登出</button>
        </div>
        
        <!-- 选项卡导航 -->
        <div class="tabs-container">
            <button class="tab-button active" onclick="switchTab('overview')">
                📋 速览
            </button>
            <button class="tab-button" onclick="switchTab('complete')">
                📄 完整报告
            </button>
            <button class="tab-button" onclick="switchTab('consultation')">
                ❓ 问诊清单
            </button>
            <button class="tab-button" onclick="switchTab('appendix')">
                📎 附件
            </button>
        </div>
        
        <!-- Tab 1: 速览 -->
        <div id="overview" class="tab-content active">
            <div class="report-content" id="overviewContent">
                <!-- 患者速览卡动态加载 -->
            </div>
        </div>
        
        <!-- Tab 2: 完整报告 -->
        <div id="complete" class="tab-content">
            <div class="report-content" id="completeContent">
                <!-- 完整报告动态加载 -->
            </div>
        </div>
        
        <!-- Tab 3: 问诊清单 -->
        <div id="consultation" class="tab-content">
            <div class="report-content" id="consultationContent">
                <!-- 问诊清单动态加载 -->
            </div>
        </div>
        
        <!-- Tab 4: 附件 -->
        <div id="appendix" class="tab-content">
            <div class="report-content" id="appendixContent">
                <!-- 附件内容动态加载 -->
            </div>
        </div>
        
        <!-- 操作按钮组 -->
        <div class="actions-container">
            <button class="btn-action" onclick="window.print()">🖨️ 打印</button>
            <button class="btn-action" onclick="downloadPDF()">📥 下载PDF</button>
            <button class="btn-action" onclick="logout()">🚪 登出</button>
        </div>
    </div>
    
    <script>
        // 密码验证逻辑
        const CORRECT_PASSWORD = "{password}";
        let errorCount = 0;
        let lastErrorTime = 0;
        const MAX_ATTEMPTS = 3;
        const RETRY_DELAY = 5000; // 5秒
        
        function verifyPassword() {{
            const input = document.getElementById('passwordInput').value;
            const errorDiv = document.getElementById('errorMessage');
            
            // 检查是否在延迟期间
            if (errorCount >= MAX_ATTEMPTS) {{
                const timeSinceError = Date.now() - lastErrorTime;
                if (timeSinceError < RETRY_DELAY) {{
                    const remainingSeconds = Math.ceil((RETRY_DELAY - timeSinceError) / 1000);
                    errorDiv.textContent = `密码错误次数过多，请在 ${{remainingSeconds}} 秒后重试`;
                    return;
                }} else {{
                    // 重置计数
                    errorCount = 0;
                }}
            }}
            
            if (input === CORRECT_PASSWORD) {{
                // 密码正确
                document.getElementById('passwordPanel').style.display = 'none';
                document.getElementById('reportContent').style.display = 'block';
                
                // 保存session
                sessionStorage.setItem('authenticated', 'true');
                sessionStorage.setItem('expiry', Date.now() + 24*60*60*1000);
                
                errorCount = 0;
                errorDiv.textContent = '';
            }} else {{
                // 密码错误
                errorCount++;
                lastErrorTime = Date.now();
                const remainingAttempts = Math.max(0, MAX_ATTEMPTS - errorCount);
                
                if (remainingAttempts > 0) {{
                    errorDiv.textContent = `密码错误，还有 ${{remainingAttempts}} 次机会`;
                }} else {{
                    errorDiv.textContent = `密码错误次数过多，请等待 5 秒后重试`;
                }}
                
                // 清空输入框
                document.getElementById('passwordInput').value = '';
            }}
        }}
        
        // Tab切换逻辑
        function switchTab(tabName) {{
            // 隐藏所有tab内容
            document.querySelectorAll('.tab-content').forEach(el => {{
                el.classList.remove('active');
            }});
            
            // 移除所有tab按钮的active类
            document.querySelectorAll('.tab-button').forEach(el => {{
                el.classList.remove('active');
            }});
            
            // 显示选中的tab
            document.getElementById(tabName).classList.add('active');
            
            // 高亮选中的按钮
            event.target.classList.add('active');
        }}
        
        // 打印
        function doPrint() {{
            window.print();
        }}
        
        // PDF下载
        function downloadPDF() {{
            // TODO: 实现PDF导出（需要html2pdf库）
            alert('PDF导出功能开发中');
        }}
        
        // 登出
        function logout() {{
            if (confirm('确认登出？登出后需要重新输入密码才能访问报告。')) {{
                sessionStorage.removeItem('authenticated');
                sessionStorage.removeItem('expiry');
                document.getElementById('passwordPanel').style.display = 'flex';
                document.getElementById('reportContent').style.display = 'none';
                document.getElementById('passwordInput').value = '';
                document.getElementById('errorMessage').textContent = '';
                errorCount = 0;
            }}
        }}
        
        // 页面加载时检查session
        window.addEventListener('load', function() {{
            const auth = sessionStorage.getItem('authenticated');
            const expiry = sessionStorage.getItem('expiry');
            
            if (auth && expiry && Date.now() < parseInt(expiry)) {{
                document.getElementById('passwordPanel').style.display = 'none';
                document.getElementById('reportContent').style.display = 'block';
            }}
        }});
        
        // 防止缓存
        window.addEventListener('beforeunload', function() {{
            if (sessionStorage.getItem('authenticated')) {{
                // 用户已认证但要离开，清除session（可选）
                // sessionStorage.removeItem('authenticated');
            }}
        }});
    </script>
</body>
</html>
"""
        return html
    
    def render_complete_page(
        self,
        password: str,
        overview_html: str,
        complete_report_html: str,
        consultation_html: str,
        appendix_items: Dict[str, str]
    ) -> str:
        """
        生成完整的报告页面
        
        Args:
            password: 访问密码
            overview_html: 速览卡HTML
            complete_report_html: 完整报告HTML
            consultation_html: 问诊清单HTML
            appendix_items: 附件内容字典 {'popular': '...', 'viz': '...', 'markers': '...'}
            
        Returns:
            str: 完整的HTML页面
        """
        # 生成password page
        html = self.render_password_page(password)
        
        # 准备内容数据（转义反引号）
        overview_safe = overview_html.replace('`', '\\`')
        complete_safe = complete_report_html.replace('`', '\\`')
        consultation_safe = consultation_html.replace('`', '\\`')
        popular_safe = appendix_items.get('popular', '').replace('`', '\\`')
        viz_safe = appendix_items.get('viz', '').replace('`', '\\`')
        markers_safe = appendix_items.get('markers', '').replace('`', '\\`')
        
        # 注入内容脚本
        inject_script = f"""
        <script>
            window.reportData = {{
                overview: `{overview_safe}`,
                complete: `{complete_safe}`,
                consultation: `{consultation_safe}`,
                appendix: {{
                    popular: `{popular_safe}`,
                    viz: `{viz_safe}`,
                    markers: `{markers_safe}`
                }}
            }};
            
            // 动态加载内容
            function loadReportData() {{
                if (sessionStorage.getItem('authenticated')) {{
                    document.getElementById('overviewContent').innerHTML = window.reportData.overview;
                    document.getElementById('completeContent').innerHTML = window.reportData.complete;
                    document.getElementById('consultationContent').innerHTML = window.reportData.consultation;
                    
                    // 生成附件列表
                    let appendixHtml = '<h2>📚 附件内容</h2><ul>';
                    if (window.reportData.appendix.popular) {{
                        appendixHtml += '<li><a href="#" onclick="showAppendix(\\'popular\\')">🎓 患者科普版</a></li>';
                    }}
                    if (window.reportData.appendix.viz) {{
                        appendixHtml += '<li><a href="#" onclick="showAppendix(\\'viz\\')">📊 医学可视化</a></li>';
                    }}
                    if (window.reportData.appendix.markers) {{
                        appendixHtml += '<li><a href="#" onclick="showAppendix(\\'markers\\')">📈 标志物趋势</a></li>';
                    }}
                    appendixHtml += '</ul>';
                    document.getElementById('appendixContent').innerHTML = appendixHtml;
                }}
            }}
            
            function showAppendix(type) {{
                alert('查看' + type);
                return false;
            }}
            
            // 页面加载时动态加载数据
            window.addEventListener('load', loadReportData);
        </script>
        """
        
        # 在closing tag前注入
        html = html.replace('</body>', inject_script + '</body>')
        
        return html
    
    def markdown_to_html(self, markdown_content: str) -> str:
        """
        简单的Markdown转HTML（基础支持）
        
        Args:
            markdown_content: Markdown内容
            
        Returns:
            str: HTML内容
        """
        try:
            import markdown
            return markdown.markdown(
                markdown_content,
                extensions=['tables', 'toc', 'sane_lists', 'fenced_code']
            )
        except ImportError:
            # 如果markdown库不可用，做基础转换
            return self._basic_markdown_to_html(markdown_content)
    
    def _basic_markdown_to_html(self, md: str) -> str:
        """基础的Markdown转HTML"""
        html = md
        
        # 标题
        html = html.replace('\n# ', '\n<h1>')
        html = html.replace('</h1>\n', '</h1>\n')
        
        # 段落
        html = '<p>' + html.replace('\n\n', '</p>\n<p>') + '</p>'
        
        return html
    
    def _get_default_styles(self) -> str:
        """获取默认样式"""
        return """
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            background-color: #f5f5f5;
            color: #333;
            line-height: 1.6;
        }
        
        /* 密码容器 */
        .password-container {
            display: flex;
            align-items: center;
            justify-content: center;
            min-height: 100vh;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        }
        
        .password-box {
            background: white;
            border-radius: 10px;
            padding: 2rem;
            box-shadow: 0 10px 40px rgba(0, 0, 0, 0.2);
            text-align: center;
            max-width: 400px;
            width: 90%;
        }
        
        .lock-icon {
            font-size: 3rem;
            margin-bottom: 1rem;
        }
        
        .password-box h1 {
            font-size: 1.8rem;
            margin-bottom: 0.5rem;
            color: #333;
        }
        
        .subtitle {
            color: #666;
            margin-bottom: 1.5rem;
            font-size: 0.95rem;
        }
        
        .input-group {
            margin-bottom: 1.5rem;
        }
        
        .password-input {
            width: 100%;
            padding: 0.75rem;
            margin-bottom: 1rem;
            border: 1px solid #ddd;
            border-radius: 5px;
            font-size: 1rem;
            font-family: 'Courier New', monospace;
        }
        
        .password-input:focus {
            outline: none;
            border-color: #667eea;
            box-shadow: 0 0 5px rgba(102, 126, 234, 0.3);
        }
        
        .btn-primary {
            width: 100%;
            padding: 0.75rem;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 5px;
            font-size: 1rem;
            cursor: pointer;
            transition: all 0.3s ease;
        }
        
        .btn-primary:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 20px rgba(102, 126, 234, 0.4);
        }
        
        .error-message {
            color: #e74c3c;
            margin-top: 1rem;
            font-size: 0.9rem;
            min-height: 1.2rem;
        }
        
        .password-tips {
            margin-top: 1.5rem;
            padding-top: 1.5rem;
            border-top: 1px solid #eee;
            font-size: 0.85rem;
            color: #999;
        }
        
        .password-tips p {
            margin: 0.5rem 0;
        }
        
        /* 报告容器 */
        .report-container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            min-height: 100vh;
        }
        
        .top-nav {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 1.5rem;
            border-bottom: 1px solid #eee;
            background: #f9f9f9;
        }
        
        .nav-title h1 {
            font-size: 1.5rem;
            color: #333;
        }
        
        .btn-logout {
            padding: 0.5rem 1rem;
            background: #e74c3c;
            color: white;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            font-size: 0.9rem;
        }
        
        .btn-logout:hover {
            background: #c0392b;
        }
        
        /* Tab导航 */
        .tabs-container {
            display: flex;
            gap: 0;
            border-bottom: 2px solid #eee;
            background: white;
            position: sticky;
            top: 0;
            z-index: 100;
        }
        
        .tab-button {
            padding: 1rem 1.5rem;
            background: none;
            border: none;
            cursor: pointer;
            font-size: 1rem;
            color: #666;
            border-bottom: 3px solid transparent;
            transition: all 0.3s ease;
            white-space: nowrap;
        }
        
        .tab-button:hover {
            color: #333;
            background: #f9f9f9;
        }
        
        .tab-button.active {
            color: #667eea;
            border-bottom-color: #667eea;
            font-weight: 600;
        }
        
        /* Tab内容 */
        .tab-content {
            display: none;
            padding: 2rem;
            animation: fadeIn 0.3s ease;
        }
        
        .tab-content.active {
            display: block;
        }
        
        @keyframes fadeIn {
            from {
                opacity: 0;
                transform: translateY(10px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
        
        .report-content {
            line-height: 1.8;
            color: #333;
        }
        
        .report-content h2 {
            margin-top: 1.5rem;
            margin-bottom: 1rem;
            color: #667eea;
            border-left: 4px solid #667eea;
            padding-left: 1rem;
        }
        
        .report-content h3 {
            margin-top: 1.2rem;
            margin-bottom: 0.8rem;
            color: #555;
        }
        
        .report-content p {
            margin-bottom: 1rem;
        }
        
        .report-content ul, .report-content ol {
            margin-left: 2rem;
            margin-bottom: 1rem;
        }
        
        .report-content li {
            margin-bottom: 0.5rem;
        }
        
        .report-content table {
            width: 100%;
            border-collapse: collapse;
            margin: 1rem 0;
        }
        
        .report-content table th,
        .report-content table td {
            padding: 0.75rem;
            text-align: left;
            border: 1px solid #ddd;
        }
        
        .report-content table th {
            background: #f9f9f9;
            font-weight: 600;
        }
        
        /* 操作按钮 */
        .actions-container {
            display: flex;
            gap: 1rem;
            padding: 2rem;
            justify-content: center;
            border-top: 1px solid #eee;
            background: #f9f9f9;
        }
        
        .btn-action {
            padding: 0.75rem 1.5rem;
            background: white;
            border: 2px solid #667eea;
            color: #667eea;
            border-radius: 5px;
            cursor: pointer;
            font-size: 0.95rem;
            transition: all 0.3s ease;
        }
        
        .btn-action:hover {
            background: #667eea;
            color: white;
        }
        
        /* 响应式设计 */
        @media (max-width: 768px) {
            .tabs-container {
                flex-wrap: wrap;
            }
            
            .tab-button {
                flex: 1;
                padding: 0.75rem;
                font-size: 0.9rem;
                min-width: 80px;
            }
            
            .tab-content {
                padding: 1.5rem;
            }
            
            .password-box {
                padding: 1.5rem;
            }
            
            .actions-container {
                flex-direction: column;
            }
            
            .btn-action {
                width: 100%;
            }
        }
        
        /* 打印样式 */
        @media print {
            .password-container,
            .top-nav,
            .tabs-container,
            .actions-container,
            .btn-logout {
                display: none;
            }
            
            .report-content {
                color: black;
            }
            
            .tab-content {
                display: block !important;
                page-break-inside: avoid;
            }
        }
        """


# 使用示例
if __name__ == '__main__':
    renderer = ReportHTMLRenderer()
    
    # 生成密码页面
    html = renderer.render_password_page('K7@mQx9pL2$j')
    
    with open('/tmp/test_report.html', 'w', encoding='utf-8') as f:
        f.write(html)
    
    print("HTML已生成：/tmp/test_report.html")
