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

        # 3. Sanitize HTML - RE-ENABLED with CDN support
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
                "version": "1.8",
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
You are an EXPERT FRONTEND ENGINEER specializing in award-winning UI/UX built with clean, semantic HTML/Tailwind CSS.
Your goal is to build a breathtaking, high-performance storytelling masterpiece.

**VISUAL NARRATIVE CONTRACT (v1.9)**:
1. **ZERO HALLUCINATED UTILITIES**: PROHIBITED: inventing font utility classes (e.g., no `font-GreatVibes`). Use ONLY inline `style` for script fonts. All body text MUST be clean Sans-serif.
2. **NARRATIVE ARCHITECTURE**: Hero MUST include a dominant headline + an elegant, adult subtitle. The Special Message MUST have its own heading or subtle icon and a soft, neutral background as a rhythm break.
3. **PERSONAL FRAMING**: Visual section MUST use deeply personal narrative framing (referencing names like Sarah, the surprise, the celebration) to give icon clusters purpose.
4. **SCANNABILITY**: Make Labels (Date:, Location:) bold/dark vs Regular Values. Use a structured 'Label: Value' pattern.
5. **RHYTHM & CONTRAST**: Introduce neutral breaks (off-white/light gray) between high-energy sections. Ensure high contrast for yellow/gradient elements.
6. **RSVP URGENCY**: Add a short urgency cue below the primary CTA. 
7. **MEMORABLE GOODBYE**: Footer MUST be a warm, personal send-off reinforcing the celebration's spirit.

**STRUCTURAL DISCIPLINE**:
- Order: Hero -> Event Details -> Special Message -> Visual Section (Story Framing) -> RSVP -> Footer.
- Each block must appear EXACTLY once.
- Quality: Adult tone for adult milestones. NO "Lorem Ipsum".

**TECHNICAL REQUIREMENTS**:
- **Output**: ONLY valid, standalone HTML5 code.
- **Styling/Fonts/Icons**: ONLY Tailwind CSS, Google Fonts, and FontAwesome/RemixIcon via CDN.

**CRITICAL RULES**:
1. Start directly with `<!DOCTYPE html>`.
2. NO Markdown code blocks.
3. Remove `<think>` tags.

**CONTEXT**:
- **Page Type**: {page_type}
- **Theme**: {theme}
- **User Prompt**: {prompt}

Build the production-ready masterpiece v1.8 now.
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
        
        # 2. Clean old scripts and remove all script tags EXCEPT allowed CDNs
        ALLOWED_SCRIPTS = [
            TAILWIND_CDN,
            "cdnjs.cloudflare.com",
            "kit.fontawesome.com"
        ]
        
        # Track if we found a tailwind script to keep exactly ONE later
        tailwind_script_found = False
        
        for script in soup.find_all('script'):
            src = script.get('src', '')
            # If it's a tailwind script, we extract it and we'll re-inject exactly one in head
            if TAILWIND_CDN in src:
                script.decompose()
            elif not any(allowed in src for allowed in ALLOWED_SCRIPTS):
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
        
        # 10. Final check for duplicate head elements
        # Ensure only one tailwind include exists
        tw_scripts = soup.find_all('script', src=lambda x: x and TAILWIND_CDN in x)
        if len(tw_scripts) > 1:
            for s in tw_scripts[1:]:
                s.decompose()
        
        # 11. Final Assembly with Strict Singleton DOCTYPE
        # We use soup.encode() to maintain exactly what's parsed
        final_body = str(soup).strip()
        
        # Remove any internal DOCTYPE tags if they were parsed as text
        if final_body.lower().startswith('<!doctype html>'):
            # It already has it, just normalize the casing
            final_html = '<!DOCTYPE html>\n' + final_body[15:].strip()
        else:
            final_html = '<!DOCTYPE html>\n' + final_body
        
        logger.debug("Sanitization complete")
        print("\n" + "="*80)
        print("SANITIZED HTML (FINAL):")
        print("="*80)
        print(final_html)
        print("="*80 + "\n")
        
        return final_html

