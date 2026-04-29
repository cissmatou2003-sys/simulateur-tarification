import streamlit as st
import pandas as pd

st.set_page_config(page_title="Simulateur GC", layout="wide")
st.title("🧮 Simulateur tarification Gestion conseillée")

# --- INITIALISATION ---
if 'panier_produits' not in st.session_state:
    st.session_state.panier_produits = []

# --- BARRE LATÉRALE : SAISIE ---
with st.sidebar:
    st.header("👤 Paramètres Client")
    # Nouveau libellé demandé
    deja_present = st.checkbox("Client GC avant juillet 2026 ou détenteur d'une convention Privilège")
    
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
        df = pd.DataFrame(st.session_state.panier_produits)
        st.table(df)

# --- LOGIQUE DE CALCUL ---
total_soumis_limites_trim = 0  # Pour AV et OPC
total_titres_vifs_trim = 0     # Pour Titres vifs (Hors forfait)

for p in st.session_state.panier_produits:
    montant = p['montant']
    produit = p['type']
    taux = 0
    
    if produit == "Assurance Vie":
        if montant < 80000: taux = 0.25
        elif montant <= 200000: taux = 0.20
        else: taux = 0.15
        total_soumis_limites_trim += (montant * (taux / 100)) / 4
        
    elif produit == "CTO/PEA OPC":
        if montant < 50000: taux = 0.60
        elif montant <= 80000: taux = 0.50
        else: taux = 0.25
        total_soumis_limites_trim += (montant * (taux / 100)) / 4
        
    else: # CTO/PEA Titres vifs
        taux = 0.75
        total_titres_vifs_trim += (montant * (taux / 100)) / 4

# --- APPLICATION DES RÈGLES SPÉCIFIQUES ---
if st.session_state.panier_produits:
    # 1. Traitement de la part AV / OPC (avec Plancher/Plafond)
    frais_av_opc_trim = total_soumis_limites_trim
    applied_plancher = False
    applied_plafond = False

    if frais_av_opc_trim > 0:
        # Application du plancher de 70€
        if frais_av_opc_trim < 70.0:
            frais_av_opc_trim = 70.0
            applied_plancher = True
        
        # Application du plafond de 120€ (si éligible)
        if deja_present and frais_av_opc_trim > 120.0:
            frais_av_opc_trim = 120.0
            applied_plafond = True

    # 2. Somme finale
    total_final_trim = frais_av_opc_trim + total_titres_vifs_trim

    with col_res:
        st.write("### 📊 Total Client")
        st.metric("Total Trimestriel", f"{total_final_trim:.2f} €")
        st.metric("Total Annuel", f"{total_final_trim * 4:.2f} €")
        
        st.divider()
        # Indicateurs de transparence
        if applied_plancher:
            st.warning("⚠️ Plancher de 70€ appliqué sur AV/OPC.")
        if applied_plafond:
            st.success("✅ Plafond Privilège (120€) appliqué sur AV/OPC.")
        if total_titres_vifs_trim > 0:
            st.info(f"ℹ️ Titres vifs : {total_titres_vifs_trim:.2f}€ (Facturés hors forfait)")
    
