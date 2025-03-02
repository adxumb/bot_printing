import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# Bahagian untuk letak ID Admin dan ID Group
ADMIN_IDS = [1631295416]  # Ganti dengan ID admin sebenar
GROUP_ID = -1002238456592  # Ganti dengan ID group sebenar

bot = telebot.TeleBot("7964541493:AAEi8S448XgM0S2Xz27fWJ9h6G8f-SFy6Nw")

# Fungsi untuk hantar mesej ke pelanggan tanpa dedahkan identiti admin
def send_message_to_user(user_id, message):
    try:
        bot.send_message(user_id, message)
    except Exception as e:
        print(f"Gagal hantar mesej ke {user_id}: {e}")

# Fungsi untuk sahkan cetakan
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
        send_message_to_user(user_id, text.strip())
        bot.send_message(message.chat.id, "Mesej dihantar kepada pelanggan!")
    except Exception as e:
        bot.send_message(message.chat.id, f"Ralat: {e}")

bot.polling(none_stop=True)


