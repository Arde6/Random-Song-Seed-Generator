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

# Load dotenv, get api key, check if there was api key
load_dotenv()
api_key = os.getenv("GROQ_API_KEY")
client = Groq(api_key=api_key) if api_key else None

# AI Model
# Change to what ever you want as long as available in groq
ai_model = "llama-3.1-8b-instant"

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

# Just a divider ---
def divider(log, color=C_DIM) -> None:
    log.write(Text("  " + "─" * (log.size.width-6), style=Style(color=color)))

# Starting commands
def hint(log) -> None:
    t = Text()
    t.append("  r", style=Style(color=C_ACCENT, bold=True))
    t.append(" random   ", style=Style(color=C_MUTED))
    t.append("m", style=Style(color=C_ACCENT, bold=True))
    t.append(" manual   ", style=Style(color=C_MUTED))
    log.write(t)

# AI commands
def ai_hint(log) -> None:
    t = Text()
    t.append("  ?", style=Style(color=C_ACCENT, bold=True))
    t.append(" AI one liner   ", style=Style(color=C_MUTED))
    t.append("  <write anything>", style=Style(color=C_ACCENT, bold=True))
    t.append(" Chat with AI   ", style=Style(color=C_MUTED))
    t.append("quit", style=Style(color=C_ACCENT, bold=True))
    t.append(" start again   ", style=Style(color=C_MUTED))
    log.write(t)

# Welcome message
def write_welcome(log) -> None:
    log.write(Text(""))
    t = Text()
    t.append("  SONG SEED GENERATOR\n", style=Style(color=C_ACCENT, bold=True))
    t.append("  Spark your next track.\n", style=Style(color=C_MUTED, italic=True))
    log.write(t)
    hint(log)
    divider(log)

# Result writing helper for the seed
def write_result(log, key, scale_name, chords, mood) -> None:
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

# Helper for writing long text with a label
# Scales with window width
def write_wrapped(log, label, content, indent="  ") -> None:
    prefix = indent + label + "\n"
    available = log.size.width - len(indent)

    t = Text()
    t.append(prefix, style=Style(color=C_MUTED))

    for para in content.split("\n"):
        words = para.split()
        current = []
        length = 0
        for word in words:
            if length + len(word) + (1 if current else 0) + len(indent) > available:
                t.append(indent + " ".join(current) + "\n", style=Style(color=C_BODY))
                current = [word]
                length = len(word)
            else:
                current.append(word)
                length += len(word) + (1 if len(current) > 1 else 0)
        if current:
            t.append(indent + " ".join(current) + "\n", style=Style(color=C_BODY))
        t.append("\n")  # preserve the original newline between paragraphs

    log.write(t)
    divider(log)

# --- Ai chat functions

# Function for getting ai answers for prompt
# Returns Ai answer
def get_maestro(log, chat_history) -> dict:
    completion = client.chat.completions.create(
        model=ai_model,
        messages=chat_history
    )
    write_wrapped(log, "Assistant:", completion.choices[0].message.content)
    return_msg = {
        "role": "assistant",
        "content": completion.choices[0].message.content
    }
    return return_msg

# --- Functions ---

# Function that pics random chord progression based on key and scale
def generate_chord_progression(key, scale_name) -> list:
    root_idx = chromatic.index(key)
    scale = scales[scale_name]
    progression = random.choice(progressions[scale_name])

    chords = []
    for i in progression:
        chords.append(chromatic[(root_idx + scale[i]) % 12])
    
    return chords

# Writes random key, scale and mood
def random_everything(log) -> None:
    key = random.choice(chromatic)
    scale_name = random.choice(list(scales.keys()))
    mood = random.choice(moods[scale_name])
    write_result(log, key, scale_name, generate_chord_progression(key, scale_name), mood)

# Prints chosen key, scale and mood nicely
def chosen(log, key, scale_name, mood) -> None:
    write_result(log, key, scale_name, generate_chord_progression(key, scale_name), mood)

# --- App ---

# Display
# Only the RichLog right now
class InstructionDisplay(HorizontalGroup):
    
    def compose(self) -> ComposeResult:
        yield RichLog(id="output", wrap=True)

# App object
class GeneratorApp(App):

    # Tcss for styling
    CSS_PATH = "generator.tcss"

    # Keybinds
    BINDINGS = [
        ("c", "clear_log", "Clear log")
    ]

    # All app items
    def compose(self) -> ComposeResult:
        yield Header()
        yield Footer()
        yield VerticalScroll(InstructionDisplay())
        yield Input(placeholder="Give your input here...")
    
    # Clears the RichLog when C is pressed
    def action_clear_log(self) -> None:
        log = self.query_one(RichLog)
        log.clear()
        self.mode = None
        write_welcome(log)

    # Whole logic of the app
    # Stuff happens when you write stuff to input box thingy
    def on_input_submitted(self, event: Input.Submitted) -> None:
        log = self.query_one(RichLog)

        # Write down given input
        choice = event.value.strip().lower()

        # Clear input box
        event.input.clear()
        if not choice:
            return

        # Echo given command
        t = Text()
        t.append("  > ", style=Style(color=C_DIM))
        t.append(choice, style=Style(color=C_MUTED, italic=True))
        log.write(t)

        # Basically start up text
        if self.mode == None:

            # Just gives random key, scale and mood
            if choice == 'r':
                random_everything(log)
                hint(log)
            
            # Switches to manual mode, also gives the prompt for the next step
            elif choice == 'm':
                self.mode = "manual"
                t = Text()
                t.append("  Choose a key:\n  ", style=Style(color=C_BODY))
                for note in chromatic:
                    color = C_GOLD if "#" in note else C_BODY
                    t.append(f"{note:<4}", style=Style(color=color))
                log.write(t)

            # Invalid input handler
            else:
                log.write(Text("  x  Invalid command.", style=Style(color=C_RED)))
        
        # -- Manual mode ---

        # Thus begins manual mode
        # Here we check the key
        elif self.mode == "manual":
            # Changing input to uppercase as the notes have been written uppercase
            self.key = choice.upper()

            # If the key is valid we give prompt to the next step: scale!
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

            # Invalid input handler
            else:
                log.write(Text("  x  Invalid key.", style=Style(color=C_RED)))
        
        # Scale mode, here we pick the wanted scale
        elif self.mode == "scale":

            # Once again if input is valid we choose the scale and give it a random mood
            # Moods are scale based.
            # If we have groq available we will proceed to next step
            if choice in scales:
                self.scale_name = choice
                self.mood = random.choice(moods[self.scale_name])
                chosen(log, self.key, self.scale_name, self.mood)

                # Check if client is available
                if client != None:
                    self.mode = "ai"
                    ai_hint(log)
                else:
                    self.mode = None
                    hint(log)

            # Invalid input handler
            else:
                log.write(Text("  x  Invalid scale.", style=Style(color=C_RED)))
        
        # Ai mode. In this step the user can chat with an I bot that is given the song seed as a context
        elif self.mode == "ai":

            # Check if first run to give context
            if self.ai_flag is False:
                self.ai_flag = True
                self.chat_history.append(
                    {
                        "role": "system", 
                        "content": f"Mood of the song is {self.mood}, key of the song is {self.key} and the scale of the song is {self.scale_name}."
                    }
                )

            # Get a oneliner
            if choice == "?":
                self.chat_history.append(
                    {
                        "role": "user", 
                        "content": f"Give me a 1-sentence evocative image for the song."
                    }
                )
                self.chat_history.append(get_maestro(log, self.chat_history))

            # Quit AI mode and start over
            elif choice == "quit":
                divider(log)
                self.mode = None
                hint(log)
                self.ai_flag = False

            # Give free prompt to AI
            else:
                self.chat_history.append(
                    {
                        "role": "user",
                        "content": choice
                    }
                )
                self.chat_history.append(get_maestro(log, self.chat_history))

    # On mount funciton
    # Gives attributes to the class that are used
    # in the input and writes welcome message
    def on_mount(self) -> None:
        self.mode = None
        self.key = None
        self.scale_name = None
        self.mood = None
        self.ai_flag = False
        self.chat_history = [{"role": "system", "content": "You are a witty music production assistant."}]
        write_welcome(self.query_one(RichLog))

if __name__ == "__main__":
    app = GeneratorApp()
    app.run()