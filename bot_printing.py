import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# Bahagian untuk letak ID Admin dan ID Group
ADMIN_IDS = [1631295416]  # Ganti dengan ID admin sebenar
GROUP_ID = -1002238456592  # Ganti dengan ID group sebenar

bot = telebot.TeleBot("7964541493:AAEi8S448XgM0S2Xz27fWJ9h6G8f-SFy6Nw")  # Ganti dengan token bot sebenar

# Simpan status cetakan untuk elak admin tekan dua kali
print_status = {}

# Fungsi untuk hantar mesej ke pelanggan tanpa dedahkan identiti admin
def send_message_to_user(user_id, message):
    try:
        bot.send_message(user_id, message)
    except Exception as e:
        print(f"Gagal hantar mesej ke {user_id}: {e}")

# ✅ /start untuk pastikan bot hidup
@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(
        message.chat.id, 
        "✅ *Bot Printing Aktif!*\n\n"
        "Anda boleh:\n"
        "- Hantar dokumen untuk cetak 📄\n"
        "- Semak status cetakan 🖨️\n"
        "- Admin boleh sahkan cetakan ✅",
        parse_mode="Markdown"
    )

# ✅ Fungsi untuk sahkan cetakan (butang boleh tekan sekali sahaja)
@bot.message_handler(commands=['confirm'])
def confirm_print(message):
    if message.chat.id in ADMIN_IDS:
        if message.chat.id in print_status and print_status[message.chat.id]:
            bot.send_message(message.chat.id, "⚠️ Anda sudah sahkan cetakan sebelum ini.")
            return
        
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("✅ Cetakan Siap", callback_data="print_done"))
        markup.add(InlineKeyboardButton("❌ Cetakan Belum Siap", callback_data="print_not_done"))
        bot.send_message(GROUP_ID, "📢 *Admin, sila pilih status cetakan:*", reply_markup=markup, parse_mode="Markdown")
        
        # Tandakan status dah sahkan
        print_status[message.chat.id] = True
    else:
        bot.send_message(message.chat.id, "⚠️ Anda bukan admin!")

# ✅ Fungsi callback untuk status cetakan
@bot.callback_query_handler(func=lambda call: call.data in ["print_done", "print_not_done"])
def handle_print_status(call):
    status = "✅ *Cetakan telah siap!*" if call.data == "print_done" else "❌ *Cetakan belum siap!*"
    bot.send_message(GROUP_ID, status, parse_mode="Markdown")
    bot.answer_callback_query(call.id, "✅ Status dikemas kini!")

# ✅ Fungsi admin untuk chat dengan pelanggan
@bot.message_handler(commands=['chat'])
def chat_with_user(message):
    if message.chat.id in ADMIN_IDS:
        bot.send_message(message.chat.id, "📩 Sila masukkan ID pelanggan & mesej dalam format:\n`ID_PELANGGAN: Mesej anda`", parse_mode="Markdown")
    else:
        bot.send_message(message.chat.id, "⚠️ Anda bukan admin!")

# ✅ Admin boleh hantar mesej kepada pelanggan secara peribadi
@bot.message_handler(func=lambda message: ':' in message.text and message.chat.id in ADMIN_IDS)
def send_admin_message(message):
    try:
        user_id, text = message.text.split(':', 1)
        user_id = user_id.strip()
        text = text.strip()

        if not user_id.isdigit():
            bot.send_message(message.chat.id, "⚠️ *ID pelanggan mesti nombor!*", parse_mode="Markdown")
            return
        
        send_message_to_user(int(user_id), text)
        bot.send_message(message.chat.id, "✅ *Mesej dihantar kepada pelanggan!*", parse_mode="Markdown")
    except Exception as e:
        bot.send_message(message.chat.id, f"⚠️ *Ralat:* {e}", parse_mode="Markdown")

# ✅ Debugging - Pastikan bot berjalan dengan betul
print(f"🔹 Bot sedang berjalan dengan token: {bot.token}")
print(f"🔹 Admin ID: {ADMIN_IDS}, Group ID: {GROUP_ID}")

# ✅ Pastikan bot polling dengan betul
bot.infinity_polling(timeout=10, long_polling_timeout=5)


