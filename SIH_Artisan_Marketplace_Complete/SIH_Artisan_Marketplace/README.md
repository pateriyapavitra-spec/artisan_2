# ArtisanAI Marketplace — SIH26090

AI-driven market linkage and smart cataloguing mobile/web application concept for marginalized artisans.

## MVP included

1. **AI Catalogue**
   - Upload a product photograph.
   - Groq vision model generates product name, description, category, material, tags, keywords and pricing inputs.
   - Human can edit the AI draft before saving.

2. **Smart Pricing**
   - Transparent pricing model using production cost, labour, craft complexity and artisan margin.
   - Shows minimum, recommended and premium price ranges.

3. **Catalogue Manager**
   - Edit product metadata.
   - Approve/publish status.
   - Delete products.

4. **Marketplace Preview**
   - Search products.
   - Filter by category.
   - Product cards with image and price.

5. **Dashboard**
   - Product count, categories, average price and AI-generated catalogue count.

## Folder structure

```text
SIH_Artisan_Marketplace/
├── app.py
├── requirements.txt
├── .env.example
├── README.md
├── services/
│   ├── __init__.py
│   ├── catalogue.py
│   ├── pricing.py
│   └── storage.py
└── data/
    ├── catalogue.csv
    └── images/
```

## Run locally

### Windows

```powershell
cd SIH_Artisan_Marketplace
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
```

Open `.env` and replace `your_groq_api_key_here` with your Groq API key.

Then:

```powershell
streamlit run app.py
```

### macOS/Linux

```bash
cd SIH_Artisan_Marketplace
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Add the Groq API key to `.env`, then:

```bash
streamlit run app.py
```

## Streamlit deployment

For Streamlit Community Cloud:

1. Upload this project to GitHub.
2. In Streamlit, create a new app.
3. Select the repository and `app.py` as the main file.
4. Add `GROQ_API_KEY` under App Settings → Secrets.
5. If required, add `GROQ_VISION_MODEL` as another secret.

Use TOML syntax in Streamlit Secrets:

```toml
GROQ_API_KEY = "your_key_here"
GROQ_VISION_MODEL = "meta-llama/llama-4-scout-17b-16e-instruct"
```

### Important

Do NOT put your real API key in GitHub or inside the Python source code.

## Demo flow for SIH

1. Open Dashboard.
2. Go to AI Catalogue.
3. Upload an artisan product image.
4. Enter artisan/SHG and location.
5. Generate the AI catalogue.
6. Review and edit the draft.
7. Save the product.
8. Open Smart Pricing and demonstrate the transparent price calculation.
9. Open Marketplace to show the product listing.
10. Use Catalogue Manager to demonstrate approval/editing.

## Future production modules

- Flutter mobile frontend
- Artisan login and onboarding
- Multilingual voice input
- Regional-language catalogue generation
- Government/SHG verification
- Geolocation and artisan clusters
- Marketplace order management
- Buyer accounts
- Payments
- Demand forecasting
- Real marketplace price data
- Image-based quality grading
- Analytics for NGOs/government agencies
- Database and cloud object storage
- Role-based admin dashboard

## Architecture

```text
Artisan
   ↓
Flutter / Streamlit UI
   ↓
Image Upload
   ↓
Groq Vision AI
   ↓
Product Metadata
   ↓
Human Review & Editing
   ↓
Smart Pricing Engine
   ↓
Catalogue Database
   ↓
Marketplace / Buyer Interface
```
