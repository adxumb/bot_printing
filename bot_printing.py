import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

TOKEN = "7964541493:AAEi8S448XgM0S2Xz27fWJ9h6G8f-SFy6Nw"
GROUP_ID = "-1002238456592"
ADMIN_ID = "1631295416"
bot = telebot.TeleBot(TOKEN)

users = {}
queue_number = 1
confirmed_requests = set()

@bot.message_handler(commands=['start'])
def start(message):
    welcome_text = ("Selamat datang ke servis printing BWP PDRM Kulim!\n\n"
                    "Servis ini dibina untuk memudahkan urusan cetakan oleh BWP sendiri.\n\n"
                    "📌 **Cara guna bot:**\n"
                    "1️⃣ Masukkan nama dan kelas anda.\n"
                    "2️⃣ Pilih jenis cetakan (warna/hitam putih).\n"
                    "3️⃣ Masukkan jumlah salinan.\n"
                    "4️⃣ Hantar bukti pembayaran.\n"
                    "5️⃣ Admin akan sahkan & proses cetakan.\n"
                    "6️⃣ Gunakan `/status` untuk semak status cetakan anda.\n\n"
                    "💰 Harga:\n"
                    "- Warna: RM2.00 per helai\n"
                    "- Hitam Putih: RM0.50 per helai\n\n"
                    "📢 Kredit:\n"
                    "- **Adam Zuwairi** - President BWP 24/25 (Pembangun Bot)\n"
                    "- **Umaira Aqilah** - Exco Keusahawanan 24/25 (Idea Bot)")
    bot.send_message(message.chat.id, welcome_text, parse_mode="Markdown")
    bot.send_message(message.chat.id, "Sila masukkan nama anda.")
    users[message.chat.id] = {"step": "name"}

@bot.message_handler(func=lambda message: message.chat.id in users and users[message.chat.id]["step"] == "name")
def get_name(message):
    users[message.chat.id]['name'] = message.text
    users[message.chat.id]['step'] = "class"
    bot.send_message(message.chat.id, "Masukkan kelas anda.")

@bot.message_handler(func=lambda message: message.chat.id in users and users[message.chat.id]["step"] == "class")
def get_class(message):
    users[message.chat.id]['class'] = message.text
    users[message.chat.id]['step'] = "color"
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("Warna (RM2.00)", callback_data='color'))
    markup.add(InlineKeyboardButton("Hitam Putih (RM0.50)", callback_data='bw'))
    bot.send_message(message.chat.id, "Pilih jenis cetakan:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data in ['color', 'bw'])
def get_color(call):
    users[call.message.chat.id]['color'] = call.data
    users[call.message.chat.id]['step'] = "copies"
    bot.send_message(call.message.chat.id, "Berapa salinan yang diperlukan?")
    bot.answer_callback_query(call.id)

@bot.message_handler(func=lambda message: message.chat.id in users and users[message.chat.id]["step"] == "copies")
def get_copies(message):
    global queue_number
    try:
        copies = int(message.text)
        users[message.chat.id]['copies'] = copies
        users[message.chat.id]['price'] = copies * (2.00 if users[message.chat.id]['color'] == 'color' else 0.50)
        users[message.chat.id]['queue'] = queue_number
        users[message.chat.id]['step'] = "payment"
        queue_number += 1
        bot.send_message(message.chat.id, f"Harga: RM{users[message.chat.id]['price']:.2f}. Sila hantar gambar bukti pembayaran.")
    except ValueError:
        bot.send_message(message.chat.id, "Masukkan nombor yang sah.")

@bot.message_handler(content_types=['photo'])
def receive_payment_proof(message):
    if message.chat.id in users and users[message.chat.id]['step'] == "payment":
        users[message.chat.id]['payment_proof'] = message.photo[-1].file_id
        users[message.chat.id]['step'] = "pending"
        caption = (f"📄 **Permintaan Baru**\n"
                   f"👤 Nama: {users[message.chat.id]['name']}\n"
                   f"🏫 Kelas: {users[message.chat.id]['class']}\n"
                   f"📑 Salinan: {users[message.chat.id]['copies']}\n"
                   f"🎨 Jenis: {'Warna' if users[message.chat.id]['color'] == 'color' else 'Hitam Putih'}\n"
                   f"💰 Harga: RM{users[message.chat.id]['price']:.2f}\n"
                   f"🔢 Nombor Giliran: {users[message.chat.id]['queue']}")
        bot.send_photo(GROUP_ID, users[message.chat.id]['payment_proof'], caption=caption, reply_markup=confirm_markup(message.chat.id))
        bot.send_message(message.chat.id, "Bukti bayaran telah dihantar kepada admin untuk pengesahan.")
    else:
        bot.send_message(message.chat.id, "Sila lengkapkan maklumat sebelum hantar bukti pembayaran.")

def confirm_markup(user_id):
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("✅ Sahkan Cetakan", callback_data=f'confirm_{user_id}'))
    return markup

@bot.callback_query_handler(func=lambda call: call.data.startswith('confirm_'))
def confirm_printing(call):
    user_id = int(call.data.split('_')[1])
    if user_id in users and user_id not in confirmed_requests:
        confirmed_requests.add(user_id)
        bot.send_message(user_id, "✅ Cetakan anda telah disahkan oleh admin dan sedang diproses.")
        bot.send_message(GROUP_ID, f"🖨 Cetakan untuk {users[user_id]['name']} telah disahkan.")
    else:
        bot.answer_callback_query(call.id, "Cetakan ini sudah disahkan.", show_alert=True)

@bot.message_handler(commands=['status'])
def check_status(message):
    if message.chat.id in users:
        status = "⏳ Dalam proses" if users[message.chat.id]['step'] == "pending" else "✅ Selesai"
        bot.send_message(message.chat.id, f"📋 Status cetakan anda: {status}")
    else:
        bot.send_message(message.chat.id, "Tiada rekod cetakan anda.")

bot.polling(none_stop=True)

