# utils/show_movie.py
from loader import bot
from telebot import types
from keyboards.inline.search_with_pagin import inline_search_keyboard


def show_current_movie(chat_id: int, user_id: int) -> None:
    """
    Универсальная функция показа текущего фильма из состояния.

    Используется в поиске по названию и по рейтингу.

    :param chat_id: ID чата
    :type chat_id: int
    :param user_id: ID пользователя
    :type user_id: int
    """
    """
    Универсальная функция показа текущего фильма из состояния.
    Используется в поиске по названию и по рейтингу.
    """
    with bot.retrieve_data(user_id, chat_id) as data:
        results = data.get("results")
        index = data.get("index", 0)

        if not results or index >= len(results):
            bot.send_message(chat_id, "Ошибка отображения результата.")
            return

        movie = results[index]

    text = (
        f"*{movie['movie_name']}* ({movie['year']})\n\n"
        f"Рейтинг: {movie.get('rating') or '—'}\n"
        f"Описание: {movie.get('description') or 'Нет описания'}\n"
        f"Жанры: {', '.join(movie.get('genres', [])) or '—'}\n"
        f"Возраст: {movie.get('age_rating') or '—'}"
    )

    markup = inline_search_keyboard(index, len(results))

    if movie.get("poster_url"):
        bot.send_photo(
            chat_id,
            movie["poster_url"],
            caption=text,
            parse_mode="Markdown",
            reply_markup=markup
        )
    else:
        bot.send_message(
            chat_id,
            text,
            parse_mode="Markdown",
            reply_markup=markup
        )