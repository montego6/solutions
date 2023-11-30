## Тестовое задание для компании Ришат
Приложение можно протестировать на [тестовом сервере](https://testrishat-production.up.railway.app/item/1/)

Далее будут описаны два варианта запуска приложения, [один с помощью Docker](#запуск-приложения-с-помощью-docker), [один без](#запуск-приложения-без-использования-docker). 

В обоих случаях используется база данных PostgreSQL

### Запуск приложения с помощью Docker
В корне проекта создайте **.env** файл и пропишите в нем следующие переменные:
```
DB_NAME=app
DB_USER=postgres
DB_PASSWORD=supersecretpassword
DB_HOST=db

DJANGO_SUPERUSER_USERNAME=admin
DJANGO_SUPERUSER_EMAIL=admin@yandex.ru
DJANGO_SUPERUSER_PASSWORD=admin

STRIPE_KEY= ваш Stripe Secret Key
STRIPE_PUBLISH_KEY= ваш Stripe Publish Key
```
Затем мы запускаем приложение следующей Docker командой в терминале:
```
docker-compose up -d
```
Приложение запуститься и должно быть доступно по локальному адресу [127.0.0.1:8000](http://127.0.0.1:8000)

Остановить приложение/запустить заново:
```
docker-compose stop
docker-compose start
```
Остановить приложение и удалить все связанные контейнеры, включая базу данных:
```
docker-compose down -v
```
При изменениях в коде проекта, необходимо заново создать образ и запустить сервисы:
```
docker-compose build
docker-compose up -d
```

### Запуск приложения без использования Docker
Сначала в корне проекта создадим виртуальное окружение и активируем его:
```
python3 -m venv venv
source venv/bin/activate
```
Затем установим все зависимости проекта, отдав следующую команду:
```
pip install -r requirements.txt
```
После этого в корне проекта создайте **.env** файл и пропишите в нем следующие переменные:
```
DB_NAME= название вашей базы данных
DB_USER= имя пользователя
DB_PASSWORD= пароль пользователя
DB_HOST=localhost

STRIPE_KEY= ваш Stripe Secret Key
STRIPE_PUBLISH_KEY= ваш Stripe Publish Key
```
***Убедитесь, что PostgreSQL запущен на локальной машине и принимает соединения на порту 5432***

Затем в корне проекта отдаем следующие команды, применяя миграции к базе данных:
```
python3 manage.py makemigrations
python3 manage.py migrate
```
Затем в интерактивном режиме создаем суперпользователя, чтобы иметь доступ к админ-панели:
```
python3 manage.py createsuperuser
```
После этого можно запускать сервер следующей командой:
```
python3 manage.py runserver
```
Приложение запуститься и должно быть доступно по локальному адресу [127.0.0.1:8000](http://127.0.0.1:8000)