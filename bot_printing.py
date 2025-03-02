import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

TOKEN = "YOUR_BOT_TOKEN"
GROUP_ID = "YOUR_GROUP_ID"
ADMIN_ID = "YOUR_ADMIN_ID"

bot = telebot.TeleBot(TOKEN)

users = {}

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "Selamat datang ke bot printing! Sila masukkan nama anda.")
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
    try:
        copies = int(message.text)
        users[message.chat.id]['copies'] = copies
        price = copies * (2.00 if users[message.chat.id]['color'] == 'color' else 0.50)
        users[message.chat.id]['price'] = price
        bot.send_message(message.chat.id, f"Harga: RM{price:.2f}. Sila hantar gambar bukti pembayaran.")
    except ValueError:
        bot.send_message(message.chat.id, "Masukkan nombor yang sah.")

@bot.message_handler(content_types=['photo'])
def receive_payment_proof(message):
    if message.chat.id in users and 'price' in users[message.chat.id]:
        users[message.chat.id]['payment_proof'] = message.photo[-1].file_id
        caption = (f"Permintaan baru:\nNama: {users[message.chat.id]['name']}\n"
                   f"Kelas: {users[message.chat.id]['class']}\nSalinan: {users[message.chat.id]['copies']}\n"
                   f"Jenis: {'Warna' if users[message.chat.id]['color'] == 'color' else 'Hitam Putih'}\n"
                   f"Harga: RM{users[message.chat.id]['price']:.2f}")
        bot.send_photo(GROUP_ID, users[message.chat.id]['payment_proof'], caption=caption,
                       reply_markup=confirm_markup(message.chat.id))
        bot.send_message(message.chat.id, "Bukti bayaran telah dihantar kepada admin untuk pengesahan.")
    else:
        bot.send_message(message.chat.id, "Hantar maklumat cetakan dahulu sebelum menghantar bukti pembayaran.")

def confirm_markup(user_id):
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("Sahkan Cetakan", callback_data=f'confirm_{user_id}'))
    return markup

@bot.callback_query_handler(func=lambda call: call.data.startswith('confirm_'))
def confirm_printing(call):
    user_id = int(call.data.split('_')[1])
    if user_id in users:
        bot.send_message(user_id, "Cetakan anda telah disahkan oleh admin dan sedang diproses.")
        bot.send_message(GROUP_ID, f"Cetakan untuk {users[user_id]['name']} telah disahkan.")
    bot.answer_callback_query(call.id)

bot.polling(none_stop=True)

