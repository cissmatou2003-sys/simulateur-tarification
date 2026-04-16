import streamlit as st

st.title("🧮 Simulateur de Tarification Juin 2026")

# 1. Barre latérale pour les saisies
with st.sidebar:
    st.header("Paramètres")
    produit = st.selectbox("Type de produit", ["Assurance Vie", "CTO/PEA OPC", "CTO/PEA Titres vifs"])
    montant = st.number_input("Montant de l'encours (€)", min_value=0.0, value=100000.0, step=1000.0)
    deja_present = st.checkbox("Client présent avant le 1er juin 2026")

# 2. Logique de calcul
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

frais_theoriques_trim = (montant * (taux / 100)) / 4
frais_reels_trim = max(frais_theoriques_trim, 70.0)

if deja_present and frais_reels_trim > 120.0:
    frais_reels_trim = 120.0

# 3. Affichage visuel
st.divider()
col1, col2 = st.columns(2)
col1.metric("Frais par trimestre", f"{frais_reels_trim:.2f} €")
col2.metric("Total annuel", f"{frais_reels_trim * 4:.2f} €")

if frais_reels_trim == 120.0:
    st.info("ℹ️ Le plafond de fidélité (120€/trim) a été appliqué.")
elif frais_reels_trim == 70.0:
    st.warning("ℹ️ Le plancher minimal (70€/trim) a été appliqué.")
