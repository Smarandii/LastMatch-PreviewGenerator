import os
import dotenv
import telebot
import preview_gen

dotenv.load_dotenv('.env')
token = os.environ["API_KEY"]
ADMIN_ID = os.environ["ADMIN_ID"]
PASSWORD = os.environ["PASSWORD"]

bot = telebot.TeleBot(token)


def clear_all(path):
    for root, dir, files in os.walk(path):
        for file in files:
            file_path = os.path.join(root, file)
            if ".png" in file or "preview" in file:
                os.remove(file_path)


def is_authorized(t_id):
    is_authorized = True
    with open(".authorized", "r") as auth:
        for line in auth:
            if str(t_id) in line:
                return is_authorized
    return False


def authorize(t_id):
    with open(".authorized", "a") as auth:
        auth.write('\n')
        auth.write(str(t_id))


@bot.message_handler(commands=["login"])
def start_command(message):
    try:
        if message.text.split(" ")[1] == PASSWORD:
            authorize(message.chat.id)
            bot.send_message(message.chat.id, "Successfully authorized!")
    except Exception:
        bot.send_message(message.chat.id, "Authorization failed!")


@bot.message_handler(commands=["start"])
def start_command(message):
    if is_authorized(message.chat.id):
        bot.send_message(message.chat.id, "Send me some images!")
        print(message.chat.id)
    else:
        bot.send_message(message.chat.id, "Authorization needed to proceed! Use /login [password] to authorize.")


@bot.message_handler(content_types=["photo"])
def get_photos(message):
    if is_authorized(message.chat.id):
        counter = 1
        try:
            os.mkdir(f"{message.chat.id}")
        except FileExistsError:
            pass
        try:
            for photo_index in range(0, len(message.photo)):
                bot.send_chat_action(message.chat.id, 'typing')
                if message.photo[-1] == message.photo[photo_index]:
                    file_id_info = bot.get_file(message.photo[photo_index].file_id)
                    downloaded_file = bot.download_file(file_id_info.file_path)
                    print(file_id_info.file_path)
                    with open(os.path.join(f"{message.chat.id}", f'{message.photo[photo_index].file_id}.png'), 'wb') as new_file:
                        bot.send_chat_action(message.chat.id, 'typing')
                        new_file.write(downloaded_file)
                counter += 1
            bot.reply_to(message, "Preview downloaded and ready! Type /generate command to proceed.")
        except Exception as ex:
            bot.send_message(message.chat.id, f"Something bad just happened. Try /reset command!")
            bot.send_message(ADMIN_ID, f"[!] error - {str(ex)}")
            print(f"[!] error - {str(ex)}")
    else:
        bot.send_message(message.chat.id, "Authorization needed to proceed! Use /login [password] to authorize.")


@bot.message_handler(content_types=["document"])
def get_document(message):
    if is_authorized(message.chat.id):
        try:
            os.mkdir(f"{message.chat.id}")
        except FileExistsError:
            pass
        try:
            bot.send_chat_action(message.chat.id, 'typing')
            file_id_info = bot.get_file(message.document.file_id)
            downloaded_file = bot.download_file(file_id_info.file_path)
            print(file_id_info.file_path)
            with open(os.path.join(f"{message.chat.id}", f'{message.document.file_id}.png'), 'wb') as new_file:
                bot.send_chat_action(message.chat.id, 'typing')
                new_file.write(downloaded_file)
            bot.reply_to(message.chat.id, "Preview downloaded and ready! Type /generate command to proceed.")
        except Exception as ex:
            bot.send_message(message.chat.id, f"Something bad just happened. Try /reset command!")
            bot.send_message(ADMIN_ID, f"[!] error - {str(ex)}")
            print(f"[!] error - {str(ex)}")
    else:
        bot.send_message(message.chat.id, "Authorization needed to proceed! Use /login [password] to authorize.")


@bot.message_handler(commands=["generate"])
def generate_command(message):
    if is_authorized(message.chat.id):
        gen = preview_gen.PreviewGenerator()
        gen.run(f"{message.chat.id}")
        bot.send_chat_action(message.chat.id, 'typing')
        try:
            bot.send_document(message.chat.id, open(os.path.join(f"{message.chat.id}", "preview.png"), 'rb'))
            clear_all(f"{message.chat.id}")
        except Exception as e:
            bot.send_message(ADMIN_ID, f"[!] error - {str(e)}")
            print(f"[!] error - {str(e)}")
            bot.send_message(message.chat.id, "Failed to generate preview...")
    else:
        bot.send_message(message.chat.id, "Authorization needed to proceed! Use /login [password] to authorize.")


@bot.message_handler(commands=["reset"])
def reset(message):
    if is_authorized(message.chat.id):
        try:
            clear_all(f"{message.chat.id}")
        except FileExistsError:
            pass
    else:
        bot.send_message(message.chat.id, "Authorization needed to proceed! Use /login [password] to authorize.")


if __name__ == "__main__":
    try:
        while True:
            bot.polling()
    except Exception as e:
        bot.send_message(ADMIN_ID, f"[!] error - {str(e)}")
