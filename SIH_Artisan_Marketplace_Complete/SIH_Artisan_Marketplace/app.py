import streamlit as st
from pathlib import Path
import pandas as pd
from PIL import Image

from services.catalogue import generate_catalogue
from services.pricing import calculate_price
from services.storage import (
    load_catalogue, save_catalogue, add_product, update_product,
    delete_product, ensure_data_dirs
)

st.set_page_config(
    page_title="ArtisanAI — SIH",
    page_icon="🧵",
    layout="wide",
    initial_sidebar_state="expanded"
)

ensure_data_dirs()

st.markdown("""
<style>
.main-title {font-size: 2.3rem; font-weight: 800; margin-bottom: 0;}
.subtitle {color: #666; margin-top: 0;}
.card {padding: 1rem; border-radius: 14px; border: 1px solid #ddd; background: #fff;}
.metric-box {padding: 14px; border-radius: 12px; border: 1px solid #ddd;}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">🧵 ArtisanAI Marketplace</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">AI-driven market linkage and smart cataloguing for marginalized artisans • SIH26090</div>', unsafe_allow_html=True)

with st.sidebar:
    st.header("Navigation")
    page = st.radio(
        "Go to",
        ["🏠 Dashboard", "📸 AI Catalogue", "💰 Smart Pricing", "🛍️ Marketplace", "📋 Catalogue Manager"]
    )
    st.divider()
    st.caption("SIH Prototype • Streamlit + Groq")

catalogue = load_catalogue()

if page == "🏠 Dashboard":
    st.subheader("Project Dashboard")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Products", len(catalogue))
    c2.metric("Categories", catalogue["category"].nunique() if len(catalogue) else 0)
    c3.metric("Avg. Price", f"₹{catalogue['suggested_price'].mean():,.0f}" if len(catalogue) else "₹0")
    c4.metric("AI Catalogued", len(catalogue[catalogue["ai_generated"] == True]) if len(catalogue) else 0)

    st.divider()
    st.markdown("### Solution Flow")
    cols = st.columns(5)
    steps = [
        ("1", "📷", "Upload Product"),
        ("2", "🤖", "AI Cataloguing"),
        ("3", "💰", "Smart Pricing"),
        ("4", "✏️", "Edit & Approve"),
        ("5", "🛍️", "Market Listing"),
    ]
    for col, (n, icon, text) in zip(cols, steps):
        with col:
            st.markdown(f"### {icon}")
            st.write(f"**{n}. {text}**")

    if len(catalogue):
        st.markdown("### Recent Products")
        show = catalogue.sort_values("created_at", ascending=False).head(6)
        st.dataframe(
            show[["product_name","category","artisan_name","suggested_price","status"]],
            use_container_width=True, hide_index=True
        )
    else:
        st.info("No products yet. Open **AI Catalogue** to create your first listing.")

elif page == "📸 AI Catalogue":
    st.subheader("AI Product Catalogue Generator")
    st.write("Upload a product image. The AI generates a draft name, description, category, tags, keywords and pricing inputs.")

    uploaded = st.file_uploader(
        "Upload artisan product image",
        type=["jpg", "jpeg", "png", "webp"]
    )

    left, right = st.columns([1, 1])
    with left:
        artisan_name = st.text_input("Artisan / SHG name", placeholder="e.g. Rani Self Help Group")
        location = st.text_input("Location", placeholder="e.g. Jhansi, Uttar Pradesh")
        language = st.selectbox("Catalogue language", ["English", "Hindi"])
        materials = st.text_input("Known material (optional)", placeholder="e.g. cotton, clay, bamboo")
        st.caption("If you know the material, adding it improves the catalogue draft.")

    if uploaded:
        image = Image.open(uploaded)
        with right:
            st.image(image, caption="Uploaded product", use_container_width=True)

        if st.button("✨ Generate AI Catalogue", type="primary", use_container_width=True):
            with st.spinner("Analysing product image and creating catalogue draft..."):
                try:
                    result = generate_catalogue(
                        image=image,
                        artisan_name=artisan_name,
                        location=location,
                        language=language,
                        known_material=materials
                    )
                    st.session_state["draft"] = result
                    st.success("AI catalogue draft generated.")
                except Exception as e:
                    st.error(str(e))

    draft = st.session_state.get("draft")
    if draft:
        st.divider()
        st.markdown("### Review & Edit AI Draft")
        with st.form("catalogue_form"):
            name = st.text_input("Product name", draft.get("product_name", ""))
            description = st.text_area("Description", draft.get("description", ""), height=130)
            category = st.text_input("Category", draft.get("category", ""))
            material = st.text_input("Material", draft.get("material", materials))
            tags = st.text_input("Tags", ", ".join(draft.get("tags", [])))
            keywords = st.text_input("Search keywords", ", ".join(draft.get("keywords", [])))

            st.markdown("#### Pricing inputs")
            p1, p2, p3 = st.columns(3)
            with p1:
                cost = st.number_input("Material + production cost (₹)", min_value=0.0, value=float(draft.get("estimated_cost", 0)))
            with p2:
                hours = st.number_input("Labour hours", min_value=0.0, value=float(draft.get("labour_hours", 1.0)))
            with p3:
                complexity = st.slider("Craft complexity", 1, 5, int(draft.get("complexity", 3)))

            submitted = st.form_submit_button("Save Catalogue Product", type="primary")
            if submitted:
                pricing = calculate_price(cost, hours, complexity)
                product = {
                    "product_name": name,
                    "description": description,
                    "category": category,
                    "material": material,
                    "tags": [x.strip() for x in tags.split(",") if x.strip()],
                    "keywords": [x.strip() for x in keywords.split(",") if x.strip()],
                    "artisan_name": artisan_name or "Artisan",
                    "location": location,
                    "estimated_cost": cost,
                    "labour_hours": hours,
                    "complexity": complexity,
                    "suggested_price": pricing["suggested_price"],
                    "min_price": pricing["min_price"],
                    "max_price": pricing["max_price"],
                    "image_name": uploaded.name,
                    "ai_generated": True,
                    "status": "Draft"
                }
                add_product(product, image)
                st.session_state.pop("draft", None)
                st.success("Product saved to catalogue.")
                st.rerun()

elif page == "💰 Smart Pricing":
    st.subheader("Smart Pricing Engine")
    st.write("A transparent MVP pricing model using production cost, labour, craft complexity and a configurable artisan margin.")

    c1, c2 = st.columns(2)
    with c1:
        cost = st.number_input("Material + production cost (₹)", 0.0, 100000.0, 300.0)
        hours = st.number_input("Labour hours", 0.0, 1000.0, 4.0)
        complexity = st.slider("Craft complexity", 1, 5, 3)
    with c2:
        labour_rate = st.number_input("Labour rate (₹/hour)", 50.0, 5000.0, 150.0)
        margin = st.slider("Target artisan margin", 0.05, 0.80, 0.25)

    if st.button("Calculate Smart Price", type="primary"):
        result = calculate_price(cost, hours, complexity, labour_rate, margin)
        a, b, c = st.columns(3)
        a.metric("Recommended", f"₹{result['suggested_price']:,.0f}")
        b.metric("Minimum", f"₹{result['min_price']:,.0f}")
        c.metric("Premium ceiling", f"₹{result['max_price']:,.0f}")

        st.markdown("### Calculation")
        st.write(f"Base production cost: ₹{result['base_cost']:,.0f}")
        st.write(f"Complexity multiplier: {result['complexity_multiplier']:.2f}×")
        st.write(f"Target margin: {result['margin']:.0%}")
        st.info("The price is a decision-support estimate, not a guaranteed market price. Local demand and marketplace fees should be added before deployment.")

elif page == "🛍️ Marketplace":
    st.subheader("Artisan Marketplace Preview")
    if not len(catalogue):
        st.info("Add products from AI Catalogue first.")
    else:
        search = st.text_input("🔎 Search products", "")
        categories = ["All"] + sorted(catalogue["category"].dropna().unique().tolist())
        selected = st.selectbox("Category", categories)

        data = catalogue.copy()
        if search:
            mask = data.apply(
                lambda r: search.lower() in str(r["product_name"]).lower()
                or search.lower() in str(r["description"]).lower()
                or search.lower() in str(r["keywords"]).lower(), axis=1
            )
            data = data[mask]
        if selected != "All":
            data = data[data["category"] == selected]

        for _, row in data.iterrows():
            with st.container(border=True):
                cols = st.columns([1, 2, 1])
                img_path = Path("data/images") / str(row.get("image_file", ""))
                with cols[0]:
                    if img_path.exists():
                        st.image(str(img_path), use_container_width=True)
                    else:
                        st.info("No image")
                with cols[1]:
                    st.markdown(f"### {row['product_name']}")
                    st.write(row["description"])
                    st.caption(f"{row['category']} • {row['material']} • {row['location']}")
                    st.write("Tags:", ", ".join(row["tags"]) if isinstance(row["tags"], list) else row["tags"])
                with cols[2]:
                    st.metric("Price", f"₹{row['suggested_price']:,.0f}")
                    st.button("View / Enquire", key=f"view_{row['id']}")

elif page == "📋 Catalogue Manager":
    st.subheader("Catalogue Manager")
    if not len(catalogue):
        st.info("Catalogue is empty.")
    else:
        for _, row in catalogue.iterrows():
            with st.expander(f"{row['product_name']} — {row['category']}"):
                with st.form(f"edit_{row['id']}"):
                    name = st.text_input("Product name", row["product_name"], key=f"name_{row['id']}")
                    desc = st.text_area("Description", row["description"], key=f"desc_{row['id']}")
                    category = st.text_input("Category", row["category"], key=f"cat_{row['id']}")
                    price = st.number_input("Suggested price", 0.0, 1000000.0, float(row["suggested_price"]), key=f"price_{row['id']}")
                    status = st.selectbox("Status", ["Draft", "Approved", "Published"], index=["Draft","Approved","Published"].index(row["status"]) if row["status"] in ["Draft","Approved","Published"] else 0, key=f"status_{row['id']}")
                    if st.form_submit_button("Update"):
                        update_product(row["id"], {
                            "product_name": name, "description": desc,
                            "category": category, "suggested_price": price,
                            "status": status
                        })
                        st.success("Updated.")
                        st.rerun()

                if st.button("Delete product", key=f"delete_{row['id']}"):
                    delete_product(row["id"])
                    st.rerun()
