from typing import Dict, List, TypeVar

from peewee import ModelSelect

from database.models import ModelBase
from database.models import db

T = TypeVar('T')


def _store_date(db, model: T, data) -> None:
    """
    Сохраняет данные в базу данных.

    :param db: Экземпляр базы данных
    :type db: Database
    :param model: Модель базы данных
    :type model: Model
    :param data: Данные для вставки
    :type data: Any
    """
    with db.atomic():
        model.insert_many(data).execute()


def _retrieve_all_data(db: db, model: T, *columns: ModelBase) -> ModelSelect:
    """
    Получает все данные из базы данных.

    :param db: Экземпляр базы данных
    :type db: Database
    :param model: Модель базы данных
    :type model: Model
    :param columns: Колонки для выборки
    :type columns: ModelBase
    :return: Выборка данных из базы
    :rtype: ModelSelect
    """
    with db.atomic():
        response = model.select(*columns)

    return response


def _update_data(db, model: T, updates: dict, where_condition) -> None:
    """
    Обновляет данные в базе данных.

    :param db: Экземпляр базы данных
    :type db: Database
    :param model: Модель базы данных
    :type model: Model
    :param updates: Словарь с обновлениями
    :type updates: dict
    :param where_condition: Условие для WHERE
    :type where_condition: Any
    """
    with db.atomic():
        query = model.update(**updates).where(where_condition)
        query.execute()


def _delete_data(db, model: T, where_condition) -> None:
    """
    Удаляет данные из базы данных.

    :param db: Экземпляр базы данных
    :type db: Database
    :param model: Модель базы данных
    :type model: Model
    :param where_condition: Условие для WHERE
    :type where_condition: Any
    """
    with db.atomic():
        query = model.delete().where(where_condition)
        query.execute()


class CRUDInterface():
    """
    Класс, предоставляющий интерфейс для операций CRUD.

    Методы возвращают функции для выполнения операций.
    """
    @staticmethod
    def create():
        return _store_date

    @staticmethod
    def retrieve():
        return _retrieve_all_data

    @staticmethod
    def update():
        return _update_data

    @staticmethod
    def delete():
        return _delete_data

