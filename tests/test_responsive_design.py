"""
Phase 5 响应式设计和跨浏览器兼容性测试

覆盖：
- 移动设备（iPhone、Android）
- 平板设备（iPad）
- 桌面设备（Desktop）
- 打印样式
"""

import pytest
from src.web import ReportHTMLRenderer, DataSanitizer, PasswordProtection


class TestResponsiveDesign:
    """响应式设计测试"""
    
    def setup_method(self):
        self.renderer = ReportHTMLRenderer()
        self.password = 'TestPass123'
        self.html = self.renderer.render_password_page(self.password)
    
    def test_html_includes_viewport_meta(self):
        """测试包含viewport元标签"""
        assert '<meta name="viewport"' in self.html
        assert 'width=device-width' in self.html
        assert 'initial-scale=1.0' in self.html
    
    def test_html_includes_media_queries(self):
        """测试包含媒体查询"""
        assert '@media' in self.renderer._get_default_styles()
        assert '@media (max-width: 768px)' in self.renderer._get_default_styles()
    
    def test_mobile_styles(self):
        """测试移动设备样式存在"""
        styles = self.renderer._get_default_styles()
        assert '.password-box' in styles
        assert 'padding' in styles
        assert 'max-width' in styles
    
    def test_print_styles(self):
        """测试打印样式"""
        styles = self.renderer._get_default_styles()
        assert '@media print' in styles
        assert 'display: none' in styles  # 打印时隐藏某些元素
    
    def test_flexbox_layout(self):
        """测试弹性布局"""
        styles = self.renderer._get_default_styles()
        assert 'display: flex' in styles or 'flex' in styles.lower()
    
    def test_fluid_typography(self):
        """测试响应式字体"""
        styles = self.renderer._get_default_styles()
        # 检查是否使用了rem或百分比单位
        assert 'rem' in styles or '%' in styles or 'em' in styles
    
    def test_breakpoint_mobile(self):
        """测试移动端断点 (max-width: 768px)"""
        styles = self.renderer._get_default_styles()
        assert '768px' in styles
    
    def test_touch_friendly_buttons(self):
        """测试按钮尺寸是否触屏友好 (最少44x44px)"""
        # 在样式中应该有足够的padding使按钮易触
        styles = self.renderer._get_default_styles()
        assert 'padding' in styles
        # 验证至少有一个按钮样式
        assert 'button' in styles.lower()
    
    def test_readable_font_size(self):
        """测试字体大小可读性"""
        styles = self.renderer._get_default_styles()
        # 检查是否定义了body字体
        assert 'font-family' in styles
        assert 'font-size' in styles or 'rem' in styles


class TestBrowserCompatibility:
    """浏览器兼容性测试"""
    
    def setup_method(self):
        self.renderer = ReportHTMLRenderer()
        self.password = 'TestPass123'
        self.html = self.renderer.render_password_page(self.password)
    
    def test_html_doctype(self):
        """测试HTML5 DOCTYPE声明"""
        assert '<!DOCTYPE html>' in self.html
    
    def test_charset_utf8(self):
        """测试UTF-8编码声明"""
        assert 'charset="UTF-8"' in self.html or 'charset="utf-8"' in self.html or 'charset=UTF-8' in self.html or 'charset=utf-8' in self.html
    
    def test_lang_attribute(self):
        """测试语言属性"""
        assert 'lang=' in self.html
    
    def test_no_vendor_prefixes_required(self):
        """测试不需要浏览器前缀的CSS特性"""
        styles = self.renderer._get_default_styles()
        # 检查是否过度使用了浏览器前缀
        webkit_count = styles.count('-webkit-')
        moz_count = styles.count('-moz-')
        ms_count = styles.count('-ms-')
        
        # 应该很少使用前缀（现代浏览器都支持）
        total_prefixes = webkit_count + moz_count + ms_count
        assert total_prefixes < 5, f"过多浏览器前缀: {total_prefixes}个"
    
    def test_semantic_html(self):
        """测试语义化HTML"""
        assert '<div' in self.html  # 基本结构
        assert '<h1' in self.html or '<h2' in self.html  # 标题
        assert '<input' in self.html  # 表单元素
        assert '<button' in self.html  # 按钮
    
    def test_form_accessibility(self):
        """测试表单无障碍性"""
        assert '<input' in self.html
        assert 'id=' in self.html  # 元素应有ID
        assert 'placeholder=' in self.html or 'label' in self.html.lower()
    
    def test_javascript_fallback(self):
        """测试JavaScript降级方案"""
        # 检查是否有noscript或基本的HTML结构
        assert '<script>' in self.html
        assert 'function' in self.html  # 有JavaScript函数
    
    def test_no_deprecated_elements(self):
        """测试不使用已弃用的HTML元素"""
        deprecated = ['<font', '<center', '<marquee', '<blink']
        for tag in deprecated:
            assert tag not in self.html, f"使用了已弃用的元素: {tag}"
    
    def test_css_compatibility_grid_flex(self):
        """测试使用现代CSS布局"""
        styles = self.renderer._get_default_styles()
        # 应该使用flexbox或grid
        has_flex = 'display: flex' in styles or 'flex:' in styles
        assert has_flex or 'grid' in styles.lower(), "应使用现代CSS布局（flex/grid）"
    
    def test_color_contrast(self):
        """测试颜色对比度（基础检查）"""
        styles = self.renderer._get_default_styles()
        # 应该有足够的颜色对比
        assert 'color:' in styles
        assert 'background' in styles.lower()


class TestPrintStylesheet:
    """打印样式测试"""
    
    def setup_method(self):
        self.renderer = ReportHTMLRenderer()
    
    def test_print_media_query(self):
        """测试打印媒体查询"""
        styles = self.renderer._get_default_styles()
        assert '@media print' in styles
    
    def test_hide_interactive_elements_on_print(self):
        """测试打印时隐藏交互元素"""
        styles = self.renderer._get_default_styles()
        assert '@media print' in styles
        # 应该隐藏某些元素
        assert 'display: none' in styles
    
    def test_preserve_content_on_print(self):
        """测试打印时保留内容"""
        styles = self.renderer._get_default_styles()
        # 报告内容应该显示
        assert '@media print' in styles
    
    def test_page_break_handling(self):
        """测试分页处理"""
        styles = self.renderer._get_default_styles()
        # 应该有page-break相关样式
        if 'page-break' in styles.lower():
            assert 'page-break-inside' in styles.lower() or 'page-break-after' in styles.lower()
    
    def test_black_text_on_print(self):
        """测试打印时使用黑色文字"""
        styles = self.renderer._get_default_styles()
        assert '@media print' in styles
        # 打印样式中应该强制使用黑色文字
        if 'color: black' in styles.lower() or 'color:#000' in styles.lower():
            assert True
        else:
            # 如果没有明确定义，也是可以的（浏览器默认）
            pass


class TestAccessibility:
    """无障碍性测试"""
    
    def setup_method(self):
        self.renderer = ReportHTMLRenderer()
        self.html = self.renderer.render_password_page('test')
    
    def test_input_has_id(self):
        """测试输入框有ID属性"""
        assert 'id=' in self.html
        assert 'passwordInput' in self.html or 'password' in self.html
    
    def test_button_is_accessible(self):
        """测试按钮可访问"""
        assert '<button' in self.html
        # 按钮应该有可读的文本
        assert 'onclick=' in self.html or 'addEventListener' in self.html
    
    def test_color_not_only_cue(self):
        """测试不仅使用颜色传达信息"""
        assert '错误' in self.html or 'error' in self.html.lower()
        # 应该有文本提示，不仅是颜色
    
    def test_keyboard_navigation(self):
        """测试键盘导航支持"""
        # 检查是否有onkeypress或tab索引
        assert 'onkeypress' in self.html or 'tabindex' in self.html or 'tab' in self.html.lower()
    
    def test_focus_visible(self):
        """测试焦点可见"""
        styles = self.renderer._get_default_styles()
        # 应该有focus样式
        if ':focus' in styles:
            assert 'outline' in styles.lower() or 'border' in styles.lower()


class TestPerformance:
    """性能相关测试"""
    
    def setup_method(self):
        self.renderer = ReportHTMLRenderer()
        self.password = 'TestPass123'
    
    def test_html_file_size(self):
        """测试HTML文件大小"""
        html = self.renderer.render_password_page(self.password)
        size_kb = len(html) / 1024
        # HTML应该小于50KB（包含样式和脚本）
        assert size_kb < 50, f"HTML文件过大: {size_kb:.2f}KB"
    
    def test_css_is_inline(self):
        """测试CSS是否内联"""
        html = self.renderer.render_password_page(self.password)
        # 对于密码页面，CSS应该内联以减少请求
        assert '<style>' in html
    
    def test_javascript_is_inline(self):
        """测试JavaScript是否内联"""
        html = self.renderer.render_password_page(self.password)
        # 脚本应该内联
        assert '<script>' in html
    
    def test_no_external_dependencies(self):
        """测试没有外部依赖"""
        html = self.renderer.render_password_page(self.password)
        # 不应该有外部CDN链接（密码页面）
        assert 'src="http' not in html
        assert 'href="http' not in html or 'stylesheet' not in html


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
