from database.CRUD import CRUDInterface
from database.models import db, SearchHistory, WatchLater

db.connect()
"""
Подключение к базе данных и создание таблиц.
"""
db.create_tables([SearchHistory, WatchLater])

"""
Экземпляр CRUD-интерфейса для выполнения операций с базой данных.
"""
crud = CRUDInterface()