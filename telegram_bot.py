import telebot
import os
from telebot import types
from config import *
from tesseract_vision import *
from funcs import *
from sql import *
from openAI_api import *


bot = telebot.TeleBot(telebot_token)


@bot.message_handler(commands=['start'])
def start(message):
    ### Check user in db and if not = add to db
    user_id = message.chat.id
    db = DataBase(db_name)
    if (not db.user_exists(user_id)):
        try:
            db.add_user(user_id)
            db.my_balance_add_user(user_id)
            db.close()
        except:
            pass
    ## Welcome message
    bot.send_message(message.chat.id, "Hello!\n"
                                      "You can send me a photo with a question or just text, and I will return the solution to this question or task to you.\n"
                                      "However, please remember to top up the balance before making a request ;)\n"
                                      "For further instructions, use the commands:\n"
                                      "/commands - to get a list of available commands\n"
                                      "/menu - to open the menu")


@bot.message_handler(commands=['commands'])
def info(message):
    ### Available project commands
    if message.chat.type == 'private':
        bot.send_message(message.chat.id, "🛠 Available commands:\n"
                                          "/commands - list of all commands\n"
                                          "/menu - active menu\n"
                                          "/get_answer - get an answer to a text question")
    else:
        bot.send_message(message.chat.id, "Sorry, but I only work in private messages.")


@bot.message_handler(commands=['menu'])
def menu(message):
    ### Accessible project menu, with buttons
    if message.chat.type == 'private':
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        send_photo = types.KeyboardButton('📷 Send Photo')
        send_text = types.KeyboardButton('📝 Send Text')
        my_balance = types.KeyboardButton('💰 My Balance')

        markup.add(send_photo, send_text, my_balance)
        bot.send_message(message.chat.id, "☑️ Menu buttons activated ☑️", reply_markup=markup)
    else:
        bot.send_message(message.chat.id, "Sorry, but I only work in private messages.")


@bot.message_handler(commands=['get_answer'])
def get_answer(message):
    if message.chat.type == 'private':
        bot.send_message(message.chat.id, "⏱ Please wait while processing... ⏱")
        text = clean_text(message.text)
        ### Check for len /get_answer text True/False
        if bool(len(text)) == True:
            ### Check for decimal len of text
            if len(text) <= 750:
                ### db payment process
                db = DataBase(db_name)
                user_id = message.chat.id
                if db.my_balance_payment(user_id) == True:
                    bot.send_message(message.chat.id, pay_token_suc)
                    ### Send request to openAI
                    correct_text = text_answer_request(text)
                    ### Send to user answer on his question
                    text_answer = post_text + correct_text
                    bot.send_message(message.chat.id, text_answer)
                    db.close()
                elif db.my_balance_payment(user_id) == False:
                    bot.send_message(message.chat.id, pay_token_decl)
            else:
                bot.send_message(message.chat.id, "⛔️ERROR⛔️\n"
                                                  "Your text has exceeded the allowed word limit.\n"
                                                  f"Set limit is {token_limit} words/per query.")
        else:
            bot.send_message(message.chat.id, "⛔️ERROR⛔️\n"
                                              "You sent an empty message to the request.\n"
                                              "Example:\n"
                                              "/get_answer <your text>")
    else:
        bot.send_message(message.chat.id, "Sorry, but I only work in private messages.")


@bot.message_handler(content_types=['text'])
def bot_send_photo(message):
    if message.chat.type == 'private':
        if message.text == '📷 Send Photo':
            bot.send_message(message.chat.id, "🔹 Send a photo with a clear text of the task on it to the chat ⬇️")
        elif message.text == '📝 Send Text':
            bot.send_message(message.chat.id, "🔹 Send the text of your request to the chat below using this example:\n"
                                              "/get_answer <your text>")
        elif message.text == '💰 My Balance':
            db = DataBase(db_name)
            user_id = message.chat.id
            token = db.my_balance_check(user_id)
            bot.send_message(message.chat.id, "💰 My Balance:\n🔘 {} $TKN".format(token))


@bot.message_handler(content_types=["photo"])
def text_detection(message):
    ### Process message
    if message.chat.type == 'private':
        bot.send_message(message.chat.id, "⏱ Please wait while processing... ⏱")

        ### Check for img size if bigger than limi >>> decline
        if message.photo[-1].file_size <= allow_img_size:
            ### Download photo by file_id
            fileID = message.photo[-1].file_id
            file_info = bot.get_file(fileID)
            downloaded_file = bot.download_file(file_info.file_path)

            ### Image path + random name
            random_file_name = random_img_name()
            image = image_path + random_file_name

            with open(image, 'wb') as new_file:
                new_file.write(downloaded_file)


            ### Tesseract text detection in var text
            text = text_detect(image)

            ### Checking for text detection
            if bool(len(text)) == True:
                try:
                    db = DataBase(db_name)
                    user_id = message.chat.id
                    if db.my_balance_payment(user_id) == True:
                        bot.send_message(message.chat.id, pay_token_suc)
                        ### Send request with text to openAI API
                        correct_text = text_answer_request(text)
                        text_answer = post_text + correct_text
                        ### Send answer text to user
                        bot.send_message(message.chat.id, text_answer)
                        db.close()
                    elif db.my_balance_payment(user_id) == False:
                        bot.send_message(message.chat.id, pay_token_decl)
                except:
                    pass
            ### Delete used photo
            os.remove(image)
        else:
            bot.send_message(message.chat.id, error_too_big_img)
    else:
        bot.send_message(message.chat.id, "Sorry, but I only work in private messages.")


if __name__ == '__main__':
     bot.infinity_polling()
