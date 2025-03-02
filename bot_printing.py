import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, InputMediaPhoto

TOKEN = "7964541493:AAEi8S448XgM0S2Xz27fWJ9h6G8f-SFy6Nw"
GROUP_ID = "-1002238456592"
ADMIN_ID = "1631295416"

bot = telebot.TeleBot(TOKEN)
users = {}
queue_number = 1

@bot.message_handler(commands=['start'])
def start(message):
    welcome_text = (
        "\U0001F4DA Selamat datang ke **Servis Printing BWP PDRM Kulim**! \n\n"
        "Dibina khas untuk memudahkan urusan cetakan oleh **BWP sendiri**.\n\n"
        "💰 **Harga:**\n"
        "- **Warna:** RM2.00 per salinan\n"
        "- **Hitam Putih:** RM0.50 per salinan\n\n"
        "📌 **Kredit:**\n"
        "- **Adam Zuwairi** - President BWP 24/25 (Pembangun bot)\n"
        "- **Umaira Aqilah** - Exco Keusahawanan 24/25 (Idea servis)\n\n"
        "Sila masukkan nama anda untuk meneruskan."
    )
    bot.send_message(message.chat.id, welcome_text, parse_mode="Markdown")
    users[message.chat.id] = {}

@bot.message_handler(func=lambda message: message.chat.id in users and 'name' not in users[message.chat.id])
def get_name(message):
    users[message.chat.id]['name'] = message.text
    bot.send_message(message.chat.id, "Masukkan kelas anda.")

@bot.message_handler(func=lambda message: message.chat.id in users and 'class' not in users[message.chat.id])
def get_class(message):
    users[message.chat.id]['class'] = message.text
    bot.send_message(message.chat.id, "Pilih jenis cetakan:", reply_markup=color_markup())

def color_markup():
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("Warna (RM2.00)", callback_data='color'))
    markup.add(InlineKeyboardButton("Hitam Putih (RM0.50)", callback_data='bw'))
    return markup

@bot.callback_query_handler(func=lambda call: call.data in ['color', 'bw'])
def get_color(call):
    users[call.message.chat.id]['color'] = call.data
    bot.send_message(call.message.chat.id, "Berapa salinan yang diperlukan?")
    bot.answer_callback_query(call.id)

@bot.message_handler(func=lambda message: message.chat.id in users and 'copies' not in users[message.chat.id])
def get_copies(message):
    global queue_number
    try:
        copies = int(message.text)
        users[message.chat.id]['copies'] = copies
        users[message.chat.id]['queue'] = queue_number
        queue_number += 1
        price = copies * (2.00 if users[message.chat.id]['color'] == 'color' else 0.50)
        users[message.chat.id]['price'] = price
        bot.send_message(message.chat.id, f"Harga: RM{price:.2f}. Sila hantar dokumen atau gambar untuk cetakan.")
    except ValueError:
        bot.send_message(message.chat.id, "Masukkan nombor yang sah.")

@bot.message_handler(content_types=['document', 'photo'])
def receive_document(message):
    users[message.chat.id]['file_id'] = message.document.file_id if message.document else message.photo[-1].file_id
    bot.send_message(message.chat.id, "Sila hantar bukti pembayaran.")

@bot.message_handler(content_types=['photo'])
def receive_payment_proof(message):
    if 'file_id' in users[message.chat.id]:
        users[message.chat.id]['payment_proof'] = message.photo[-1].file_id
        caption = (f"\U0001F4C4 **Permintaan Baru:**\n"
                   f"👤 Nama: {users[message.chat.id]['name']}\n"
                   f"🏫 Kelas: {users[message.chat.id]['class']}\n"
                   f"📄 Salinan: {users[message.chat.id]['copies']}\n"
                   f"🎨 Jenis: {'Warna' if users[message.chat.id]['color'] == 'color' else 'Hitam Putih'}\n"
                   f"💰 Harga: RM{users[message.chat.id]['price']:.2f}\n"
                   f"🔢 Nombor Giliran: {users[message.chat.id]['queue']}")
        bot.send_photo(GROUP_ID, users[message.chat.id]['payment_proof'], caption=caption, reply_markup=confirm_markup(message.chat.id))
        bot.send_message(message.chat.id, "Bukti bayaran telah dihantar kepada admin untuk pengesahan.")
    else:
        bot.send_message(message.chat.id, "Hantar dokumen dahulu sebelum menghantar bukti pembayaran.")

def confirm_markup(user_id):
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("Sahkan Cetakan", callback_data=f'confirm_{user_id}'))
    markup.add(InlineKeyboardButton("Tolak Cetakan", callback_data=f'reject_{user_id}'))
    return markup

@bot.callback_query_handler(func=lambda call: call.data.startswith('confirm_'))
def confirm_printing(call):
    user_id = int(call.data.split('_')[1])
    if user_id in users:
        bot.send_message(user_id, "✅ Cetakan anda telah disahkan oleh admin dan sedang diproses.")
        bot.send_message(GROUP_ID, f"📌 Cetakan untuk {users[user_id]['name']} telah disahkan.")
    bot.answer_callback_query(call.id)

@bot.callback_query_handler(func=lambda call: call.data.startswith('reject_'))
def reject_printing(call):
    user_id = int(call.data.split('_')[1])
    if user_id in users:
        bot.send_message(user_id, "❌ Cetakan anda ditolak oleh admin. Sila hubungi admin untuk maklumat lanjut.")
        bot.send_message(GROUP_ID, f"⚠️ Cetakan untuk {users[user_id]['name']} ditolak.")
    bot.answer_callback_query(call.id)

@bot.message_handler(commands=['status'])
def check_status(message):
    if message.chat.id in users:
        bot.send_message(message.chat.id, "Status cetakan anda: Masih dalam proses.")
    else:
        bot.send_message(message.chat.id, "Anda belum membuat permintaan cetakan.")

bot.polling(none_stop=True)
