# CPU-Usage-Sensor

### Summary
* [Описание](#описание)
* [Установка](#установка)
* [Использование](#использование)
* [Примеры](#примеры)
* [Стек проекта и принятые решения](#стек-проекта-и-принятые-решения)


## Описание

**CPU-Sensor** - веб сервис, который постоянно сохраняет в базу данных историю величины загрузки процессора с интервалом в 5 секунд и предоставляет страницу, которая изображает срез данных с историей загрузки процессора за последний час в виде двух графиков:
* Первый - отображает историю изменения моментальной загрузки процессора.
* Второй - отображает график усредненной загрузки процессора (среднее значение за 1 минуту).

В случае, если сервис на какое-то время окажется выключен, на графиках будут видны пустые промежутки времени, для которых нет данных. Графики рисуются на фронтенде, вычисление значений второго графика производятся на бэкенде.

## Установка

1. Активируйте виртуальное окружение, выполнив в терминале команду:

```Bash
source venv/bin/activate
```

После выполнения этой команды вы увидите, что приглашение терминала изменилось. Это означает, что вы находитесь внутри виртуального окружения.

2. Установите зависимости в пакет, используя менеджер пакетов pip и файл requirements.txt. Для этого выполните команду:

```Bash
pip install -r requirements.txt
```

## Использование

Запуск программы производится из корневой директории проекта командой:

```Bash
python main.py
```

После этого веб-сервис должен быть запущен на локальном сервере и доступен по адресу http://localhost:5000.

На странице вы увидите два графика. Первый - почти моментально (5 секунд). Второй нужно будет подождать 1 минуту, пока скриптом не будут запрошены первые данные из БД.

## Примеры

Как пример, вы через некоторое время можете увидеть что-то подобное:

* Первый график

![](../../PycharmProjects/CPU-Sensor/content/1.png)

* Второй график

![](../../PycharmProjects/CPU-Sensor/content/2.png)

Обратите внимание на пустоты в графиках. В эти промежутки времени скрипт не работал!

## Стек проекта и принятые решения

При выполнении задания было принято решение использовать фреймворк **Flask** в качестве легковесного и гибкого веб-фреймворка для быстрой разработки и запуска прототипа сервиса. Для мониторинга процессора безальтернативно использовалась библиотека **psutil**. На фронте отрисовка графиков осуществляется за счет библиотеки **chart.js** и fetch-запросов на эндпоинты для регулярного обновления данных без перезагрузки страницы.

Для сохранения истории загрузки процессора было принято решение использовать две отдельные таблицы в базе данных **SQLite**. Одна таблица для хранения мгновенной загрузки процессора, а другая для хранения усредненной загрузки за минуту. Для периодического сохранения данных было использовано два отдельных потока (**threading**), работающих в фоновом режиме.

Для решения задачи можно было использовать асинхронность или очереди задач, а также планировщики задач, например, Cron. В данном случае мы **используем потоки для непрерывной записи данных** в базу данных и расчета средней загрузки процессора, что позволяет **освободить основной поток для обработки пользовательских запросов**. Использование асинхронности, очередей задач или планировщиков задач может быть полезно в других ситуациях, например, если мы бы хотели обработать большое количество запросов на обработку данных в фоновом режиме или запланировать выполнение определенных задач на определенное время. Однако, для решения данной задачи, я считаю, что использование потоков является более оптимальным и эффективным решением.

___
