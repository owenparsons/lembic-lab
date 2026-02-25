"""Word-pair name generator for cells: adjective-noun combinations."""

import random

ADJECTIVES = [
    "amber", "azure", "bold", "bright", "calm", "cedar", "clean", "clear",
    "cool", "coral", "crisp", "cyber", "dark", "deep", "eager", "early",
    "fair", "fast", "fine", "first", "fresh", "frost", "glad", "gold",
    "grand", "green", "happy", "honey", "iron", "ivory", "jade", "keen",
    "kind", "lemon", "light", "lime", "lucky", "lunar", "maple", "mellow",
    "mild", "misty", "neat", "noble", "north", "olive", "opal", "open",
    "pale", "pearl", "pine", "plain", "plum", "proud", "pure", "quick",
    "quiet", "rapid", "rare", "regal", "rich", "rosy", "royal", "ruby",
    "rusty", "sage", "sharp", "shiny", "silk", "silver", "slim", "smart",
    "smooth", "snowy", "soft", "solar", "solid", "sonic", "south", "spare",
    "spicy", "star", "steel", "still", "stone", "sunny", "super", "sweet",
    "swift", "tall", "teal", "thin", "tidy", "tiny", "topaz", "true",
    "ultra", "upper", "vast", "vivid", "warm", "west", "white", "wild",
    "wise", "young", "zesty", "agile", "ample", "ashen", "basic", "blaze",
    "bliss", "brave", "brisk", "broad", "burnt", "civic", "cloud", "coast",
    "comet", "cozy", "cream", "dawn", "delta", "dense", "drift", "dusk",
    "dusty", "elfin", "ember", "equal", "exact", "extra", "fable", "fancy",
    "fern", "fiery", "flame", "fleet", "flora", "focal", "forge", "frank",
    "gale", "giant", "glass", "gleam", "globe", "grace", "grape", "great",
    "grove", "hazel", "hilly", "hush", "icy", "ideal", "indie", "inner",
    "jazzy", "jolly", "leafy", "level", "lilac", "linen", "lofty", "lucid",
    "magic", "major", "marsh", "matte", "maxim", "melon", "metro", "micro",
    "minus", "modal", "mocha", "mossy", "muted", "naval", "nifty", "nimble",
    "noted", "novel", "ocean", "orbit", "outer", "oxide", "pasty", "peach",
    "penny", "petal", "pixel", "plaza", "polar", "prime", "prism", "pulse",
]

NOUNS = [
    "arch", "atlas", "aura", "badge", "basin", "beam", "bloom", "bluff",
    "bolt", "bower", "braid", "brick", "brook", "cairn", "cape", "cell",
    "chain", "charm", "chord", "cider", "cliff", "cloud", "coast", "coil",
    "coral", "craft", "crane", "creek", "crest", "crown", "curve", "dawn",
    "delta", "depth", "drift", "drum", "dune", "edge", "ember", "fable",
    "feast", "field", "flame", "flare", "flask", "fleet", "flint", "float",
    "flora", "forge", "frost", "glade", "gleam", "globe", "glyph", "grace",
    "grain", "graph", "grove", "haven", "heart", "hedge", "heron", "hive",
    "hover", "index", "inlet", "ivory", "jewel", "kayak", "knoll", "lance",
    "latch", "layer", "ledge", "lever", "light", "lodge", "lotus", "maple",
    "marsh", "mason", "mast", "medal", "merit", "mesa", "metal", "mirth",
    "model", "moose", "mount", "nexus", "north", "oasis", "ocean", "orbit",
    "otter", "oxide", "panel", "patch", "pearl", "petal", "phase", "pilot",
    "pivot", "plank", "plaza", "plume", "point", "prism", "probe", "pulse",
    "quail", "quartz", "quest", "radar", "range", "rapid", "raven", "reach",
    "realm", "reef", "ridge", "river", "robin", "route", "rover", "sable",
    "scale", "scout", "shaft", "shell", "shore", "sigil", "slate", "slope",
    "smoke", "solar", "spark", "spire", "spoke", "spray", "squad", "staff",
    "stage", "stake", "star", "steam", "steel", "stem", "stone", "storm",
    "surge", "swift", "thorn", "tide", "tiger", "torch", "tower", "trace",
    "trail", "trend", "triad", "tulip", "vault", "vigor", "vista", "voice",
    "watch", "wave", "wheat", "wheel", "wren", "yacht", "yield", "zen",
    "anvil", "arrow", "aspen", "berry", "birch", "blaze", "brine", "canoe",
    "cedar", "chalk", "chess", "chisel", "cloak", "cobalt", "coda", "cone",
    "copse", "crux", "cypress", "daisy", "drake", "easel", "echo", "fawn",
    "ferry", "finch", "focus", "forum", "gavel", "gecko", "gourd", "grail",
    "gust", "haiku", "halo", "haven", "heath", "helix", "holly", "iris",
    "isle", "ivory", "jasper", "kite", "lark", "lilac", "lynx", "mango",
    "mantle", "mica", "mist", "moth", "myrrh", "nook", "nova", "oak",
    "onyx", "opal", "orca", "palm", "pixel", "ploy", "quill", "rain",
]


def generate_name(existing: set[str] | None = None) -> str:
    """Generate a unique adjective-noun word pair name.

    Tries random combinations until a unique one is found.
    Falls back to appending a number if the space is exhausted.
    """
    if existing is None:
        existing = set()

    # Try random combos first (plenty of space: ~200*200 = 40k combinations)
    for _ in range(100):
        name = f"{random.choice(ADJECTIVES)}-{random.choice(NOUNS)}"
        if name not in existing:
            return name

    # Fallback: append numbers
    for i in range(1, 10000):
        name = f"{random.choice(ADJECTIVES)}-{random.choice(NOUNS)}-{i}"
        if name not in existing:
            return name

    raise RuntimeError("Could not generate unique name")
