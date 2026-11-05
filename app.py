"""Температурен помощник — Streamlit приложение.

Пускане:  streamlit run app.py
Нужна версия: streamlit >= 1.27   (pip install -U streamlit)
"""
import random
import time

import pandas as pd
import streamlit as st

st.set_page_config(page_title="Температурен помощник", page_icon="🌡️",
                   initial_sidebar_state="expanded")

# ───────────────────── Данни: температурни зони ─────────────────────
ZONES = [
    dict(limit=0, emoji="🥶", title="Ледено!", kind="info", show="snow",
         msg="Под нулата е! Облечи се на пластове и пази ръцете и ушите си.",
         colors=("#0f2027", "#2c78c8"), fx="❄️", motion="fall",
         clothes=["🧥 Дебело зимно яке", "🧣 Шал", "🧤 Ръкавици", "🧢 Шапка", "🥾 Топли ботуши"],
         activities=["⛷️ Ски или шейна", "☕ Горещ чай вкъщи", "🎬 Филм под одеялото"]),
    dict(limit=10, emoji="🧥", title="Студено е!", kind="info", show=None,
         msg="Студено е! Облечи топло яке.",
         colors=("#1e3c72", "#2a9df4"), fx="💧", motion="fall",
         clothes=["🧥 Топло яке", "🧶 Пуловер", "🧣 Шал", "👖 Дълги панталони"],
         activities=["🚶 Кратка разходка", "🍲 Топла супа", "📚 Книга на закрито"]),
    dict(limit=20, emoji="🌥️", title="Прохладно", kind="warning", show=None,
         msg="Прохладно е. Подходящо е леко яке.",
         colors=("#0f9b8e", "#6dd5a7"), fx="🍃", motion="fall",
         clothes=["🧥 Леко яке", "👕 Блуза с дълъг ръкав", "👖 Дънки", "👟 Маратонки"],
         activities=["🚴 Колоездене", "🥾 Разходка в парка", "☕ Кафе навън"]),
    dict(limit=30, emoji="😎", title="Приятно топло", kind="success", show="balloons",
         msg="Приятно топло е! Радвай се на деня.",
         colors=("#f46b45", "#eea849"), fx="✨", motion="rise",
         clothes=["👕 Тениска", "🩳 Къси панталони", "🕶️ Слънчеви очила", "👟 Леки обувки"],
         activities=["🏞️ Излет сред природата", "⚽ Спорт навън", "🍦 Сладолед"]),
    dict(limit=36, emoji="🥵", title="Горещо!", kind="warning", show=None,
         msg="Горещо е! Търси сянка и пий вода редовно.",
         colors=("#cb2d3e", "#ef473a"), fx="☀️", motion="rise",
         clothes=["👕 Лека свободна тениска", "🧢 Шапка", "🕶️ Слънчеви очила", "🩴 Сандали", "🧴 Крем със SPF"],
         activities=["🏊 Плуване", "🍉 Диня на сянка", "🌳 Разходка привечер"]),
    dict(limit=float("inf"), emoji="🔥", title="Опасна жега!", kind="error", show=None,
         msg="Много е горещо! Пий повече вода и избягвай слънцето.",
         colors=("#5f0a0a", "#ff4e00"), fx="🔥", motion="rise",
         clothes=["👚 Много лека светла дреха", "🧢 Шапка с козирка", "🕶️ Слънчеви очила",
                  "🧴 SPF 50+", "💧 Бутилка с вода"],
         activities=["❄️ Климатик и прохлада", "🏊 Басейн", "🚫 Без спорт по обяд"]),
]

PRESETS = {"❄️ -10°": -10.0, "🌧️ 8°": 8.0, "🍃 18°": 18.0, "☀️ 28°": 28.0, "🔥 38°": 38.0}

# ───────────────────── Стилове и анимации ─────────────────────
CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Unbounded:wght@500;800&display=swap');

.hero{position:relative;overflow:hidden;border-radius:28px;padding:36px 16px 30px;text-align:center;
  color:#fff;text-shadow:0 2px 10px rgba(0,0,0,.35);box-shadow:0 14px 34px rgba(0,0,0,.22)}
.hero>div{position:relative}
.hero .big{font-size:72px;line-height:1.1;display:inline-block;animation:float 3s ease-in-out infinite}
.hero .deg{font-family:'Unbounded',sans-serif;font-weight:800;font-size:clamp(44px,12vw,76px);line-height:1.1}
.hero .ttl{font-family:'Unbounded',sans-serif;font-weight:500;font-size:clamp(16px,4vw,22px);margin-top:6px}

.p{position:absolute;opacity:0;pointer-events:none;
  animation-timing-function:linear;animation-iteration-count:infinite}
.fall{top:0;animation-name:fall}
.rise{bottom:0;animation-name:rise}

.gauge{position:relative;height:12px;border-radius:99px;margin:30px 8px 4px;
  background:linear-gradient(90deg,#1e3c72 0%,#2a9df4 37%,#6dd5a7 55%,#ffd200 70%,#ff7a00 85%,#ff3d00 100%)}
.pin{position:absolute;top:-10px;left:var(--w);transform:translateX(-50%);font-size:28px;line-height:1;
  animation:slide 1s cubic-bezier(.2,.8,.2,1)}
.scale{display:flex;justify-content:space-between;padding:0 8px;font-size:12px;opacity:.6}

.chip{display:inline-block;margin:4px 6px 4px 0;padding:7px 14px;border-radius:99px;
  background:rgba(128,128,128,.14);border:1px solid rgba(128,128,128,.28)}
div.stButton>button{width:100%;border-radius:12px}

@keyframes float{0%,100%{transform:translateY(0)}50%{transform:translateY(-10px)}}
@keyframes slide{from{left:0}}
@keyframes fall{0%{transform:translateY(-30px) rotate(0);opacity:0}10%{opacity:.9}
  100%{transform:translateY(300px) rotate(240deg);opacity:0}}
@keyframes rise{0%{transform:translateY(30px);opacity:0}15%{opacity:.85}
  100%{transform:translateY(-300px) scale(1.4);opacity:0}}
@media (prefers-reduced-motion:reduce){.p{display:none}.hero .big,.pin{animation:none}}
</style>
"""


# ───────────────────── Изчисления ─────────────────────
def get_zone(t):
    return next(z for z in ZONES if t < z["limit"])


def c_to_f(c):
    return c * 9 / 5 + 32


def c_to_k(c):
    return c + 273.15


def to_celsius(value, unit):
    if unit == "°F":
        return (value - 32) * 5 / 9
    if unit == "K":
        return value - 273.15
    return value


def feels_like(t, wind, rh):
    """Усещане: вятърен охлаждащ фактор (студено) или топлинен индекс (горещо)."""
    if t <= 10 and wind > 4.8:
        v = wind ** 0.16
        return 13.12 + 0.6215 * t - 11.37 * v + 0.3965 * t * v
    if t >= 27 and rh >= 40:
        f = c_to_f(t)
        hi = (-42.379 + 2.04901523 * f + 10.14333127 * rh - 0.22475541 * f * rh
              - 0.00683783 * f * f - 0.05481717 * rh * rh + 0.00122874 * f * f * rh
              + 0.00085282 * f * rh * rh - 0.00000199 * f * f * rh * rh)
        return (hi - 32) * 5 / 9
    return t


def hydration(t):
    """Ориентировъчно количество вода за деня (литри)."""
    return round(2 + max(0.0, t - 20) * 0.1, 1)


# ───────────────────── HTML компоненти ─────────────────────
def particles(zone, n=16):
    rng = random.Random(7)
    return "".join(
        f'<span class="p {zone["motion"]}" style="left:{rng.randint(2, 96)}%;'
        f'font-size:{rng.randint(14, 28)}px;animation-duration:{rng.uniform(3, 7):.1f}s;'
        f'animation-delay:-{rng.uniform(0, 6):.1f}s">{zone["fx"]}</span>'
        for _ in range(n)
    )


def hero_html(t, zone):
    c1, c2 = zone["colors"]
    return (f'<div class="hero" style="background:linear-gradient(135deg,{c1},{c2})">'
            f'{particles(zone)}<div class="big">{zone["emoji"]}</div>'
            f'<div class="deg">{t:g}°C</div><div class="ttl">{zone["title"]}</div></div>')


def gauge_html(t):
    pct = min(max((t + 30) / 80 * 100, 0), 100)
    return (f'<div class="gauge"><div class="pin" style="--w:{pct:.1f}%">🌡️</div></div>'
            '<div class="scale"><span>-30°</span><span>10°</span><span>50°</span></div>')


def chips_html(items):
    return "".join(f'<span class="chip">{x}</span>' for x in items)


# ───────────────────── Действия ─────────────────────
def set_temp(value):
    st.session_state.temp = value


def type_message(zone, animate):
    """Показва съвета в цветно поле — буква по буква, ако е включено."""
    box = st.empty()
    show = getattr(box, zone["kind"])  # info / warning / success / error
    if animate:
        for i in range(1, len(zone["msg"]) + 1):
            show(zone["msg"][:i] + "▌")
            time.sleep(0.025)
    show(zone["msg"])


def run_check(temp, fl, zone, effects, typing):
    bar = st.progress(0, text="Измервам...")
    for i in range(1, 101):
        time.sleep(0.008)
        bar.progress(i, text="Измервам...")
    bar.empty()

    st.session_state.history.append({
        "Час": time.strftime("%H:%M:%S"),
        "Температура °C": temp,
        "Усеща се °C": round(fl, 1),
        "Състояние": zone["title"],
    })
    st.toast(f"{temp:g}°C — {zone['title']}", icon=zone["emoji"])
    type_message(zone, typing)
    if effects and zone["show"]:
        getattr(st, zone["show"])()  # st.snow() или st.balloons()


# ───────────────────── Интерфейс ─────────────────────
def main():
    st.markdown(CSS, unsafe_allow_html=True)
    st.session_state.setdefault("temp", 20.0)
    st.session_state.setdefault("history", [])

    st.title("🌡️ Температурен помощник")

    with st.sidebar:
        st.header("⚙️ Настройки")
        wind = st.slider("💨 Вятър (км/ч)", 0, 100, 0)
        humidity = st.slider("💧 Влажност (%)", 0, 100, 50)
        effects = st.toggle("🎈 Ефекти (сняг, балони)", value=True)
        typing = st.toggle("⌨️ Ефект на писане", value=True)

    temp = st.slider("Температура (°C)", -30.0, 50.0, step=0.5, key="temp")
    for col, (label, value) in zip(st.columns(len(PRESETS)), PRESETS.items()):
        col.button(label, key=f"preset_{value}", on_click=set_temp, args=(value,))

    fl = feels_like(temp, wind, humidity)
    delta = fl - temp
    zone = get_zone(temp)

    st.markdown(hero_html(temp, zone) + gauge_html(temp), unsafe_allow_html=True)

    m1, m2, m3 = st.columns(3)
    m1.metric("Фаренхайт", f"{c_to_f(temp):.1f} °F")
    m2.metric("Келвин", f"{c_to_k(temp):.2f} K")
    m3.metric("Усеща се като", f"{fl:.1f} °C",
              f"{delta:+.1f} °C" if abs(delta) >= 0.05 else None, delta_color="off")

    if st.button("🔍 Провери", type="primary"):
        run_check(temp, fl, zone, effects, typing)

    tab1, tab2, tab3 = st.tabs(["👕 Съвети", "🔄 Конвертор", "📜 История"])

    with tab1:
        st.markdown("**Какво да облека?**")
        st.markdown(chips_html(zone["clothes"]), unsafe_allow_html=True)
        st.markdown("**Какво да правя?**")
        st.markdown(chips_html(zone["activities"]), unsafe_allow_html=True)
        st.markdown(f"**Вода за деня:** около {hydration(fl)} л 💧")
        if abs(delta) >= 3:
            st.info(f"Заради вятъра и влажността се усеща като {fl:.1f} °C.")

    with tab2:
        a, b = st.columns([2, 1])
        unit = a.radio("Преобразувай от", ["°C", "°F", "K"], horizontal=True)
        value = b.number_input("Стойност", value=0.0, step=1.0)
        c = to_celsius(value, unit)
        if c < -273.15 - 1e-9:
            st.error("Под абсолютната нула (-273,15 °C) е невъзможно! 🧊")
        else:
            x1, x2, x3 = st.columns(3)
            x1.metric("Целзий", f"{c:.2f} °C")
            x2.metric("Фаренхайт", f"{c_to_f(c):.2f} °F")
            x3.metric("Келвин", f"{c_to_k(c):.2f} K")

    with tab3:
        history = st.session_state.history
        if history:
            df = pd.DataFrame(history)
            st.line_chart(df[["Температура °C", "Усеща се °C"]])
            st.dataframe(df, hide_index=True)
            st.button("🗑️ Изчисти историята", on_click=history.clear)
        else:
            st.info("Още няма проверки. Натисни „Провери“ над таблиците.")


main()
