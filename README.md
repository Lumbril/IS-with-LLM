# IS-with-LLM
Проект для ИБ в сфере ИИ

## Чтобы продемонстрировать работу проекта:
1. Скачать репозиторий  
`git clone https://github.com/Lumbril/IS-with-LLM.git`
2. Установить Docker Compose (https://docs.docker.com/compose/install/)
3. Открыть папку с проектом
4. Открыть папку `backend` и создать там файл `.env` на основе файла `.envEx`
5. Открыть терминал
6. Перейти в дирикторию с проектом  
`cd <путь до проекта>/`
7. Выполнить команду  
`docker compose up --build -d`
8. Открыть в браузере страницу  
`localhost:5050`
9. Ввести данные  
* email - admin@admin.com
* password - admin
10. Выбрать слева `Server` и на верхнем меню открыть `Object -> Register -> Server`
* На закладке `General` заполнить поле `Name`
* На закладке `Connection`
    * `Host Name/address` - db
    * `Port` - как был указан `POSTGRES_PORT` в `.env`
    * `Maintenance database` - как был указан `POSTGRES_DB` в `.env`
    * `Username` - как был указан `POSTGRES_USER` в `.env`
    * `Password` - как был указан `POSTGRES_PASSWORD` в `.env`
* Нажать `Save`
11. Открыть в браузере страницу
`localhost:8000/docs`
12. Выолнить `Try it out` у `log/analyze`

## Результат
На странице `localhost:5050`, если раскрыть слева дерево до `Servers -> <указаннный Name> -> Databases -> <указаннный Maintenance database> -> Schemas -> public -> Tables` можно увидеть таблицы: users, logs, anomalies. 
В логах были зафиксированы события выполнения демонстрационного скрипта из папки `demo`. После того как был выполнен шаг 12, 
в аномалиях появилась запись результата анализа последних 50 логов с помощью LLM.