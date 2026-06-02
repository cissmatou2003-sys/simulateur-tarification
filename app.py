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

# 1. Cumul des montants globaux par catégorie de produit
cumul_assurance_vie = 0
cumul_opc = 0

for p in st.session_state.panier_produits:
    montant = p['montant']
    produit = p['type']
    
    if produit == "Assurance Vie":
        cumul_
