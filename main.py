from pynput import keyboard
from pynput.keyboard import Key, Controller
import pyperclip
import time
import httpx
from string import Template

keyboard_controller = Controller()

OLLAMA_ENDPOINT = "http://localhost:11434/api/generate"
OLLAMA_CONFIG = {
    "model": "mistral:7b",
    "keep_alive": "5m",
    "stream": False
}

PROMPT_TEMPLATE = Template(
    """Fix all typos and casing and punctuation in this text, but preserve all new line characters:

$text

Return only the corrected text, don't include a preamble."""
)

def fix_text(text):
    prompt = PROMPT_TEMPLATE.substitute(text=text)
    response = httpx.post(
        OLLAMA_ENDPOINT,
        json={"prompt": prompt, **OLLAMA_CONFIG},
        headers={"Content-Type": "application/json"},
        timeout=10
    )
    if response.status_code != 200:
        print("Error:", response.text)
        return None
    return response.json()["response"].strip()

def fix_current_line():
    with keyboard_controller.pressed(Key.ctrl):
        with keyboard_controller.pressed(Key.shift):
            keyboard_controller.tap(Key.left)
    fix_selection()

def fix_selection():
    # Copy to clipboard
    with keyboard_controller.pressed(Key.ctrl):
        keyboard_controller.tap('c')
    
    time.sleep(0.2)  # wait for clipboard to update
    text = pyperclip.paste()

    fixed_text = fix_text(text)
    if not fixed_text:
        return

    pyperclip.copy(fixed_text)
    time.sleep(0.1)

    # Paste back the text
    with keyboard_controller.pressed(Key.ctrl):
        keyboard_controller.tap('v')

def on_f9():
    fix_current_line()

def on_f10():
    fix_selection()

with keyboard.GlobalHotKeys({
    '<f9>': on_f9,
    '<f10>': on_f10
}) as h:
    h.join()
