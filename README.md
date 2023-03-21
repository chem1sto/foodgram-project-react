# **Проект Foodgram**
## **Описание**
**Foodgram** - продуктовый помощник с базой кулинарных рецептов. Позволяет публиковать рецепты, сохранять избранные, а также формировать список покупок для выбранных рецептов.

- Рецепты на всех страницах сортируются по дате публикации (новые — выше).
- Работает фильтрация по тегам, в том числе на странице избранного и на странице рецептов одного автора.
- Работает пагинатор (в том числе при фильтрации по тегам).
- Для авторизованных пользователей:
  * Доступна главная страница.
  * Доступна страница другого пользователя.
  * Доступна страница отдельного рецепта.
  * Доступна страница «Мои подписки»:
    - Можно подписаться и отписаться на странице рецепта.
    - Можно подписаться и отписаться на странице автора.
    - При подписке рецепты автора добавляются на страницу «Мои подписки» и удаляются оттуда при отказе от подписки.
  * Доступна страница «Избранное»:
    - На странице рецепта есть возможность добавить рецепт в список избранного и удалить его оттуда.
    - На любой странице со списком рецептов есть возможность добавить рецепт в список избранного и удалить его оттуда.
  * Доступна страница «Список покупок»:
    - На странице рецепта есть возможность добавить рецепт в список покупок и удалить его оттуда.
    - На любой странице со списком рецептов есть возможность добавить рецепт в список покупок и удалить его оттуда.
    - Есть возможность выгрузить файл (.pdf) с перечнем и количеством необходимых ингредиентов для рецептов из «Списка покупок».
    - Ингредиенты в выгружаемом списке не повторяются, корректно подсчитывается общее количество для каждого ингредиента.
  * Доступна страница «Создать рецепт»:
    - Есть возможность опубликовать свой рецепт.
    - Есть возможность отредактировать и сохранить изменения в своём рецепте.
    - Есть возможность удалить свой рецепт.
  * Доступна и работает форма изменения пароля.
  * Доступна возможность выйти из системы (разлогиниться)
- Для неавторизованных пользователей:
  * Доступна главная страница
  * Доступна страница отдельного рецепта
  * Доступна и работает форма авторизации
  * Доступна и работает система восстановления пароля
  * Доступна и работает форма регистрации
- Администратор и админ-зона:
  * Все модели выведены в админ-зону
  * Для модели пользователей включена фильтрация по имени и email
  * Для модели рецептов включена фильтрация по названию, автору и тегам
  * На админ-странице рецепта отображается общее число добавлений этого рецепта в избранное
  * Для модели ингредиентов включена фильтрация по названию

**Проект доступен [по адресу](http://chemisto-blog.ddns.net/)**.

**Документация по проекту доступна [по адресу](http://chemisto-blog.ddns.net/api/docs/)**.

### Технологии
- Python 3.10.6
- Django 4.1.7
- Django Rest Framework 3.14.0
- Webcolors 1.12
- Reportlab 3.6.12
- Gunicorn 20.1.0
- Nginx
- Postgres
- Djoser 2.0.5
- Docker 20.10.23
- Docker Compose 2.15.1

## **Как запустить проект на локальном компьютере**
1. Клонируйте репозиторий:
```
git@github.com:chem1sto/foodgram-project-react.git
```
2. Перейдите в него в командной строке:
```
cd foodgram-project-react/
```
3. Cоздайте и активируйте виртуальное окружение:
```
python3 -m venv venv
```
```
source env/bin/activate
```
4. Установите зависимости из файла requirements.txt:
```
python3 -m pip install --upgrade pip
```
```
pip install -r requirements.txt
```
5. Перейдите в папку foodgram-project-react/infra/
```
cd infra/
```
6. Выполните команду для развертывания приложения и его запуска:
```
docker compose up -d
```
7. Выполните миграции:
```
docker compose exec backend python manage.py makemigrations users recipes
```
```
docker compose exec backend python manage.py migrate
```
8. Загрузите в базу данные из CSV-файлов:
```
python manage.py upload ingredients.csv tags.csv
```
9. Соберите все статические файлы в папку static:
```
docker compose exec backend python manage.py collectstatic --no-input 
```
9. Создайте суперпользователя:
```
docker compose exec backend python manage.py createsuperuser
```
10. Приложение активно и готово к использованию. Можно перейти [по адресу](http://localhost/admin/) и авторизоваться, введя свои данные от созданного суперпользователя.

## **Документация**
Доступна после запуска сервера: [Redoc](http://localhost/api/docs/redoc.html).

## **Как запустить проект на удалённом сервере**
1. Клонируйте репозиторий:
```
git@github.com:chem1sto/foodgram-project-react.git
```
2. Установите на сервере Docker, Docker Compose:

```
sudo apt install curl                                   # установка утилиты для скачивания файлов
curl -fsSL https://get.docker.com -o get-docker.sh      # скачать скрипт для установки
sh get-docker.sh                                        # запуск скрипта
sudo apt-get install docker-compose-plugin              # последняя версия docker compose
```
3. На сервере перейдите в папку foodgram-project-react/infra/
```
cd foodgram-project-react/infra/
```
4. Создайте и запустите контейнеры Docker, выполнив команду на сервере
*(версии команд "docker compose" или "docker-compose" отличаются в зависимости от установленной версии Docker Compose):*
```
sudo docker compose up -d
```
5. Выполните миграции:
```
sudo docker compose exec backend python manage.py makemigrations users recipes
```
```
sudo docker compose exec backend python manage.py migrate
```
6. Загрузите в базу данные из CSV-файлов:
```
sudo python manage.py upload ingredients.csv tags.csv
```
7. Соберите все статические файлы в папку static:
```
sudo docker compose exec backend python manage.py collectstatic --no-input 
```
8. Создайте суперпользователя:
```
sudo docker compose exec backend python manage.py createsuperuser
```
9. Приложение активно и готово к использованию.

10. Для остановки контейнеров Docker:
```
sudo docker compose stop
```
11. Для удаления контейнеров Docker:
```
sudo docker compose down -v      # с удалением контейнеров и volumes
sudo docker compose down         # без удаления volumes
```

### Автор
- Владимир Васильев | [chem1sto](https://github.com/chem1sto)