import json

class MetaPromptService:
    @staticmethod
    def construct_prompt(user_data):
        occasion = user_data.get('occasion', 'generic').replace('_', ' ').title()
        title = user_data.get('title', '')
        theme = user_data.get('theme', 'modern')

        prompt_parts = [
            f"You are a professional web designer and frontend developer.",
            f"Create a visually attractive, single-page {occasion} website.",
            "",
            f"Page Title: {title}",
            f"Design Theme: {theme.title()}",
            "",
            "### Content Details"
        ]

        exclude_keys = ['occasion', 'email', 'theme', 'title', 'specific_fields']

        for key, value in user_data.items():
            if key not in exclude_keys and value:
                readable_key = key.replace('_', ' ').title()
                prompt_parts.append(f"- {readable_key}: {value}")

        specific_fields = user_data.get('specific_fields', {})
        if specific_fields:
            prompt_parts.append("")
            prompt_parts.append("### Occasion-Specific Details")
            for key, value in specific_fields.items():
                if value and value != 'undefined':
                    readable_key = key.replace('_', ' ').title()
                    prompt_parts.append(f"- {readable_key}: {value}")

        prompt_parts.extend([
            "",
            "### Design & Layout Instructions",
            f"- Use a {theme.lower()} visual style suitable for a {occasion}.",
            "- Follow this section order:",
            "  1. Hero section (title, short message)",
            "  2. Event details (date, time, venue)",
            "  3. Additional information / special message",
            "  4. Contact or RSVP section",
            "- Use clean spacing, clear typography, and balanced layout.",
            "- Add subtle decorative elements relevant to the occasion.",
            "",
            "### Technical Requirements",
            "- Output ONLY valid HTML with Tailwind CSS utility classes.",
            "- Use semantic HTML5 elements.",
            "- Include Tailwind CSS CDN in the <head> section: <script src=\"https://cdn.tailwindcss.com\"></script>",
            "- Use ONLY Tailwind CSS utility classes for styling - NO custom CSS or <style> tags.",
            "- Do NOT include explanations, markdown, or comments.",
            "- Do NOT include external libraries or images (except Tailwind CDN).",
            "- Do NOT include any JavaScript code.",
            "- The page must be fully responsive using Tailwind's responsive classes.",
            "- Use Tailwind's color palette and spacing system.",
            "- Example: Use classes like 'bg-blue-500', 'text-white', 'p-4', 'rounded-lg', etc."
        ])

        return "\n".join(prompt_parts)
