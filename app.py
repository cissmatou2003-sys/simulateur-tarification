import streamlit as st
import pandas as pd

# --- CONFIGURATION PAGE ---
st.set_page_config(page_title="Simulateur GC", layout="wide")

# --- AJOUT DU LOGO ET STYLE CSS ---
# On utilise du CSS pour placer le logo proprement et colorer les titres en bleu CA
st.markdown("""
    <style>
        .main-title {
            color: #007D8F;
            font-weight: bold;
            margin-bottom: 0px;
        }
        /* Style pour les metrics pour rappeler la banque */
        [data-testid="stMetricValue"] {
            color: #007D8F;
        }
    </style>
""", unsafe_allow_html=True)

# --- BARRE LATÉRALE ---
with st.sidebar:
    # Logo Crédit Agricole (via URL pour test immédiat)
    st.image("https://share.google/B4pysDu12kKyyL9Qt", width=150)
    
    st.header("👤 Paramètres Client")
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

# --- CORPS DU SIMULATEUR ---
st.markdown('<h1 class="main-title">🧮 Simulateur tarification Gestion conseillée</h1>', unsafe_allow_html=True)
st.write("---")

if 'panier_produits' not in st.session_state:
    st.session_state.panier_produits = []

col_table, col_res = st.columns([2, 1])

with col_table:
    st.write("### 📝 Détail des avoirs du client")
    if not st.session_state.panier_produits:
        st.info("Utilisez le menu à gauche pour ajouter des actifs.")
    else:
        df = pd.DataFrame(st.session_state.panier_produits)
        # Formatage pour l'affichage
        df_display = df.copy()
        df_display['montant'] = df_display['montant'].apply(lambda x: f"{x:,.2f} €")
        st.table(df_display)

# --- LOGIQUE DE CALCUL ---
total_soumis_limites_trim = 0  
total_titres_vifs_trim = 0     

for p in st.session_state.panier_produits:
    montant = p['montant']
    produit = p['type']
    
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
        
    else: # Titres vifs
        taux = 0.75
        total_titres_vifs_trim += (montant * (taux / 100)) / 4

# --- AFFICHAGE DES RÉSULTATS ---
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
        st.write("### 📊 Résultat de la simulation")
        st.metric("Total Trimestriel", f"{total_final_trim:.2f} €")
        st.metric("Total Annuel", f"{total_final_trim * 4:.2f} €")
        
        st.divider()
        if applied_plancher:
            st.warning("⚠️ Plancher (70€) appliqué sur AV/OPC.")
        if applied_plafond:
            st.success("✅ Plafond Privilège (120€) appliqué.")
        if total_titres_vifs_trim > 0:
            st.info(f"ℹ️ Dont {total_titres_vifs_trim:.2f}€ de Titres vifs hors forfait.")
