from pathlib import Path
from datetime import datetime
import json
import uuid
import pandas as pd

DATA = Path("data")
IMAGES = DATA / "images"
CATALOGUE = DATA / "catalogue.csv"

COLUMNS = [
    "id","product_name","description","category","material","tags","keywords",
    "artisan_name","location","estimated_cost","labour_hours","complexity",
    "suggested_price","min_price","max_price","image_name","image_file",
    "ai_generated","status","created_at"
]

def ensure_data_dirs():
    DATA.mkdir(exist_ok=True)
    IMAGES.mkdir(exist_ok=True)
    if not CATALOGUE.exists():
        pd.DataFrame(columns=COLUMNS).to_csv(CATALOGUE, index=False)

def _decode(v):
    if isinstance(v, str):
        try:
            return json.loads(v)
        except Exception:
            return [x.strip() for x in v.split(",") if x.strip()]
    return v

def load_catalogue():
    ensure_data_dirs()
    df = pd.read_csv(CATALOGUE)
    for col in COLUMNS:
        if col not in df.columns:
            df[col] = ""
    if len(df):
        for col in ["tags","keywords"]:
            df[col] = df[col].apply(_decode)
        for col in ["suggested_price","min_price","max_price","estimated_cost","labour_hours","complexity"]:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)
    return df[COLUMNS]

def _save(df):
    out = df.copy()
    for col in ["tags","keywords"]:
        out[col] = out[col].apply(lambda x: json.dumps(x if isinstance(x, list) else [str(x)]))
    out.to_csv(CATALOGUE, index=False)

def add_product(product, image):
    ensure_data_dirs()
    pid = str(uuid.uuid4())[:8]
    filename = f"{pid}.jpg"
    image.convert("RGB").save(IMAGES / filename, quality=92)

    row = {c: "" for c in COLUMNS}
    row.update(product)
    row["id"] = pid
    row["image_file"] = filename
    row["tags"] = product.get("tags", [])
    row["keywords"] = product.get("keywords", [])
    row["created_at"] = datetime.now().isoformat(timespec="seconds")

    df = load_catalogue()
    df = pd.concat([df, pd.DataFrame([row])], ignore_index=True)
    _save(df)

def update_product(pid, updates):
    df = load_catalogue()
    mask = df["id"].astype(str) == str(pid)
    for key, value in updates.items():
        if key in df.columns:
            df.loc[mask, key] = value
    _save(df)

def delete_product(pid):
    df = load_catalogue()
    match = df[df["id"].astype(str) == str(pid)]
    if len(match):
        image_file = match.iloc[0].get("image_file", "")
        if image_file:
            path = IMAGES / str(image_file)
            if path.exists():
                path.unlink()
    df = df[df["id"].astype(str) != str(pid)]
    _save(df)
