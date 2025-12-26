from diagrams import Diagram, Cluster, Edge
from diagrams.onprem.client import Client  # Замість User
from diagrams.programming.framework import FastAPI  # Для сервера
from diagrams.onprem.database import PostgreSQL  # SQLite немає, використовуємо PostgreSQL як аналог (або GenericDatabase)
from diagrams.generic.blank import Blank
from diagrams.generic.storage import Storage  # Альтернатива для БД

# Папка для збереження діаграм
graph_attr = {
    "fontsize": "24",
    "bgcolor": "white",
    "pad": "1.0"
}

# 1. Архітектура системи
with Diagram("Архітектура програмної системи", filename="diagrams/architecture", show=False, graph_attr=graph_attr):
    client = Client("Клієнти\n(Менеджер, Касир, IoT)")
    server = FastAPI("FastAPI Server\nREST API + JWT")
    db = Storage("SQLite БД")  # Storage — універсальний блок для БД

    client >> Edge(label="HTTP-запити") >> server
    server >> Edge(label="Збереження/читання даних") >> db

# 2. UML прецеденти (спрощена блок-схема)
with Diagram("UML діаграма прецедентів", filename="diagrams/use_case", show=False, graph_attr=graph_attr):
    with Cluster("Актори"):
        manager = Client("Менеджер")
        cashier = Client("Касир")
        iot = Blank("IoT-клієнт")

    with Cluster("Прецеденти"):
        auth = Blank("Авторизація")
        view = Blank("Перегляд черг")
        update = Blank("Оновлення черги")
        notify = Blank("Сповіщення")

    manager >> auth >> view >> notify
    cashier >> auth >> notify
    iot >> update

# 3. ER-діаграма
with Diagram("ER-діаграма бази даних", filename="diagrams/er_diagram", show=False, graph_attr=graph_attr):
    users = Blank("Users\n- id (PK)\n- email\n- role")
    checkouts = Blank("Checkouts\n- id (PK)\n- name\n- is_active")
    queues = Blank("Queues\n- id (PK)\n- checkout_id (FK)\n- people_count\n- updated_at")

    checkouts >> Edge(label="1 : N") >> queues

# 4. Структура БД
with Diagram("Структура бази даних", filename="diagrams/db_structure", show=False, graph_attr=graph_attr):
    with Cluster("Таблиці"):
        users = Blank("users")
        checkouts = Blank("checkouts")
        queues = Blank("queues")

    checkouts >> Edge(label="FK: checkout_id", style="dashed") >> queues

print("Усі 4 діаграми успішно створено в папці 'diagrams/'!")