from dotenv import load_dotenv
import telebot
import os
from telebot.types import ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
from database import *
import schedule
import time
import threading

load_dotenv()

TOKEN = os.getenv('BOT_TOKEN')
bot = telebot.TeleBot(token=TOKEN)

cashe = []
reminder_cashe = []




#buttons
reply_keyboard = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)
reply_keyboard.add(
    'Add a new word', 'Check your knowledge'
)



#START
@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(
        message.chat.id,
        f"Hello {message.from_user.first_name}!\n\nI was created to help people to learn English words. My method is based on a Ebbinghaus forgetting curve.\n\nIf you want to get an instruction of using, just write /help",
        reply_markup=reply_keyboard
    )

#HELP
@bot.message_handler(commands=['help'])
def help(message):
    bot.send_message(message.chat.id, "There is no instruction yet.\n\n/start - start a bot", reply_markup=reply_keyboard)



#adding a word
def process_word(message):
    cashe.append(message.text)
    bot.send_message(message.chat.id, "Now write a translation in your native language")
    bot.register_next_step_handler(message, process_translation)

def process_translation(message):
    global cashe
    cashe.append(message.text)
    add_new_word(cashe, message.chat.id)
    cashe = []
    bot.send_message(message.chat.id, "Great. I memorized your word.\n\nIf you want to see the content of your vocabulary, just write /voc")



#VOC
@bot.message_handler(commands='voc')
def show_vocabulary(message):
    if all_the_words() == []: 
        bot.send_message(
            message.chat.id,
            "There's no words yet.\n\nIf you want to add words, click to a button below.",
            reply_markup=reply_keyboard
            )
    else: 
        content = ''
        for el in all_the_words():
            content += f'{el[0]}. <b>{el[2]}</b> — {el[3]}\n'
        bot.send_message(
            message.chat.id, f"Here's your vocabulary:\n\n{content}", reply_markup=reply_keyboard, parse_mode="HTML"
            )



# keyboard buttons and msg processing
@bot.message_handler(func=lambda message: True)
def check_keyboard_button(message):
    if message.text == 'Add a new word':
        bot.reply_to(message, "Send your word in English")
        bot.register_next_step_handler(message, process_word)

    elif message.text == 'Check your knowledge':
        bot.reply_to(message, "Still in development...")

    else:
        inline_button_agree = InlineKeyboardButton(text='Yes', callback_data=f'agr:{message.text}')
        inline_button_refuse = InlineKeyboardButton(text='Hell, no', callback_data=f'ref:')
        inline_keyboard_agree_or_refuse = InlineKeyboardMarkup(row_width=2)
        inline_keyboard_agree_or_refuse.add(inline_button_agree, inline_button_refuse)
        bot.send_message(
            message.chat.id,
            f"Do you want to add this word to your vocabulary — <b>{message.text}</b>?",
            reply_markup=inline_keyboard_agree_or_refuse, parse_mode="HTML"
            )
        




@bot.callback_query_handler(func=lambda call: call.data[0:3] == 'agr' or call.data[0:3]=='ref')
def check_inline_buttons_agree_or_refuse(call):
    action, word = call.data.split(':')
    bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)

    if action == 'agr':
        cashe.append(word)
        bot.send_message(call.message.chat.id, "Now write a translation in your native language")
        bot.register_next_step_handler(call.message, process_translation)

    else:
        bot.send_message(call.message.chat.id, 'OK 👌')






# REMINDER
def send_word_repetition():
    now = datetime.now()

    for w in all_the_words():
        if now >= datetime.fromisoformat(w[5]) and w[0] not in reminder_cashe:

            inline_button_yes = InlineKeyboardButton(text='✅I remember that', callback_data=f'cor:{w[0]}')
            inline_button_no = InlineKeyboardButton(text='🔁Need to repeat', callback_data=f'rep:{w[0]}')
            inline_keyboard_yes_or_no = InlineKeyboardMarkup(row_width=2)
            inline_keyboard_yes_or_no.add(inline_button_yes, inline_button_no)

            bot.send_message(
                w[1], 
                f"⏰It's time to repeat.\n\n<b>{w[2]}</b> — {telebot.formatting.hspoiler(w[3])}", 
                parse_mode='HTML',
                reply_markup=inline_keyboard_yes_or_no
                )
            
            reminder_cashe.append(w[0])



# inline buttons request
@bot.callback_query_handler(func=lambda call: call.data[0:3]=='cor' or call.data[0:3]=='rep')
def check_inline_buttons_correct_or_repeat(call):
    action, i_d = call.data.split(':')
    current_step = get_from_db(i_d, 4)

    bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
    reminder_cashe.remove(int(i_d))

    if action == 'cor':
        db_change_step_and_next_time(i_d, current_step+1)
        bot.answer_callback_query(call.id, "Well done!")
        bot.send_message(call.message.chat.id, f'Great! The next repeating will be in {FORGETTING_CURVE_TIME[current_step+1]}.')
    
    else:
        bot.answer_callback_query(call.id, "It's a path of mastery")

        if current_step>0:
            db_change_step_and_next_time(i_d, current_step-1)
            bot.send_message(call.message.chat.id, f"OK, I'll remind you in {FORGETTING_CURVE_TIME[current_step-1]} to repeat this word again.")
        else:
            db_change_step_and_next_time(i_d, current_step)
            bot.send_message(call.message.chat.id, f"OK, I'll remind you in {FORGETTING_CURVE_TIME[current_step]} to repeat this word again.")



def run_scheduler():
    schedule.every(1).minute.do(send_word_repetition)

    while True:
        schedule.run_pending()
        time.sleep(60)



threading.Thread(target=run_scheduler, daemon=True).start()   # Let bot.polling() and scheduler run simultaneously.

bot.polling()