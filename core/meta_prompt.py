import json

class MetaPromptService:
    @staticmethod
    def construct_prompt(user_data):
        occasion = user_data.get('occasion', 'generic').replace('_', ' ').title()
        title = user_data.get('title', '')
        theme = user_data.get('theme', 'modern')

        visual_richness = user_data.get('visual_richness', 'medium')
        ui_tier = user_data.get('ui_tier', 'festive' if 'birthday' in occasion.lower() else 'premium')

        # Check if any image URLs are provided
        has_images = any('http' in str(v) for k, v in user_data.items() if 'image' in k or 'photo' in k)
        
        prompt_parts = [
            f"You are a professional web designer and frontend developer.",
            f"Create a visually stunning, single-page {occasion} website.",
            "",
            f"Page Title: {title}",
            f"Design Theme: {theme.title()}",
            f"Visual Richness Level: {visual_richness.title()}",
            f"UI Quality Mode: {ui_tier.title()}",
            "",
            "### Design Contract (v1.7 Visual Harmony)",
            "- **Unlocked Expression**: You are ENCOURAGED to use expressive layouts, gradients (`bg-gradient-to-*`), and celebratory color combinations. Use ONLY official Tailwind colors (`pink`, `rose`, `purple`, `violet`, `yellow`, `amber`, `sky`, `blue`).",
            "- **Drama Permission**: The Hero and RSVP sections may ignore standard spacing and layout rules to create maximum visual impact and drama.",
            "- **Font Application (CRITICAL)**: If a custom font is used, import it via Google Fonts. Apply fonts using inline `style=\"font-family: '...';\"` or valid Tailwind-compatible usage. PROHIBITED: inventing font utility classes.",
            "- **Image vs. Mood**: STRICT: NO `<img>` tags unless URLs are provided. The Visual/Centerpiece section must create MOOD using icons (recommended sizing), layered shapes, and color blocks—not just list icons.",
            "- **Content Safety**: NEVER output gibberish or 'Lorem Ipsum'. Rewrite unclear text into a warm, meaningful message.",
            "- **Age Consistency**: Use an adult/elegant tone for milestones (e.g., 21st). Avoid childlike language unless for a small child.",
            "- **Technical**: Output ONLY valid HTML5 and Tailwind CSS. No JavaScript.",
            "",
            "### Content Details"
        ]

        exclude_keys = ['occasion', 'email', 'theme', 'title', 'specific_fields', 'visual_richness', 'ui_tier']

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
            "### v1.9 Emotional Narrative & Visual Rhythm",
            "- **Zero Hallucinated Utilities**: PROHIBITED: inventing font utility classes (e.g., NO `font-GreatVibes`). Use ONLY inline `style=\"font-family: '...';\"` for script fonts imported via Google Fonts. All body text must use clean Sans-serif.",
            "- **Hero & Message Identity**: The Hero section must include an elegant, adult subtitle below the headline. The Special Message section must have its own identity (e.g., 'A Note from the Family') or a subtle unique icon, and use a soft, neutral background section to provide a visual break.",
            "- **Event Scannability**: Use a 'Label: Value' pattern for details. Visually differentiate by making Labels (e.g., Date:, Location:) slightly bolder or darker than the regular weight Values.",
            "- **Visual Storytelling**: Rewrite the Visual section framing to be deeply personal—reference names (e.g., Sarah), the surprise, or specific celebration energy. Group icons tightly or center-align vertically for impact.",
            "- **RSVP Urgency & CTA**: Strengthen the RSVP business goal with a short urgency cue below the primary CTA (e.g., 'Please confirm by...'). Ensure the button is the unavoidable visual anchor.",
            "- **Color Rhythm & Softening**: Rebalance gradients by introducing soft neutral sections (off-white, light gray, or warm neutral) between high-energy blocks. This prevents color fatigue while maintaining vibrancy.",
            "- **Memorable Goodbye**: Rewrite the footer to sound like a warm, personal send-off that reinforces the celebration's emotion, not just a polite closing.",
            "- **Accessibility & Contrast**: Ensure sufficient color contrast for yellow buttons and gradient text. Maintain professional-grade readability at all times.",
            "",
            "### Narrative Flow & Emotional Continuity",
            "- **Storytelling**: Every section must feel like the next chapter with smooth transitions.",
            "- **Emotional Goodbye**: The Footer must be a warm closing wave—thank the visitor and express anticipation.",
            "",
            "### Layout & Structural Alignment",
            "- **Order**: Hero -> Event Details -> Special Message -> Visual Section -> RSVP -> Footer.",
            "- Each block must appear EXACTLY once. Prohibit all repetitions.",
            "- Icons must be functional and placed beside/before the info they represent.",
            "- Ensure 100% responsiveness on all device sizes."
        ])

        return "\n".join(prompt_parts)
