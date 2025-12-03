from telebot import types
from loader import bot
from states.my_states import SearchStates
from api.api_search import SiteApiInterface
from keyboards.inline import search_with_pagin
from database.history import add_to_search_history, add_to_watch_later
from keyboards.reply.main_keyboard import main_keyboard


def build_film_message(index: int, results: list) -> tuple:
    """
    Формирует текстовое сообщение и URL постера для фильма.

    :param index: Индекс фильма в списке результатов
    :type index: int
    :param results: Список результатов поиска
    :type results: list
    :return: Кортеж из текста сообщения и URL постера
    :rtype: tuple
    """
    film = results[index]

    text = (
        f"🎬 {film['movie_name']} ({film['year']})\n"
        f"⭐ Рейтинг: {film['rating']}\n"
        f"📄 Описание: {film['description'] or 'нет описания'}\n"
        f"🎞 Жанры: {', '.join(film['genres'])}\n"
        f"🔞 {film['age_rating'] or 'нет данных'}"
    )

    poster_url = film.get("poster_url")
    return text, poster_url


# -----------------------------
# Отправка первого фильма
# -----------------------------
def send_film(chat_id: int, user_id: int, index: int) -> None:
    """
    Отправляет сообщение с информацией о фильме.

    :param chat_id: ID чата
    :type chat_id: int
    :param user_id: ID пользователя
    :type user_id: int
    :param index: Индекс фильма в списке
    :type index: int
    """
    with bot.retrieve_data(user_id, chat_id) as data:
        results = data["results"]

    text, poster_url = build_film_message(index, results)
    markup = search_with_pagin.inline_search_keyboard(index, len(results))

    if poster_url:
        bot.send_photo(chat_id, poster_url, caption=text, reply_markup=markup)
    else:
        bot.send_message(chat_id, text, reply_markup=markup)


@bot.message_handler(func=lambda m: m.text == "🔎 Поиск")
def search_movie(message: types.Message) -> None:
    """
    Обработчик выбора поиска по названию.

    Устанавливает состояние и запрашивает название фильма.

    :param message: Сообщение от пользователя
    :type message: types.Message
    """
    bot.delete_state(message.from_user.id, message.chat.id)
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data.clear()
    bot.set_state(message.from_user.id, SearchStates.name, message.chat.id)
    bot.send_message(message.chat.id, "🔎 Введи название фильма:")


@bot.message_handler(state=SearchStates.name)
def get_name(message) -> None:
    """
    Обработчик ввода названия фильма.

    Сохраняет название и запрашивает количество результатов.

    :param message: Сообщение с названием фильма
    """
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data["title"] = message.text
    bot.set_state(message.from_user.id, SearchStates.pages, message.chat.id)
    bot.send_message(message.chat.id, "Сколько результатов отобразить? (1–10)")


@bot.message_handler(state=SearchStates.pages)
def get_amount(message) -> None:
    """
    Обработчик ввода количества результатов.

    Выполняет поиск и показывает первый результат.

    :param message: Сообщение с количеством результатов
    """
    try:
        amount = int(message.text)
        if not (1 <= amount <= 10):
            raise ValueError
    except ValueError:
        bot.send_message(message.chat.id, "Введите число от 1 до 10")
        return

    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        title = data["title"]

    bot.send_message(message.chat.id, f"Ищу '{title}', результаты...")

    results = SiteApiInterface.find_film(title, limit=amount)

    if not results:
        bot.send_message(message.chat.id, f"Фильм '{title}' не найден")
        bot.delete_state(message.from_user.id, message.chat.id)
        return

    add_to_search_history(results)

    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data["results"] = results
        data["index"] = 0

    send_film(chat_id=message.chat.id, user_id=message.from_user.id, index=0)


@bot.callback_query_handler(func=lambda c: c.data and (
        c.data.startswith(("prev_", "next_", "watch_later_")) or c.data == "main_menu"
))
def handle_search_callbacks(call: types.CallbackQuery) -> None:
    """
    Обработчик кнопок пагинации и действий с фильмом.

    :param call: Callback-запрос от кнопки
    :type call: types.CallbackQuery
    """
    bot.answer_callback_query(call.id)
    user_id = call.from_user.id
    chat_id = call.message.chat.id

    with bot.retrieve_data(user_id, chat_id) as data:
        results = data.get("results", [])
        if not results:
            return

    if call.data.startswith("prev_") or call.data.startswith("next_"):
        try:
            new_idx = int(call.data.split("_")[-1])
        except:
            return
        if 0 <= new_idx < len(results):
            with bot.retrieve_data(user_id, chat_id) as data:
                data["index"] = new_idx

            text, poster_url = build_film_message(new_idx, results)
            markup = search_with_pagin.inline_search_keyboard(new_idx, len(results))

            try:
                if call.message.photo:

                    if poster_url:

                        media = types.InputMediaPhoto(poster_url, caption=text)
                        bot.edit_message_media(
                            chat_id=chat_id,
                            message_id=call.message.message_id,
                            media=media,
                            reply_markup=markup
                        )
                    else:

                        bot.delete_message(chat_id, call.message.message_id)
                        bot.send_message(chat_id, text, reply_markup=markup)
                else:

                    if poster_url:

                        bot.delete_message(chat_id, call.message.message_id)
                        bot.send_photo(chat_id, poster_url, caption=text, reply_markup=markup)
                    else:

                        bot.edit_message_text(
                            chat_id=chat_id,
                            message_id=call.message.message_id,
                            text=text,
                            reply_markup=markup
                        )
            except Exception as e:
                print(f"Ошибка редактирования сообщения: {e}")

                bot.delete_message(chat_id, call.message.message_id)
                send_film(chat_id, user_id, new_idx)

    elif call.data.startswith("watch_later_"):
        idx = int(call.data.split("_")[-1])
        movie = results[idx]
        from database.history import add_to_watch_later
        add_to_watch_later(movie)

        try:
            if call.message.photo:
                bot.edit_message_caption(
                    chat_id=chat_id,
                    message_id=call.message.message_id,
                    caption="Фильм добавлен в «Смотреть позже»",
                    reply_markup=None
                )
            else:
                bot.edit_message_text(
                    chat_id=chat_id,
                    message_id=call.message.message_id,
                    text="Фильм добавлен в «Смотреть позже»",
                    reply_markup=None
                )
        except Exception as e:
            print(f"Ошибка редактирования сообщения: {e}")

        bot.send_message(chat_id, "Главное меню:", reply_markup=main_keyboard())
        bot.delete_state(user_id, chat_id)
        with bot.retrieve_data(user_id, chat_id) as data:
            data.clear()

    elif call.data == "main_menu":
        bot.delete_message(chat_id, call.message.message_id)
        bot.delete_state(user_id, chat_id)
        with bot.retrieve_data(user_id, chat_id) as data:
            data.clear()
        bot.send_message(chat_id, "Главное меню:", reply_markup=main_keyboard())
