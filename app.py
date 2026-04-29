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
            st.rerun() # On force le rafraîchissement pour voir le produit
        else:
            st.warning("Le montant doit être supérieur à 0.")

    if st.button("Tout réinitialiser", type="secondary", use_container_width=True):
        st.session_state.panier_produits = []
        st.rerun()

# --- ZONE D'AFFICHAGE ET SUPPRESSION ---
col_table, col_res = st.columns([2, 1])

with col_table:
    st.write("### 📝 Détail des avoirs du client")
    if not st.session_state.panier_produits:
        st.info("Le panier est vide.")
    else:
        # On transforme le panier en DataFrame
        df_actuel = pd.DataFrame(st.session_state.panier_produits)
        
        st.write("💡 *Vous pouvez modifier les montants ou supprimer une ligne en la sélectionnant et en appuyant sur la touche 'Suppr' de votre clavier.*")
        
        # UTILISATION DU DATA_EDITOR POUR LA SUPPRESSION
        # num_rows="dynamic" permet d'ajouter/supprimer des lignes
        df_modifie = st.data_editor(
            df_actuel, 
            use_container_width=True, 
            num_rows="dynamic",
            column_config={
                "montant": st.column_config.NumberColumn("Montant (€)", format="%d €"),
                "type": st.column_config.SelectboxColumn("Type", options=["Assurance Vie", "CTO/PEA OPC", "CTO/PEA Titres vifs"])
            }
        )
        
        # MISE À JOUR DU SESSION STATE SI MODIFICATION
        if not df_modifie.equals(df_actuel):
            st.session_state.panier_produits = df_modifie.to_dict('records')
            st.rerun()

# --- LOGIQUE DE CALCUL (inchangée mais basée sur le panier potentiellement modifié) ---
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

# --- APPLICATION DES RÈGLES ---
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

    with col_res:
        st.write("### 📊 Total Client")
        st.metric("Total Trimestriel", f"{total_final_trim:.2f} €")
        st.metric("Total Annuel", f"{total_final_trim * 4:.2f} €")
        st.divider()
        if applied_plancher: st.warning("⚠️ Plancher de 70€ appliqué.")
        if applied_plafond: st.success("✅ Plafond Privilège appliqué.")
        if total_titres_vifs_trim > 0: st.info(f"ℹ️ Titres vifs : {total_titres_vifs_trim:.2f}€")
