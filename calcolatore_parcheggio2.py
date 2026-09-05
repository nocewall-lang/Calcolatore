import math
from datetime import datetime
import streamlit as st

# ==========================================
# DEFINIZIONE PARCHEGGI E SISTEMI TARIFFARI
# ==========================================
PARCHEGGI = {
    "Bisceglie": "SBME",
    "Caterina da Forlì": "SBME",
    "Lampugnano": "SBME",
    "Molino Dorino": "SBME",
    "Cascina Gobba": "SBME",
    "Famagosta": "SBME",
    "Maciachini": "SBME",
    "Rogoredo": "SBME",
    "San Donato": "SBME",
    "Forlanini": "SBME",
    "San Leonardo": "RASI+",
    "Cologno Nord": "RASI",
    "Gessate": "RASI",
    "Vittor Pisani": "HUB",
    "Cassiodoro": "CASSIO",
}

# ==========================================
# ALGORITMI DI CALCOLO TARIFFA
# ==========================================

def calcola_sbme(minuti, manifestazioni=False):
    if manifestazioni:
        return 4.00
    
    giorni = int(minuti // (24 * 60))
    resto_minuti = minuti % (24 * 60)
    costo_giorni = giorni * 7.50

    if resto_minuti == 0:
        return max(costo_giorni, 1.50 if giorni == 0 else costo_giorni)

    ore_resto = resto_minuti / 60.0

    if ore_resto <= 5:
        costo_resto = 1.50
    elif ore_resto <= 10:
        costo_resto = 2.00
    elif ore_resto <= 15:
        costo_resto = 2.50
    elif ore_resto <= 19:
        costo_resto = 4.00
    else:
        costo_resto = 7.50

    return costo_giorni + costo_resto


def calcola_rasi_plus(minuti):
    giorni = int(minuti // (24 * 60))
    resto_minuti = minuti % (24 * 60)
    costo_giorni = giorni * 2.50

    if resto_minuti == 0:
        return max(costo_giorni, 1.50 if giorni == 0 else costo_giorni)

    ore_resto = resto_minuti / 60.0

    if ore_resto <= 5:
        costo_resto = 1.50
    elif ore_resto <= 10:
        costo_resto = 2.00
    else:
        costo_resto = 2.50

    return costo_giorni + costo_resto


def calcola_rasi(minuti):
    giorni = math.ceil(minuti / (24 * 60))
    return max(giorni, 1) * 2.00


def calcola_cassio(minuti):
    if minuti <= 0:
        return 0.0
    
    ore_totali = math.ceil(minuti / 60)

    if ore_totali <= 1:
        return 1.50
    elif ore_totali == 2:
        return 2.50
    elif ore_totali == 3:
        return 3.10
    else:
        ore_extra = ore_totali - 3
        return 3.10 + (ore_extra * 0.50)


def e_weekend_hub(dt_ingresso, dt_uscita):
    w_in = dt_ingresso.weekday()
    h_in = dt_ingresso.hour
    
    w_out = dt_uscita.weekday()
    h_out = dt_uscita.hour + dt_uscita.minute / 60.0

    in_weekend = (w_in == 4 and h_in >= 12) or (w_in in [5, 6]) or (w_in == 0 and h_in < 2)
    out_weekend = (w_out == 4 and h_out <= 24) or (w_out in [5, 6]) or (w_out == 0 and h_out <= 2)

    durata_ore = (dt_uscita - dt_ingresso).total_seconds() / 3600
    if in_weekend and out_weekend and durata_ore <= 62:
        return True
    return False


def calcola_hub(dt_ingresso, dt_uscita):
    minuti = (dt_uscita - dt_ingresso).total_seconds() / 60
    
    if e_weekend_hub(dt_ingresso, dt_uscita):
        return 37.00

    scaglioni_hub = {
        1: 2.00, 2: 4.00, 3: 6.00, 4: 8.00, 5: 10.00, 6: 12.00,
        7: 14.00, 8: 16.00, 9: 17.50, 10: 19.00, 11: 20.50, 12: 22.00,
        13: 23.20, 14: 24.40, 15: 25.60, 16: 26.80, 17: 28.00, 18: 29.20,
        19: 30.40, 20: 31.60, 21: 32.80, 22: 34.00, 23: 35.20, 24: 36.40
    }

    giorni = int(minuti // (24 * 60))
    resto_min = minuti % (24 * 60)
    costo_giorni = giorni * 36.40

    if resto_min == 0:
        return max(costo_giorni, 2.00 if giorni == 0 else costo_giorni)

    ore_resto = math.ceil(resto_min / 60)
    costo_resto = scaglioni_hub.get(ore_resto, 36.40)

    return costo_giorni + costo_resto


def calcola_totale(nome_parcheggio, dt_ingresso, dt_uscita, manifestazioni=False):
    sistema = PARCHEGGI[nome_parcheggio]
    minuti = (dt_uscita - dt_ingresso).total_seconds() / 60

    if minuti <= 0:
        raise ValueError("L'orario di uscita deve essere successivo a quello di ingresso.")

    if sistema == "SBME":
        costo = calcola_sbme(minuti, manifestazioni)
    elif sistema == "RASI+":
        costo = calcola_rasi_plus(minuti)
    elif sistema == "RASI":
        costo = calcola_rasi(minuti)
    elif sistema == "CASSIO":
        costo = calcola_cassio(minuti)
    elif sistema == "HUB":
        costo = calcola_hub(dt_ingresso, dt_uscita)
    else:
        costo = 0.0

    return costo, sistema, minuti

# ==========================================
# INTERFACCIA WEB (Streamlit)
# ==========================================

st.set_page_config(page_title="Calcolatore Parcheggi ATM", page_icon="🅿️", layout="centered")

st.title("🅿️ Calcolo Sosta Parcheggio ATM")
st.write("Calcola facilmente la tariffa del tuo parcheggio selezionando le date di ingresso e uscita.")

# Selezione parcheggio
parcheggio = st.selectbox("Seleziona Parcheggio:", list(PARCHEGGI.keys()))
sistema_attuale = PARCHEGGI[parcheggio]

st.info(f"**Sistema Tariffario applicato:** {sistema_attuale}")

# Input date e ore
col1, col2 = st.columns(2)

with col1:
    st.subheader("Ingresso")
    data_in = st.date_input("Data Ingresso", datetime.now().date(), key="d_in")
    ora_in = st.time_input("Ora Ingresso", datetime.now().time(), key="t_in")

with col2:
    st.subheader("Uscita")
    data_out = st.date_input("Data Uscita", datetime.now().date(), key="d_out")
    ora_out = st.time_input("Ora Uscita", datetime.now().time(), key="t_out")

# Checkbox per manifestazioni (solo per SBME)
manifestazioni = False
if sistema_attuale == "SBME":
    manifestazioni = st.checkbox("Tariffa Manifestazioni (€ 4,00 fissa)")

# Pulsante di calcolo
if st.button("Calcola Importo", type="primary", use_container_width=True):
    dt_ingresso = datetime.combine(data_in, ora_in)
    dt_uscita = datetime.combine(data_out, ora_out)

    try:
        costo, sistema, minuti = calcola_totale(parcheggio, dt_ingresso, dt_uscita, manifestazioni)
        
        ore = int(minuti // 60)
        mins = int(minuti % 60)

        st.success("### Risultato Calcolo")
        st.write(f"⏱️ **Durata Sosta:** {ore} ore e {mins} minuti")
        st.metric(label="TOTALE DA PAGARE", value=f"€ {costo:.2f}".replace('.', ','))

    except ValueError as e:
        st.error(f"⚠️ Errore nei dati inseriti: {e}")