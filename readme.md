# 🎬 Kinopoisk Telegram Bot

![Python](https://img.shields.io/badge/Python-3.8+-blue)
![pyTelegramBotAPI](https://img.shields.io/badge/pyTelegramBotAPI-FSM-green)
![SQLite](https://img.shields.io/badge/SQLite-Peewee_ORM-lightgrey)

Telegram-бот для поиска фильмов через Kinopoisk API. 
Поддерживает поиск по названию и жанру, историю запросов 
и список "Смотреть позже".

## Архитектура

Модульная структура с чётким разделением слоёв:
├── api/           # HTTP-клиент Kinopoisk API
├── handlers/      # Обработчики команд и сообщений
├── keyboards/     # Inline и Reply клавиатуры
├── database/      # Peewee ORM: модели, CRUD, история
├── states/        # FSM-состояния диалогов
└── utils/         # Вспомогательные утилиты

**Ключевые решения:**
- FSM (Finite State Machine) через pyTelegramBotAPI — 
  многошаговые диалоги без захламления глобального состояния
- Peewee ORM + SQLite — лёгкая персистентность без внешних зависимостей
- Пагинация результатов через Inline-клавиатуры

## Функциональность

| Команда / кнопка | Описание |
|---|---|
| `/start` | Запуск, главное меню |
| `🔎 Поиск` | Поиск по названию с пагинацией |
| `🔍 Поиск по рейтингу` | Фильтр по жанру + диапазон рейтинга |
| `🎬 История поиска` | Последние запросы из SQLite |
| `📋 Буду смотреть` | Список избранного, отметка как просмотрено |

## Установка и запуск

**1. Клонируй репозиторий:**
```bash
git clone https://github.com/Huginn41/kinopoisk_bot.git
cd kinopoisk_bot
```

**2. Создай `.env` файл:**
```env
BOT_TOKEN=your_telegram_bot_token
RAPID_API_KEY=your_kinopoisk_api_key
```

**3. Установи зависимости и запусти:**
```bash
pip install -r requirements.txt
python main.py
```

## Получение ключей

- `BOT_TOKEN` — создай бота через [@BotFather](https://t.me/BotFather)
- `RAPID_API_KEY` — зарегистрируйся на [RapidAPI](https://rapidapi.com) 
  и подключи Kinopoisk Unofficial API

## Требования

- Python 3.8+
- Зависимости из `requirements.txt`
