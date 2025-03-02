import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

TOKEN = "7964541493:AAEi8S448XgM0S2Xz27fWJ9h6G8f-SFy6Nw"
ADMIN_CHAT_ID = "-1002238456592"  # Gantikan dengan ID grup admin
bot = telebot.TeleBot(TOKEN)

# Simpan maklumat pelanggan
print_requests = {}
customer_chat = {}
queue_number = 1

def generate_order_summary(user_id):
    req = print_requests.get(user_id, {})
    return (f"🖨 *Cetakan Baru*
Nombor Giliran: {req.get('queue_number', '-')}
Nama: {req.get('name', '-')}
Kelas: {req.get('class', '-')}
Jenis: {req.get('color', '-')}"
    )

def admin_keyboard(user_id):
    keyboard = InlineKeyboardMarkup()
    keyboard.row(
        InlineKeyboardButton("✅ Cetakan Siap", callback_data=f"done_{user_id}"),
        InlineKeyboardButton("❌ Cetakan Belum Siap", callback_data=f"not_done_{user_id}")
    )
    keyboard.row(
        InlineKeyboardButton("💬 Hubungi Pelanggan", callback_data=f"chat_{user_id}")
    )
    return keyboard

@bot.message_handler(commands=['start'])
def start(message):
    global queue_number
    user_id = message.chat.id
    bot.send_message(user_id, "Selamat datang ke servis printing BWP PDRM Kulim!")
    print_requests[user_id] = {"queue_number": queue_number}
    queue_number += 1
    bot.send_message(user_id, "Sila masukkan nama anda.")

@bot.message_handler(func=lambda message: message.chat.id in print_requests and 'name' not in print_requests[message.chat.id])
def get_name(message):
    user_id = message.chat.id
    print_requests[user_id]['name'] = message.text
    bot.send_message(user_id, "Masukkan kelas anda.")

@bot.message_handler(func=lambda message: message.chat.id in print_requests and 'class' not in print_requests[message.chat.id])
def get_class(message):
    user_id = message.chat.id
    print_requests[user_id]['class'] = message.text
    bot.send_message(user_id, "Warna atau hitam putih? (Tulis 'Color' atau 'B/W')")

@bot.message_handler(func=lambda message: message.chat.id in print_requests and 'color' not in print_requests[message.chat.id])
def get_color(message):
    user_id = message.chat.id
    print_requests[user_id]['color'] = message.text
    bot.send_message(user_id, "Hantar dokumen atau gambar untuk dicetak.")

@bot.message_handler(content_types=['document', 'photo'])
def receive_document(message):
    user_id = message.chat.id
    if user_id in print_requests:
        bot.send_message(user_id, "Sila hantar bukti pembayaran.")

@bot.message_handler(content_types=['photo'])
def receive_payment(message):
    user_id = message.chat.id
    if user_id in print_requests and 'payment' not in print_requests[user_id]:
        print_requests[user_id]['payment'] = True
        summary = generate_order_summary(user_id)
        bot.send_message(user_id, "Permintaan anda telah dihantar kepada admin!")
        bot.send_message(ADMIN_CHAT_ID, summary, reply_markup=admin_keyboard(user_id))
    else:
        bot.send_message(user_id, "Bukti pembayaran telah dihantar sebelum ini.")

@bot.callback_query_handler(func=lambda call: call.data.startswith('done_') or call.data.startswith('not_done_'))
def update_status(call):
    user_id = int(call.data.split('_')[1])
    status = "Siap!" if call.data.startswith('done_') else "Belum Siap."
    bot.send_message(user_id, f"Status cetakan anda: {status}")
    bot.answer_callback_query(call.id, "Status dikemaskini.")

@bot.callback_query_handler(func=lambda call: call.data.startswith('chat_'))
def contact_customer(call):
    user_id = int(call.data.split('_')[1])
    customer_chat[call.message.chat.id] = user_id
    bot.send_message(call.message.chat.id, "Anda kini boleh menghantar mesej kepada pelanggan.")
    bot.answer_callback_query(call.id)

@bot.message_handler(func=lambda message: message.chat.id in customer_chat)
def relay_message_to_customer(message):
    user_id = customer_chat[message.chat.id]
    bot.send_message(user_id, f"📩 Admin: {message.text}")

bot.polling()

