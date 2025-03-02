import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# Konfigurasi ID Admin dan ID Group
ADMIN_IDS = [1631295416]  # Ganti dengan ID admin sebenar
GROUP_ID = -1002238456592  # Ganti dengan ID group sebenar

bot = telebot.TeleBot("7964541493:AAEi8S448XgM0S2Xz27fWJ9h6G8f-SFy6Nw")

# Simpan status pesanan
orders = {}

# Pengenalan awal
@bot.message_handler(commands=['start'])
def send_welcome(message):
    welcome_text = (
        "Selamat datang ke **Servis Printing BWP PDRM Kulim**! 🖨️\n\n"
        "Bot ini dibina untuk memudahkan urusan cetakan anda. Dibina oleh **Adam Zuwairi (President BWP 24/25)** "
        "berdasarkan idea dari **Umaira Aqilah (Exco Keusahawanan 24/25).**\n\n"
        "**Harga Cetakan:**\n"
        "- Warna: RM2.00 per helai\n"
        "- Hitam Putih: RM0.50 per helai\n\n"
        "Sila hantarkan dokumen atau gambar yang ingin dicetak."
    )
    bot.send_message(message.chat.id, welcome_text)
    bot.send_message(message.chat.id, "Sila masukkan nama penuh anda:")
    orders[message.chat.id] = {"status": "waiting_name"}

# Simpan nama pelanggan
@bot.message_handler(func=lambda message: orders.get(message.chat.id, {}).get("status") == "waiting_name")
def save_name(message):
    orders[message.chat.id]["name"] = message.text
    orders[message.chat.id]["status"] = "waiting_document"
    bot.send_message(message.chat.id, "Sekarang sila hantar dokumen atau gambar untuk cetakan.")

# Terima dokumen
@bot.message_handler(content_types=['document', 'photo'])
def receive_document(message):
    user_id = message.chat.id
    if user_id not in orders or "name" not in orders[user_id]:
        bot.send_message(user_id, "Sila mulakan dengan /start dahulu.")
        return
    
    order_number = len(orders)  # Nombor giliran
    orders[user_id]["order_number"] = order_number
    orders[user_id]["status"] = "waiting_payment"

    # Hantar ke admin group
    bot.send_message(GROUP_ID, f"📌 **Pesanan Baru #{order_number}**\nNama: {orders[user_id]['name']}\nUser ID: {user_id}")
    if message.content_type == 'document':
        bot.forward_message(GROUP_ID, user_id, message.document.file_id)
    elif message.content_type == 'photo':
        bot.forward_message(GROUP_ID, user_id, message.photo[-1].file_id)

    bot.send_message(user_id, "Sila muat naik bukti pembayaran.")

# Terima bukti pembayaran
@bot.message_handler(content_types=['photo'], func=lambda message: orders.get(message.chat.id, {}).get("status") == "waiting_payment")
def receive_payment_proof(message):
    user_id = message.chat.id
    orders[user_id]["status"] = "pending_approval"

    # Hantar ke admin untuk pengesahan
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("✅ Sahkan", callback_data=f"confirm_{user_id}"))
    bot.forward_message(GROUP_ID, user_id, message.photo[-1].file_id)
    bot.send_message(GROUP_ID, f"📢 **Sahkan Pembayaran untuk Order #{orders[user_id]['order_number']}**", reply_markup=markup)

    bot.send_message(user_id, "Bukti pembayaran diterima. Admin akan menyemak dan mengesahkan pesanan anda.")

# Admin sahkan cetakan
@bot.callback_query_handler(func=lambda call: call.data.startswith("confirm_"))
def confirm_order(call):
    user_id = int(call.data.split("_")[1])
    if call.from_user.id in ADMIN_IDS and user_id in orders:
        orders[user_id]["status"] = "approved"

        # Hantar butang kemaskini status kepada admin
        markup = InlineKeyboardMarkup()
        markup.add(
            InlineKeyboardButton("✅ Cetakan Siap", callback_data=f"done_{user_id}"),
            InlineKeyboardButton("❌ Cetakan Belum Siap", callback_data=f"not_done_{user_id}")
        )
        bot.send_message(GROUP_ID, f"Admin, sila kemaskini status cetakan untuk Order #{orders[user_id]['order_number']}.", reply_markup=markup)
        bot.send_message(user_id, "✅ Pesanan anda telah disahkan dan sedang dicetak.")
        bot.answer_callback_query(call.id, "Pesanan telah disahkan!")

# Admin kemaskini status cetakan
@bot.callback_query_handler(func=lambda call: call.data.startswith("done_") or call.data.startswith("not_done_"))
def update_print_status(call):
    user_id = int(call.data.split("_")[1])
    if call.from_user.id in ADMIN_IDS and user_id in orders:
        status_message = "✅ Cetakan anda telah siap! Sila ambil di lokasi yang ditetapkan." if call.data.startswith("done_") else "❌ Cetakan anda masih belum siap. Sila tunggu."
        bot.send_message(user_id, status_message)
        bot.send_message(GROUP_ID, f"Status pesanan #{orders[user_id]['order_number']} dikemas kini.")
        orders[user_id]["status"] = "completed" if call.data.startswith("done_") else "pending"

# Pelanggan semak status pesanan
@bot.message_handler(commands=['status'])
def check_status(message):
    user_id = message.chat.id
    if user_id in orders:
        status_map = {
            "waiting_name": "Sila masukkan nama.",
            "waiting_document": "Sila hantar dokumen atau gambar.",
            "waiting_payment": "Sila muat naik bukti pembayaran.",
            "pending_approval": "Bukti pembayaran sedang disemak oleh admin.",
            "approved": "Pesanan sedang dicetak.",
            "pending": "Cetakan belum siap.",
            "completed": "Cetakan sudah siap! Sila ambil."
        }
        bot.send_message(user_id, f"📌 **Status Pesanan Anda:** {status_map.get(orders[user_id]['status'], 'Tidak Diketahui')}")
    else:
        bot.send_message(user_id, "Anda belum menghantar sebarang pesanan.")

# Admin boleh hantar mesej kepada pelanggan
@bot.message_handler(commands=['chat'])
def chat_with_user(message):
    if message.chat.id in ADMIN_IDS:
        bot.send_message(message.chat.id, "Gunakan format: `ID_PELANGGAN:Mesej` untuk menghantar mesej.")
    else:
        bot.send_message(message.chat.id, "Anda bukan admin!")

@bot.message_handler(func=lambda message: ':' in message.text and message.chat.id in ADMIN_IDS)
def send_admin_message(message):
    try:
        user_id, text = message.text.split(':', 1)
        user_id = int(user_id.strip())
        bot.send_message(user_id, f"📢 **Mesej dari Admin:** {text.strip()}")
        bot.send_message(message.chat.id, "Mesej dihantar kepada pelanggan!")
    except Exception as e:
        bot.send_message(message.chat.id, f"Ralat: {e}")

bot.polling(none_stop=True)


