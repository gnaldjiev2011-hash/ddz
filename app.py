import streamlit as st

st.title("🌡️ Температурен помощник")

temperature = st.number_input(
  "Въведи температурата в °C:",
  min_value=-50,
  max_value=60,
  value=20
)

if st.button("Провери"):

  if temperature < 10:
    st.info("Студено е! Облечи топло яке.")

  elif temperature < 20:
    st.warning("Прохладно е. Подходящо е леко яке.")

  elif temperature < 30:
    st.success("Приятно топло е!")

  else:
    st.error("Много е горещо! Пий повече вода.")
