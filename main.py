import sqlite3
from threading import Thread
import time
from datetime import datetime, timedelta

from flask import Flask, render_template, jsonify
import psutil

save_cpu_load = "INSERT INTO cpu_load (timestamp, load) VALUES (?, ?)"
select_cpu_load_by_1_min = "SELECT AVG(load) FROM cpu_load WHERE timestamp >= datetime('now', '-60 seconds')"
save_cpu_average_by_1_min = "INSERT INTO cpu_average (timestamp, average) VALUES (?, ?)"
save_cpu_load_by_1_hour = "SELECT timestamp, load FROM cpu_load WHERE timestamp >= datetime('now', '-1 hour', 'localtime') ORDER BY id"
save_cpu_average_by_1_hour = "SELECT timestamp, average FROM cpu_average WHERE timestamp >= datetime('now', '-1 hour', 'localtime') ORDER BY id"

app = Flask(__name__)

# Создаем соединение с базой данных и таблицу, если она не существует
conn = sqlite3.connect('data.db', check_same_thread=False)
cursor = conn.cursor()
cursor.execute('''
                CREATE TABLE IF NOT EXISTS cpu_load (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME,
                    load FLOAT
                )
                ''')
cursor.execute('''
                CREATE TABLE IF NOT EXISTS cpu_average (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME,
                    average FLOAT
                )
                ''')
conn.commit()


# Функция мониторинга загрузки процессора
# Которая сохраняет данные в базу
def save_cpu_load():
    while True:
        cpu_load = psutil.cpu_percent(interval=1)
        timestamp = datetime.now()
        cursor.execute(str(save_cpu_load), (timestamp, cpu_load))
        conn.commit()
        time.sleep(5)


# Функция мониторинга загрузки процессора
# Которая берет данные из cpu_load за 1 минуту, считает среднее значение
# и сохраняет в таблицу cpu_average
def save_cpu_average():
    while True:
        cursor.execute(str(select_cpu_load_by_1_min))
        cpu_average = cursor.fetchone()[0]
        cpu_average = round(cpu_average, 2) if isinstance(cpu_average, float) else cpu_average
        timestamp = datetime.now()
        cursor.execute(save_cpu_average_by_1_min, (timestamp, cpu_average))
        conn.commit()
        time.sleep(60)


def fetch_historical_data():
    # Выбираем записи из таблицы cpu_load за последний час, отсортированные по id в обратном порядке
    cursor.execute(str(save_cpu_load_by_1_hour))
    rows = list(cursor.fetchall())

    # Создаем пустые списки для хранения временных меток и значений CPU
    timestamps = []
    cpu_values = []

    # Проходимся по всем записям и извлекаем временную метку и значение CPU
    for row in rows:
        timestamp = datetime.strptime(row[0], '%Y-%m-%d %H:%M:%S.%f')
        cpu_load = row[1]

        # Проверяем, есть ли уже записи в списке timestamps
        # Если да, то проверяем, находится ли текущая запись
        # более чем на 6 секунд (с запасом 1 секунда) от предыдущей
        if timestamps and (timestamp - timestamps[-1]) > timedelta(seconds=6):

            # Если разница больше 5 секунд, то добавляем пустые значения для пропущенных интервалов
            for i in range(int((timestamp - timestamps[-1]).total_seconds() / 5) - 1):
                timestamps.append(timestamps[-1] + timedelta(seconds=5))
                cpu_values.append(None)

        # Добавляем текущую временную метку и значение CPU в списки
        timestamps.append(timestamp)
        cpu_values.append(cpu_load)

    # Создаем словарь с данными для возврата в формате JSON
    data = {'x': timestamps, 'y': cpu_values}
    return jsonify(data)


def fetch_average_data():
    # Выбираем записи из таблицы cpu_average за последний час, отсортированные по id в обратном порядке
    cursor.execute(str(save_cpu_average_by_1_hour))
    rows = list(cursor.fetchall())

    # Создаем пустые списки для хранения временных меток и значений CPU
    timestamps = []
    cpu_values = []

    # Проходим по всем записям из таблицы и парсим значения timestamp и average
    for row in rows:
        timestamp_str = row[0]
        timestamp = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S.%f')
        cpu_value = row[1]

        # Добавляем значения в соответствующие списки
        timestamps.append(timestamp)
        cpu_values.append(cpu_value)

    # Создаем словарь для хранения данных, которые будут отправлены клиенту
    data = {'x': [], 'y': []}

    # Проходим по всем временным меткам
    for i, timestamp in enumerate(timestamps):
        # Если это первая временная метка, то добавляем ее и соответствующее значение CPU
        if i == 0:
            data['x'].append(timestamp.isoformat())
            data['y'].append(cpu_values[i])
        else:
            # Иначе находим разницу между текущей и предыдущей временной меткой
            previous_timestamp = timestamps[i - 1]
            diff = timestamp - previous_timestamp

            # Если разница больше 65 секунд (с запасом 5 секунд), то добавляем пустой интервал на график
            if diff > timedelta(seconds=65):
                gap = {
                    'x': [previous_timestamp.isoformat(), timestamp.isoformat()],
                    'y': [None, None]
                }
                data['x'].extend(gap['x'])
                data['y'].extend(gap['y'])

            # Добавляем текущую временную метку и соответствующее значение CPU
            data['x'].append(timestamp.isoformat())
            data['y'].append(cpu_values[i])

    # Преобразуем словарь в JSON и возвращаем его
    return jsonify(data)


@app.route('/')
def index():
    return render_template('../../PycharmProjects/CPU-Sensor/templates/index.html')


@app.route('/get-historical-data')
def get_historical_data():
    return fetch_historical_data()


@app.route('/get-average-data')
def get_average_data():
    return fetch_average_data()


if __name__ == '__main__':
    thread_save_cpu_load = Thread(target=save_cpu_load)
    thread_save_cpu_load.daemon = True
    thread_save_cpu_load.start()

    thread_save_cpu_average = Thread(target=save_cpu_average)
    thread_save_cpu_average.daemon = True
    thread_save_cpu_average.start()

    app.run()