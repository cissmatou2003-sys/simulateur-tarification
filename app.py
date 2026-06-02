import streamlit as st
import pandas as pd

# --- CONFIGURATION DE LA PAGE ---
st.set_page_config(page_title="Simulateur GC", layout="wide")
st.title("🧮 Simulateur tarification Gestion conseillée")

# --- INITIALISATION DU PANIER ---
if 'panier_produits' not in st.session_state:
    st.session_state.panier_produits = []

# --- BARRE LATÉRALE : SAISIE DES DONNÉES ---
with st.sidebar:
    st.header("👤 Paramètres Client")
    deja_present = st.checkbox("Client GC avant juillet 2026 ou Privilège")
    
    st.divider()
    st.subheader("➕ Ajouter un produit")
    type_p = st.selectbox("Type", ["Assurance Vie", "CTO/PEA OPC", "CTO/PEA Titres vifs"])
    mnt_p = st.number_input("Montant (€)", min_value=0.0, step=1000.0)
    
    if st.button("Ajouter au panier", use_container_width=True):
        if mnt_p > 0:
            st.session_state.panier_produits.append({"type": type_p, "montant": mnt_p})
            st.rerun()
        else:
            st.warning("Le montant doit être supérieur à 0.")

    if st.button("Tout réinitialiser", type="secondary", use_container_width=True):
        st.session_state.panier_produits = []
        st.rerun()

# --- AFFICHAGE DU PANIER ---
col_table, col_res = st.columns([1.6, 1.4])

with col_table:
    st.write("### 📝 Détail des avoirs")
    if not st.session_state.panier_produits:
        st.info("Le panier est vide. Utilisez la barre latérale pour ajouter des contrats.")
    else:
        for i, item in enumerate(st.session_state.panier_produits):
            c1, c2, c3 = st.columns([2, 2, 0.5])
            with c1:
                st.write(f"**{item['type']}**")
            with c2:
                new_mnt = st.number_input(f"Montant (€)", value=float(item['montant']), key=f"mnt_{i}", label_visibility="collapsed")
                st.session_state.panier_produits[i]['montant'] = new_mnt
            with c3:
                if st.button("🗑️", key=f"del_{i}"):
                    st.session_state.panier_produits.pop(i)
                    st.rerun()
            st.divider()

# --- LOGIQUE DE CALCUL ---
total_soumis_limites_trim = 0  
total_titres_vifs_trim = 0     

# 1. On commence par cumuler les montants globaux par type de produit
cumul_assurance_vie = 0
cumul_opc = 0

for p in st.session_state.panier_produits:
    montant = p['montant']
    produit = p['type']
    
    if produit == "Assurance Vie":
        cumul_assurance_vie += montant
    elif produit == "CTO/PEA OPC":
        cumul_opc += montant
    else: # Titres vifs
        total_titres_vifs_trim += (montant * (0.75 / 100)) / 4

# 2. On applique le barème sur les montants cumulés globaux
# Calcul pour l'Assurance Vie globale
if cumul_assurance_vie > 0:
    taux_av = 0.25 if cumul_assurance_vie < 80000 else (0.20 if cumul_assurance_vie <= 200000 else 0.15)
    total_soumis_limites_trim += (cumul_assurance_vie * (taux_av / 100)) / 4

# Calcul pour les OPC globaux
if cumul_opc > 0:
    taux_opc = 0.60 if cumul_opc < 50000 else (0.50 if cumul_opc <= 80000 else 0.25)
    total_soumis_limites_trim += (cumul_opc * (taux_opc / 100)) / 4

# --- AFFICHAGE DES RÉSULTATS ---
with col_res:
    st.write("### 📊 Calcul des frais")

    if st.session_state.panier_produits:
        frais_av_opc_trim = total_soumis_limites_trim
        applied_plancher = False
        applied_plafond = False

        if frais_av_opc_trim > 0 and frais_av_opc_trim < 70.0:
            frais_av_opc_trim = 70.0
            applied_plancher = True
        
        if deja_present and frais_av_opc_trim > 120.0:
            frais_av_opc_trim = 120.0
            applied_plafond = True

        total_final_trim = frais_av_opc_trim + total_titres_vifs_trim

        st.metric("Total Trimestriel", f"{total_final_trim:.2f} €")
        st.metric("Total Annuel", f"{total_final_trim * 4:.2f} €")
        
        if applied_plancher: 
            st.warning("⚠️ **Plancher de 70€ appliqué** sur le bloc Assurance Vie / OPC.")
        if applied_plafond: 
            st.success("✅ **Plafond Privilège (120€) appliqué** sur le bloc Assurance Vie / OPC.")
        
        if total_titres_vifs_trim > 0:
            st.info(f"Information : {total_titres_vifs_trim:.2f} € de frais Titres Vifs inclus.")
    else:
        st.write("Ajoutez des produits pour voir le détail.")

    # --- IMAGE DE SYNTHÈSE PLACÉE EN BAS ---
    st.divider() # Petite ligne de séparation visuelle
    with st.expander("🔍 Voir le barème et les règles de calcul", expanded=False):
        try:
            st.image("tarification_GC_synthese.png", use_container_width=True)
        except:
            st.error("Fichier 'tarification_GC_synthese.png' introuvable.")
