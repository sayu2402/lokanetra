This is a simple payment app backend where users log in with OTP, get an auto-created wallet, and can credit, debit, or transfer money. All operations create transaction logs, and the admin can view all wallets and transactions. The super admin creates users, and a small bash script helps quickly assign phone numbers. The whole system is built with Django, DRF, JWT, and Swagger documentation## Quick Setup (Local / Development)

1. Clone repo
```bash
git clone <repo-url> lokanetra
cd lokanetra
````

2. Create virtual environment and activate

```bash
python -m venv venv
# Linux / macOS
source venv/bin/activate
# Windows (PowerShell)
venv\Scripts\Activate.ps1
```

3. Install requirements

```bash
pip install -r requirements.txt
```

4. Environment variables (recommended)
   Create a `.env` or export variables (example):

```bash
export DJANGO_SECRET_KEY="replace-with-secure-secret"
export DATABASE_URL="sqlite:///db.sqlite3"  # optional
export DEBUG="True"
```

5. Run migrations & create superuser

```bash
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
```

6. Run the server

```bash
python manage.py runserver
```

Swagger UI: [http://127.0.0.1:8000/swagger/](http://127.0.0.1:8000/swagger/)
ReDoc: [http://127.0.0.1:8000/redoc/](http://127.0.0.1:8000/redoc/)
Swagger JSON: [http://127.0.0.1:8000/swagger.json](http://127.0.0.1:8000/swagger.json)

---

## Important Files & Structure

```
lokanetra/
├── lokanetra/           # project settings and urls
├── users/               # user, OTP models, auth endpoints
├── wallet/              # Wallet model, wallet endpoints
├── transactions/        # Transaction model, admin listing
├── requirements.txt
├── manage.py
└── README.md
```

Key modules:

* `users.models` → `UserProfile`, `OTP`
* `wallet.models` → `Wallet`
* `transactions.models` → `Transaction`
* `users.views` → `send-otp`, `verify-otp` (returns JWT)
* `wallet.views` → balance, credit, debit, transfer (uses DB `select_for_update`)
* `transactions.views` → admin transaction listing with filters
* `lokanetra.urls` → includes `auth/`, `wallet/`, `transactions/`, swagger routes

---

## API Endpoints (Examples)

### 1) Send OTP

```
POST /auth/send-otp/
Content-Type: application/json

{
  "phone_number": "9999999999"
}
```

**Response (for machine test):**

```json
{
  "phone_number": "9999999999",
  "otp": "1234"
}
```

---

### 2) Verify OTP (and auto-create user + wallet)

```
POST /auth/verify-otp/
Content-Type: application/json

{
  "phone_number": "9999999999",
  "otp": "1234"
}
```

**Response:**

```json
{
  "access": "<jwt-access-token>",
  "refresh": "<jwt-refresh-token>",
  "user": {"id": 5, "username": "user_9999999999", "phone_number": "9999999999"}
}
```

---

### 3) Get Wallet Balance

```
GET /wallet/balance/
Authorization: Bearer <access-token>
```

**Response:**

```json
{
  "user": "user_9999999999",
  "balance": "0.00"
}
```

---

### 4) Credit Wallet

```
POST /wallet/credit/
Authorization: Bearer <access-token>
Content-Type: application/json

{
  "amount": "150.50",
  "remarks": "Initial top-up"
}
```

**Behavior:** Creates a CREDIT transaction, updates balance atomically.

---

### 5) Debit Wallet

```
POST /wallet/debit/
Authorization: Bearer <access-token>
Content-Type: application/json

{
  "amount": "50.00",
  "remarks": "Purchase"
}
```

**Validation:** Fails with `400` if insufficient funds.

---

### 6) Transfer to another user (by phone)

```
POST /wallet/transfer/
Authorization: Bearer <access-token>
Content-Type: application/json

{
  "to_phone_number": "8888888888",
  "amount": "25.00",
  "remarks": "Payment"
}
```

**Behavior:** Atomic update of sender and receiver wallets using `select_for_update()` and creates a `TRANSFER` transaction.

---

### 7) Admin: List Transactions

```
GET /transactions/admin-list/
Authorization: admin session or Bearer <admin-token>
```

Supports search by sender/receiver/transaction_type and ordering by `timestamp`/`amount`.

---

## Postman / Thunder Client Checklist

Create requests for:

* Send OTP
* Verify OTP (store tokens)
* Get balance (use Bearer token)
* Credit, Debit, Transfer
* Admin: transactions listing (use admin credentials)

Tip: Save environment variables: `base_url`, `access_token`, `refresh_token`, `admin_token`.

---

## Testing & Manual Flow (quick)

1. Send OTP to `9999999999` → copy `otp`.
2. Verify OTP → get tokens.
3. `GET /wallet/balance/` → should be `0.00`.
4. `POST /wallet/credit/` amount `200.00` → balance `200.00`.
5. Create another user via OTP and `verify-otp`.
6. Transfer `50.00` to second user → verify both balances and transaction record.

---

## Swagger & API Documentation

* drf-yasg configured:

  * `/swagger/` → interactive UI
  * `/redoc/` → ReDoc UI
  * `/swagger.json` → OpenAPI JSON
    Ensure `drf_yasg` is included in `INSTALLED_APPS` and schema view is added to `lokanetra/urls.py`.

---

## Quick commands summary

```bash
# env
python -m venv venv
source venv/bin/activate

# install
pip install -r requirements.txt

# migrations
python manage.py makemigrations
python manage.py migrate

# create admin
python manage.py createsuperuser

# run server
python manage.py runserver
```
=======
