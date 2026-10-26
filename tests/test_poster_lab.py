"""Tests del motor (`poster_lab.py`): catálogo, selección y determinismo."""
import json
import random

import pytest

from poster_lab import (
    ColorPalette,
    Technique,
    generate_concept_title,
    get_kanji_subtitle,
    process_concept,
    select_technique,
)


def test_technique_catalog_has_eleven():
    assert len(list(Technique)) == 11


def test_palette_requires_exactly_three_colors():
    with pytest.raises(ValueError):
        ColorPalette(colors=["#000000", "#FFFFFF"])
    ColorPalette(colors=["#000000", "#FFFFFF", "#FF0000"])  # no lanza


@pytest.mark.parametrize(
    "concept, esperado",
    [
        ("cyberpunk samurai", Technique.BLEND_IN_BLACK),
        ("minimal watercolor", Technique.BLEND_ON_WHITE),
        ("cutout silhouette collage", Technique.MASK_CUT),
        ("glitch datamosh", Technique.GLITCH_ART),
        ("vaporwave retro", Technique.VAPORWAVE),
        ("mecha blueprint", Technique.MECHA_BLUEPRINT),
    ],
)
def test_select_technique_by_keyword(concept, esperado):
    assert select_technique(concept) == esperado


def test_select_technique_fallback_is_a_valid_technique():
    random.seed(0)
    assert select_technique("zzz sin palabra clave") in list(Technique)


def test_kanji_subtitle_known_and_unknown():
    assert get_kanji_subtitle("cyberpunk city") == "サイバーパンク"
    assert get_kanji_subtitle("sin coincidencia") is None


def test_concept_title_uses_concept_words():
    random.seed(1)
    titulo = generate_concept_title("cyberpunk samurai", Technique.BLEND_IN_BLACK)
    assert "Cyberpunk" in titulo or "Samurai" in titulo


def test_process_concept_is_deterministic_with_seed():
    random.seed(123)
    a = process_concept("cyberpunk samurai").to_json()
    random.seed(123)
    b = process_concept("cyberpunk samurai").to_json()
    assert a == b


def test_process_concept_output_structure():
    random.seed(7)
    data = json.loads(process_concept("neo tokyo rain").to_json())

    assert data["app_metadata"]["engine_version"] == "2.5-AI"
    assert data["app_metadata"]["project_name"] == "Anime Experimental Poster Lab"

    design = data["design_parameters"]
    assert design["technique"] in [t.value for t in Technique]
    paleta = design["color_palette"]["colors"]
    assert len(paleta) == 3

    payloads = data["generation_payloads"]
    assert payloads["image_generation_prompt"]
    assert payloads["video_autocut_prompt"]
    for color in paleta:
        assert color in payloads["image_generation_prompt"]
