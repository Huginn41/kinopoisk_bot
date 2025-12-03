from telebot.states import StatesGroup, State


class SearchStates(StatesGroup):
    """
    Группа состояний для поиска по названию.

    name: Ожидание ввода названия фильма
    pages: Ожидание ввода количества результатов
    data: Хранение данных поиска
    """
    name = State()
    pages = State()
    data = State()


class RatingSearchStates(StatesGroup):
    """
    Группа состояний для поиска по рейтингу.

    genre: Ожидание выбора жанра
    rating: Ожидание ввода рейтинга
    amount: Ожидание ввода количества результатов
    results: Хранение результатов поиска
    index: Хранение текущего индекса
    """
    genre = State()
    rating = State()
    amount = State()
    results = State()
    index = State()

class HistoryStates(StatesGroup):
    """
    Группа состояний для просмотра истории.

    browsing: Просмотр элементов истории
    """
    browsing = State()