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
