import streamlit as st
import random
import time

st.set_page_config(layout="wide")

if "levels" not in st.session_state:
st.session_state.levels = []

if "price" not in st.session_state:
st.session_state.price = 100.0

if "running" not in st.session_state:
st.session_state.running = False

if "setup_id" not in st.session_state:
st.session_state.setup_id = 0

if "history" not in st.session_state:
st.session_state.history = []

st.title("Trading Bot")

col1, col2, col3 = st.columns(3)

with col1:
l1 = st.number_input("L1", value=100.0)

with col2:
l10 = st.number_input("L10", value=90.0)

with col3:
kill = st.number_input("Kill Switch ($)", value=0.0)

colA, colB, colC = st.columns(3)

if colA.button("HESAPLA"):
ratios = [1, 0.95, 0.886, 0.786, 0.705, 0.618, 0.5, 0.382, 0.236, 0]
levels = []

```
for i, r in enumerate(ratios):
    p = l1 - (l1 - l10) * (1 - r)
    levels.append({
        "name": f"L{i+1}",
        "price": round(p, 2),
        "state": "WAITING",
        "entry": None,
        "stop": None,
        "pct": 0,
        "pnl": 0,
        "be": round(p * 1.04, 2),
        "trail": round(p * 1.05, 2),
        "max_price": None,
        "setup_id": st.session_state.setup_id
    })

st.session_state.levels = levels
```

if colB.button("START"):
if not st.session_state.running:
st.session_state.setup_id += 1
for l in st.session_state.levels:
l["setup_id"] = st.session_state.setup_id
st.session_state.running = True

if colC.button("KILL"):
current_pnl = sum([l["pnl"] for l in st.session_state.levels])
st.session_state.history.append({
"setup": st.session_state.setup_id,
"pnl": round(current_pnl, 2)
})
st.session_state.running = False
st.session_state.levels = []

if st.session_state.running:
st.session_state.price += random.uniform(-3, 3)

st.subheader(f"Fiyat: {round(st.session_state.price, 2)}")

for l in st.session_state.levels:

```
if l["state"] == "WAITING" and st.session_state.price <= l["price"]:
    l["state"] = "FILLED"
    l["entry"] = l["price"]
    l["max_price"] = st.session_state.price

if l["state"] == "FILLED":

    change_pct = (st.session_state.price - l["entry"]) / l["entry"] * 100
    l["pct"] = round(change_pct, 2)

    if st.session_state.price > l["max_price"]:
        l["max_price"] = st.session_state.price

    if change_pct >= 4 and l["stop"] is None:
        l["stop"] = l["entry"]

    if change_pct >= 5:
        trailing_stop = l["max_price"] * (1 - 0.04)
        if l["stop"] is None or trailing_stop > l["stop"]:
            l["stop"] = round(trailing_stop, 2)

    if l["stop"] is not None and st.session_state.price <= l["stop"]:
        l["state"] = "WAITING"
        l["entry"] = None
        l["stop"] = None
        l["pct"] = 0
        l["pnl"] = 0
        l["max_price"] = None

    l["pnl"] = round(st.session_state.price - l["entry"], 2) if l["entry"] else 0
```

total_pnl = sum([l["pnl"] for l in st.session_state.levels])

st.subheader(f"Setup #{st.session_state.setup_id} PnL: {round(total_pnl, 2)} $")

if total_pnl > 0:
st.markdown(f"### 🟢 Toplam PnL: {round(total_pnl, 2)} $")
elif total_pnl < 0:
st.markdown(f"### 🔴 Toplam PnL: {round(total_pnl, 2)} $")
else:
st.markdown(f"### ⚪ Toplam PnL: {round(total_pnl, 2)} $")

if kill > 0 and total_pnl <= -kill:
st.session_state.history.append({
"setup": st.session_state.setup_id,
"pnl": round(total_pnl, 2)
})
st.session_state.running = False
st.session_state.levels = []
st.warning("KILL SWITCH TETİKLENDİ")

st.table(st.session_state.levels)

st.subheader("Setup Geçmişi")
st.table(st.session_state.history)

if st.session_state.running:
time.sleep(0.5)
st.rerun()
