import streamlit as st
import pandas as pd

# --- CONFIGURATION PAGE ---
st.set_page_config(page_title="Simulateur GC - Crédit Agricole", layout="wide")

# --- DESIGN VERT & BLANC ---
st.markdown("""
    <style>
        /* Couleur de fond générale (Blanc) */
        .stApp {
            background-color: #FFFFFF;
        }
        
        /* Titres en Vert CA */
        h1, h2, h3 {
            color: #007D8F !important;
        }
        
        /* Sidebar en gris très clair pour faire ressortir le blanc */
        [data-testid="stSidebar"] {
            background-color: #F9FBFB;
            border-right: 1px solid #E0E0E0;
        }

        /* Boutons Vert CA */
        .stButton > button {
            background-color: #007D8F;
            color: white;
            border-radius: 4px;
            border: none;
            width: 100%;
            font-weight: bold;
        }
        
        .stButton > button:hover {
            background-color: #97BE0D; /* Passage au vert pomme au survol */
            color: white;
        }

        /* Métriques (Montants financiers) */
        [data-testid="stMetricValue"] {
            color: #007D8F;
        }

        /* Cartouche de résultat Blanc & Vert */
        .result-box {
            background-color: #FFFFFF;
            padding: 25px;
            border: 2px solid #007D8F;
            border-radius: 15px;
            text-align: center;
        }
    </style>
""", unsafe_allow_html=True)

# --- INITIALISATION ---
if 'panier_produits' not in st.session_state:
    st.session_state.panier_produits = []

# --- BARRE LATÉRALE ---
with st.sidebar:
    # Logo
    st.image("https://www.credit-agricole.fr/content/dam/assetsca/logos/ca-logo.png", width=160)
    
    st.markdown("### 👤 Paramètres")
    deja_present = st.checkbox("Client GC avant juillet 2026 ou détenteur d'une convention Privilège")
    
    st.divider()
    st.markdown("### ➕ Ajouter un produit")
    type_p = st.selectbox("Type d'actif", ["Assurance Vie", "CTO/PEA OPC", "CTO/PEA Titres vifs"])
    mnt_p = st.number_input("Montant (€)", min_value=0.0, step=10000.0, format="%.2f")
    
    if st.button("Ajouter à la simulation"):
        if mnt_p > 0:
            st.session_state.panier_produits.append({"type": type_p, "montant": mnt_p})
            st.rerun()

    if st.button("Réinitialiser"):
        st.session_state.panier_produits = []
        st.rerun()

# --- CORPS DE PAGE ---
st.markdown('# 🧮 Simulateur de tarification <span style="color:#97BE0D">Gestion Conseillée</span>', unsafe_allow_html=True)
st.write("")

col_left, col_right = st.columns([2, 1], gap="large")

with col_left:
    st.subheader("📝 Récapitulatif du Patrimoine")
    if not st.session_state.panier_produits:
        st.info("Veuillez ajouter des produits depuis le panneau latéral pour débuter la simulation.")
    else:
        df = pd.DataFrame(st.session_state.panier_produits)
        # Affichage propre du tableau
        st.dataframe(df.style.format({"montant": "{:,.2f} €"}), use_container_width=True, hide_index=True)

# --- CALCULS ---
base_frais_trim = 0  # AV et OPC
titres_vifs_trim = 0 # Hors plafond/plancher

for p in st.session_state.panier_produits:
    m, t = p['montant'], p['type']
    if t == "Assurance Vie":
        tx = 0.25 if m < 80000 else (0.20 if m <= 200000 else 0.15)
        base_frais_trim += (m * (tx / 100)) / 4
    elif t == "CTO/PEA OPC":
        tx = 0.60 if m < 50000 else (0.50 if m <= 80000 else 0.25)
        base_frais_trim += (m * (tx / 100)) / 4
    else: # Titres vifs
        titres_vifs_trim += (m * (0.75 / 100)) / 4

# --- AFFICHAGE SYNTHÈSE ---
with col_right:
    st.subheader("📊 Tarification")
    if st.session_state.panier_produits:
        applied_plancher = False
        applied_plafond = False

        # Logique Plancher/Plafond sur AV et OPC
        frais_fixes = base_frais_trim
        if frais_fixes > 0:
            if frais_fixes < 70.0:
                frais_fixes = 70.0
                applied_plancher = True
            if deja_present and frais_fixes > 120.0:
                frais_fixes = 120.0
                applied_plafond = True

        total_trim = frais_fixes + titres_vifs_trim

        # Encadré final blanc et vert
        st.markdown(f"""
            <div class="result-box">
                <p style="color: #666; font-size: 14px; margin-bottom: 5px;">COÛT TRIMESTRIEL TOTAL</p>
                <h1 style="margin: 0; color: #007D8F;">{total_trim:.2f} €</h1>
                <hr style="border: 0.5px solid #EEE;">
                <p style="color: #666; font-size: 14px; margin-bottom: 5px;">COÛT ANNUEL ESTIMÉ</p>
                <h2 style="margin: 0; color: #97BE0D;">{total_trim * 4:.2f} €</h2>
            </div>
        """, unsafe_allow_html=True)

        st.write("")
        if applied_plancher:
            st.warning("Plancher de 70€ appliqué sur la part hors titres vifs.")
        if applied_plafond:
            st.success("Plafond 'Fidélité/Privilège' appliqué.")
        if titres_vifs_trim > 0:
            st.info(f"Dont {titres_vifs_trim:.2f}€ de frais sur titres vifs (hors forfait).")
