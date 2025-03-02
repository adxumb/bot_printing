import telebot
from telebot.types import InputMediaPhoto

TOKEN = "7964541493:AAEi8S448XgM0S2Xz27fWJ9h6G8f-SFy6Nw"
GROUP_ID = -1002238456592  # Gantikan dengan ID kumpulan anda

bot = telebot.TeleBot(TOKEN)
user_data = {}  # Simpan data pengguna sementara

# 🟢 Mula Bot
@bot.message_handler(commands=['start'])
def start_handler(message):
    user_id = message.chat.id
    user_data[user_id] = {"step": 1}
    bot.send_message(user_id, "👋 Selamat datang ke Bot Printing! Sila berikan maklumat satu per satu.\n\n📚 Kelas anda?")

# 📝 Proses Input Pengguna
@bot.message_handler(func=lambda message: message.chat.id in user_data and "step" in user_data[message.chat.id])
def handle_user_input(message):
    user_id = message.chat.id
    step = user_data[user_id]["step"]

    if step == 1:
        user_data[user_id]["kelas"] = message.text
        user_data[user_id]["step"] = 2
        bot.send_message(user_id, "🧑‍🎓 Nama anda?")

    elif step == 2:
        user_data[user_id]["nama"] = message.text
        user_data[user_id]["step"] = 3
        bot.send_message(user_id, "🎨 Warna cetakan? (Hitam Putih / Berwarna)")

    elif step == 3:
        user_data[user_id]["warna"] = message.text
        user_data[user_id]["step"] = 4
        bot.send_message(user_id, "📝 Nota tambahan? (Jika tiada, taip 'Tiada')")

    elif step == 4:
        user_data[user_id]["nota"] = message.text
        user_data[user_id]["step"] = 5
        bot.send_message(user_id, "📄 Hantar fail atau gambar yang ingin dicetak.")

# 📤 Terima Dokumen/Gambar
@bot.message_handler(content_types=['document', 'photo'])
def handle_file(message):
    user_id = message.chat.id
    if user_id not in user_data or user_data[user_id].get("step") != 5:
        bot.send_message(user_id, "⚠️ Sila isi maklumat dahulu sebelum menghantar fail.")
        return

    # Hantar ke group printing
    caption = (f"🖨 **Permintaan Cetakan Baru!**\n"
               f"👤 Nama: {user_data[user_id]['nama']}\n"
               f"🏫 Kelas: {user_data[user_id]['kelas']}\n"
               f"🎨 Warna: {user_data[user_id]['warna']}\n"
               f"📝 Nota: {user_data[user_id]['nota']}")

    if message.content_type == "document":
        bot.send_document(GROUP_ID, message.document.file_id, caption=caption, parse_mode="Markdown")
    elif message.content_type == "photo":
        bot.send_photo(GROUP_ID, message.photo[-1].file_id, caption=caption, parse_mode="Markdown")

    bot.send_message(user_id, "✅ Fail anda telah dihantar untuk cetakan! 🖨")
    del user_data[user_id]  # Padam data selepas dihantar

# ❌ Batal Permintaan
@bot.message_handler(commands=['batal'])
def batal_handler(message):
    user_id = message.chat.id
    if user_id in user_data:
        del user_data[user_id]
        bot.send_message(user_id, "❌ Permintaan anda telah dibatalkan.")
    else:
        bot.send_message(user_id, "⚠️ Anda tiada permintaan yang sedang berjalan.")

# 🔄 Jalankan bot
print("Bot sedang berjalan...")
bot.infinity_polling()
