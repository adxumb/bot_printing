import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# ----------------- Tetapan Bot -----------------
TOKEN = "7964541493:AAEi8S448XgM0S2Xz27fWJ9h6G8f-SFy6Nw"  # Masukkan Token Bot
ADMIN_IDS = [1631295416]  # Masukkan ID Admin
GROUP_ID = -1002238456592  # Masukkan ID Group Cetakan
PAYMENT_NUMBER = "+60 1164243774 (Aina)"

bot = telebot.TeleBot(TOKEN)

# ----------------- Fungsi Permulaan (/start) -----------------
@bot.message_handler(commands=['start'])
def send_welcome(message):
    welcome_text = (
        "\U0001F4E3 *Selamat datang ke Bot Cetakan BWP MRSM PDRM!* \U0001F4E3\n\n"
        "Cara guna bot ini:\n"
        "1️⃣ Masukkan *Nama, Kelas & Nota Tambahan*\n"
        "2️⃣ Pilih *Jenis Cetakan*\n"
        "3️⃣ Bayar ke *" + PAYMENT_NUMBER + "* dan hantar bukti pembayaran\n"
        "4️⃣ Hantar *dokumen* untuk dicetak\n"
        "5️⃣ Semak *status cetakan* dengan /status\n\n"
        "\U0001F4B0 *Harga cetakan:*\n"
        "🎨 Warna → RM2.00 per salinan\n"
        "⚫ Hitam Putih → RM0.50 per salinan\n\n"
        "Gunakan /help jika anda perlukan bantuan."
    )
    bot.send_message(message.chat.id, welcome_text, parse_mode="Markdown")
    request_details(message)

# ----------------- Fungsi Bantuan (/help) -----------------
@bot.message_handler(commands=['help'])
def send_help(message):
    help_text = (
        "\U0001F916 *Bantuan Bot Cetakan* \U0001F916\n\n"
        "📌 *Cara guna bot:*\n"
        "- Masukkan *Nama, Kelas & Nota Tambahan*\n"
        "- Pilih *Jenis Cetakan*\n"
        "- Bayar & hantar *bukti pembayaran*\n"
        "- Hantar *dokumen*\n"
        "- Semak *status cetakan* dengan /status\n\n"
        "📞 *Hubungi Admin:*\n"
        "- Gunakan /admin [Mesej] untuk hubungi admin\n"
        "- Batalkan tempahan dengan /cancel sebelum diproses"
    )
    bot.send_message(message.chat.id, help_text, parse_mode="Markdown")

# ----------------- Fungsi Mula Tempahan -----------------
def request_details(message):
    bot.send_message(message.chat.id, "Sila masukkan nama anda:")
    bot.register_next_step_handler(message, get_class)

def get_class(message):
    name = message.text
    bot.send_message(message.chat.id, "Sila masukkan kelas anda:")
    bot.register_next_step_handler(message, get_notes, name)

def get_notes(message, name):
    class_name = message.text
    bot.send_message(message.chat.id, "Masukkan sebarang nota tambahan (atau taip 'Tiada'):")
    bot.register_next_step_handler(message, select_print_type, name, class_name)

def select_print_type(message, name, class_name):
    notes = message.text
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("🎨 Warna", callback_data=f"color_{name}_{class_name}_{notes}"))
    markup.add(InlineKeyboardButton("⚫ Hitam Putih", callback_data=f"bw_{name}_{class_name}_{notes}"))
    bot.send_message(message.chat.id, "Pilih jenis cetakan:", reply_markup=markup)

# ----------------- Callback Jenis Cetakan -----------------
@bot.callback_query_handler(func=lambda call: call.data.startswith("color") or call.data.startswith("bw"))
def handle_print_type(call):
    data = call.data.split("_")
    print_type = "Warna" if data[0] == "color" else "Hitam Putih"
    name, class_name, notes = data[1], data[2], data[3]
    bot.send_message(call.message.chat.id, f"Anda memilih cetakan *{print_type}*. Sila masukkan jumlah salinan:", parse_mode="Markdown")
    bot.register_next_step_handler(call.message, request_payment, print_type, name, class_name, notes)

def request_payment(message, print_type, name, class_name, notes):
    try:
        copies = int(message.text)
        price = 2.00 if print_type == "Warna" else 0.50
        total_price = copies * price
        bot.send_message(message.chat.id, f"Jumlah harga: *RM{total_price:.2f}*. Sila buat pembayaran ke {PAYMENT_NUMBER} dan hantar bukti pembayaran.", parse_mode="Markdown")
        bot.register_next_step_handler(message, confirm_payment, print_type, name, class_name, notes, copies, total_price)
    except ValueError:
        bot.send_message(message.chat.id, "Sila masukkan jumlah salinan yang sah.")
        bot.register_next_step_handler(message, request_payment, print_type, name, class_name, notes)

def confirm_payment(message, print_type, name, class_name, notes, copies, total_price):
    bot.send_message(GROUP_ID, f"📌 Permintaan Cetakan Baru\n👤 Nama: {name}\n🏫 Kelas: {class_name}\n📄 Nota: {notes}\n🖨️ Jenis Cetakan: {print_type}\n📝 Bilangan Salinan: {copies}\n💰 Jumlah Harga: RM{total_price:.2f}\n\nAdmin, sila sahkan pembayaran!")
    bot.send_message(message.chat.id, "Bukti pembayaran diterima. Admin akan mengesahkan dalam masa terdekat.")

# ----------------- Fungsi Hubungi Admin (/admin) -----------------
@bot.message_handler(commands=['admin'])
def contact_admin(message):
    text = message.text.replace('/admin', '').strip()
    if text:
        for admin in ADMIN_IDS:
            bot.send_message(admin, f"📩 Mesej dari pelanggan @{message.chat.username}: {text}")
        bot.send_message(message.chat.id, "Mesej anda telah dihantar kepada admin!")
    else:
        bot.send_message(message.chat.id, "Sila masukkan mesej selepas /admin untuk hubungi admin.")

# ----------------- Mulakan Bot -----------------
bot.polling(none_stop=True)





