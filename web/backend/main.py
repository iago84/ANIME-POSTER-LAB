from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
import json
import sys
import os

# Add the poster_lab module to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from poster_lab import process_concept, Technique, PosterLabOutput

app = FastAPI(title="Anime Experimental Poster Lab API", version="2.5-AI")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class GenerateRequest(BaseModel):
    concept: str
    technique: Optional[str] = None
    seed: Optional[int] = None

class GenerateResponse(BaseModel):
    success: bool
    data: Optional[dict] = None
    error: Optional[str] = None

class TechniqueInfo(BaseModel):
    id: str
    name: str
    description: str
    keywords: List[str]
    palette_example: List[str]

@app.get("/")
async def root():
    return {"message": "Anime Experimental Poster Lab API", "version": "2.5-AI"}

@app.get("/techniques", response_model=List[TechniqueInfo])
async def list_techniques():
    technique_details = {
        "BLEND_IN_BLACK": {
            "name": "Blend in Black",
            "description": "Deep black backgrounds, cinematic lighting, luminous fluid inks (electric blue, violet, magenta), negative space typography",
            "keywords": ["cyberpunk", "neon", "dark", "noir"],
            "palette_example": ["#00FFFF", "#8A2BE2", "#FF00FF"]
        },
        "BLEND_ON_WHITE": {
            "name": "Blend on White",
            "description": "Ivory/textured white backgrounds, translucent watercolors, overlapping geometric shapes, minimalist 3-color palettes",
            "keywords": ["minimal", "clean", "watercolor", "soft"],
            "palette_example": ["#F5F5DC", "#87CEEB", "#DDA0DD"]
        },
        "MASK_CUT": {
            "name": "Mask Cut",
            "description": "Cut-out silhouettes, flat color blocks, negative space containing landscapes or patterns, editorial collage and masked typography",
            "keywords": ["silhouette", "collage", "cutout", "editorial"],
            "palette_example": ["#FF6B35", "#004E89", "#FFFFFF"]
        },
        "GLITCH_ART": {
            "name": "Glitch Art",
            "description": "Datamoshing artifacts, RGB channel separation, scanlines, pixel sorting, corrupted data aesthetic, fragmented glitch typography",
            "keywords": ["glitch", "datamosh", "rgb", "corrupt"],
            "palette_example": ["#FF0066", "#00FFFF", "#FFFF00"]
        },
        "CEL_SHADED": {
            "name": "Cel Shaded",
            "description": "Hard cel-shaded shadows, flat color regions, clean line art, dramatic rim lighting, anime key frame style",
            "keywords": ["cel", "anime frame", "keyframe"],
            "palette_example": ["#FF6B35", "#2C3E50", "#ECF0F1"]
        },
        "UKIYO_E_MODERN": {
            "name": "Modern Ukiyo-e",
            "description": "Modern woodblock texture, bokashi gradients, flat perspective, floating world aesthetic, paper grain, brush stroke kanji",
            "keywords": ["ukiyo", "woodblock", "floating world"],
            "palette_example": ["#DC143C", "#1E3A5F", "#F5F0E1"]
        },
        "VAPORWAVE": {
            "name": "Vaporwave",
            "description": "Retro 80s/90s gradient skies, grid horizon, palm silhouettes, greek statues, CRT monitor glow, nostalgia filter",
            "keywords": ["vaporwave", "retro", "synthwave", "80s"],
            "palette_example": ["#FF6EC7", "#4EFFFF", "#FFFF4E"]
        },
        "INK_WASH": {
            "name": "Ink Wash (Sumi-e)",
            "description": "Sumi-e ink wash, wet brush strokes, negative space mastery, spontaneous brushwork, rice paper texture, calligraphy",
            "keywords": ["ink wash", "sumi", "brush", "calligraphy"],
            "palette_example": ["#1C1C1C", "#4A4A4A", "#F5F5F0"]
        },
        "NEO_TOKYO": {
            "name": "Neo Tokyo",
            "description": "Rain-slicked streets, holographic advertisements, neon reflections, towering megastructures, volumetric fog",
            "keywords": ["neo tokyo", "megacity", "hologram", "rain"],
            "palette_example": ["#FF0080", "#00FFFF", "#FFB800"]
        },
        "MECHA_BLUEPRINT": {
            "name": "Mecha Blueprint",
            "description": "Technical blueprint grid, white line schematics, measurement annotations, exploded view diagrams, engineering paper",
            "keywords": ["mecha", "blueprint", "schematic", "technical"],
            "palette_example": ["#00FF41", "#003366", "#FFFFFF"]
        },
        "CHROMATIC_ABERRATION": {
            "name": "Chromatic Aberration",
            "description": "Extreme lens distortion, RGB channel offset, prismatic color separation, surreal depth, optical aberration",
            "keywords": ["chromatic", "aberration", "prism", "lens"],
            "palette_example": ["#FF0044", "#00FF88", "#4400FF"]
        }
    }
    
    return [
        TechniqueInfo(
            id=k,
            name=v["name"],
            description=v["description"],
            keywords=v["keywords"],
            palette_example=v["palette_example"]
        )
        for k, v in technique_details.items()
    ]

@app.post("/generate", response_model=GenerateResponse)
async def generate_poster(request: GenerateRequest):
    try:
        if request.seed:
            import random
            random.seed(request.seed)
        
        # Process concept using the existing engine
        result = process_concept(request.concept)
        
        # Override technique if specified
        if request.technique:
            try:
                technique_enum = Technique(request.technique.upper())
                # Re-process with forced technique (would need modification to poster_lab)
                pass
            except ValueError:
                raise HTTPException(status_code=400, detail=f"Invalid technique: {request.technique}")
        
        return GenerateResponse(
            success=True,
            data=json.loads(result.to_json())
        )
    except Exception as e:
        return GenerateResponse(
            success=False,
            error=str(e)
        )

@app.post("/generate/video-prompt")
async def generate_video_prompt(request: GenerateRequest):
    try:
        result = process_concept(request.concept)
        return {
            "success": True,
            "video_prompt": result.generation_payloads.video_autocut_prompt,
            "technique": result.design_parameters.technique.value
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)