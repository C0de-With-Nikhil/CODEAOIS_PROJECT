import os
import re
from playwright.sync_api import sync_playwright
from rich.console import Console
from codeaois.models.llm_interface import call_openrouter

console = Console()

def generate_vision_code(user_input, full_context=""):
    """Opens local HTML files in a headless browser and uses Vision AI to critique the UI."""
    
    # Look for an HTML file mentioned in the user's prompt
    match = re.search(r'([a-zA-Z0-9_\-\.]+\.html)', user_input)
    if not match:
        return "❌ Please specify an HTML file to test (e.g., 'look at clock.html')."
    
    file_name = match.group(1)
    file_path = os.path.abspath(file_name)
    
    if not os.path.exists(file_path):
        return f"❌ Could not find {file_name} in the current directory."

    screenshot_path = "debug_screenshot.png"
    
    console.print(f"[dim]👁️  [Vision Engine] Launching headless browser to view {file_name}...[/dim]")
    
    try:
        # Spin up the hidden browser and take a picture!
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(f"file://{file_path}")
            page.screenshot(path=screenshot_path)
            browser.close()
    except Exception as e:
        return f"❌ Headless Browser Error: {e}"

    console.print(f"[dim]📸 [Vision Engine] Screenshot captured! Sending to Vision AI...[/dim]")
    
    sys_prompt = "You are an Expert UI/UX Frontend Reviewer. Look at the provided screenshot of the user's web page. Critique the design, layout, alignment, and colors. Point out any visible CSS bugs or ugly elements, and provide the exact CSS code to fix them."
    
    # Send the screenshot to your custom AI model! (Requires the updated llm_interface.py from earlier)
    review = call_openrouter(sys_prompt, user_input, intent="chat", history=[], image_path=screenshot_path)
    
    return f"{review}"