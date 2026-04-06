import os
import re
import secrets
import sqlite3
from contextlib import closing
from datetime import datetime, timedelta
from email.message import EmailMessage
import smtplib

import requests
from dotenv import load_dotenv
from flask import Flask, jsonify, request
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

load_dotenv()

DB_PATH = os.path.join(os.path.dirname(__file__), "site.db")
TIME_GAP_MINUTES = 60
TRAINING_CAPACITY = 25
TRAINING_PRICE_KZT = int(os.getenv("TRAINING_PRICE_KZT", "75000"))
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "0000")
ADMIN_SESSION_MINUTES = int(os.getenv("ADMIN_SESSION_MINUTES", "720"))

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("APP_SECRET_KEY", "dev-secret")

ALLOWED_ORIGINS = [
    origin.strip()
    for origin in os.getenv(
        "ALLOWED_ORIGINS",
        "http://127.0.0.1:5500,http://localhost:5500,https://abdramanovtimur71-ux.github.io",
    ).split(",")
    if origin.strip()
]

limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["120 per hour"],
    storage_uri="memory://",
)
limiter.init_app(app)

ADMIN_SESSIONS = {}


def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with closing(get_conn()) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS bookings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT NOT NULL,
                phone TEXT,
                service TEXT NOT NULL,
                format TEXT,
                note TEXT,
                booking_at TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS training_enrollments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT NOT NULL,
                phone TEXT,
                payment_verified INTEGER NOT NULL,
                payment_id TEXT,
                status TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS payments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                payment_id TEXT NOT NULL UNIQUE,
                amount INTEGER NOT NULL,
                currency TEXT NOT NULL,
                card_last4 TEXT,
                holder TEXT,
                status TEXT NOT NULL,
                consumed INTEGER NOT NULL DEFAULT 0,
                created_at TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS content_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                kind TEXT NOT NULL,
                title TEXT NOT NULL,
                body TEXT,
                media_url TEXT,
                created_at TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS client_messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                from_email TEXT NOT NULL,
                to_email TEXT NOT NULL,
                subject TEXT,
                text TEXT NOT NULL,
                sender_role TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )
        conn.commit()


def cleanup_admin_sessions():
    now = datetime.now()
    expired = [token for token, exp in ADMIN_SESSIONS.items() if exp < now]
    for token in expired:
        ADMIN_SESSIONS.pop(token, None)


def issue_admin_token() -> str:
    cleanup_admin_sessions()
    token = secrets.token_urlsafe(32)
    ADMIN_SESSIONS[token] = datetime.now() + timedelta(minutes=ADMIN_SESSION_MINUTES)
    return token


def is_admin_request() -> bool:
    cleanup_admin_sessions()
    token = request.headers.get("X-Admin-Token", "").strip()
    return bool(token and token in ADMIN_SESSIONS)


def require_admin_or_401():
    if not is_admin_request():
        return jsonify({"ok": False, "message": "Требуется спецвход администратора"}), 401
    return None


def luhn_valid(card_number: str) -> bool:
    digits = [int(ch) for ch in card_number if ch.isdigit()]
    if len(digits) < 13:
        return False
    checksum = 0
    parity = len(digits) % 2
    for i, digit in enumerate(digits):
        if i % 2 == parity:
            digit *= 2
            if digit > 9:
                digit -= 9
        checksum += digit
    return checksum % 10 == 0


def exp_valid(mm_yy: str) -> bool:
    if not re.match(r"^\d{2}/\d{2}$", mm_yy or ""):
        return False
    month = int(mm_yy[:2])
    year = int(mm_yy[3:]) + 2000
    if month < 1 or month > 12:
        return False
    now = datetime.now()
    # Card valid through end of month.
    return (year > now.year) or (year == now.year and month >= now.month)


def parse_iso(dt_str: str):
    try:
        return datetime.fromisoformat(dt_str)
    except Exception:
        return None


def validate_email(email: str) -> bool:
    return bool(re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", email or ""))


def validate_phone(phone: str) -> bool:
    if not phone:
        return True
    return bool(re.match(r"^\+?[0-9\-\s\(\)]{7,20}$", phone))


def send_email_notification(subject: str, text: str):
    smtp_host = os.getenv("SMTP_HOST")
    smtp_port = int(os.getenv("SMTP_PORT", "587"))
    smtp_user = os.getenv("SMTP_USER")
    smtp_pass = os.getenv("SMTP_PASS")
    to_email = os.getenv("ADMIN_NOTIFY_EMAIL")
    use_tls = os.getenv("SMTP_USE_TLS", "true").lower() == "true"

    if not (smtp_host and smtp_user and smtp_pass and to_email):
        return False, "email-not-configured"

    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = smtp_user
    msg["To"] = to_email
    msg.set_content(text)

    with smtplib.SMTP(smtp_host, smtp_port, timeout=20) as server:
        if use_tls:
            server.starttls()
        server.login(smtp_user, smtp_pass)
        server.send_message(msg)
    return True, "email-sent"


def send_telegram_notification(text: str):
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    if not (token and chat_id):
        return False, "telegram-not-configured"

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    resp = requests.post(url, json={"chat_id": chat_id, "text": text}, timeout=20)
    resp.raise_for_status()
    return True, "telegram-sent"


def send_whatsapp_notification(text: str):
    api_url = os.getenv("WHATSAPP_API_URL")
    api_token = os.getenv("WHATSAPP_API_TOKEN")
    if not (api_url and api_token):
        return False, "whatsapp-not-configured"

    resp = requests.post(
        api_url,
        json={"message": text, "to": "87072867777"},
        headers={"Authorization": f"Bearer {api_token}"},
        timeout=20,
    )
    resp.raise_for_status()
    return True, "whatsapp-sent"


def send_all_notifications(subject: str, text: str):
    results = {"email": None, "telegram": None, "whatsapp": None}

    try:
        results["email"] = send_email_notification(subject, text)
    except Exception as ex:
        results["email"] = (False, f"email-error:{ex}")

    try:
        results["telegram"] = send_telegram_notification(text)
    except Exception as ex:
        results["telegram"] = (False, f"telegram-error:{ex}")

    try:
        results["whatsapp"] = send_whatsapp_notification(text)
    except Exception as ex:
        results["whatsapp"] = (False, f"whatsapp-error:{ex}")

    return results


@app.after_request
def add_security_headers(resp):
    origin = request.headers.get("Origin")
    if origin and origin in ALLOWED_ORIGINS:
        resp.headers["Access-Control-Allow-Origin"] = origin
        resp.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization, X-Admin-Token"
        resp.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
        resp.headers["Vary"] = "Origin"

    resp.headers["X-Content-Type-Options"] = "nosniff"
    resp.headers["X-Frame-Options"] = "DENY"
    resp.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    resp.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
    resp.headers["Content-Security-Policy"] = "default-src 'self'; connect-src 'self' https://api.openai.com https://api.telegram.org; img-src 'self' data:; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; font-src 'self' https://fonts.gstatic.com; script-src 'self' 'unsafe-inline';"
    return resp


@app.before_request
def handle_preflight():
    if request.method == "OPTIONS":
        return ("", 204)


@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({"ok": True})


@app.route("/api/admin/login", methods=["POST"])
@limiter.limit("20 per minute")
def admin_login():
    payload = request.get_json(silent=True) or {}
    password = (payload.get("password") or "").strip()
    if password != ADMIN_PASSWORD:
        return jsonify({"ok": False, "message": "Неверный пароль спецвхода"}), 401
    token = issue_admin_token()
    return jsonify({"ok": True, "token": token, "expiresInMinutes": ADMIN_SESSION_MINUTES})


@app.route("/api/admin/content", methods=["GET", "POST"])
def admin_content():
    auth_error = require_admin_or_401()
    if auth_error:
        return auth_error

    if request.method == "GET":
        with closing(get_conn()) as conn:
            rows = conn.execute(
                "SELECT id, kind, title, body, media_url, created_at FROM content_items ORDER BY id DESC"
            ).fetchall()
        return jsonify({"ok": True, "items": [dict(r) for r in rows]})

    payload = request.get_json(silent=True) or {}
    kind = (payload.get("kind") or "").strip().lower()
    title = (payload.get("title") or "").strip()
    body = (payload.get("body") or "").strip()
    media_url = (payload.get("mediaUrl") or "").strip()

    if kind not in {"story", "doc", "photo", "video"}:
        return jsonify({"ok": False, "message": "Тип должен быть: story/doc/photo/video"}), 400
    if not title:
        return jsonify({"ok": False, "message": "Укажите заголовок"}), 400

    with closing(get_conn()) as conn:
        conn.execute(
            """
            INSERT INTO content_items (kind, title, body, media_url, created_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            (kind, title, body, media_url, datetime.now().isoformat()),
        )
        conn.commit()

    return jsonify({"ok": True, "message": "Контент добавлен"})


@app.route("/api/content", methods=["GET"])
def public_content():
    with closing(get_conn()) as conn:
        rows = conn.execute(
            "SELECT id, kind, title, body, media_url, created_at FROM content_items ORDER BY id DESC LIMIT 50"
        ).fetchall()
    return jsonify({"ok": True, "items": [dict(r) for r in rows]})


@app.route("/api/admin/participants", methods=["GET"])
def admin_participants():
    auth_error = require_admin_or_401()
    if auth_error:
        return auth_error

    with closing(get_conn()) as conn:
        bookings = conn.execute(
            """
            SELECT name, email, phone, booking_at, created_at
            FROM bookings
            ORDER BY id DESC
            LIMIT 500
            """
        ).fetchall()
        learners = conn.execute(
            """
            SELECT name, email, phone, status, created_at
            FROM training_enrollments
            ORDER BY id DESC
            LIMIT 500
            """
        ).fetchall()

    return jsonify(
        {
            "ok": True,
            "bookings": [dict(r) for r in bookings],
            "learners": [dict(r) for r in learners],
        }
    )


@app.route("/api/admin/messages", methods=["GET"])
def admin_messages():
    auth_error = require_admin_or_401()
    if auth_error:
        return auth_error

    with closing(get_conn()) as conn:
        rows = conn.execute(
            """
            SELECT id, from_email, to_email, subject, text, sender_role, created_at
            FROM client_messages
            ORDER BY id DESC
            LIMIT 500
            """
        ).fetchall()
    return jsonify({"ok": True, "messages": [dict(r) for r in rows]})


@app.route("/api/admin/messages/send", methods=["POST"])
def admin_send_message():
    auth_error = require_admin_or_401()
    if auth_error:
        return auth_error

    payload = request.get_json(silent=True) or {}
    to_email = (payload.get("toEmail") or "").strip().lower()
    subject = (payload.get("subject") or "").strip()
    text = (payload.get("text") or "").strip()

    if not validate_email(to_email):
        return jsonify({"ok": False, "message": "Некорректный email клиента"}), 400
    if len(text) < 2:
        return jsonify({"ok": False, "message": "Введите текст сообщения"}), 400

    with closing(get_conn()) as conn:
        conn.execute(
            """
            INSERT INTO client_messages (from_email, to_email, subject, text, sender_role, created_at)
            VALUES (?, ?, ?, ?, 'admin', ?)
            """,
            ("admin@roza-ogly.local", to_email, subject, text, datetime.now().isoformat()),
        )
        conn.commit()

    return jsonify({"ok": True, "message": "Сообщение отправлено клиенту"})


@app.route("/api/messages/inbox", methods=["GET"])
def client_inbox():
    email = (request.args.get("email") or "").strip().lower()
    if not validate_email(email):
        return jsonify({"ok": False, "message": "Некорректный email"}), 400

    with closing(get_conn()) as conn:
        rows = conn.execute(
            """
            SELECT id, from_email, to_email, subject, text, sender_role, created_at
            FROM client_messages
            WHERE to_email=? OR from_email=?
            ORDER BY id DESC
            LIMIT 300
            """,
            (email, email),
        ).fetchall()

    return jsonify({"ok": True, "messages": [dict(r) for r in rows]})


@app.route("/api/messages/reply", methods=["POST"])
@limiter.limit("30 per hour")
def client_reply():
    payload = request.get_json(silent=True) or {}
    from_email = (payload.get("fromEmail") or "").strip().lower()
    text = (payload.get("text") or "").strip()

    if not validate_email(from_email):
        return jsonify({"ok": False, "message": "Некорректный email"}), 400
    if len(text) < 2:
        return jsonify({"ok": False, "message": "Введите текст сообщения"}), 400

    with closing(get_conn()) as conn:
        conn.execute(
            """
            INSERT INTO client_messages (from_email, to_email, subject, text, sender_role, created_at)
            VALUES (?, ?, ?, ?, 'client', ?)
            """,
            (from_email, "admin@roza-ogly.local", "Ответ клиента", text, datetime.now().isoformat()),
        )
        conn.commit()

    return jsonify({"ok": True, "message": "Ответ отправлен администратору"})


@app.route("/api/payments/verify", methods=["POST"])
@limiter.limit("20 per minute")
def verify_payment():
    payload = request.get_json(silent=True) or {}
    amount = int(payload.get("amount") or 0)
    currency = (payload.get("currency") or "KZT").strip().upper()
    card = (payload.get("card") or "").replace(" ", "")
    exp = (payload.get("exp") or "").strip()
    cvv = (payload.get("cvv") or "").strip()
    holder = (payload.get("holder") or "").strip()

    if amount != TRAINING_PRICE_KZT or currency != "KZT":
        return jsonify({"ok": False, "message": "Сумма или валюта платежа не совпадает"}), 400

    mode = os.getenv("PAYMENT_VERIFY_MODE", "mock").strip().lower()
    if mode not in {"mock", "strict"}:
        mode = "mock"

    if mode == "strict":
        return jsonify({"ok": False, "message": "Strict-провайдер не настроен. Установите PAYMENT_VERIFY_MODE=mock или подключите шлюз."}), 503

    if not luhn_valid(card):
        return jsonify({"ok": False, "message": "Неверный номер карты"}), 400
    if not exp_valid(exp):
        return jsonify({"ok": False, "message": "Срок карты истек или некорректен"}), 400
    if not re.match(r"^\d{3,4}$", cvv):
        return jsonify({"ok": False, "message": "Некорректный CVV"}), 400
    if len(holder) < 2:
        return jsonify({"ok": False, "message": "Укажите имя владельца"}), 400

    payment_id = f"PAY-{int(datetime.now().timestamp() * 1000)}"
    with closing(get_conn()) as conn:
        conn.execute(
            """
            INSERT INTO payments (payment_id, amount, currency, card_last4, holder, status, created_at)
            VALUES (?, ?, ?, ?, ?, 'paid', ?)
            """,
            (payment_id, amount, currency, card[-4:], holder, datetime.now().isoformat()),
        )
        conn.commit()

    return jsonify({"ok": True, "paymentId": payment_id, "status": "paid"})


@app.route("/api/bookings", methods=["POST"])
@limiter.limit("20 per minute")
def create_booking():
    payload = request.get_json(silent=True) or {}
    name = (payload.get("name") or "").strip()
    email = (payload.get("email") or "").strip()
    phone = (payload.get("phone") or "").strip()
    service = (payload.get("service") or "").strip()
    date = (payload.get("date") or "").strip()
    time = (payload.get("time") or "").strip()
    form = (payload.get("format") or "").strip()
    note = (payload.get("note") or "").strip()

    if not all([name, email, service, date, time]):
        return jsonify({"ok": False, "message": "Заполните обязательные поля"}), 400
    if not validate_email(email):
        return jsonify({"ok": False, "message": "Некорректный email"}), 400
    if not validate_phone(phone):
        return jsonify({"ok": False, "message": "Некорректный номер телефона"}), 400

    booking_at = parse_iso(f"{date}T{time}:00")
    if not booking_at:
        return jsonify({"ok": False, "message": "Некорректная дата или время"}), 400

    now = datetime.now()
    if booking_at < now + timedelta(minutes=30):
        return jsonify({"ok": False, "message": "Нельзя записаться на прошедшее или слишком близкое время"}), 400

    with closing(get_conn()) as conn:
        rows = conn.execute("SELECT booking_at FROM bookings").fetchall()
        for row in rows:
            existing = parse_iso(row["booking_at"])
            if not existing:
                continue
            diff = abs((existing - booking_at).total_seconds()) / 60
            if diff < TIME_GAP_MINUTES:
                next_available = existing + timedelta(minutes=TIME_GAP_MINUTES)
                return jsonify(
                    {
                        "ok": False,
                        "conflict": True,
                        "message": "К сожалению, это время занято. Выберите минимум через 1 час.",
                        "suggestedTime": next_available.strftime("%H:%M"),
                    }
                ), 409

        conn.execute(
            """
            INSERT INTO bookings (name, email, phone, service, format, note, booking_at, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                name,
                email,
                phone,
                service,
                form,
                note,
                booking_at.isoformat(),
                now.isoformat(),
            ),
        )
        conn.commit()

    msg = (
        "Новая запись на приём\n"
        f"Имя: {name}\n"
        f"Email: {email}\n"
        f"Телефон: {phone or '—'}\n"
        f"Услуга: {service}\n"
        f"Дата/время: {booking_at.strftime('%d.%m.%Y %H:%M')}\n"
        f"Формат: {form or '—'}\n"
        f"Комментарий: {note or '—'}"
    )
    notify = send_all_notifications("Новая запись на прием", msg)

    return jsonify({"ok": True, "message": "Вы успешно записаны", "notifications": notify})


@app.route("/api/training/status", methods=["GET"])
def training_status():
    with closing(get_conn()) as conn:
        accepted = conn.execute("SELECT COUNT(*) c FROM training_enrollments WHERE status='accepted'").fetchone()["c"]
        waiting = conn.execute("SELECT COUNT(*) c FROM training_enrollments WHERE status='waitlist'").fetchone()["c"]
    return jsonify({"ok": True, "capacity": TRAINING_CAPACITY, "accepted": accepted, "waiting": waiting})


@app.route("/api/training/enroll", methods=["POST"])
@limiter.limit("15 per minute")
def enroll_training():
    payload = request.get_json(silent=True) or {}
    name = (payload.get("name") or "").strip()
    email = (payload.get("email") or "").strip()
    phone = (payload.get("phone") or "").strip()
    payment_id = (payload.get("paymentId") or "").strip()

    if not all([name, email, payment_id]):
        return jsonify({"ok": False, "message": "Для зачисления нужна подтвержденная оплата"}), 400
    if not validate_email(email):
        return jsonify({"ok": False, "message": "Некорректный email"}), 400
    if not validate_phone(phone):
        return jsonify({"ok": False, "message": "Некорректный номер телефона"}), 400

    with closing(get_conn()) as conn:
        payment = conn.execute(
            "SELECT payment_id, status, consumed, card_last4 FROM payments WHERE payment_id=?",
            (payment_id,),
        ).fetchone()
        if not payment or payment["status"] != "paid":
            return jsonify({"ok": False, "message": "Платеж не подтвержден"}), 409
        if int(payment["consumed"]) == 1:
            return jsonify({"ok": False, "message": "Этот платеж уже использован"}), 409

        dup = conn.execute("SELECT id FROM training_enrollments WHERE email=?", (email,)).fetchone()
        if dup:
            return jsonify({"ok": False, "message": "Вы уже в списке обучения"}), 409

        accepted = conn.execute("SELECT COUNT(*) c FROM training_enrollments WHERE status='accepted'").fetchone()["c"]
        status = "accepted" if accepted < TRAINING_CAPACITY else "waitlist"

        conn.execute(
            """
            INSERT INTO training_enrollments (name, email, phone, payment_verified, payment_id, status, created_at)
            VALUES (?, ?, ?, 1, ?, ?, ?)
            """,
            (name, email, phone, payment_id, status, datetime.now().isoformat()),
        )
        conn.execute("UPDATE payments SET consumed=1 WHERE payment_id=?", (payment_id,))
        conn.commit()

    if status == "accepted":
        text = f"Новый ученик зачислен: {name}, {email}, карта ****{payment['card_last4']}, paymentId={payment_id}"
    else:
        text = f"Оплата принята, но мест нет. Добавлен в лист ожидания: {name}, {email}, paymentId={payment_id}"

    notify = send_all_notifications("Новая заявка на обучение", text)

    return jsonify(
        {
            "ok": True,
            "status": status,
            "capacity": TRAINING_CAPACITY,
            "message": "Вы зачислены в обучение" if status == "accepted" else "Места закончились: вы добавлены в лист ожидания",
            "notifications": notify,
        }
    )


@app.route("/api/support", methods=["POST"])
@limiter.limit("20 per minute")
def support_ai():
    payload = request.get_json(silent=True) or {}
    question = (payload.get("question") or "").strip()
    if len(question) < 4:
        return jsonify({"ok": False, "message": "Опишите проблему подробнее"}), 400

    api_key = os.getenv("OPENAI_API_KEY")
    model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    if not api_key:
        return jsonify({"ok": False, "message": "AI техподдержка временно недоступна"}), 503

    system_prompt = (
        "Ты техническая поддержка сайта Роза Оглы. "
        "Отвечай только по техническим проблемам: запись, оплата, вход, ошибки на сайте, обучение, личный кабинет. "
        "Если вопрос не про техподдержку — вежливо откажись и предложи написать в WhatsApp 87072867777. "
        "Не задавай лишние вопросы. Дай короткие пошаговые инструкции."
    )

    resp = requests.post(
        "https://api.openai.com/v1/chat/completions",
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        json={
            "model": model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": question},
            ],
            "temperature": 0.2,
            "max_tokens": 350,
        },
        timeout=30,
    )
    if resp.status_code >= 400:
        return jsonify({"ok": False, "message": "AI сервис временно недоступен"}), 502

    data = resp.json()
    answer = data.get("choices", [{}])[0].get("message", {}).get("content", "")
    return jsonify({"ok": True, "answer": answer})


init_db()


if __name__ == "__main__":
    port = int(os.getenv("PORT", "5000"))
    app.run(host="0.0.0.0", port=port, debug=False)
