import json

class MetaPromptService:
    @staticmethod
    def construct_prompt(user_data):
        sub_type = user_data.get('sub_type', 'wishes')
        title = user_data.get('title', '')
        theme = user_data.get('theme', 'modern')

        visual_richness = user_data.get('visual_richness', 'medium')
        ui_tier = 'festive'

        # Determine the goal and narrative focus based on sub-type
        if sub_type == 'wishes':
            page_intent = "Birthday Wishes"
            intent_goal = "Create an emotional, heart-centered birthday wish page with expressive visuals and zero effort for the user."
            section_order = "Hero -> Emotional Message (Story) -> Visual Section (Personal framing) -> Warm Closure (Goodbye)"
        else:
            page_intent = "Birthday Invitation"
            intent_goal = "Create a clear, informative birthday invitation page focusing on Date, Time, and Venue details for guests."
            section_order = "Hero -> Event Details (Timing/Location) -> Special Message -> Visual Section -> RSVP -> Footer"

        prompt_parts = [
            f"You are a professional web designer and frontend developer.",
            f"Create a visually stunning, single-page {page_intent} website.",
            "",
            f"Goal: {intent_goal}",
            f"Page Title: {title}",
            f"Design Theme: {theme.title()}",
            f"Visual Richness Level: {visual_richness.title()}",
            f"UI Quality Mode: {ui_tier.title()}",
            "",
            "### Design Contract (v2.1 Visual Narrative)",
            "- **Unlocked Expression**: You are ENCOURAGED to use expressive layouts, gradients, and celebratory color combinations.",
            "- **Drama Permission**: Hero and primary call-to-action sections may use bold typography and high-impact visual anchors.",
            "- **Zero Hallucination**: Use ONLY valid Tailwind CSS utilities. Use inline style for custom fonts if needed.",
            "- **Adult Milestone Awareness**: Use an adult/elegant tone for milestones (e.g., 21st, 50th). Avoid childlike themes unless explicitly for a child.",
            "- **Technical**: Output ONLY valid HTML5 and Tailwind CSS. No JavaScript.",
            "",
            "### Content Details"
        ]

        exclude_keys = ['occasion', 'sub_type', 'email', 'theme', 'title', 'specific_fields']

        for key, value in user_data.items():
            if key not in exclude_keys and value:
                readable_key = key.replace('_', ' ').title()
                prompt_parts.append(f"- {readable_key}: {value}")

        specific_fields = user_data.get('specific_fields', {})
        gender = specific_fields.get('gender', 'Neutral')
        color_suggestion = ""
        if gender == 'Female':
            color_suggestion = "Use a soft, feminine palette (e.g., Pink, Lavender, Rose Gold, or Pastels)."
        elif gender == 'Male':
            color_suggestion = "Use a masculine, sophisticated palette (e.g., Royal Blue, Slate, Charcoal, or Deep Emerald)."
        else:
            color_suggestion = "Use a vibrant, gender-neutral palette (e.g., Purple, Teal, Yellow, or Modern Gradients)."

        if specific_fields:
            prompt_parts.append("")
            prompt_parts.append(f"### {page_intent} Specifics")
            for key, value in specific_fields.items():
                if value and value != 'undefined':
                    readable_key = key.replace('_', ' ').title()
                    prompt_parts.append(f"- {readable_key}: {value}")

        prompt_parts.extend([
            "",
            "### v2.1 Emotional Narrative & Visual Rhythm",
            f"- **Intent-Focused Storytelling**: This is a {page_intent}. Ensure the layout reflects this purpose.",
            f"- **Color Palette Suggestion**: {color_suggestion}",
            "- **Visual Section Framing**: Use deeply personal framing—reference names, the relationship, or specific celebration energy.",
            "- **Rhythm & Contrast**: Use neutral sections (off-whites/gray-50) between high-energy sections to prevent visual fatigue.",
            "- **Event Scannability**: (If Invitation) Use clear 'Label: Value' blocks with bold labels for Date, Time, and Venue.",
            "- **Memorable Send-off**: The footer must be a warm, personal wave that reinforces the celebration's spirit.",
            "",
            "### Layout & Structural Alignment",
            f"- **Order**: {section_order}.",
            "- Each block must appear EXACTLY once. Avoid all repetitions.",
            "- Ensure 100% mobile responsiveness and professional-grade accessibility."
        ])

        return "\n".join(prompt_parts)
