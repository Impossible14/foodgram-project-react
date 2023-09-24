# Foodgram

# Описание

Cайт Foodgram - онлайн-сервис, на котором пользователи могут публиковать рецепты, подписываться на публикации других пользователей, добавлять понравившиеся рецепты в список «Избранное», а перед походом в магазин скачивать сводный список продуктов, необходимых для приготовления одного или нескольких выбранных блюд.

> # Технологии

**Python, Django, Django Rest, Djoser**

> # Установка

> ## Клонируем репозиторий
```
git clone git@github.com:Impossible14/foodgram-project-react.git
```
> ## Создаём виртуальное окружение и активируем (venv)
```
python -m venv venv
./venv/Scripts/Activate
```
> ## Загружаем все нужные библитеки
```
pip install -r requirements.txt
```
> ## Выполняем миграции и запускаем проект
```
python manage.py migrate
python manage.py runserver
```
> # Наполнение базы данных:
В репозитории, в директории ```/backend/recipes/data```, подготовлен файл в формате ```csv``` с ингредиентами. 
Для заполния базы данных контентом из приложенных csv-файлов необходимо запустить файл ```load_cvs_data.py```, расположенный в папке ```recipes/management/commands```:
```
python manage.py load_cvs_data
```

> # Автор
* **Максим Матвеев** (https://github.com/Impossible14)
