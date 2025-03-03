import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, InputFile

# Ruang untuk masukkan token dan ID
TOKEN = "7964541493:AAEi8S448XgM0S2Xz27fWJ9h6G8f-SFy6Nw"
ID_ADMIN = ["1631295416"]  # Masukkan ID admin dalam senarai
ID_GROUP = "-1002238456592"
QR_CODE_PATH = "/mnt/data/image.png"  # Lokasi QR Code

bot = telebot.TeleBot(TOKEN)

# Fungsi untuk permulaan bot
@bot.message_handler(commands=['start'])
def send_welcome(message):
    welcome_text = """
    🔹 *Selamat datang ke Bot Cetakan BWP MRSM PDRM!* 🔹
    
    🖨️ *Cara guna bot:*
    1️⃣ Tekan "*Mula Tempahan*" untuk buat tempahan.
    2️⃣ Masukkan Nama & Kelas.
    3️⃣ Pilih Jenis Cetakan & bayar melalui Touch ‘n Go.
    4️⃣ Hantar bukti pembayaran dan dokumen.
    5️⃣ Semak status cetakan dengan "📌 Tanya Status".
    
    💰 *Harga cetakan:*
    🎨 Warna → RM2.00 per salinan
    ⚫ Hitam Putih → RM0.50 per salinan
    
    📢 Tekan "🖨️ Mula Tempahan" untuk mula.
    📌 Gunakan /help jika anda perlukan bantuan.
    """
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("🖨️ Mula Tempahan", callback_data="start_order"))
    bot.send_photo(message.chat.id, photo=InputFile(QR_CODE_PATH), caption=welcome_text, reply_markup=markup, parse_mode="Markdown")

# Fungsi bantuan
@bot.message_handler(commands=['help'])
def send_help(message):
    help_text = """
    🤖 *Bantuan Bot Cetakan* 🤖
    
    📝 *Cara guna bot:*
    - Tekan "*Mula Tempahan*"
    - Masukkan butiran cetakan
    - Hantar bukti pembayaran
    
    📌 *Semak status cetakan:*
    - Gunakan /status untuk melihat status cetakan
    
    ❌ *Guna /cancel* untuk batalkan tempahan sebelum diproses.
    
    📞 *Hubungi Admin:*
    - Gunakan /admin [Mesej] untuk hubungi admin.
    """
    bot.send_message(message.chat.id, help_text, parse_mode="Markdown")

# Fungsi pelanggan hubungi admin
@bot.message_handler(commands=['admin'])
def contact_admin(message):
    text = message.text.replace('/admin', '').strip()
    if text:
        for admin in ID_ADMIN:
            bot.send_message(admin, f"📩 Mesej dari pelanggan @{message.chat.username}: {text}")
        bot.send_message(message.chat.id, "Mesej anda telah dihantar kepada admin!")
    else:
        bot.send_message(message.chat.id, "Sila masukkan mesej selepas /admin untuk hubungi admin.")

# Fungsi admin hubungi pelanggan
@bot.message_handler(commands=['chat'])
def chat_with_user(message):
    if message.chat.id in ID_ADMIN:
        bot.send_message(message.chat.id, "Masukkan ID pelanggan dan mesej dalam format: \nID_PELANGGAN:Mesej")
    else:
        bot.send_message(message.chat.id, "Anda bukan admin!")

@bot.message_handler(func=lambda message: ':' in message.text and message.chat.id in ID_ADMIN)
def send_admin_message(message):
    try:
        user_id, text = message.text.split(':', 1)
        user_id = int(user_id.strip())
        bot.send_message(user_id, text.strip())
        bot.send_message(message.chat.id, "Mesej dihantar kepada pelanggan!")
    except Exception as e:
        bot.send_message(message.chat.id, f"Ralat: {e}")

# Fungsi pembatalan tempahan
@bot.message_handler(commands=['cancel'])
def cancel_order(message):
    bot.send_message(message.chat.id, "Tempahan anda telah dibatalkan.")

# Fungsi untuk melihat status cetakan
@bot.message_handler(commands=['status'])
def check_status(message):
    bot.send_message(message.chat.id, "📌 Status cetakan anda sedang diproses. Sila tunggu notifikasi.")

# Kredit bot
@bot.message_handler(commands=['credit'])
def bot_credit(message):
    credit_text = """
    🔹 *Bot Printing BWP MRSM PDRM* 🔹
    
    👨‍💻 *Dibangunkan oleh:*
    - **Adam Zuwairi** - Pembina bot
    - **Umaira Aqilah** - Idea servis bot printing
    
    🤝 Terima kasih kerana menggunakan bot ini!
    """
    bot.send_message(message.chat.id, credit_text, parse_mode="Markdown")

bot.polling(none_stop=True)




