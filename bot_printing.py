import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# Masukkan maklumat bot di sini
TOKEN = "7964541493:AAEi8S448XgM0S2Xz27fWJ9h6G8f-SFy6Nw"
ADMIN_IDS = [-1002238456592]  # ID Admin
GROUP_ID = -1002238456592  # ID Group Cetakan
TNG_NUMBER = "+60 1164243774"  # Nombor untuk bayaran

bot = telebot.TeleBot(TOKEN)

# /start - Pengenalan bot
@bot.message_handler(commands=['start'])
def send_welcome(message):
    welcome_text = """
    🔹 *Selamat datang ke Bot Cetakan BWP MRSM PDRM!* 🔹
    
    🖨️ *Cara guna bot ini:*
    1️⃣ Tekan "Mula Tempahan" untuk membuat tempahan cetakan.
    2️⃣ Masukkan Nama & Kelas.
    3️⃣ Pilih Jenis Cetakan & bayar melalui *Touch 'n Go*.
    4️⃣ Hantar bukti pembayaran dan dokumen.
    5️⃣ Semak status cetakan dengan 📌 Tanya Status.
    
    💰 *Harga cetakan:*
    🎨 Warna → RM2.00 per salinan
    ⚫ Hitam Putih → RM0.50 per salinan
    
    📢 *Bayaran perlu dibuat ke nombor:* {TNG_NUMBER}
    📌 Gunakan /help jika anda perlukan bantuan.
    """.format(TNG_NUMBER=TNG_NUMBER)
    
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("🖨️ Mula Tempahan", callback_data="start_order"))
    bot.send_message(message.chat.id, welcome_text, reply_markup=markup, parse_mode="Markdown")

# /help - Bantuan penggunaan bot
@bot.message_handler(commands=['help'])
def send_help(message):
    help_text = """
    🤖 *Bantuan Bot Cetakan* 🤖
    
    💬 *Cara membuat tempahan:*
    - Tekan *Mula Tempahan*
    - Masukkan butiran cetakan
    - Hantar bukti pembayaran
    
    📌 *Cara semak status cetakan:*
    - Gunakan /status untuk melihat status cetakan
    
    ❌ *Pembatalan Tempahan:*
    - Gunakan /cancel untuk batalkan sebelum diproses.
    
    📞 *Hubungi Admin:*
    - Gunakan /admin [Mesej] untuk menghubungi admin
    """
    bot.send_message(message.chat.id, help_text, parse_mode="Markdown")

# /admin - Pelanggan hubungi admin
@bot.message_handler(commands=['admin'])
def contact_admin(message):
    text = message.text.replace('/admin', '').strip()
    if text:
        for admin in ADMIN_IDS:
            bot.send_message(admin, f"📩 Mesej dari pelanggan @{message.chat.username}: {text}")
        bot.send_message(message.chat.id, "Mesej anda telah dihantar kepada admin!")
    else:
        bot.send_message(message.chat.id, "Sila masukkan mesej selepas /admin untuk hubungi admin.")

# /chat - Admin hubungi pelanggan
@bot.message_handler(commands=['chat'])
def chat_with_user(message):
    if message.chat.id in ADMIN_IDS:
        bot.send_message(message.chat.id, "Masukkan ID pelanggan dan mesej dalam format: \nID_PELANGGAN:Mesej")
    else:
        bot.send_message(message.chat.id, "Anda bukan admin!")

@bot.message_handler(func=lambda message: ':' in message.text and message.chat.id in ADMIN_IDS)
def send_admin_message(message):
    try:
        user_id, text = message.text.split(':', 1)
        user_id = int(user_id.strip())
        bot.send_message(user_id, text.strip())
        bot.send_message(message.chat.id, "Mesej dihantar kepada pelanggan!")
    except Exception as e:
        bot.send_message(message.chat.id, f"Ralat: {e}")

# /cancel - Pelanggan batalkan tempahan sebelum diproses
@bot.message_handler(commands=['cancel'])
def cancel_order(message):
    bot.send_message(message.chat.id, "❌ Tempahan anda telah dibatalkan sebelum diproses.")

# Kredit bot
CREDIT_TEXT = """
🔹 *Bot Cetakan BWP MRSM PDRM* 🔹

👨‍💻 *Pembangun:* Adam Zuwairi
💡 *Idea & Konsep:* Umaira Aqilah
"""

@bot.message_handler(commands=['credit'])
def send_credit(message):
    bot.send_message(message.chat.id, CREDIT_TEXT, parse_mode="Markdown")

bot.polling(none_stop=True)





