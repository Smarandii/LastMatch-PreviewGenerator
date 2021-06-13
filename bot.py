import os

import telebot
import preview_gen

token = "1852831543:AAFDNO9fMNk6qR6G_U0ejDW7Ba7ZjvJtwEs"
bot = telebot.TeleBot(token)


def clear_all():
    for root, dir, files in os.walk("previews"):
        for file in files:
            file_path = os.path.join(root, file)
            if ".png" in file or "preview" in file:
                os.remove(file_path)


@bot.message_handler(commands=["start"])
def start_command(message):
    bot.send_message(message.chat.id, "Send me some previews in an album!")


@bot.message_handler(content_types=["photo"])
def get_photos(message):
    counter = 1
    try:
        for photo_index in range(0, len(message.photo)):
            bot.send_chat_action(message.chat.id, 'typing')
            if counter % 4 == 0:
                file_id_info = bot.get_file(message.photo[photo_index].file_id)
                downloaded_file = bot.download_file(file_id_info.file_path)
                print(file_id_info.file_path)
                with open(os.path.join("previews", f'{message.photo[photo_index].file_id}.png'), 'wb') as new_file:
                    bot.send_chat_action(message.chat.id, 'typing')
                    new_file.write(downloaded_file)
            counter += 1
        bot.send_message(message.chat.id, "Preview downloaded and ready! Type /generate command to proceed.")
    except Exception as ex:
        bot.send_message(message.chat.id, f"[!] error - {str(ex)}")


@bot.message_handler(commands=["generate"])
def generate_command(message):
    gen = preview_gen.PreviewGenerator()
    gen.run("previews")
    bot.send_chat_action(message.chat.id, 'typing')
    try:
        bot.send_photo(message.chat.id, open(os.path.join("previews", "preview.png"), 'rb'))
        clear_all()
    except Exception as e:
        print(e.args)
        bot.send_message(message.chat.id, "Failed to generate preview...")


if __name__ == "__main__":
    bot.polling()
