import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# ===========================
# KONFIGURASI BOT
# ===========================
TOKEN = "7964541493:AAEi8S448XgM0S2Xz27fWJ9h6G8f-SFy6Nw"  # Masukkan Token Bot Telegram
ADMIN_IDS = [1631295416]  # Masukkan ID Admin
GROUP_ID = -1002238456592  # Masukkan ID Group Admin
BANK_ACCOUNT = "+60 1164243774 (Aina)"  # Nombor akaun pembayaran

bot = telebot.TeleBot(TOKEN)

# ===========================
# PERMULAAN BOT
# ===========================
@bot.message_handler(commands=['start'])
def send_welcome(message):
    welcome_text = """
    🔹 *Selamat Datang ke Bot Printing BWP MRSM PDRM!* 🔹
    
    🖨️ Cara guna bot ini:
    1️⃣ Masukkan Nama, Kelas & Nota tambahan.
    2️⃣ Pilih jenis cetakan & bayar ke *{}*.
    3️⃣ Hantar bukti pembayaran & dokumen.
    4️⃣ Admin akan sahkan dan maklumkan bila siap.
    
    💰 *Harga cetakan:*
    🎨 Warna → RM2.00/salinan
    ⚫ Hitam Putih → RM0.50/salinan
    
    📌 Gunakan /help jika perlukan bantuan.
    """.format(BANK_ACCOUNT)
    bot.send_message(message.chat.id, welcome_text, parse_mode="Markdown")
    request_order(message.chat.id)

# ===========================
# PERMINTAAN TEMPAHAN
# ===========================
def request_order(chat_id):
    bot.send_message(chat_id, "Sila masukkan nama anda:")
    bot.register_next_step_handler_by_chat_id(chat_id, get_name)

def get_name(message):
    name = message.text.strip()
    bot.send_message(message.chat.id, "Masukkan kelas anda:")
    bot.register_next_step_handler_by_chat_id(message.chat.id, get_class, name)

def get_class(message, name):
    class_name = message.text.strip()
    bot.send_message(message.chat.id, "Sebarang nota tambahan? (Jika tiada, taip 'Tiada')")
    bot.register_next_step_handler_by_chat_id(message.chat.id, get_note, name, class_name)

def get_note(message, name, class_name):
    note = message.text.strip()
    bot.send_message(message.chat.id, "Pilih jenis cetakan:\n🎨 Warna (RM2.00/salinan)\n⚫ Hitam Putih (RM0.50/salinan)")
    bot.register_next_step_handler_by_chat_id(message.chat.id, get_print_type, name, class_name, note)

def get_print_type(message, name, class_name, note):
    print_type = message.text.strip()
    bot.send_message(message.chat.id, "Masukkan bilangan salinan:")
    bot.register_next_step_handler_by_chat_id(message.chat.id, get_copy_count, name, class_name, note, print_type)

def get_copy_count(message, name, class_name, note, print_type):
    try:
        copies = int(message.text.strip())
        total_price = copies * (2 if "warna" in print_type.lower() else 0.5)
        order_text = f"""
        📝 *Tempahan Anda:*
        👤 Nama: {name}
        🏫 Kelas: {class_name}
        📝 Nota: {note}
        🖨️ Jenis Cetakan: {print_type}
        📄 Bilangan Salinan: {copies}
        💰 Jumlah Bayaran: RM{total_price:.2f}
        
        📌 *Sila buat pembayaran ke:*
        {BANK_ACCOUNT}
        
        ✅ Hantar bukti pembayaran di sini.
        """
        bot.send_message(message.chat.id, order_text, parse_mode="Markdown")
    except ValueError:
        bot.send_message(message.chat.id, "Sila masukkan nombor yang sah.")
        bot.register_next_step_handler_by_chat_id(message.chat.id, get_copy_count, name, class_name, note, print_type)

# ===========================
# ADMIN PANEL
# ===========================
@bot.message_handler(commands=['admin'])
def admin_panel(message):
    if message.chat.id in ADMIN_IDS:
        bot.send_message(message.chat.id, "Admin panel diaktifkan.")
    else:
        bot.send_message(message.chat.id, "Anda bukan admin!")

@bot.message_handler(commands=['chat'])
def chat_with_user(message):
    if message.chat.id in ADMIN_IDS:
        bot.send_message(message.chat.id, "Gunakan format: /chat <Nombor_Giliran> <Mesej>")
    else:
        bot.send_message(message.chat.id, "Anda bukan admin!")

@bot.message_handler(func=lambda message: message.text.startswith('/chat '))
def send_admin_message(message):
    if message.chat.id in ADMIN_IDS:
        try:
            _, queue_number, text = message.text.split(' ', 2)
            queue_number = queue_number.strip()
            bot.send_message(message.chat.id, f"Mesej dihantar kepada pelanggan # {queue_number}")
        except ValueError:
            bot.send_message(message.chat.id, "Format tidak sah. Gunakan: /chat <Nombor_Giliran> <Mesej>")
    else:
        bot.send_message(message.chat.id, "Anda bukan admin!")

@bot.message_handler(commands=['help'])
def send_help(message):
    help_text = """
    🤖 *Bantuan Bot Printing BWP MRSM PDRM* 🤖
    
    📝 *Cara guna bot:*
    - Ikut arahan yang diberikan selepas /start.
    - Hantar bukti pembayaran & dokumen untuk diproses.
    - Gunakan /status untuk semak cetakan.
    - Gunakan /cancel untuk batalkan sebelum diproses.
    
    📞 *Hubungi Admin:*
    - Gunakan /admin jika ada masalah.
    - Admin boleh chat pelanggan guna /chat <Nombor_Giliran> <Mesej>.
    """
    bot.send_message(message.chat.id, help_text, parse_mode="Markdown")

bot.polling(none_stop=True)





