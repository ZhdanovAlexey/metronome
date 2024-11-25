import telebot
from telebot import types

# Замените на ваш токен
TOKEN = '8128618821:AAEVXwdLHufalKA3IhaFHaZX20rnDezcoIA'
# Замените на URL вашей страницы на GitHub Pages
GITHUB_PAGES_URL = 'https://zhdanovalexey.github.io/metronome/'

bot = telebot.TeleBot(TOKEN)

# Словарь для хранения временного состояния пользователей
user_states = {}

def create_tempo_keyboard():
    keyboard = types.ReplyKeyboardMarkup(row_width=5, resize_keyboard=True)
    tempo_buttons = [str(i) for i in range(5, 51, 5)]
    rows = [tempo_buttons[i:i+5] for i in range(0, len(tempo_buttons), 5)]
    for row in rows:
        keyboard.add(*row)
    keyboard.add("Stop")
    return keyboard

def create_duration_keyboard():
    keyboard = types.ReplyKeyboardMarkup(row_width=3, resize_keyboard=True)
    # Длительности в минутах
    durations = ["1 мин", "2 мин", "3 мин", "5 мин", "7 мин", "10 мин"]
    rows = [durations[i:i+3] for i in range(0, len(durations), 3)]
    for row in rows:
        keyboard.add(*row)
    return keyboard

@bot.message_handler(commands=['start'])
def start(message):
    keyboard = create_tempo_keyboard()
    bot.reply_to(
        message,
        "Привет! Я бот-метроном.\n\n"
        "Выберите темп (ударов в минуту):",
        reply_markup=keyboard
    )
    user_states[message.chat.id] = {'state': 'waiting_for_tempo'}

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    chat_id = message.chat.id
    
    if message.text == "Stop":
        bot.reply_to(message, 
            "Чтобы остановить метроном, нажмите кнопку 'Стоп' на веб-странице или закройте её.")
        return
    
    # Получаем текущее состояние пользователя
    user_state = user_states.get(chat_id, {'state': 'waiting_for_tempo'})
    
    if user_state['state'] == 'waiting_for_tempo':
        try:
            tempo = int(message.text)
            if 5 <= tempo <= 50:
                user_state['tempo'] = tempo
                user_state['state'] = 'waiting_for_duration'
                
                keyboard = create_duration_keyboard()
                bot.reply_to(
                    message,
                    f"Темп установлен: {tempo} BPM\n"
                    f"Теперь выберите длительность подхода (по умолчанию 5 минут):",
                    reply_markup=keyboard
                )
            else:
                bot.reply_to(message, "Пожалуйста, выберите темп от 5 до 50 ударов в минуту")
        except ValueError:
            bot.reply_to(message, "Пожалуйста, выберите темп из предложенных кнопок")
    
    elif user_state['state'] == 'waiting_for_duration':
        try:
            # Извлекаем число минут из текста кнопки
            duration_text = message.text.split()[0]
            duration_minutes = int(duration_text)
            duration_seconds = duration_minutes * 60
            tempo = user_state['tempo']
            
            # Создаем URL с параметрами
            url = f"{GITHUB_PAGES_URL}?bpm={tempo}&duration={duration_seconds}&autostart=true"
            
            keyboard = create_tempo_keyboard()
            bot.reply_to(
                message,
                f"✅ Параметры установлены:\n"
                f"• Темп: {tempo} BPM\n"
                f"• Длительность: {duration_minutes} минут\n\n"
                f"🎵 Нажмите здесь, чтобы запустить метроном:\n{url}\n\n"
                f"Подсказка: Вы можете открыть эту ссылку на любом устройстве!\n\n"
                f"Чтобы начать новый подход, выберите темп:",
                reply_markup=keyboard
            )
            
            # Сбрасываем состояние пользователя
            user_state['state'] = 'waiting_for_tempo'
            
        except (ValueError, IndexError):
            bot.reply_to(message, "Пожалуйста, выберите длительность из предложенных вариантов")
    
    # Сохраняем обновленное состояние
    user_states[chat_id] = user_state

if __name__ == "__main__":
    print("Bot started")
    bot.infinity_polling()