import json
import random
from dataclasses import dataclass, asdict
from typing import Optional
from enum import Enum


class Technique(Enum):
    BLEND_IN_BLACK = "BLEND_IN_BLACK"
    BLEND_ON_WHITE = "BLEND_ON_WHITE"
    MASK_CUT = "MASK_CUT"
    GLITCH_ART = "GLITCH_ART"
    CEL_SHADED = "CEL_SHADED"
    UKIYO_E_MODERN = "UKIYO_E_MODERN"
    VAPORWAVE = "VAPORWAVE"
    INK_WASH = "INK_WASH"
    NEO_TOKYO = "NEO_TOKYO"
    MECHA_BLUEPRINT = "MECHA_BLUEPRINT"
    CHROMATIC_ABERRATION = "CHROMATIC_ABERRATION"


@dataclass
class ColorPalette:
    colors: list[str]

    def __post_init__(self):
        if len(self.colors) != 3:
            raise ValueError("Palette must have exactly 3 colors")


@dataclass
class Typography:
    primary_text: str
    kanji_sub: Optional[str] = None


@dataclass
class DesignParameters:
    technique: Technique
    concept_title: str
    color_palette: ColorPalette
    typography: Typography


@dataclass
class GenerationPayloads:
    image_generation_prompt: str
    video_autocut_prompt: str


@dataclass
class AppMetadata:
    engine_version: str = "2.5-AI"
    project_name: str = "Anime Experimental Poster Lab"
    target_output: list[str] = None

    def __post_init__(self):
        if self.target_output is None:
            self.target_output = ["print_poster_2:3", "social_story_9:16", "tiktok_autocut_video"]


@dataclass
class PosterLabOutput:
    app_metadata: AppMetadata
    design_parameters: DesignParameters
    generation_payloads: GenerationPayloads

    def to_json(self) -> str:
        def serialize(obj):
            if isinstance(obj, Enum):
                return obj.value
            if hasattr(obj, '__dict__'):
                return {k: serialize(v) for k, v in obj.__dict__.items()}
            elif isinstance(obj, list):
                return [serialize(v) for v in obj]
            elif isinstance(obj, dict):
                return {k: serialize(v) for k, v in obj.items()}
            return obj
        return json.dumps(serialize(self), indent=2, ensure_ascii=False)


TECHNIQUE_PROFILES = {
    Technique.BLEND_IN_BLACK: {
        "palettes": [
            ["#00FFFF", "#8A2BE2", "#FF00FF"],
            ["#00BFFF", "#9400D3", "#FF1493"],
            ["#7DF9FF", "#BF00FF", "#FF007F"],
        ],
        "bg_desc": "deep black background, cinematic lighting, luminous fluid inks",
        "typo_style": "negative space typography, white/neon text on black",
    },
    Technique.BLEND_ON_WHITE: {
        "palettes": [
            ["#F5F5DC", "#87CEEB", "#DDA0DD"],
            ["#FFFFF0", "#98FB98", "#F0E68C"],
            ["#FAF0E6", "#AFEEEE", "#DEB887"],
        ],
        "bg_desc": "ivory/textured white background, translucent watercolors, overlapping geometric shapes",
        "typo_style": "minimalist latin typography, 3-color palette",
    },
    Technique.MASK_CUT: {
        "palettes": [
            ["#FF6B35", "#004E89", "#FFFFFF"],
            ["#E85D04", "#1B4F72", "#F5F5F5"],
            ["#D63031", "#00B894", "#ECF0F1"],
        ],
        "bg_desc": "cut-out silhouettes, flat color blocks, negative space containing landscapes or patterns, editorial collage",
        "typo_style": "masked typography integrated into silhouettes",
    },
    Technique.GLITCH_ART: {
        "palettes": [
            ["#FF0066", "#00FFFF", "#FFFF00"],
            ["#FF0033", "#00FFCC", "#CCFF00"],
            ["#CC00FF", "#33FFFF", "#FFCC00"],
        ],
        "bg_desc": "datamoshing artifacts, RGB channel separation, scanlines, pixel sorting, corrupted data aesthetic",
        "typo_style": "fragmented glitch typography, RGB split text, corrupted characters",
    },
    Technique.CEL_SHADED: {
        "palettes": [
            ["#FF6B35", "#2C3E50", "#ECF0F1"],
            ["#E74C3C", "#1A1A2E", "#F5F5F5"],
            ["#D35400", "#0D1B2A", "#FFFFFF"],
        ],
        "bg_desc": "hard cel-shaded shadows, flat color regions, clean line art, dramatic rim lighting, anime key frame style",
        "typo_style": "bold outline typography, cel-shaded text with hard shadows",
    },
    Technique.UKIYO_E_MODERN: {
        "palettes": [
            ["#DC143C", "#1E3A5F", "#F5F0E1"],
            ["#B22222", "#0D2B4A", "#FDF5E6"],
            ["#8B0000", "#191970", "#FFF8DC"],
        ],
        "bg_desc": "modern ukiyo-e woodblock texture, bokashi gradients, flat perspective, floating world aesthetic, paper grain",
        "typo_style": "brush stroke kanji, vertical text layout, seal stamp marks",
    },
    Technique.VAPORWAVE: {
        "palettes": [
            ["#FF6EC7", "#4EFFFF", "#FFFF4E"],
            ["#FF10F0", "#00F0FF", "#F0FF10"],
            ["#DA70D6", "#00FFFF", "#FFD700"],
        ],
        "bg_desc": "retro 80s/90s gradient skies, grid horizon, palm silhouettes, greek statues, CRT monitor glow, nostalgia filter",
        "typo_style": "wide-tracking latin, japanese vaporwave font, chrome/metal text effects",
    },
    Technique.INK_WASH: {
        "palettes": [
            ["#1C1C1C", "#4A4A4A", "#F5F5F0"],
            ["#0D0D0D", "#3D3D3D", "#FAF8F3"],
            ["#2B2B2B", "#5C5C5C", "#F0EDE5"],
        ],
        "bg_desc": "sumi-e ink wash, wet brush strokes, negative space mastery, spontaneous brushwork, rice paper texture",
        "typo_style": "calligraphy brush strokes, flowing cursive kanji, red seal chop",
    },
    Technique.NEO_TOKYO: {
        "palettes": [
            ["#FF0080", "#00FFFF", "#FFB800"],
            ["#FF1A75", "#00E5E5", "#FFCC00"],
            ["#E6006B", "#00CCCC", "#E6B800"],
        ],
        "bg_desc": "rain-slicked streets, holographic advertisements, neon reflections, towering megastructures, volumetric fog",
        "typo_style": "holographic floating text, bilingual neon signs, kinetic typography",
    },
    Technique.MECHA_BLUEPRINT: {
        "palettes": [
            ["#00FF41", "#003366", "#FFFFFF"],
            ["#00CC33", "#002244", "#F0F0F0"],
            ["#00AA22", "#001133", "#E8E8E8"],
        ],
        "bg_desc": "technical blueprint grid, white line schematics, measurement annotations, exploded view diagrams, engineering paper",
        "typo_style": "technical font, dimension labels, specification callouts, monospace data",
    },
    Technique.CHROMATIC_ABERRATION: {
        "palettes": [
            ["#FF0044", "#00FF88", "#4400FF"],
            ["#FF0033", "#00FF77", "#3300FF"],
            ["#CC0033", "#00CC66", "#2200CC"],
        ],
        "bg_desc": "extreme lens distortion, RGB channel offset, prismatic color separation, surreal depth, optical aberration",
        "typo_style": "split channel typography, each color channel offset, prism text effect",
    },
}

CONCEPT_KEYWORDS = {
    "cyberpunk": Technique.BLEND_IN_BLACK,
    "neon": Technique.BLEND_IN_BLACK,
    "dark": Technique.BLEND_IN_BLACK,
    "noir": Technique.BLEND_IN_BLACK,
    "minimal": Technique.BLEND_ON_WHITE,
    "clean": Technique.BLEND_ON_WHITE,
    "watercolor": Technique.BLEND_ON_WHITE,
    "soft": Technique.BLEND_ON_WHITE,
    "silhouette": Technique.MASK_CUT,
    "collage": Technique.MASK_CUT,
    "cutout": Technique.MASK_CUT,
    "editorial": Technique.MASK_CUT,
    "glitch": Technique.GLITCH_ART,
    "datamosh": Technique.GLITCH_ART,
    "rgb": Technique.GLITCH_ART,
    "corrupt": Technique.GLITCH_ART,
    "cel": Technique.CEL_SHADED,
    "cel shaded": Technique.CEL_SHADED,
    "anime frame": Technique.CEL_SHADED,
    "keyframe": Technique.CEL_SHADED,
    "ukiyo": Technique.UKIYO_E_MODERN,
    "ukiyo-e": Technique.UKIYO_E_MODERN,
    "woodblock": Technique.UKIYO_E_MODERN,
    "floating world": Technique.UKIYO_E_MODERN,
    "vaporwave": Technique.VAPORWAVE,
    "retro": Technique.VAPORWAVE,
    "synthwave": Technique.VAPORWAVE,
    "80s": Technique.VAPORWAVE,
    "90s": Technique.VAPORWAVE,
    "ink wash": Technique.INK_WASH,
    "sumi": Technique.INK_WASH,
    "sumi-e": Technique.INK_WASH,
    "brush": Technique.INK_WASH,
    "calligraphy": Technique.INK_WASH,
    "neo tokyo": Technique.NEO_TOKYO,
    "megacity": Technique.NEO_TOKYO,
    "hologram": Technique.NEO_TOKYO,
    "rain": Technique.NEO_TOKYO,
    "mecha": Technique.MECHA_BLUEPRINT,
    "blueprint": Technique.MECHA_BLUEPRINT,
    "schematic": Technique.MECHA_BLUEPRINT,
    "technical": Technique.MECHA_BLUEPRINT,
    "engineering": Technique.MECHA_BLUEPRINT,
    "chromatic": Technique.CHROMATIC_ABERRATION,
    "aberration": Technique.CHROMATIC_ABERRATION,
    "prism": Technique.CHROMATIC_ABERRATION,
    "lens": Technique.CHROMATIC_ABERRATION,
    "distort": Technique.CHROMATIC_ABERRATION,
}

JAPANESE_TITLES = {
    "cyberpunk": "サイバーパンク",
    "neon city": "ネオンシティ",
    "samurai": "侍",
    "ronin": "浪人",
    "dream": "夢",
    "shadow": "影",
    "light": "光",
    "void": "虚無",
    "echo": "残響",
    "pulse": "鼓動",
    "glitch": "グリッチ",
    "cel": "セル画",
    "ukiyo": "浮世絵",
    "vaporwave": "ヴェイパーウェーブ",
    "ink": "墨",
    "neo tokyo": "ネオ東京",
    "mecha": "メカ",
    "chromatic": "色収差",
}


def select_technique(concept: str) -> Technique:
    concept_lower = concept.lower()
    for keyword, technique in CONCEPT_KEYWORDS.items():
        if keyword in concept_lower:
            return technique
    return random.choice(list(Technique))


def generate_concept_title(concept: str, technique: Technique) -> str:
    concept_words = concept.title().split()
    if technique == Technique.BLEND_IN_BLACK:
        prefixes = ["Neon", "Void", "Shadow", "Pulse", "Circuit", "Phantom"]
    elif technique == Technique.BLEND_ON_WHITE:
        prefixes = ["Pure", "Calm", "Flow", "Essence", "Breath", "Whisper"]
    elif technique == Technique.MASK_CUT:
        prefixes = ["Cut", "Form", "Shape", "Silhouette", "Fragment", "Layer"]
    elif technique == Technique.GLITCH_ART:
        prefixes = ["Corrupt", "Error", "Noise", "Static", "Fragment", "Artifact"]
    elif technique == Technique.CEL_SHADED:
        prefixes = ["Frame", "Key", "Cell", "Shadow", "Rim", "Line"]
    elif technique == Technique.UKIYO_E_MODERN:
        prefixes = ["Ukiyo", "Edo", "Float", "Wave", "Crane", "Cherry"]
    elif technique == Technique.VAPORWAVE:
        prefixes = ["Retro", "Synth", "Wave", "Mall", "Sunset", "Grid"]
    elif technique == Technique.INK_WASH:
        prefixes = ["Sumi", "Brush", "Stroke", "Void", "Flow", "Zen"]
    elif technique == Technique.NEO_TOKYO:
        prefixes = ["Neo", "Tokyo", "Rain", "Holo", "Tower", "Sector"]
    elif technique == Technique.MECHA_BLUEPRINT:
        prefixes = ["Spec", "Plan", "Unit", "Frame", "Core", "System"]
    elif technique == Technique.CHROMATIC_ABERRATION:
        prefixes = ["Prism", "Split", "Offset", "Lens", "Shift", "Bend"]
    else:
        prefixes = ["Untitled"]
    prefix = random.choice(prefixes)
    return f"{prefix} {' '.join(concept_words[:2])}"


def get_kanji_subtitle(concept: str) -> Optional[str]:
    concept_lower = concept.lower()
    for keyword, kanji in JAPANESE_TITLES.items():
        if keyword in concept_lower:
            return kanji
    return None


def build_image_prompt(design: DesignParameters) -> str:
    profile = TECHNIQUE_PROFILES[design.technique]
    palette_str = ", ".join(design.color_palette.colors)
    
    base = f"Anime experimental poster, {design.concept_title}, {profile['bg_desc']}, "
    base += f"strict 3-color palette: {palette_str}, "
    base += f"{profile['typo_style']}, "
    base += f"editorial design composition, high detail, 8k resolution, "
    base += f"aspect ratio 2:3, print quality"
    
    if design.typography.kanji_sub:
        base += f", Japanese text: {design.typography.kanji_sub}"
    
    return base


def build_video_prompt(design: DesignParameters) -> str:
    profile = TECHNIQUE_PROFILES[design.technique]
    palette_str = ", ".join(design.color_palette.colors)
    
    base = f"TikTok autocut style video, {design.concept_title}, {profile['bg_desc']}, "
    base += f"3-color palette: {palette_str}, "
    base += f"rapid cuts 3-5 seconds each, ink sweep transitions, glitch effects, "
    base += f"particle effects, cinematic zoom, dynamic visual beat sync, "
    base += f"vertical 9:16 aspect ratio, high energy pacing, "
    base += f"anime aesthetic, experimental motion graphics"
    
    return base


def process_concept(concept: str) -> PosterLabOutput:
    technique = select_technique(concept)
    profile = TECHNIQUE_PROFILES[technique]
    palette = ColorPalette(colors=random.choice(profile["palettes"]))
    
    concept_title = generate_concept_title(concept, technique)
    kanji_sub = get_kanji_subtitle(concept)
    typography = Typography(
        primary_text=concept_title.split()[-1] if concept_title else "EDITION 01",
        kanji_sub=kanji_sub
    )
    
    design_params = DesignParameters(
        technique=technique,
        concept_title=concept_title,
        color_palette=palette,
        typography=typography
    )
    
    payloads = GenerationPayloads(
        image_generation_prompt=build_image_prompt(design_params),
        video_autocut_prompt=build_video_prompt(design_params)
    )
    
    return PosterLabOutput(
        app_metadata=AppMetadata(),
        design_parameters=design_params,
        generation_payloads=payloads
    )


def main():
    import sys
    concept = sys.argv[1] if len(sys.argv) > 1 else "cyberpunk samurai"
    
    print("Anime Experimental Poster Lab - AI Design Engine")
    print("=" * 55)
    print(f"\nProcessing concept: '{concept}'...")
    result = process_concept(concept)
    
    print("\n" + "=" * 55)
    print("GENERATED JSON OUTPUT")
    print("=" * 55)
    json_output = result.to_json()
    print(json_output.encode('ascii', 'replace').decode('ascii'))
    
    print("\n" + "=" * 55)
    print("PREVIEW SUMMARY")
    print("=" * 55)
    dp = result.design_parameters
    print(f"Technique:      {dp.technique.value}")
    print(f"Title:          {dp.concept_title}")
    print(f"Palette:        {', '.join(dp.color_palette.colors)}")
    print(f"Primary Text:   {dp.typography.primary_text}")
    kanji = dp.typography.kanji_sub or 'None'
    print(f"Kanji Sub:      {kanji.encode('ascii', 'replace').decode('ascii')}")
    print(f"\nImage Prompt:   {result.generation_payloads.image_generation_prompt[:100]}...")
    print(f"Video Prompt:   {result.generation_payloads.video_autocut_prompt[:100]}...")


if __name__ == "__main__":
    main()