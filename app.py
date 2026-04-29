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

# --- AFFICHAGE ET GESTION DU PANIER ---
col_table, col_res = st.columns([1.8, 1.2])

with col_table:
    st.write("### 📝 Détail des avoirs")
    if not st.session_state.panier_produits:
        st.info("Le panier est vide.")
    else:
        # On crée une ligne pour chaque produit avec un bouton de suppression
        for i, item in enumerate(st.session_state.panier_produits):
            c1, c2, c3 = st.columns([2, 2, 0.5])
            with c1:
                st.write(f"**{item['type']}**")
            with c2:
                # Modification simplifiée : un champ numérique par ligne
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

for p in st.session_state.panier_produits:
    montant = p['montant']
    produit = p['type']
    
    if produit == "Assurance Vie":
        taux = 0.25 if montant < 80000 else (0.20 if montant <= 200000 else 0.15)
        total_soumis_limites_trim += (montant * (taux / 100)) / 4
    elif produit == "CTO/PEA OPC":
        taux = 0.60 if montant < 50000 else (0.50 if montant <= 80000 else 0.25)
        total_soumis_limites_trim += (montant * (taux / 100)) / 4
    else: # Titres vifs
        total_titres_vifs_trim += (montant * (0.75 / 100)) / 4

# --- RÉSULTATS ---
with col_res:
    st.write("### 📊 Calcul des frais")
    if st.session_state.panier_produits:
        frais_av_opc_trim = total_soumis_limites_trim
        applied_plancher = False
        applied_plafond = False

        if frais_av_opc_trim > 0:
            if frais_av_opc_trim < 70.0:
                frais_av_opc_trim = 70.0
                applied_plancher = True
            if deja_present and frais_av_opc_trim > 120.0:
                frais_av_opc_trim = 120.0
                applied_plafond = True

        total_final_trim = frais_av_opc_trim + total_titres_vifs_trim

        st.metric("Total Trimestriel", f"{total_final_trim:.2f} €")
        st.metric("Total Annuel", f"{total_final_trim * 4:.2f} €")
        
        if applied_plancher: st.warning("⚠️ Plancher de 70€ appliqué.")
        if applied_plafond: st.success("✅ Plafond Privilège appliqué.")
    else:
        st.write("Ajoutez des produits pour voir le calcul.")
