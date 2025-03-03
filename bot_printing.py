import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, InputFile

# Gantikan dengan Token Bot Telegram anda
TOKEN = '7964541493:AAEi8S448XgM0S2Xz27fWJ9h6G8f-SFy6Nw'
ADMIN_ID = '-1002238456592'
QR_CODE_PATH = '/mnt/data/image.png'  # Path gambar QR Code

bot = telebot.TeleBot(TOKEN)

# Menu permulaan
@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("🖨️ Mula Tempahan", callback_data='start_order'))
    
    welcome_text = """
    📢 *Selamat Datang ke Bot Printing!*
    
    🖨️ *Cara guna bot:*
    1️⃣ Tekan "Mula Tempahan" untuk buat tempahan.
    2️⃣ Masukkan *Nama & Kelas*.
    3️⃣ Pilih *Jenis Cetakan* & bayar melalui *Touch 'n Go*.
    4️⃣ Hantar *bukti pembayaran* dan *dokumen*.
    5️⃣ Semak status cetakan dengan "📌 Tanya Status".
    
    💰 *Harga cetakan:*
    🎨 Warna → RM2.00/salinan
    ⚫ Hitam Putih → RM0.50/salinan
    
    ℹ️ *Gunakan /help jika perlukan bantuan.*
    """
    
    bot.send_message(message.chat.id, welcome_text, parse_mode="Markdown", reply_markup=markup)

# Menu bantuan
@bot.message_handler(commands=['help'])
def send_help(message):
    help_text = """
    🆘 *Bantuan & FAQ*
    
    📌 *Cara guna bot:*
    1️⃣ Tekan "Mula Tempahan" untuk buat tempahan.
    2️⃣ Masukkan *Nama & Kelas*.
    3️⃣ Pilih *Jenis Cetakan*.
    4️⃣ Hantar *bukti pembayaran* dan *dokumen*.
    5️⃣ Semak status cetakan dengan "📌 Tanya Status".
    
    ❌ Guna /cancel untuk batalkan tempahan sebelum diproses.
    
    🆘 *Hubungi Admin:* Tekan butang di bawah untuk hubungi admin.
    """
    
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("🆘 Hubungi Admin", url=f"https://t.me/{ADMIN_ID}"))
    
    bot.send_message(message.chat.id, help_text, parse_mode="Markdown", reply_markup=markup)

# Proses tempahan
@bot.callback_query_handler(func=lambda call: call.data == 'start_order')
def start_order(call):
    bot.send_message(call.message.chat.id, "📌 Sila masukkan nama dan kelas anda.")
    bot.register_next_step_handler(call.message, get_name)

def get_name(message):
    name = message.text
    bot.send_message(message.chat.id, "📌 Pilih jenis cetakan:", reply_markup=print_options())

def print_options():
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("🎨 Warna - RM2.00/salinan", callback_data='color'))
    markup.add(InlineKeyboardButton("⚫ Hitam Putih - RM0.50/salinan", callback_data='bw'))
    return markup

@bot.callback_query_handler(func=lambda call: call.data in ['color', 'bw'])
def select_print_type(call):
    print_type = "Warna" if call.data == 'color' else "Hitam Putih"
    bot.send_message(call.message.chat.id, f"💰 Anda pilih *{print_type}*. Sila masukkan bilangan salinan.", parse_mode="Markdown")
    bot.register_next_step_handler(call.message, get_quantity, print_type)

def get_quantity(message, print_type):
    try:
        quantity = int(message.text)
        price = quantity * (2 if print_type == "Warna" else 0.5)
        
        bot.send_message(message.chat.id, f"💵 Jumlah yang perlu dibayar: *RM{price:.2f}*\nSila buat bayaran menggunakan Touch 'n Go dan hantar bukti pembayaran.", parse_mode="Markdown")
        
        with open(QR_CODE_PATH, 'rb') as qr_code:
            bot.send_photo(message.chat.id, qr_code, caption="📌 Imbas QR ini untuk pembayaran.")
        
        bot.register_next_step_handler(message, receive_payment)
    except ValueError:
        bot.send_message(message.chat.id, "❌ Sila masukkan nombor yang betul.")
        bot.register_next_step_handler(message, get_quantity, print_type)

def receive_payment(message):
    if message.photo:
        bot.send_message(message.chat.id, "✅ Bukti pembayaran diterima. Sila hantar dokumen untuk dicetak.")
        bot.register_next_step_handler(message, receive_document)
    else:
        bot.send_message(message.chat.id, "❌ Sila hantar gambar bukti pembayaran.")
        bot.register_next_step_handler(message, receive_payment)

def receive_document(message):
    if message.document or message.photo:
        bot.send_message(message.chat.id, "📄 Dokumen diterima. Cetakan akan diproses. Anda boleh semak status menggunakan 📌 Tanya Status.")
        bot.send_message(ADMIN_ID, f"📌 *Permintaan Baru!*\n👤 Pelanggan: {message.chat.id}\n📄 Dokumen dihantar. Sila semak pembayaran.", parse_mode="Markdown")
    else:
        bot.send_message(message.chat.id, "❌ Sila hantar dokumen dalam format yang betul.")
        bot.register_next_step_handler(message, receive_document)

bot.polling()




