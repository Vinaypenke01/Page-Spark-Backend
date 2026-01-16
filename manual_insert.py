import os
import django
import sys
from pathlib import Path

# Setup Django Environment
BASE_DIR = Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from core.models import Page
import uuid

def create_dummy_page():
    print("Creating dummy page...")
    try:
        page = Page.objects.create(
            email="test@manual.com",
            prompt="Manual Test",
            page_type="landing",
            theme="dark",
            html_content="""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Test Page</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-gray-900 text-white flex items-center justify-center min-h-screen">
    <div class="text-center">
        <h1 class="text-6xl font-bold mb-4">It Works!</h1>
        <p class="text-xl text-gray-400">This page was manually inserted to test rendering.</p>
    </div>
</body>
</html>
            """,
            meta_data={'manual': True}
        )
        print(f"SUCCESS: Created Page {page.id}")
        return str(page.id)
    except Exception as e:
        print(f"ERROR: {e}")
        return None

if __name__ == "__main__":
    create_dummy_page()
