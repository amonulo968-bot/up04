"""Streamlit-дашборд директора. Запуск: streamlit run dashboard/app.py"""

import os

import pandas as pd
import plotly.express as px
import requests
import streamlit as st

API_URL = os.getenv("API_URL", "http://localhost:8000")

st.set_page_config(page_title="Магазин — Аналитика", page_icon="🛒", layout="wide")
st.title("🛒 Магазин — Панель руководителя")


# ---------- ВХОД (JWT) ----------
def do_login(username: str, password: str) -> None:
    try:
        r = requests.post(
            f"{API_URL}/api/auth/login/",
            json={"username": username, "password": password},
            timeout=10,
        )
    except requests.RequestException:
        st.error(f"Нет связи с API ({API_URL}). Запущен ли Django-сервер?")
        return
    if r.ok:
        st.session_state["token"] = r.json()["access"]
        st.rerun()
    else:
        st.error("Неверный логин или пароль")


if "token" not in st.session_state:
    with st.form("login"):
        st.subheader("Вход")
        username = st.text_input("Логин")
        password = st.text_input("Пароль", type="password")
        if st.form_submit_button("Войти"):
            do_login(username, password)
    st.stop()


# ---------- ЗАГРУЗКА ДАННЫХ ИЗ API ----------
@st.cache_data(ttl=60, show_spinner=False)
def api_get(path: str, token: str, params: dict | None = None):
    r = requests.get(
        f"{API_URL}{path}",
        headers={"Authorization": f"Bearer {token}"},
        params=params,
        timeout=15,
    )
    r.raise_for_status()
    return r.json()


def load(path: str, **params):
    try:
        return api_get(path, st.session_state["token"], params or None)
    except requests.HTTPError as exc:
        code = exc.response.status_code
        if code == 401:
            st.session_state.pop("token", None)
            st.warning("Сессия истекла — войдите снова.")
        elif code == 403:
            st.error("Нет доступа: отчёты доступны только директору и администратору.")
        else:
            st.error(f"Ошибка API: {code}")
        st.stop()
    except requests.RequestException:
        st.error(f"Нет связи с API ({API_URL}).")
        st.stop()


# ---------- БОКОВАЯ ПАНЕЛЬ ----------
with st.sidebar:
    st.header("⚙️ Фильтры")
    days = st.selectbox("Период", [7, 30, 90, 365], index=1, format_func=lambda x: f"{x} дней")
    if st.button("🔄 Обновить"):
        st.cache_data.clear()
        st.rerun()
    if st.button("Выйти"):
        st.session_state.pop("token", None)
        st.rerun()

# ---------- KPI-ПЛИТКИ ----------
kpi = load("/api/reports/kpi/", days=days)
c1, c2, c3, c4 = st.columns(4)
c1.metric("💰 Выручка", f"{kpi['revenue']:,.0f} ₽")
c2.metric("✅ Заказов", kpi["orders_count"])
c3.metric("📈 Средний чек", f"{kpi['avg_check']:,.0f} ₽")
c4.metric("📦 Товаров в наличии", kpi["in_stock_products"])

# ---------- ГРАФИК ВЫРУЧКИ ----------
st.header("📈 Динамика выручки")
revenue_df = pd.DataFrame(load("/api/reports/revenue/", days=days))
if not revenue_df.empty:
    fig = px.line(revenue_df, x="date", y="total", markers=True,
                  labels={"date": "Дата", "total": "Выручка, ₽"})
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("За выбранный период нет завершённых заказов.")

# ---------- 2 КОЛОНКИ ----------
col1, col2 = st.columns(2)

with col1:
    st.header("🏆 Топ-5 товаров")
    top = pd.DataFrame(load("/api/reports/top-products/", limit=5))
    if not top.empty:
        fig = px.bar(top, x="qty", y="product", color="category", orientation="h",
                     labels={"qty": "Продано, шт.", "product": "Товар", "category": "Категория"})
        st.plotly_chart(fig, use_container_width=True)

with col2:
    st.header("👥 Загрузка менеджеров")
    managers = pd.DataFrame(load("/api/reports/manager-load/", days=days))
    if not managers.empty:
        fig = px.pie(managers, values="orders", names="manager")
        st.plotly_chart(fig, use_container_width=True)

# ---------- СКЛАД ----------
st.header("🏭 Состояние склада")
stock = pd.DataFrame(load("/api/reports/stock/"))
if not stock.empty:
    fig = px.pie(stock, values="count", names="status", color="status",
                 color_discrete_map={"В наличии": "green", "Заканчивается": "orange", "Нет в наличии": "red"})
    st.plotly_chart(fig, use_container_width=True)
