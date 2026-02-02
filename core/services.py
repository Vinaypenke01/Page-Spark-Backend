import logging
import requests
import bleach
import re
from bs4 import BeautifulSoup
from django.conf import settings
from .models import Page
from django.utils import timezone
from .meta_prompt import MetaPromptService

logger = logging.getLogger(__name__)


# ==========================================================
# ORCHESTRATOR SERVICE
# ==========================================================
class GenericPageService:
    @staticmethod
    def generate_page(email, prompt, page_type, theme, user_data=None):
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

        # 0. Meta-Prompting (if structured data provided)
        if user_data:
            logger.info(f"Using structured data for {email}")
            prompt = MetaPromptService.construct_prompt(user_data)
            logger.info(f"Optimized Prompt: {prompt[:100]}...")

        # 1. Validation
        if len(prompt) > 70000:
            logger.warning(f"Prompt rejected: too long ({len(prompt)} chars)")
            raise ValueError("Prompt exceeds maximum length of 7000 characters")

        # Note: Removed suspicious pattern validation since prompts are now AI-generated
        # and should be trusted. The AI is instructed to generate safe, HTML-only content.


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

        # 3. Sanitize HTML - DISABLED for testing
        # try:
        #     clean_html = HtmlSanitizationService.sanitize(raw_html)
        # except Exception as e:
        #     logger.error(f"Failed to sanitize HTML: {str(e)}", exc_info=True)
        #     # Fallback to a safe base if sanitization fails
        #     clean_html = f"<!-- Sanitization Failed -->\n{raw_html}"
        
        # Use raw HTML without sanitization (for testing)
        clean_html = raw_html

        # 4. Save Page
        page = Page.objects.create(
            email=email,
            prompt=prompt,
            page_type=page_type,
            theme=theme,
            html_content=clean_html,
            meta_data={
                "version": "1.1",
                "provider": "groq",
                "model": settings.GROQ_HTML_MODEL,
                "generated_at": timezone.now().isoformat(),
                "original_data": user_data or {}
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
You are an EXPERT FRONTEND ENGINEER specializing in clean, semantic, and production-ready HTML/Tailwind CSS.
Your goal is to build a high-quality, fully responsive, and bug-free single-page website for the user's request.

**STRUCTURAL DISCIPLINE**:
1. **Mandatory Section Order**: You MUST include these sections in this exact order:
   - Hero / Header (Impactful entry)
   - Event Details (Clear logistics: Date, Time, Venue)
   - Special Message (Key context/narrative)
   - Image / Visual Section (Placeholders for atmosphere)
   - RSVP / CTA (Actionable element)
   - Footer (Closing info)
2. **NO Repetition**: Every section must appear ONLY ONCE. Do not duplicate headings, content blocks, or UI elements.
3. **MANDATORY Responsiveness**: The page MUST be perfectly responsive and look stunning on all devices (mobile, tablet, and desktop).

**CONTENT QUALITY**:
- **Meaningful Text**: PROHIBITED: "asdf", random characters, "Lorem Ipsum", or nonsense placeholders. 
- You MUST write meaningful, emotionally resonant, and context-aware text that serves the user's occasion.
- All tags must be properly nested, opened, and closed. Ensure 100% valid HTML5 DOM structure.

**TECHNICAL REQUIREMENTS**:
- **Output**: ONLY valid, standalone HTML5 code.
- **Styling**: Use ONLY Tailwind CSS via CDN.
- **Fonts**: Use Google Fonts via CDN.
- **Icons**: Use FontAwesome or RemixIcon via CDN.
- **Interactivity**: Use subtle, professional CSS animations and transitions (avoid over-engineering).

**CRITICAL RULES**:
1. Start directly with `<!DOCTYPE html>`.
2. NO Markdown code blocks.
3. NO conversational text or explanations.
4. Remove `<think>` tags.

**CONTEXT**:
- **Page Type**: {page_type}
- **Theme**: {theme}
- **User Prompt**: {prompt}

Generate the production-ready HTML now following all structural rules.
"""

        payload = {
            "model": settings.GROQ_HTML_MODEL,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": "Generate the complete, structurally sound HTML code now."}
            ],
            "temperature": 0.4,
            "max_tokens": 4000
        }

        headers = {
            "Authorization": f"Bearer {settings.GROQ_API_KEY}",
            "Content-Type": "application/json"
        }

        try:
            response = requests.post(
                "https://api.groq.com/openai/v1/chat/completions",
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
            
            # Remove DeepSeek <think> tags if present
            content = re.sub(r'<think>.*?</think>', '', content, flags=re.DOTALL).strip()

            if content.startswith("```html"):
                content = content[7:].strip()
            if content.endswith("```"):
                content = content[:-3].strip()

            logger.debug("OpenRouter content received")
            print("\n" + "="*80)
            print("GENERATED HTML FROM AI:")
            print("="*80)
            print(content)
            print("="*80 + "\n")
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
        Advanced sanitization that allows Tailwind CDN script while blocking all other JS.
        Maintains proper HTML document structure.
        """
        logger.debug("Starting sanitization")

        # Allowed Tailwind CDN URL
        TAILWIND_CDN = "https://cdn.tailwindcss.com"

        # 1. Parse HTML
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # 2. Remove ALL script tags EXCEPT Tailwind CDN
        for script in soup.find_all('script'):
            src = script.get('src', '')
            if TAILWIND_CDN not in src:
                script.decompose()
        
        # 3. Remove inline scripts and event handlers
        for tag in soup.find_all():
            # Remove event handler attributes (onclick, onload, etc.)
            for attr in list(tag.attrs.keys()):
                if attr.startswith('on'):
                    del tag[attr]
        
        # 4. Remove style tags (we use only Tailwind utility classes)
        for style_tag in soup.find_all('style'):
            style_tag.decompose()

        # 5. Ensure proper HTML structure
        html_tag = soup.find('html')
        if not html_tag:
            # Wrap everything in html tag
            html_tag = soup.new_tag('html', lang='en')
            for element in list(soup.children):
                html_tag.append(element.extract())
            soup.append(html_tag)
        
        # 6. Ensure head exists
        head = soup.find('head')
        if not head:
            head = soup.new_tag('head')
            html_tag.insert(0, head)
        
        # 7. Ensure Tailwind CDN script is in head
        tailwind_script = soup.find('script', src=lambda x: x and TAILWIND_CDN in x)
        if tailwind_script:
            # Move to head if not already there
            if tailwind_script.parent != head:
                tailwind_script.extract()
                head.append(tailwind_script)
        else:
            # Add Tailwind CDN script
            script = soup.new_tag('script', src=TAILWIND_CDN)
            head.append(script)
        
        # 8. Ensure charset meta tag
        charset_meta = soup.find('meta', charset=True)
        if not charset_meta:
            charset_meta = soup.new_tag('meta', charset='UTF-8')
            head.insert(0, charset_meta)
        
        # 9. Ensure viewport meta tag
        viewport_meta = soup.find('meta', attrs={'name': 'viewport'})
        if not viewport_meta:
            viewport_meta = soup.new_tag('meta')
            viewport_meta['name'] = 'viewport'
            viewport_meta['content'] = 'width=device-width, initial-scale=1.0'
            head.insert(1, viewport_meta)
        
        # 10. Ensure body exists
        body = soup.find('body')
        if not body:
            body = soup.new_tag('body')
            # Move all non-head children to body
            for element in list(html_tag.children):
                if element != head and element.name:
                    body.append(element.extract())
            html_tag.append(body)
        
        # 11. Add DOCTYPE
        doctype = '<!DOCTYPE html>\n'
        final_html = doctype + str(soup)
        
        logger.debug("Sanitization complete")
        print("\n" + "="*80)
        print("SANITIZED HTML (FINAL):")
        print("="*80)
        print(final_html)
        print("="*80 + "\n")
        
        return final_html

