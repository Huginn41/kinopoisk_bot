from datetime import datetime
from peewee import *

db = SqliteDatabase('database.db')


class ModelBase(Model):
    """
    Базовая модель с общими полями.

    Наследуется всеми другими моделями.
    """
    id = AutoField(primary_key=True)
    created_at = DateField(default=datetime.now())

    class Meta:
        database = db


class SearchHistory(ModelBase):
    """
    Модель для хранения истории поиска фильмов.

    Содержит информацию о найденных фильмах и статусе просмотра.
    """
    movie_name = CharField()
    description = TextField(null=True)
    rating = FloatField(null=True)
    year = IntegerField()
    genres = CharField()
    age_rating = IntegerField(null=True)
    poster_url = TextField(null=True)
    watched = BooleanField(default=False)

    class Meta:
        db_table = 'search_history'


class WatchLater(ModelBase):
    """
    Модель для списка "Буду смотреть".

    Аналогична SearchHistory, но предназначена для отложенных фильмов.
    """
    movie_name = CharField()
    description = TextField(null=True)
    rating = FloatField(null=True)
    year = IntegerField()
    genres = CharField()
    age_rating = IntegerField(null=True)
    poster_url = TextField(null=True)
    watched = BooleanField(default=False)

    class Meta:
        db_table = 'watch_later_list'
