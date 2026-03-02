# Imports
import random
from textual.app import App, ComposeResult
from textual.containers import HorizontalGroup, VerticalScroll
from textual.widgets import Footer, Header, RichLog, Input

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
    "major":      [[0, 4, 5, 3], [0, 3, 4], [0, 5, 3, 4]],
    "minor":      [[0, 5, 2, 6], [0, 3, 4], [0, 6, 5, 6]],
    "dorian":     [[0, 3], [0, 3, 0], [0, 6, 3]],
    "phrygian":   [[0, 1], [0, 1, 0], [0, 6, 5]],
    "lydian":     [[0, 1], [0, 1, 4], [0, 1, 0]],
    "mixolydian": [[0, 6, 3], [0, 6, 0], [0, 3, 6]],
}

# Chromatic notes to resolve indices to actual note names
chromatic = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]

C_DIM    = "#3a3a5a"
C_MUTED  = "#6a6a8a"
C_BODY   = "#c8bfa8"
C_ACCENT = "#7a6fff"
C_GOLD   = "#d4a853"
C_GREEN  = "#5ecfa0"
C_RED    = "#e05a5a"

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
    chords = generate_chord_progression(key, scale_name)
    log.write(f" {key} {scale_name}, chords: {chords}")

def chosen(log, key, scale_name):
    chords = generate_chord_progression(key, scale_name)
    log.write(f"{key} {scale_name}, chords: {chords}")

class InstructionDisplay(HorizontalGroup):
    
    def compose(self) -> ComposeResult:
        yield RichLog(id="output")

class GeneratorApp(App):

    CSS_PATH = "generator.tcss"
    
    BINDINGS = [
        ("d", "toggle_dark", "Toggle dark mode"),
        ("c", "clear_log", "Clear log")
    ]

    mode = None
    key = None
    scale_name = None

    def compose(self) -> ComposeResult:
        yield Header()
        yield Footer()
        yield VerticalScroll(InstructionDisplay())
        yield Input(placeholder="Give your input here...")
    
    def action_toggle_dark(self) -> None:
        self.theme = (
            "textual-dark" if self.theme == "textual-light" else "textual-light"
        )
    
    def action_clear_log(self) -> None:
        log = self.query_one(RichLog)
        log.clear()
        self.mode = None
        log.write("Welcome to random song seed generator!")
        log.write("Press R for random, M for manual.")

    def on_input_submitted(self, event: Input.Submitted) -> None:
        log = self.query_one(RichLog)
        log.write(f"You typed: {event.value}")
        choice = event.value.strip().lower()
        event.input.clear()

        if self.mode == None:
            if choice == 'r':
                random_everything(log)
                log.write("Press R for random, M for manual.")
            elif choice == 'm':
                self.mode = "manual"
                log.write("Choose a song key.")
                log.write(f"{chromatic}")
            else:
                log.write("Invalid!")
        
        elif self.mode == "manual":
            self.key = choice.upper()
            if self.key in chromatic:
                self.mode = "scale"
                root_idx = chromatic.index(self.key)
                for scale, notes in scales.items():
                    notes_names = []
                    for note in notes:
                        notes_names.append(chromatic[(root_idx + note)])
                    log.write(f" {scale:<15} {", ".join(f"{note:<2}" for note in notes_names)}")
            else:
                log.write("Invalid! Choose a song key.")
                log.write(f"{chromatic}")
        
        elif self.mode == "scale":
            if choice in scales:
                self.scale_name = choice
                chosen(log, self.key, self.scale_name)
                self.mode = None
                log.write("Press R for random, M for manual.")

    def on_mount(self) -> None:
        log = self.query_one(RichLog)
        log.write("Welcome to random song seed generator!")
        log.write("Press R for random, M for manual.")

if __name__ == "__main__":
    app = GeneratorApp()
    app.run()