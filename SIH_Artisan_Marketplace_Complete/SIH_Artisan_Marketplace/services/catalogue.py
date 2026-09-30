import os
import base64
import json
from io import BytesIO
from PIL import Image
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

def _client():
    key = os.getenv("GROQ_API_KEY")
    if not key:
        raise ValueError(
            "GROQ_API_KEY not found. Create a .env file in the project root using .env.example."
        )
    return Groq(api_key=key)

def generate_catalogue(image, artisan_name="", location="", language="English", known_material=""):
    """
    Uses a Groq vision-capable model through the OpenAI-compatible chat API.
    Set GROQ_VISION_MODEL in .env if your account uses a different vision model.
    """
    model = os.getenv("GROQ_VISION_MODEL", "meta-llama/llama-4-scout-17b-16e-instruct")

    buf = BytesIO()
    image.convert("RGB").save(buf, format="JPEG", quality=90)
    encoded = base64.b64encode(buf.getvalue()).decode("utf-8")

    prompt = f"""
You are an expert Indian handicraft catalogue assistant.
Create structured marketplace metadata for an artisan product from the image.

Artisan/SHG: {artisan_name or "unknown"}
Location: {location or "unknown"}
Known material: {known_material or "unknown"}
Output language: {language}

Return ONLY valid JSON with these keys:
product_name, description, category, material, tags, keywords,
estimated_cost, labour_hours, complexity

Rules:
- Do not invent specific certification, geographical indication, historical claims,
  artisan identity, or material when the image cannot establish it.
- estimated_cost is a rough editable estimate in INR.
- labour_hours is a rough estimate.
- complexity is an integer 1 to 5.
- tags and keywords must be arrays of short strings.
- Keep description suitable for an e-commerce marketplace.
"""

    response = _client().chat.completions.create(
        model=model,
        temperature=0.2,
        max_tokens=900,
        messages=[{
            "role": "user",
            "content": [
                {"type": "text", "text": prompt},
                {
                    "type": "image_url",
                    "image_url": {"url": f"data:image/jpeg;base64,{encoded}"}
                }
            ]
        }]
    )

    raw = response.choices[0].message.content.strip()
    raw = raw.replace("```json", "").replace("```", "").strip()

    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ValueError(f"AI returned invalid JSON. Raw response: {raw[:1000]}") from exc

    data.setdefault("tags", [])
    data.setdefault("keywords", [])
    data.setdefault("estimated_cost", 0)
    data.setdefault("labour_hours", 1)
    data.setdefault("complexity", 3)
    return data
