import os
import sqlite3
import telebot

API_TOKEN = os.environ.get("BOT_TOKEN")
if not API_TOKEN:
    raise ValueError("Переменная окружения BOT_TOKEN не установлена.")

bot = telebot.TeleBot(API_TOKEN, threaded=True, parse_mode=None)
DB_PATH = "users.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    # "Успокаиваем" Replit, но ничего не затираем
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            name TEXT,
            language TEXT,
            difficulty TEXT,
            climb_type TEXT,
            country TEXT,
            country_other TEXT,
            city TEXT,
            city_other TEXT,
            photo_bytes BLOB,
            gender TEXT,
            weight TEXT,
            bio TEXT,
            consent_accepted INTEGER DEFAULT 0
        )
    """)
    conn.commit()
    conn.close()


@bot.message_handler(commands=['start'])
def start_handler(message):
    bot.reply_to(message, "Привет")

@bot.message_handler(commands=['name'])
def name_handler(message):
    parts = message.text.strip().split(maxsplit=1)
    if len(parts) < 2:
        bot.reply_to(message, "Пожалуйста, укажи имя: /name ТвоёИмя")
        return

    name = parts[1].strip()
    user_id = message.from_user.id
    username = message.from_user.username or ""

    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO users (user_id, name, username)
            VALUES (?, ?, ?)
            ON CONFLICT(user_id) DO UPDATE SET
                name = excluded.name,
                username = excluded.username
        """, (user_id, name, username))
        conn.commit()
        conn.close()
        bot.reply_to(message, f"Имя '{name}' обновлено.")
    except Exception as e:
        bot.reply_to(message, f"Ошибка при сохранении: {e}")

@bot.message_handler(commands=['dump'])
def dump_users(message):
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT user_id, name FROM users")
        rows = cursor.fetchall()
        conn.close()

        if not rows:
            bot.reply_to(message, "Пользователей пока нет.")
            return

        msg = "Пользователи:\n"
        for row in rows:
            msg += f"ID: {row[0]}, Имя: {row[1]}\n"

        bot.reply_to(message, msg[:4096])  # Telegram ограничение на длину
    except Exception as e:
        bot.reply_to(message, f"Ошибка при чтении из базы: {e}")

if __name__ == "__main__":
    print("Бот запущен...")
    bot.infinity_polling(long_polling_timeout=30)

