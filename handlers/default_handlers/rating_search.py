from telebot import types
from loader import bot
from states.my_states import RatingSearchStates
from api.api_search import SiteApiInterface
from keyboards.inline.search_with_pagin import inline_search_keyboard
from keyboards.reply.genre_keyboard import genre_keyboard
from keyboards.reply.main_keyboard import main_keyboard
from database.history import add_to_search_history, add_to_watch_later


@bot.message_handler(func=lambda m: m.text == "🔍 Поиск по рейтингу")
def rating_search_start(message: types.Message) -> None:
    """
    Обработчик выбора поиска по рейтингу.

    Устанавливает состояние и запрашивает жанр.

    :param message: Сообщение от пользователя
    :type message: types.Message
    """

    bot.delete_state(message.from_user.id, message.chat.id)
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data.clear()
    bot.set_state(message.from_user.id, RatingSearchStates.genre, message.chat.id)
    bot.send_message(
        message.chat.id,
        "🎭 Выбери жанр:",
        reply_markup=genre_keyboard()
    )


@bot.message_handler(state=RatingSearchStates.genre)
def get_genre(message: types.Message) -> None:
    """
    Обработчик ввода жанра.

    Сохраняет жанр и запрашивает рейтинг.

    :param message: Сообщение с жанром
    :type message: types.Message
    """
    text = message.text.strip()
    if text.lower() == "отмена":
        bot.send_message(message.chat.id, "Отмена. Главное меню:", reply_markup=main_keyboard())
        bot.delete_state(message.from_user.id, message.chat.id)
        return
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data["genre"] = text.lower()
    bot.send_message(
        message.chat.id,
        "⭐ Введи рейтинг.\nМожно так:\n- 7 (равно 7)\n- 7-10 (диапазон)",
        reply_markup=types.ReplyKeyboardRemove()
    )
    bot.set_state(message.from_user.id, RatingSearchStates.rating, message.chat.id)



@bot.message_handler(state=RatingSearchStates.rating)
def get_rating(message: types.Message) -> None:
    """
    Обработчик ввода рейтинга.

    Сохраняет рейтинг и запрашивает количество результатов.

    :param message: Сообщение с рейтингом
    :type message: types.Message
    """
    rating = message.text.strip()
    if not ("-" in rating or rating.isdigit()):
        bot.send_message(message.chat.id, "Введите число или диапазон, например: 7 или 7-10")
        return
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data["rating"] = rating
    bot.send_message(message.chat.id, "Сколько результатов показать? (1–10)")
    bot.set_state(message.from_user.id, RatingSearchStates.amount, message.chat.id)


@bot.message_handler(state=RatingSearchStates.amount)
def get_amount(message: types.Message) -> None:
    """
    Обработчик ввода количества результатов.

    Выполняет поиск по рейтингу и показывает первый результат.

    :param message: Сообщение с количеством результатов
    :type message: types.Message
    """
    try:
        amount = int(message.text)
        if not (1 <= amount <= 10):
            raise ValueError
    except:
        bot.send_message(message.chat.id, "Введи число 1–10")
        return

    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        genre = data["genre"]
        rating = data["rating"]

    bot.send_message(message.chat.id, f"🔍 Ищу фильмы жанра '{genre}' с рейтингом {rating}...")

    results = SiteApiInterface.rating_search(genre=genre, rating=rating, limit=amount)

    if not results:
        bot.send_message(message.chat.id, "❌ По вашему запросу ничего не найдено")
        bot.delete_state(message.from_user.id, message.chat.id)
        return

    add_to_search_history(results)

    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data["results"] = results
        data["index"] = 0

    show_result(message.chat.id, message.from_user.id)



def show_result(chat_id: int, user_id: int) -> None:
    """
    Отображает результат поиска по рейтингу.

    :param chat_id: ID чата
    :type chat_id: int
    :param user_id: ID пользователя
    :type user_id: int
    """
    with bot.retrieve_data(user_id, chat_id) as data:
        index = data["index"]
        results = data["results"]

    movie = results[index]

    text = (
        f"🎬 {movie['movie_name']} ({movie['year']})\n"
        f"⭐ Рейтинг: {movie['rating']}\n"
        f"📄 {movie['description'] or 'нет описания'}\n"
        f"🎞 Жанры: {', '.join(movie['genres'])}\n"
        f"🔞 {movie['age_rating'] or 'нет данных'}"
    )

    markup = inline_search_keyboard(index, len(results))

    if movie['poster_url']:
        bot.send_photo(chat_id, movie["poster_url"], caption=text, reply_markup=markup)
    else:
        bot.send_message(chat_id, text, reply_markup=markup)


@bot.callback_query_handler(func=lambda c: c.data and (
        c.data.startswith(("prev_", "next_", "watch_later_")) or c.data == "main_menu"
))
def handle_search_callbacks(call: types.CallbackQuery) -> None:
    """
    Обработчик кнопок пагинации и действий с фильмом при поиске по рейтингу.

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


            movie = results[new_idx]
            text = (
                f"🎬 {movie['movie_name']} ({movie['year']})\n"
                f"⭐ Рейтинг: {movie['rating']}\n"
                f"📄 {movie['description'] or 'нет описания'}\n"
                f"🎞 Жанры: {', '.join(movie['genres'])}\n"
                f"🔞 {movie['age_rating'] or 'нет данных'}"
            )
            markup = inline_search_keyboard(new_idx, len(results))

            try:
                if call.message.photo:

                    if movie.get('poster_url'):

                        media = types.InputMediaPhoto(movie['poster_url'], caption=text)
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

                    if movie.get('poster_url'):

                        bot.delete_message(chat_id, call.message.message_id)
                        bot.send_photo(chat_id, movie['poster_url'], caption=text, reply_markup=markup)
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
                show_result(chat_id, user_id)

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
