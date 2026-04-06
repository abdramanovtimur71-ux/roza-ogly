import os
import re
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
                status TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )
        conn.commit()


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
        resp.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
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
    card_last4 = (payload.get("cardLast4") or "").strip()

    if not all([name, email, payment_id, card_last4]):
        return jsonify({"ok": False, "message": "Для зачисления нужна подтвержденная оплата"}), 400
    if not validate_email(email):
        return jsonify({"ok": False, "message": "Некорректный email"}), 400
    if not validate_phone(phone):
        return jsonify({"ok": False, "message": "Некорректный номер телефона"}), 400

    with closing(get_conn()) as conn:
        dup = conn.execute("SELECT id FROM training_enrollments WHERE email=?", (email,)).fetchone()
        if dup:
            return jsonify({"ok": False, "message": "Вы уже в списке обучения"}), 409

        accepted = conn.execute("SELECT COUNT(*) c FROM training_enrollments WHERE status='accepted'").fetchone()["c"]
        status = "accepted" if accepted < TRAINING_CAPACITY else "waitlist"

        conn.execute(
            """
            INSERT INTO training_enrollments (name, email, phone, payment_verified, status, created_at)
            VALUES (?, ?, ?, 1, ?, ?)
            """,
            (name, email, phone, status, datetime.now().isoformat()),
        )
        conn.commit()

    if status == "accepted":
        text = f"Новый ученик зачислен: {name}, {email}, карта ****{card_last4}, paymentId={payment_id}"
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


if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000, debug=False)
