# Магазин — Django + DRF + PostgreSQL + Redis + Streamlit

Учебный проект (практические работы №3 и №5): 5 модулей и дашборд.

| Модуль | Что делает |
|---|---|
| `accounts` | пользователи с ролями, регистрация/вход по JWT |
| `catalog` | категории и товары (остатки, цены) |
| `clients` | клиенты магазина |
| `orders` | заказы с позициями, резерв товара, подтверждение/завершение/отмена |
| `reports` | KPI, выручка по дням, топ товаров, загрузка менеджеров, склад |
| `dashboard/` | Streamlit-панель директора |

## Быстрый старт (Windows, PowerShell)

```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env        # затем впишите свой SECRET_KEY
```

SECRET_KEY:
```powershell
python -c "from django.core.management.utils import get_random_secret_key as k; print(k())"
```

База (PostgreSQL), в `psql -U postgres`:
```sql
CREATE USER shop WITH PASSWORD 'shop';
CREATE DATABASE shop OWNER shop;
GRANT ALL ON SCHEMA public TO shop;
```
Redis: должна работать служба Memurai (порт 6379).

```powershell
python manage.py makemigrations accounts catalog clients orders
python manage.py migrate
python manage.py createsuperuser
python manage.py seed_demo       # демо-данные (необязательно)
python manage.py runserver
```
Админка: http://localhost:8000/admin/

Дашборд (второй терминал, venv активен):
```powershell
streamlit run dashboard/app.py
```
Войти нужно под суперпользователем, администратором или директором.

## API
- `POST /api/auth/register/`, `POST /api/auth/login/`, `GET /api/auth/me/`, `POST /api/auth/token/refresh/`
- `/api/categories/`, `/api/products/` (поиск `?search=`, фильтры `?category=`, сортировка `?ordering=price`)
- `/api/clients/`
- `/api/orders/` + `POST /api/orders/{id}/confirm|complete|cancel/`
- `/api/reports/kpi|revenue|top-products|manager-load|stock/`

Пример создания заказа:
```json
POST /api/orders/
{"client": 1, "comment": "Доставка", "items": [{"product": 1, "quantity": 2}]}
```

## Публикация на GitHub
```powershell
git init
git add .
git commit -m "Магазин: 5 модулей и дашборд"
git branch -M main
git remote add origin https://github.com/<ваш-логин>/<репозиторий>.git
git push -u origin main
```
`.env` в `.gitignore` — секреты в репозиторий не попадут.
