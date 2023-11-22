import telebot
from datetime import datetime, timedelta

TOKEN = "YOUR_TELEGRAM_BOT_TOKEN"
CLIENT_CHAT_ID = "CLIENT_CHAT_ID"
MANAGER_CHAT_ID = "MANAGER_CHAT_ID"
LEADER_CHAT_ID = "LEADER_CHAT_ID"

# Создаем экземпляр бота
bot = telebot.TeleBot(TOKEN)

# Список конфликтных слов
NEGATIVE_WORDS = ["негативное слово1", "негативное слово2", "негативное слово3"]

# Список для хранения задач на встречи с клиентом
meetings = []


def get_last_message_time(CLIENT_CHAT_ID):
    pass


@bot.message_handler(func=lambda message: True)
def handle_message(message):
    # Проверяем, является ли отправитель клиентом
    if str(message.chat.id) == CLIENT_CHAT_ID:
        current_time = datetime.now()
        # Получаем время последнего сообщения от клиента
        last_message_time = get_last_message_time(CLIENT_CHAT_ID)

        # Проверяем, прошло ли N часов с последнего сообщения
        if (current_time - last_message_time).total_seconds() > 5 * 3600:
            # Отправляем уведомление ответственному менеджеру о пропущенном сообщении
            bot.send_message(chat_id=MANAGER_CHAT_ID, text="Клиент написал, но вы так ничего и не ответили!")

    # Проверяем, является ли отправитель ответственным менеджером
    elif str(message.chat.id) == MANAGER_CHAT_ID:
        # Проверяем, наличие конфликтных слов в сообщении
        if any(word in message.text.lower() for word in NEGATIVE_WORDS):
            # Отправляем уведомление руководителю о конфликте
            bot.send_message(chat_id=LEADER_CHAT_ID,
                             text="Обнаружен конфликт в переписке с клиентом. Пожалуйста, обратите внимание и примите меры по его разрешению.")


@bot.message_handler(commands=['set_meeting'])
def set_meeting(message):
    # Получаем дату и время встречи и тему звонка
    # Пример команды: /set_meeting 2022-01-01 15:00 Встреча с клиентом
    command_parts = message.text.split()
    date_str = command_parts[1]
    time_str = command_parts[2]
    meeting_topic = ' '.join(command_parts[3:])

    # Преобразуем строку с датой и временем в объект datetime
    meeting_date = datetime.strptime(date_str + " " + time_str, "%Y-%m-%d %H:%M")

    # Добавляем задачу на встречу в список
    meetings.append({"date": meeting_date, "topic": meeting_topic, "chat_id": message.chat.id})

    # Отправляем уведомление о создании задачи
    bot.send_message(chat_id=message.chat.id, text="Задача на встречу создана!")


def check_meetings():
    current_time = datetime.now()
    for meeting in meetings:
        # Проверяем, осталось ли 24 или 2 часа до встречи
        if (meeting["date"] - current_time) == timedelta(hours=24):
            # Отправляем напоминание за 24 часа
            bot.send_message(chat_id=meeting["chat_id"],
                             text=f"Напоминание для встречи '{meeting['topic']}' через 24 часа!")
        elif (meeting["date"] - current_time) == timedelta(hours=2):
            # Отправляем напоминание за 2 часа
            bot.send_message(chat_id=meeting["chat_id"],
                             text=f"Напоминание для встречи '{meeting['topic']}' через 2 часа!")


# Запускаем проверку встреч каждые 10 минут
bot.polling(none_stop=True, interval=600)

# Получаем тему звонка
meeting_topic = ' '.join(command_parts[2:])

# Добавляем встречу в список meetings
meetings.append({"datetime": meeting_datetime, "topic": meeting_topic})

# Отправляем подтверждение клиенту
bot.send_message(chat_id=CLIENT_CHAT_ID, text=f"Встреча назначена на {meeting_datetime.strftime('%Y-%m-%d %H:%M')}. Тема: {meeting_topic}")


# Фильтруем встречи, оставляя только будущие
upcoming_meetings = [m for m in meetings if m["datetime"] > current_time]

# Проверяем, есть ли будущие встречи
if upcoming_meetings:
    # Формируем сообщение со списком встреч
    response = "Ближайшие встречи:\n"
    for meeting in upcoming_meetings:
        response += f"- {meeting['datetime'].strftime('%Y-%m-%d %H:%M')}: {meeting['topic']}\n"
else:
    response = "У вас нет запланированных встреч."

# Отправляем сообщение с списком встреч
bot.send_message(chat_id=MANAGER_CHAT_ID, text=response)