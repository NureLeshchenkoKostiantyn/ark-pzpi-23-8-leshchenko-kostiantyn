import requests
import time
import json

# Завантаження налаштувань з файлу
with open("config.json", "r", encoding="utf-8") as f:
    config = json.load(f)

SERVER_URL = config["server_url"]
CHECKOUT_ID = config["checkout_id"]
ALERT_THRESHOLD = config["alert_threshold"]
SIMULATED_PEOPLE = config["simulated_people"]
INTERVAL = config["interval_seconds"]

def simulate_people_count():
    # Симуляція YOLOv8 (у реальності тут підрахунок з камери)
    return SIMULATED_PEOPLE

def send_to_server(people_count):
    url = f"{SERVER_URL}/queues/{CHECKOUT_ID}"
    data = {"people_count": people_count}
    try:
        response = requests.put(url, json=data)
        return response.json()
    except Exception as e:
        return {"error": str(e)}

print("IoT-клієнт запущено. Налаштування:")
print(f"Сервер: {SERVER_URL}, Каса ID: {CHECKOUT_ID}, Поріг: {ALERT_THRESHOLD}")

while True:
    people = simulate_people_count()
    print(f"\nВиявлено {people} людей у черзі")

    # БІЗНЕС-ЛОГІКА: локальне сповіщення
    if people > ALERT_THRESHOLD:
        print("ЛОКАЛЬНЕ СПОСТЕРЕЖЕННЯ: Черга переповнена! Рекомендується відкрити додаткову касу.")

    # Відправка на сервер
    result = send_to_server(people)
    print("Відповідь сервера:", result)

    time.sleep(INTERVAL)