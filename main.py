# Imports
import random
from textual.app import App, ComposeResult
from textual.containers import HorizontalGroup, VerticalScroll
from textual.widgets import Footer, Header, RichLog, Input, Button

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

class InstructionDisplay(HorizontalGroup):
    
    def compose(self) -> ComposeResult:
        yield RichLog(id="output")

class GeneratorApp(App):
    
    BINDINGS = [("d", "toggle_dark", "Toggle dark mode")]

    def compose(self) -> ComposeResult:
        yield Header()
        yield Footer()
        yield VerticalScroll(InstructionDisplay())
        yield Input(placeholder="Give your input here...")
    
    def action_toggle_dark(self) -> None:
        self.theme = (
            "textual-dark" if self.theme == "textual-light" else "textual-light"
        )

    def on_input_submitted(self, event: Input.Submitted) -> None:
        log = self.query_one(RichLog)
        log.write(f"You typed: {event.value}")
        event.input.clear()


def generate_chord_progression(key, scale_name):
    root_idx = chromatic.index(key)
    scale = scales[scale_name]
    progression = random.choice(progressions[scale_name])

    chords = []
    for i in progression:
        chords.append(chromatic[(root_idx + scale[i]) % 12])
    
    return chords

def random_everything():
    key = random.choice(chromatic)
    scale_name = random.choice(list(scales.keys()))
    chords = generate_chord_progression(key, scale_name)
    print("----------------------------------------\n")
    print(f" {key} {scale_name}, chords: {chords}\n")
    print("----------------------------------------\n")

def chosen():
    print("----------------------------------------\n")
    print(f" {chromatic}")
    while True:
        choice = input(" Give a key: ")
        if choice in chromatic:
            key = choice
            break
        else:
            print(" Invalid!")

    print("----------------------------------------\n")
    root_idx = chromatic.index(key)
    for scale, notes in scales.items():
        notes_names = []
        for note in notes:
            notes_names.append(chromatic[(root_idx + note)])
        print(f" {scale:<15} {", ".join(f"{note:<2}" for note in notes_names)}")
    while True:
        choice = input(" Give a scale: ")
        if choice in scales:
            scale_name = choice
            break
        else:
            print(" Invalid!")

    print("----------------------------------------\n")
    chords = generate_chord_progression(key, scale_name)
    print(f"{key} {scale_name}, chords: {chords}")

def main():
    print("----------------------------------------\n")
    print(" Welcome to random song seed generator! \n")
    while True:
        print(" What do you want to do? Press Q for quit,")
        print(" R for Random or M for manually given: " )
        choice = input()
        if choice == 'R' or choice == 'r':
            random_everything()
        elif choice == 'M' or choice == 'm':
            chosen()
        elif choice == 'Q' or choice == 'q':
            break

if __name__ == "__main__":
    app = GeneratorApp()
    app.run()
    # main()