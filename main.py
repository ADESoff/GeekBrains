import telebot
from datetime import datetime, timedelta


def get_manager_chat_id(message):
    """ Получение ID пользователя из ответа на сообщение """
    # Возвращает ID пользователя
    return message.reply_to_message.from_user.id


# Создаем бота и указываем токен
bot = telebot.TeleBot('6724379265:AAFuMMpi5E3Zppg1uUsLUS6TRoU4frtKd8o')

# Задаем время ожидания ответа и адресата для уведомления руководителя
waiting_time = timedelta(hours=24)
supervisor_chat_id = '1172183750'

# Словарь для хранения последнего сообщения от клиента для каждого менеджера
last_message = {}


# Обработка команды /start
@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, 'Привет! Я бот для анализа переписки с клиентами.')


# Обработка сообщений от клиентов
@bot.message_handler(func=lambda message: message.chat.type == 'private')
def handle_client_message(message):
    # Получаем ID чата клиента и ответственного менеджера
    client_chat_id = message.chat.id
    manager_chat_id = get_manager_chat_id(message)

    # Запоминаем последнее сообщение от клиента
    last_message[manager_chat_id] = message

    # Определяем время ожидания ответа
    waiting_time_exceeded = datetime.now() - message.reply_to_message.date > waiting_time

    if waiting_time_exceeded:
        # Отправляем уведомление ответственному менеджеру
        bot.send_message(manager_chat_id, 'Вы не ответили на сообщение клиента!')

        # Отправляем уведомление руководителю
        bot.send_message(supervisor_chat_id, 'Менеджер {} не ответил на сообщение клиента!'.format(manager_chat_id))

    # Анализируем переписку на предмет негатива
    if 'негативное слово' in message.text:
        # Отправляем уведомление руководителю о конфликте
        bot.send_message(supervisor_chat_id,
                         'Обнаружен конфликт клиента {} с менеджером {}!'.format(client_chat_id, manager_chat_id))


# Обработка команды для назначения встречи
@bot.message_handler(commands=['meeting'])
def schedule_meeting(message):
    # Получаем ID чата менеджера и назначаемую дату-время и тему звонка
    manager_chat_id = message.from_user.id
    meeting_data = message.text.split(' ', 1)[1]

    # Проверяем, что есть последнее сообщение от клиента
    if manager_chat_id in last_message:
        # Получаем данные для напоминания
        task_date_time, task_description = meeting_data.split(',', 1)

        # Парсим дату и время задачи
        task_date_time = datetime.strptime(task_date_time.strip(), '%Y-%m-%d %H:%M')

        # Запланировать напоминания
        reminders = [task_date_time - timedelta(hours=24), task_date_time - timedelta(hours=2)]
        for reminder in reminders:
            bot.send_message(manager_chat_id, 'Напоминание! Встреча "{}" через {}'.format(task_description.strip(),
                                                                                          timedelta_to_string(
                                                                                              task_date_time - reminder)))


# Функция для преобразования timedelta в строку
def timedelta_to_string(td):
    days = td.days
    hours = td.seconds // 3600
    minutes = (td.seconds % 3600) // 60
    seconds = td.seconds % 60
    return '{} дней, {} часов, {} минут, {} секунд'.format(days, hours, minutes, seconds)


bot.infinity_polling()
