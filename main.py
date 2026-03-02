# Imports
import random
import os

from textual.app import App, ComposeResult
from textual.containers import HorizontalGroup, VerticalScroll
from textual.widgets import Footer, Header, RichLog, Input
from rich.text import Text
from rich.style import Style

from dotenv import load_dotenv
from groq import Groq

# --- dotenv and grok ---
load_dotenv()

api_key = os.getenv("GROQ_API_KEY")

client = Groq(api_key=api_key)

# --- Lists ---

# Scale intervals (semitones from root)
scales = {
    "major":      [0, 2, 4, 5, 7, 9, 11],
    "minor":      [0, 2, 3, 5, 7, 8, 10],
    "dorian":     [0, 2, 3, 5, 7, 9, 10],
    "phrygian":   [0, 1, 3, 5, 7, 8, 10],
    "lydian":     [0, 2, 4, 6, 7, 9, 11],
    "mixolydian": [0, 2, 4, 5, 7, 9, 10],
}

# Progressions as scale degree indices (0-based, so 0=root, 2=third degree, etc.)
progressions = {
    "major":      [[0, 4, 5, 3], [0, 3, 4], [0, 5, 3, 4], [0, 1, 4, 0], [0, 5, 3, 0], [0, 2, 5, 0], [0, 3, 0, 4]],
    "minor":      [[0, 5, 2, 6], [0, 3, 4], [0, 6, 5, 6], [0, 3, 6, 2], [0, 4, 0, 6], [0, 2, 5, 0], [0, 5, 6, 4]],
    "dorian":     [[0, 3], [0, 3, 0], [0, 6, 3], [0, 4, 3], [0, 3, 6, 4], [0, 1, 3, 4], [0, 6, 4, 3]],
    "phrygian":   [[0, 1], [0, 1, 0], [0, 6, 5], [0, 1, 6, 5], [0, 5, 1, 0], [0, 4, 1, 0], [0, 1, 4, 5]],
    "lydian":     [[0, 1], [0, 1, 4], [0, 1, 0], [0, 4, 1, 5], [0, 2, 1, 4], [0, 1, 3, 4], [0, 5, 1, 3]],
    "mixolydian": [[0, 6, 3], [0, 6, 0], [0, 3, 6], [0, 4, 6, 3], [0, 1, 6, 4], [0, 6, 4, 0], [0, 3, 4, 6]],
}

# Mood pool for scales
moods = {
    "major":      ["uplifting", "triumphant", "nostalgic", "hopeful", "carefree", "anthemic"],
    "minor":      ["melancholic", "dark", "emotional", "haunting", "brooding", "tense"],
    "dorian":     ["soulful", "cool", "mysterious", "groovy", "introspective", "hypnotic"],
    "phrygian":   ["exotic", "intense", "eerie", "cinematic", "aggressive", "ancient"],
    "lydian":     ["dreamy", "floating", "ethereal", "whimsical", "otherworldly", "warm"],
    "mixolydian": ["bluesy", "laid-back", "earthy", "swagger", "driving", "rebellious"],
}

# Chromatic notes to resolve indices to actual note names
chromatic = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]

# --- Colours ---

C_DIM    = "#3a3a5a"
C_MUTED  = "#6a6a8a"
C_BODY   = "#c8bfa8"
C_ACCENT = "#7a6fff"
C_GOLD   = "#d4a853"
C_GREEN  = "#5ecfa0"
C_RED    = "#e05a5a"

# --- Text helpers ---

def divider(log, color=C_DIM):
    log.write(Text("  " + "─" * 48, style=Style(color=color)))

def hint(log):
    t = Text()
    t.append("  r", style=Style(color=C_ACCENT, bold=True))
    t.append(" random   ", style=Style(color=C_MUTED))
    t.append("m", style=Style(color=C_ACCENT, bold=True))
    t.append(" manual   ", style=Style(color=C_MUTED))
    log.write(t)

def ai_hint(log):
    t = Text()
    t.append("  ?", style=Style(color=C_ACCENT, bold=True))
    t.append(" AI one liner   ", style=Style(color=C_MUTED))
    t.append("r", style=Style(color=C_ACCENT, bold=True))
    t.append(" reset   ", style=Style(color=C_MUTED))
    log.write(t)

def write_welcome(log):
    log.write(Text(""))
    t = Text()
    t.append("  SONG SEED GENERATOR\n", style=Style(color=C_ACCENT, bold=True))
    t.append("  Spark your next track.\n", style=Style(color=C_MUTED, italic=True))
    log.write(t)
    hint(log)
    divider(log)

def write_result(log, key, scale_name, chords, mood):
    divider(log)
    t = Text()
    t.append("  KEY    ", style=Style(color=C_MUTED))
    t.append(f"{key} {scale_name}\n", style=Style(color=C_GOLD, bold=True))
    t.append("  CHORDS ", style=Style(color=C_MUTED))
    t.append("  ".join(f"{c:<2}" for c in chords) + "\n", style=Style(color=C_GREEN, bold=True))
    t.append("  MOOD   ", style=Style(color=C_MUTED))
    t.append(mood, style=Style(color=C_ACCENT, italic=True))
    log.write(t)
    divider(log)

def get_maestro_vibe(log, key, scale, mood_desc):
    completion = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {
                "role": "system", 
                "content": "You are a witty music production assistant."
            },
            {
                "role": "user", 
                "content": f"Give me a 1-sentence evocative image for a {mood_desc} song in {key} {scale}."
            }
        ],
        max_tokens=50
    )
    # return completion.choices[0].message.content
    t = Text()
    t.append("  ")
    t.append(completion.choices[0].message.content)
    log.write(t)
    divider(log)

# --- Functions ---

def generate_chord_progression(key, scale_name):
    root_idx = chromatic.index(key)
    scale = scales[scale_name]
    progression = random.choice(progressions[scale_name])

    chords = []
    for i in progression:
        chords.append(chromatic[(root_idx + scale[i]) % 12])
    
    return chords

def random_everything(log):
    key = random.choice(chromatic)
    scale_name = random.choice(list(scales.keys()))
    mood = random.choice(moods[scale_name])
    write_result(log, key, scale_name, generate_chord_progression(key, scale_name), mood)

def chosen(log, key, scale_name, mood):
    write_result(log, key, scale_name, generate_chord_progression(key, scale_name), mood)

# --- App ---

class InstructionDisplay(HorizontalGroup):
    
    def compose(self) -> ComposeResult:
        yield RichLog(id="output")

class GeneratorApp(App):

    CSS_PATH = "generator.tcss"
    BINDINGS = [
        ("c", "clear_log", "Clear log")
    ]

    mode = None
    key = None
    scale_name = None
    mood = None

    def compose(self) -> ComposeResult:
        yield Header()
        yield Footer()
        yield VerticalScroll(InstructionDisplay())
        yield Input(placeholder="Give your input here...")
    
    def action_clear_log(self) -> None:
        log = self.query_one(RichLog)
        log.clear()
        self.mode = None
        write_welcome(log)

    def on_input_submitted(self, event: Input.Submitted) -> None:
        log = self.query_one(RichLog)
        choice = event.value.strip().lower()
        event.input.clear()
        if not choice:
            return

        # echo dimly
        t = Text()
        t.append("  > ", style=Style(color=C_DIM))
        t.append(choice, style=Style(color=C_MUTED, italic=True))
        log.write(t)

        if self.mode == None:
            if choice == 'r':
                random_everything(log)
                hint(log)
            elif choice == 'm':
                self.mode = "manual"
                t = Text()
                t.append("  Choose a key:\n  ", style=Style(color=C_BODY))
                for note in chromatic:
                    color = C_GOLD if "#" in note else C_BODY
                    t.append(f"{note:<4}", style=Style(color=color))
                log.write(t)
            else:
                t = Text()
                t.append(f"Invalid!", style=Style(color=C_RED))
                log.write(t)
        
        elif self.mode == "manual":
            self.key = choice.upper()
            if self.key in chromatic:
                self.mode = "scale"
                root_idx = chromatic.index(self.key)
                t = Text()
                t.append("  Key: ", style=Style(color=C_MUTED))
                t.append(f"{self.key}\n", style=Style(color=C_GOLD, bold=True))
                t.append("  Choose a scale:\n", style=Style(color=C_BODY))
                log.write(t)
                for scale, notes in scales.items():
                    notes_names = [chromatic[(root_idx + n) % 12] for n in notes]
                    t = Text()
                    t.append(f"  {scale:<13}", style=Style(color=C_ACCENT, bold=True))
                    t.append("  ".join(f"{n:<2}" for n in notes_names), style=Style(color=C_MUTED))
                    log.write(t)
            else:
                log.write(Text("  x  Invalid key.", style=Style(color=C_RED)))
        
        elif self.mode == "scale":
            if choice in scales:
                self.scale_name = choice
                self.mood = random.choice(moods[self.scale_name])
                chosen(log, self.key, self.scale_name, self.mood)
                self.mode = "ai"
                ai_hint(log)
                # self.mode = None
                # hint(log)
            else:
                log.write(Text("  x  Invalid scale.", style=Style(color=C_RED)))
        
        elif self.mode == "ai":
            if choice == "?":
                get_maestro_vibe(log, self.key, self.scale_name, self.mood)
                self.mode = None
                hint(log)
            elif choice == "r":
                divider(log)
                self.mode = None
                hint(log)
            else:
                log.write(Text("  x  Invalid scale.", style=Style(color=C_RED)))

    def on_mount(self) -> None:
        write_welcome(self.query_one(RichLog))

if __name__ == "__main__":
    app = GeneratorApp()
    app.run()