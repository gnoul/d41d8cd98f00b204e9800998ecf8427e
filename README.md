Для запуска проекта нужно с помощью собрать окружение:
``` shell
docker-compose up --build
```
Для создания таблиц в БД запустите:
``` shell
docker-compose run service1 python db_create.py
```

Для запуска выполните:
``` shell
docker-compose up -d
```