
from loader import bot
from telebot import types
from database.history import add_to_watch_later
from keyboards.reply.main_keyboard import main_keyboard
from keyboards.inline.search_with_pagin import inline_search_keyboard


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
        results = data.get("results")
        if not results:
            return
        current_index = data.get("index", 0)

    if call.data.startswith("prev_") or call.data.startswith("next_"):
        try:
            new_index = int(call.data.split("_")[-1])
        except:
            return

        if 0 <= new_index < len(results):
            data["index"] = new_index
            movie = results[new_index]

            text = (
                f"*{movie['movie_name']}* ({movie['year']})\n\n"
                f"Рейтинг: {movie.get('rating') or '—'}\n"
                f"Описание: {movie.get('description') or 'Нет описания'}\n"
                f"Жанры: {', '.join(movie.get('genres', [])) or '—'}\n"
                f"Возраст: {movie.get('age_rating') or '—'}"
            )
            markup = inline_search_keyboard(new_index, len(results))

            try:
                if call.message.photo:
                    media = types.InputMediaPhoto(
                        movie.get("poster_url") or "https://via.placeholder.com/400x600.png?text=No+Poster",
                        caption=text,
                        parse_mode="Markdown"
                    )
                    bot.edit_message_media(chat_id=chat_id, message_id=call.message.message_id, media=media, reply_markup=markup)
                else:
                    bot.edit_message_text(text=text, chat_id=chat_id, message_id=call.message.message_id,
                                          parse_mode="Markdown", reply_markup=markup)
            except Exception as e:
                print(f"Edit failed: {e}")
                # fallback
                from utils.show_movie import show_current_movie
                show_current_movie(chat_id, user_id)

    elif call.data.startswith("watch_later_"):
        idx = int(call.data.split("_")[-1])
        movie = results[idx]
        add_to_watch_later(movie)

        text = "Фильм добавлен в «Смотреть позже»\n\nГлавное меню:"

        try:
            if call.message.photo:
                bot.edit_message_caption(chat_id=chat_id, message_id=call.message.message_id,
                                         caption=text, reply_markup=main_keyboard())
            else:
                bot.edit_message_text(text=text, chat_id=chat_id, message_id=call.message.message_id,
                                      reply_markup=main_keyboard())
        except:
            bot.send_message(chat_id, text, reply_markup=main_keyboard())

        bot.delete_state(user_id, chat_id)
        data.clear()

    elif call.data == "main_menu":
        text = "Главное меню:"

        try:
            if call.message.photo:
                bot.edit_message_caption(chat_id=chat_id, message_id=call.message.message_id,
                                         caption=text, reply_markup=main_keyboard())
            else:
                bot.edit_message_text(text=text, chat_id=chat_id, message_id=call.message.message_id,
                                      reply_markup=main_keyboard())
        except:
            bot.send_message(chat_id, text, reply_markup=main_keyboard())

        bot.delete_state(user_id, chat_id)
        with bot.retrieve_data(user_id, chat_id) as data:
            data.clear()