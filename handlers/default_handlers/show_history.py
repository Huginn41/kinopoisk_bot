from loader import bot
from database.core import crud, db
from database.models import SearchHistory
from keyboards.inline.history_keyboard import inline_history_keyboard
from keyboards.reply.main_keyboard import main_keyboard
from states.my_states import HistoryStates
from telebot import types


@bot.message_handler(commands=["history"])
@bot.message_handler(func=lambda m: m.text == "🎬 История поиска")
def show_history_command(message) -> None:
    """
    Обработчик команды истории поиска.

    Загружает и отображает историю поиска пользователя.

    :param message: Сообщение от пользователя
    """
    bot.send_message(
        message.chat.id,
        "Загружаю историю...",
        reply_markup=types.ReplyKeyboardRemove()
    )
    chat_id = message.chat.id
    user_id = message.from_user.id

    bot.set_state(user_id, HistoryStates.browsing, chat_id)
    show_history(chat_id, user_id)


def show_history(chat_id: int, user_id: int) -> None:
    """
    Отображает историю поиска пользователя.

    :param chat_id: ID чата
    :type chat_id: int
    :param user_id: ID пользователя
    :type user_id: int
    """
    movies_db = crud.retrieve()(db=db, model=SearchHistory)
    movies = list(movies_db.order_by(SearchHistory.created_at.desc()))

    if not movies:
        bot.send_message(chat_id, "История поиска пуста")
        bot.delete_state(user_id, chat_id)
        return

    with bot.retrieve_data(user_id, chat_id) as data:
        data.clear()
        data["results"] = [
            {
                "id": m.id,
                "movie_name": m.movie_name,
                "year": m.year,
                "rating": m.rating,
                "description": m.description,
                "genres": m.genres.split(", ") if m.genres else [],
                "age_rating": m.age_rating,
                "poster_url": m.poster_url,
                "created_at": m.created_at,
                "watched": m.watched
            }
            for m in movies
        ]
        data["index"] = 0

    send_history_item(chat_id, user_id, 0)


def build_history_message(movie: dict) -> str:
    """
    Формирует текстовое сообщение для элемента истории.

    :param movie: Словарь с данными о фильме
    :type movie: dict
    :return: Текст сообщения
    :rtype: str
    """
    watch_status = "Просмотрено" if movie['watched'] else "Не просмотрено"

    text = (
        f"{movie['movie_name']} ({movie['year']})\n"
        f"Рейтинг: {movie['rating']}\n"
        f"Описание: {movie['description'] or 'нет описания'}\n"
        f"Жанры: {', '.join(movie['genres'])}\n"
        f"{movie['age_rating'] or 'нет данных'}\n"
        f"Дата поиска: {movie['created_at'].strftime('%d.%m.%Y')}\n"
        f"Статус: {watch_status}"
    )
    return text


def send_history_item(chat_id: int, user_id: int, index: int) -> None:
    """
    Отправляет сообщение с элементом истории.

    :param chat_id: ID чата
    :type chat_id: int
    :param user_id: ID пользователя
    :type user_id: int
    :param index: Индекс элемента в истории
    :type index: int
    """
    with bot.retrieve_data(user_id, chat_id) as data:
        results = data.get("results", [])

    if not results or index < 0 or index >= len(results):
        bot.send_message(chat_id, "Нет данных для отображения")
        return

    movie = results[index]
    text = build_history_message(movie)
    markup = inline_history_keyboard(index, len(results), movie['watched'])

    try:
        if movie['poster_url']:
            bot.send_photo(chat_id, movie['poster_url'], caption=text, reply_markup=markup)
        else:
            bot.send_message(chat_id, text, reply_markup=markup)
    except Exception as e:
        bot.send_message(chat_id, f"Ошибка при отправке: {e}")


def mark_as_watched(movie_id: int) -> None:
    """
    Отмечает фильм в истории как просмотренный.

    :param movie_id: ID фильма
    :type movie_id: int
    """
    crud.update()(
        db=db,
        model=SearchHistory,
        updates={"watched": True},
        where_condition=(SearchHistory.id == movie_id)
    )


@bot.callback_query_handler(func=lambda c: c.data and c.data.startswith("history_"))
def handle_history_callbacks(call: types.CallbackQuery) -> None:
    """
    Обработчик кнопок управления историей поиска.

    :param call: Callback-запрос от кнопки
    :type call: types.CallbackQuery
    """
    bot.answer_callback_query(call.id)
    user_id = call.from_user.id
    chat_id = call.message.chat.id

    with bot.retrieve_data(user_id, chat_id) as data:
        if "results" not in data:
            return
        results = data["results"]
        idx = data.get("index", 0)

    data_str = call.data

    if data_str.startswith(("history_prev_", "history_next_")):
        try:
            new_idx = int(data_str.rsplit("_", 1)[-1])
        except ValueError:
            return

        if 0 <= new_idx < len(results):
            data["index"] = new_idx
            movie = results[new_idx]
            text = build_history_message(movie)
            markup = inline_history_keyboard(new_idx, len(results), movie['watched'])

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
                send_history_item(chat_id, user_id, new_idx)


    elif data_str.startswith("history_mark_watched_"):
        try:
            idx_to_mark = int(data_str.rsplit("_", 1)[-1])
        except ValueError:
            return

        if 0 <= idx_to_mark < len(results):
            movie_id = results[idx_to_mark]["id"]
            crud.update()(
                db=db,
                model=SearchHistory,
                updates={"watched": True},
                where_condition=(SearchHistory.id == movie_id)
            )
            results[idx_to_mark]["watched"] = True
            data["index"] = idx_to_mark

            movie = results[idx_to_mark]
            text = build_history_message(movie)
            markup = inline_history_keyboard(idx_to_mark, len(results), movie['watched'])

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
                        bot.edit_message_caption(
                            chat_id=chat_id,
                            message_id=call.message.message_id,
                            caption=text,
                            reply_markup=markup
                        )
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
                send_history_item(chat_id, user_id, idx_to_mark)

            bot.answer_callback_query(call.id, "Отмечено как просмотренное!")


    elif data_str == "history_main_menu":
        bot.delete_message(chat_id, call.message.message_id)
        bot.delete_state(user_id, chat_id)
        with bot.retrieve_data(user_id, chat_id) as data:
            data.clear()
        bot.send_message(chat_id, "Главное меню:", reply_markup=main_keyboard())
