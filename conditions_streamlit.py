import streamlit as st
import pandas as pd
import math

# === Charger le fichier Excel ===
@st.cache_data
def charger_donnees(path):
    df = pd.read_excel(path)
    df["Matière"] = df["Matière"].str.strip().str.lower()
    return df
df_vc = charger_donnees("condition_de_coupe.xlsx")

# Interface principale
st.title("🛠️ Assistant Usinage - Fraisage & Tournage")

operation = st.sidebar.radio("Choisissez l’opération :", ["Fraisage", "Tournage"])

# Fonction commune pour récupérer la Vc
def get_vc(matiere, mode="moyenne"):
    ligne = df_vc[df_vc["Matière"] == matiere.strip().lower()]
    if ligne.empty:
        return None
    return ligne.iloc[0][f"Vitesse de coupe {mode} (m/min)"]

# === Appli Streamlit ===
#st.title("🛠️ Conditions de Coupe – Usinage")

# Interface Fraisage
if operation == "Fraisage":
    st.subheader("🔧 Mode Fraisage")

    # Saisie utilisateur
    classes_disponibles = sorted(df_vc["Classe"].unique())
    classe_selectionnee = st.selectbox("Choisir une classe de matériau :", classes_disponibles)

    matieres_filtrees = df_vc[df_vc["Classe"] == classe_selectionnee]
    matiere = st.selectbox("Choisir une matière :", sorted(matieres_filtrees["Matière"].unique()))
    mode = st.radio("Mode de vitesse de coupe :", ["moyenne", "mini"], horizontal=True)

    # Récupérer la ligne correspondante à la matière
    ligne = df_vc[df_vc["Matière"].str.lower() == matiere.lower()]

    if not ligne.empty:
        if mode == "mini":
            vc = ligne.iloc[0]["Vitesse de coupe mini (m/min)"]
        else:
            vc = ligne.iloc[0]["Vitesse de coupe moyenne (m/min)"]

        st.success(f"💡 Vitesse de coupe {mode} : **{vc} m/min**")
    else:
        st.error("❌ Matière non trouvée dans le tableau.")

    diametre = st.number_input("Diamètre outil (mm)", min_value=0.1, step=0.1)
    avance_dent = st.number_input("Avance par dent (mm/dent)", min_value=0.001, step=0.001, format="%.3f")
    nb_dents = st.number_input("Nombre de dents", min_value=1, step=1)
    epaisseur_passe = st.number_input("Épaisseur de passe (mm)", min_value=0.01, step=0.01)
    longueur = st.number_input("Longueur d'usinage (mm)", min_value=1.0, step=1.0)

    if st.button("🧮 Calculer"):
        vc = get_vc(df_vc, matiere, mode)
        if vc is None:
            st.error("⚠️ Matière non trouvée dans le fichier Excel.")
        else:
            n = (1000 * vc) / (math.pi * diametre)
            vf = n * avance_dent * nb_dents
            temps = longueur / vf if vf > 0 else 0
            h = 2 * avance_dent * math.sqrt((epaisseur_passe / diametre) * (1 - epaisseur_passe / diametre))
            hmini = 0.007 * (diametre / nb_dents) if diametre >= 3 else 0.0035 * (diametre / nb_dents)

            st.subheader("📊 Résultats")
            resultats = {
                "Vitesse de rotation (N)": f"{n:.0f} tr/min",
                "Vitesse d’avance (Vf)": f"{vf:.1f} mm/min",
                "Copeau calculé (h)": f"{h:.3f} mm",
                "Copeau mini (h min)": f"{hmini:.3f} mm",
                #"Temps d’usinage estimé": f"{temps:.2f} min"
            }
            st.table(pd.DataFrame(resultats.items(), columns=["Paramètre", "Valeur"]))

            if h < hmini:
                st.warning("⚠️ Copeau trop faible : risque de frottement ou usure prématurée de l’outil.")

            # Export
            df_export = pd.DataFrame([{
                "Matière": matiere,
                "VC (m/min)": vc,
                "Diamètre (mm)": diametre,
                "Avance/dent": avance_dent,
                "Dents": nb_dents,
                "Épaisseur": epaisseur_passe,
                "Longueur": longueur,
                "N (tr/min)": round(n),
                "Vf (mm/min)": round(vf, 1),
                "h (mm)": round(h, 3),
                "hmin (mm)": round(hmini, 3),
                "Temps (min)": round(temps, 2)
            }])
            st.download_button("⬇️ Télécharger les résultats", df_export.to_csv(index=False).encode('utf-8'), file_name="resultats_usinage.csv", mime="text/csv")

# Interface Tournage
elif operation == "Tournage":
    st.subheader("🔩 Mode Tournage")

    # Saisie utilisateur
    classes_disponibles = sorted(df_vc["Classe"].unique())
    classe_selectionnee = st.selectbox("Choisir une classe de matériau :", classes_disponibles)

    matieres_filtrees = df_vc[df_vc["Classe"] == classe_selectionnee]
    matiere = st.selectbox("Choisir une matière :", sorted(matieres_filtrees["Matière"].unique()))
    mode = st.radio("Mode de vitesse de coupe :", ["moyenne", "mini"], horizontal=True)

    # Récupérer la ligne correspondante à la matière
    ligne = df_vc[df_vc["Matière"].str.lower() == matiere.lower()]

    if not ligne.empty:
        if mode == "mini":
            vc = ligne.iloc[0]["Vitesse de coupe mini (m/min)"]
        else:
            vc = ligne.iloc[0]["Vitesse de coupe moyenne (m/min)"]

        st.success(f"💡 Vitesse de coupe {mode} : **{vc} m/min**")
    else:
        st.error("❌ Matière non trouvée dans le tableau.")

    if vc is not None:
        st.success(f"✅ Vitesse de coupe ({mode}) : {vc} m/min")

    D = st.number_input("📏 Diamètre brut (mm)", min_value=1.0, value=50.0)
    f = st.number_input("⚙️ Avance par tour f (mm/tr)", min_value=0.01, value=0.2, step=0.01)
    longueur = st.number_input("📐 Longueur d’usinage (mm)", min_value=1.0, value=100.0)
    Ra = st.number_input("🎯 Rugosité visée Ra (µm)", min_value=0.1, value=1.6, step=0.1)
    Re = st.number_input("🧩 Rayon de plaquette (mm)", min_value=0.1, value=0.4, step=0.1)

    st.image("images/listel.png", caption="Longueur de listel (zone sans arête de coupe)", use_column_width=True)
    st.caption(
        "ℹ️ L’avance par tour doit être **supérieure à la longueur de listel** pour activer correctement le brise-copeaux.")

    N = (1000 * vc) / (math.pi * D)
    Vf = f
    t = longueur / Vf if Vf > 0 else 0

    fmax = 0.18 * math.sqrt(Ra * Re)

    st.markdown("### ✅ Résultats")
    st.write(f"🔁 Vitesse de rotation (N) : **{N:.0f} tr/min**")
    st.write(f"➡️ Vitesse d’avance (f) : **{Vf:.1f} mm/tr**")
    #st.write(f"⏱️ Temps estimé d’usinage : **{t:.2f} min**")
    st.write(f"🔎 Avance max recommandée f<sub>max</sub> = **{fmax:.3f} mm/tr**", unsafe_allow_html=True)

    if f > fmax:
        st.warning("⚠️ L’avance par tour saisie dépasse la valeur recommandée pour la rugosité visée.")
else:
    st.error("❌ Matière non trouvée dans le tableau. Vérifie la casse et l'orthographe.")

