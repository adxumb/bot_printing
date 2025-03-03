import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, InputFile

# Tetapan bot
TOKEN = "7964541493:AAEi8S448XgM0S2Xz27fWJ9h6G8f-SFy6Nw"
ADMIN_IDS = [1631295416]  # Ganti dengan ID admin sebenar
GROUP_ID = -1002238456592  # Ganti dengan ID group sebenar
QR_CODE_PATH = "/mnt/data/image.png"  # Lokasi QR Code
bot = telebot.TeleBot(TOKEN)

# Simpan permintaan cetakan
print_requests = {}

# Mesej pengenalan
INTRO_MESSAGE = """
🤖 *Selamat datang ke Bot Printing!*

📌 *Harga Cetakan:*
🎨 Warna: RM2.00/salinan
⚫ Hitam Putih: RM0.50/salinan

📜 *Cara Guna:*
1️⃣ Hantar nama & kelas anda.
2️⃣ Pilih jenis cetakan & bilangan salinan.
3️⃣ Bayar menggunakan QR Code & hantar resit.
4️⃣ Hantar dokumen untuk dicetak.
5️⃣ Tunggu notifikasi siap!

🆘 Gunakan /help jika perlu bantuan.

💳 *Pembayaran:* Tekan *Bayar Sekarang* untuk scan QR.
"""

# Fungsi untuk mulakan bot
@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("💳 Bayar Sekarang", callback_data="pay_now"))
    bot.send_message(message.chat.id, INTRO_MESSAGE, parse_mode="Markdown", reply_markup=markup)

# Fungsi untuk tunjuk QR Code untuk pembayaran
@bot.callback_query_handler(func=lambda call: call.data == "pay_now")
def send_qr_code(call):
    with open(QR_CODE_PATH, "rb") as qr:
        bot.send_photo(call.message.chat.id, qr, caption="Scan QR ini untuk pembayaran!")

# Fungsi untuk pelanggan dapatkan bantuan
@bot.message_handler(commands=['help'])
def send_help(message):
    bot.send_message(message.chat.id, "🆘 Jika anda memerlukan bantuan, sila hubungi admin atau gunakan /status untuk semak cetakan anda.")

# Fungsi untuk sahkan status cetakan oleh admin
@bot.message_handler(commands=['confirm'])
def confirm_print(message):
    if message.chat.id in ADMIN_IDS:
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("✅ Cetakan Siap", callback_data="print_done"))
        markup.add(InlineKeyboardButton("❌ Cetakan Belum Siap", callback_data="print_not_done"))
        bot.send_message(GROUP_ID, "Admin, sila pilih status cetakan:", reply_markup=markup)
    else:
        bot.send_message(message.chat.id, "Anda bukan admin!")

# Fungsi callback untuk status cetakan
@bot.callback_query_handler(func=lambda call: call.data in ["print_done", "print_not_done"])
def handle_print_status(call):
    status = "✅ Cetakan telah siap!" if call.data == "print_done" else "❌ Cetakan belum siap."
    bot.send_message(GROUP_ID, status)
    bot.answer_callback_query(call.id, "Status dikemas kini!")

# Fungsi admin untuk hubungi pelanggan
@bot.message_handler(commands=['chat'])
def chat_with_user(message):
    if message.chat.id in ADMIN_IDS:
        bot.send_message(message.chat.id, "Sila masukkan ID pelanggan dan mesej dalam format: \nID_PELANGGAN:Mesej")
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

bot.polling(none_stop=True)


