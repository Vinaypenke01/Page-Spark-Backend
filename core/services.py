import logging
import requests
import bleach
from bs4 import BeautifulSoup
from django.conf import settings
from .models import Page
from django.utils import timezone

logger = logging.getLogger(__name__)


# ==========================================================
# ORCHESTRATOR SERVICE
# ==========================================================
class GenericPageService:
    @staticmethod
    def generate_page(email, prompt, page_type, theme):
        """
        Full page generation flow:
        1. Validates input
        2. Generate HTML via OpenRouter
        3. Sanitize HTML
        4. Save page to DB
        """
        logger.info(f"Starting page generation for {email}", extra={
            'page_type': page_type,
            'theme': theme,
            'prompt_preview': prompt[:50]
        })

        # 1. Validation
        if len(prompt) > 5000:
            logger.warning(f"Prompt rejected: too long ({len(prompt)} chars)")
            raise ValueError("Prompt exceeds maximum length of 5000 characters")

        dangerous_patterns = ['{{', '}}', '{%', '%}', '<script', 'javascript:']
        if any(pattern in prompt.lower() for pattern in dangerous_patterns):
            logger.warning(f"Prompt rejected: suspicious patterns detected for {email}")
            raise ValueError("Prompt contains potentially unsafe content")

        # 2. Generate HTML
        try:
            raw_html = OpenRouterService.generate_html(
                prompt=prompt,
                page_type=page_type,
                theme=theme
            )
        except Exception as e:
            logger.error(f"Failed to generate raw HTML: {str(e)}", exc_info=True)
            raise

        # 3. Sanitize HTML
        try:
            clean_html = HtmlSanitizationService.sanitize(raw_html)
        except Exception as e:
            logger.error(f"Failed to sanitize HTML: {str(e)}", exc_info=True)
            # Fallback to a safe base if sanitization fails
            clean_html = f"<!-- Sanitization Failed -->\n{raw_html}"

        # 4. Save Page
        page = Page.objects.create(
            email=email,
            prompt=prompt,
            page_type=page_type,
            theme=theme,
            html_content=clean_html,
            meta_data={
                "version": "1.1",
                "provider": "openrouter",
                "model": settings.OPENROUTER_MODEL,
                "generated_at": timezone.now().isoformat()
            }
        )

        logger.info(f"Page generated successfully: {page.id}")
        return page


# ==========================================================
# OPENROUTER SERVICE
# ==========================================================
class OpenRouterService:
    @staticmethod
    def generate_html(prompt, page_type, theme):
        logger.debug("Preparing OpenRouter request")

        system_prompt = f"""
You are an expert web developer specializing in modern, responsive designs.

Generate a complete, single-file HTML5 page based on the following instructions.

Instructions:
1. Return ONLY the raw HTML content. Do not include markdown code blocks or additional text.
2. Use Tailwind CSS via the official CDN.
3. No custom JavaScript is allowed.
4. Use semantic HTML elements (header, footer, main, section, etc.).
5. Ensure a polished, professional UI.
6. Design Theme: {theme}
7. Page Category: {page_type}

User Request:
"{prompt}"
"""

        payload = {
            "model": settings.OPENROUTER_MODEL,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": "Build the page now as per the requirements."}
            ],
            "temperature": 0.7,
            "max_tokens": 3000
        }

        headers = {
            "Authorization": f"Bearer {settings.OPENROUTER_API_KEY}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://pagegen.app",
            "X-Title": "PageSpark AI"
        }

        try:
            response = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                json=payload,
                headers=headers,
                timeout=60
            )
            response.raise_for_status()
            
            data = response.json()
            if "choices" not in data or not data["choices"]:
                logger.error(f"OpenRouter empty/invalid response: {data}")
                raise ValueError("Incomplete response from AI provider")

            content = data["choices"][0]["message"]["content"]
            
            # Clean up potential markdown wrapper if LLM didn't follow instructions
            content = content.strip()
            if content.startswith("```html"):
                content = content[7:].strip()
            if content.endswith("```"):
                content = content[:-3].strip()

            logger.debug("OpenRouter content received")
            return content

        except Exception as e:
            logger.error(f"OpenRouter API call failed: {str(e)}", exc_info=True)
            return OpenRouterService.get_fallback_html(prompt)

    @staticmethod
    def get_fallback_html(prompt):
        return f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Service Unavailable</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-slate-50 text-slate-900 flex items-center justify-center min-h-screen p-6">
    <div class="max-w-md w-full bg-white shadow-xl rounded-2xl p-8 border border-slate-200">
        <div class="text-red-500 mb-4">
            <svg class="h-12 w-12" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
            </svg>
        </div>
        <h1 class="text-2xl font-bold mb-2">Service Temporarily Unavailable</h1>
        <p class="text-slate-600 mb-6">We couldn't generate your page due to a technical issue with our AI provider. Please try again in a few minutes.</p>
        <div class="bg-slate-100 p-4 rounded-lg text-sm font-mono text-slate-700 break-words">
            <strong>Your Prompt:</strong> {prompt}
        </div>
    </div>
</body>
</html>
"""


# ==========================================================
# HTML SANITIZATION SERVICE
# ==========================================================
class HtmlSanitizationService:
    @staticmethod
    def sanitize(html_content):
        """
        Advanced sanitization using bleach for tag stripping and 
        BeautifulSoup for structure enforcement and CDN management.
        """
        logger.debug("Starting sanitization")

        allowed_tags = [
            "html", "head", "body", "title", "meta", "link", "style",
            "div", "span", "section", "article", "header", "footer",
            "nav", "main", "aside",
            "h1", "h2", "h3", "h4", "h5", "h6",
            "p", "br", "hr", "blockquote", "pre", "code",
            "ul", "ol", "li", "dl", "dt", "dd",
            "table", "thead", "tbody", "tfoot", "tr", "th", "td",
            "img", "a", "button", "form", "label",
            "input", "textarea", "select", "option",
            "strong", "em", "b", "i", "small", "sub", "sup",
            "svg", "path", "circle", "rect", "line", "g", "defs", "linearGradient", "stop"
        ]

        allowed_attributes = {
            "*": [
                "class", "id", "style", "href", "src", "alt", "title",
                "type", "name", "value", "placeholder", "required", "checked",
                "width", "height", "viewBox", "xmlns",
                "fill", "stroke", "d", "r", "cx", "cy", "x1", "y1", "x2", "y2"
            ],
            "meta": ["charset", "name", "content"],
            "link": ["rel", "href", "crossorigin", "integrity"],
            "a": ["href", "target", "rel"]
        }

        # 1. Pre-cleanup with BeautifulSoup to remove scripts/styles entirely
        soup = BeautifulSoup(html_content, 'html.parser')
        for s in soup(['script', 'style']):
            s.decompose()
        
        pre_clean_html = str(soup)

        # 2. Bleach Cleanup
        clean_html = bleach.clean(
            pre_clean_html,
            tags=allowed_tags,
            attributes=allowed_attributes,
            strip=True
        )

        # 3. Structure Fixup and Tailwind Injection
        soup = BeautifulSoup(clean_html, 'html.parser')
        
        # Ensure Tailwind CDN is in the head
        tailwind_url = "https://cdn.tailwindcss.com"
        script_tag = soup.find('script', src=tailwind_url)
        
        if not script_tag:
            head = soup.find('head') or soup.new_tag('head')
            if not soup.find('head'):
                if soup.html:
                    soup.html.insert(0, head)
                else:
                    new_html = soup.new_tag('html')
                    new_html.append(head)
                    soup.append(new_html)
            
            new_script = soup.new_tag('script', src=tailwind_url)
            head.append(new_script)

        logger.debug("Sanitization complete")
        return str(soup)
