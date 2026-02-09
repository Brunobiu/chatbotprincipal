"""
Testes de Segurança - FASE 4
Valida proteções contra XSS, headers de segurança
"""
import pytest
from app.core.sanitizer import (
    HTMLSanitizer,
    JavaScriptSanitizer,
    URLSanitizer,
    strip_html_tags,
    sanitize_html,
    validate_no_xss,
    validate_safe_url
)


class TestHTMLSanitizer:
    """Testes de sanitização HTML"""
    
    def test_strip_all_tags(self):
        """Testa remoção de todas as tags"""
        html = "<p>Hello <strong>World</strong></p>"
        result = HTMLSanitizer.strip_all_tags(html)
        assert result == "Hello World"
    
    def test_strip_script_tags(self):
        """Testa remoção de tags script"""
        html = "<script>alert('xss')</script>Hello"
        result = HTMLSanitizer.strip_all_tags(html)
        assert "<script>" not in result
        assert "Hello" in result
    
    def test_sanitize_removes_dangerous_tags(self):
        """Testa remoção de tags perigosas"""
        dangerous_html = """
        <script>alert('xss')</script>
        <iframe src="evil.com"></iframe>
        <object data="evil.swf"></object>
        <p>Safe content</p>
        """
        result = HTMLSanitizer.sanitize(dangerous_html)
        
        assert "<script>" not in result
        assert "<iframe>" not in result
        assert "<object>" not in result
        assert "Safe content" in result
    
    def test_sanitize_removes_event_handlers(self):
        """Testa remoção de event handlers"""
        html = '<img src="x" onerror="alert(1)">'
        result = HTMLSanitizer.sanitize(html)
        assert "onerror" not in result.lower()
    
    def test_sanitize_removes_javascript_protocol(self):
        """Testa remoção de javascript: protocol"""
        html = '<a href="javascript:alert(1)">Click</a>'
        result = HTMLSanitizer.sanitize(html)
        assert "javascript:" not in result.lower()
    
    def test_escape_html(self):
        """Testa escape de caracteres HTML"""
        text = '<script>alert("xss")</script>'
        result = HTMLSanitizer.escape_html(text)
        assert "&lt;script&gt;" in result
        assert "<script>" not in result


class TestJavaScriptSanitizer:
    """Testes de detecção de JavaScript malicioso"""
    
    def test_detects_script_tag(self):
        """Testa detecção de tag script"""
        malicious = "<script>alert('xss')</script>"
        assert not JavaScriptSanitizer.is_safe(malicious)
    
    def test_detects_javascript_protocol(self):
        """Testa detecção de javascript: protocol"""
        malicious = "javascript:alert(1)"
        assert not JavaScriptSanitizer.is_safe(malicious)
    
    def test_detects_onerror_handler(self):
        """Testa detecção de onerror handler"""
        malicious = '<img src=x onerror="alert(1)">'
        assert not JavaScriptSanitizer.is_safe(malicious)
    
    def test_detects_iframe(self):
        """Testa detecção de iframe"""
        malicious = '<iframe src="evil.com"></iframe>'
        assert not JavaScriptSanitizer.is_safe(malicious)
    
    def test_detects_eval(self):
        """Testa detecção de eval()"""
        malicious = "eval('alert(1)')"
        assert not JavaScriptSanitizer.is_safe(malicious)
    
    def test_safe_text_passes(self):
        """Testa que texto seguro passa"""
        safe = "Este é um texto normal sem código malicioso"
        assert JavaScriptSanitizer.is_safe(safe)
    
    def test_sanitize_raises_on_malicious(self):
        """Testa que sanitize lança erro em código malicioso"""
        malicious = "<script>alert('xss')</script>"
        
        with pytest.raises(ValueError, match="malicioso"):
            JavaScriptSanitizer.sanitize(malicious)
    
    def test_sanitize_allows_safe_text(self):
        """Testa que sanitize permite texto seguro"""
        safe = "Texto normal"
        result = JavaScriptSanitizer.sanitize(safe)
        assert result == safe


class TestURLSanitizer:
    """Testes de sanitização de URLs"""
    
    def test_allows_http(self):
        """Testa que permite http://"""
        url = "http://example.com"
        assert URLSanitizer.is_safe_url(url)
    
    def test_allows_https(self):
        """Testa que permite https://"""
        url = "https://example.com"
        assert URLSanitizer.is_safe_url(url)
    
    def test_allows_mailto(self):
        """Testa que permite mailto:"""
        url = "mailto:test@example.com"
        assert URLSanitizer.is_safe_url(url)
    
    def test_blocks_javascript(self):
        """Testa que bloqueia javascript:"""
        url = "javascript:alert(1)"
        assert not URLSanitizer.is_safe_url(url)
    
    def test_blocks_data_protocol(self):
        """Testa que bloqueia data:"""
        url = "data:text/html,<script>alert(1)</script>"
        assert not URLSanitizer.is_safe_url(url)
    
    def test_blocks_vbscript(self):
        """Testa que bloqueia vbscript:"""
        url = "vbscript:msgbox(1)"
        assert not URLSanitizer.is_safe_url(url)
    
    def test_blocks_file_protocol(self):
        """Testa que bloqueia file:"""
        url = "file:///etc/passwd"
        assert not URLSanitizer.is_safe_url(url)
    
    def test_sanitize_raises_on_dangerous(self):
        """Testa que sanitize lança erro em URL perigosa"""
        dangerous = "javascript:alert(1)"
        
        with pytest.raises(ValueError, match="não permitido"):
            URLSanitizer.sanitize(dangerous)


class TestHelperFunctions:
    """Testes de funções helper"""
    
    def test_strip_html_tags_helper(self):
        """Testa helper strip_html_tags"""
        html = "<p>Hello</p>"
        result = strip_html_tags(html)
        assert result == "Hello"
    
    def test_sanitize_html_helper(self):
        """Testa helper sanitize_html"""
        html = "<script>alert(1)</script><p>Safe</p>"
        result = sanitize_html(html)
        assert "<script>" not in result
        assert "Safe" in result
    
    def test_validate_no_xss_helper(self):
        """Testa helper validate_no_xss"""
        safe = "texto normal"
        result = validate_no_xss(safe)
        assert result == safe
        
        malicious = "<script>alert(1)</script>"
        with pytest.raises(ValueError):
            validate_no_xss(malicious)
    
    def test_validate_safe_url_helper(self):
        """Testa helper validate_safe_url"""
        safe = "https://example.com"
        result = validate_safe_url(safe)
        assert result == safe
        
        dangerous = "javascript:alert(1)"
        with pytest.raises(ValueError):
            validate_safe_url(dangerous)


class TestXSSVectors:
    """Testes com vetores reais de XSS"""
    
    def test_xss_vector_img_onerror(self):
        """Testa vetor: <img src=x onerror=alert(1)>"""
        xss = '<img src=x onerror=alert(1)>'
        assert not JavaScriptSanitizer.is_safe(xss)
    
    def test_xss_vector_svg_onload(self):
        """Testa vetor: <svg onload=alert(1)>"""
        xss = '<svg onload=alert(1)>'
        assert not JavaScriptSanitizer.is_safe(xss)
    
    def test_xss_vector_body_onload(self):
        """Testa vetor: <body onload=alert(1)>"""
        xss = '<body onload=alert(1)>'
        assert not JavaScriptSanitizer.is_safe(xss)
    
    def test_xss_vector_iframe_srcdoc(self):
        """Testa vetor: <iframe srcdoc="<script>alert(1)</script>">"""
        xss = '<iframe srcdoc="<script>alert(1)</script>">'
        assert not JavaScriptSanitizer.is_safe(xss)
    
    def test_xss_vector_object_data(self):
        """Testa vetor: <object data="javascript:alert(1)">"""
        xss = '<object data="javascript:alert(1)">'
        assert not JavaScriptSanitizer.is_safe(xss)
    
    def test_xss_vector_embed_src(self):
        """Testa vetor: <embed src="javascript:alert(1)">"""
        xss = '<embed src="javascript:alert(1)">'
        assert not JavaScriptSanitizer.is_safe(xss)


# Para rodar os testes:
# pytest apps/backend/tests/test_security_fase4.py -v
