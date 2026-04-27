import streamlit as st

st.set_page_config(page_title="Simulateur Multi-Produits", layout="wide")
st.title("🧮 Simulateur de Tarification Client (Juin 2026)")

# --- INITIALISATION ---
if 'panier_produits' not in st.session_state:
    st.session_state.panier_produits = []

# --- BARRE LATÉRALE : SAISIE ---
with st.sidebar:
    st.header("👤 Paramètres Client")
    deja_present = st.checkbox("Client présent avant le 1er juin 2026")
    
    st.divider()
    st.subheader("➕ Ajouter un produit")
    type_p = st.selectbox("Type", ["Assurance Vie", "CTO/PEA OPC", "CTO/PEA Titres vifs"])
    mnt_p = st.number_input("Montant (€)", min_value=0.0, step=1000.0)
    
    if st.button("Ajouter au panier"):
        if mnt_p > 0:
            st.session_state.panier_produits.append({"type": type_p, "montant": mnt_p})
            st.success(f"{type_p} ajouté !")
        else:
            st.warning("Le montant doit être supérieur à 0.")

    if st.button("Réinitialiser le simulateur"):
        st.session_state.panier_produits = []
        st.rerun()

# --- AFFICHAGE DU RÉCAPITULATIF ---
col_table, col_res = st.columns([2, 1])

with col_table:
    st.write("### 📝 Détail des avoirs du client")
    if not st.session_state.panier_produits:
        st.info("Aucun produit ajouté pour le moment.")
    else:
        # Affichage sous forme de tableau
        import pandas as pd
        df = pd.DataFrame(st.session_state.panier_produits)
        st.table(df)

# --- LOGIQUE DE CALCUL GLOBAL ---
total_theorique_trim = 0

for p in st.session_state.panier_produits:
    montant = p['montant']
    produit = p['type']
    taux = 0
    
    if produit == "Assurance Vie":
        if montant < 80000: taux = 0.25
        elif montant <= 200000: taux = 0.20
        else: taux = 0.15
    elif produit == "CTO/PEA OPC":
        if montant < 50000: taux = 0.60
        elif montant <= 80000: taux = 0.50
        else: taux = 0.25
    else: # Titres vifs
        taux = 0.75
    
    total_theorique_trim += (montant * (taux / 100)) / 4

# --- APPLICATION DES RÈGLES CLIENT ---
if st.session_state.panier_produits:
    # 1. Application du plancher de 70€
    frais_reels_trim = max(total_theorique_trim, 70.0)
    
    # 2. Application du plafond de 120€ si client historique
    is_plafonné = False
    if deja_present and frais_reels_trim > 120.0:
        frais_reels_trim = 120.0
        is_plafonné = True

    with col_res:
        st.write("### 📊 Total Client")
        st.metric("Total Trimestriel", f"{frais_reels_trim:.2f} €")
        st.metric("Total Annuel", f"{frais_reels_trim * 4:.2f} €")
        
        if total_theorique_trim < 70.0:
            st.warning(f"⚠️ Plancher appliqué (Théorique: {total_theorique_trim:.2f} €)")
        if is_plafonné:
            st.success("✅ Plafond 'Fidélité' appliqué (120 €)")
    
    
