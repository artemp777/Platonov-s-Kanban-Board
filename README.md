# Platonov-s-Kanban-Board
<img width="751" height="417" alt="image" src="https://github.com/user-attachments/assets/0ceccdbf-8fbe-4b90-850f-75bdc55606a9" />


Функционал: 

Создание

<img width="399" height="328" alt="image" src="https://github.com/user-attachments/assets/e559c1d9-a4fb-4967-8f12-62ea4343b574" />

Изменение

<img width="399" height="327" alt="image" src="https://github.com/user-attachments/assets/8d2ac8c1-83d4-4360-b02b-ebb758991720" />

Удаление

<img width="750" height="419" alt="image" src="https://github.com/user-attachments/assets/9d1af5fc-e214-41e0-822a-82aac10fe543" />

Сохранение

<img width="261" height="148" alt="image" src="https://github.com/user-attachments/assets/66a39422-0395-41a6-ad83-40a3064fe604" />

<img width="651" height="113" alt="image" src="https://github.com/user-attachments/assets/ae7f49ff-1e2d-4435-b865-fe5f805eeef4" />

Поиск по заметкам

Через название

<img width="210" height="116" alt="image" src="https://github.com/user-attachments/assets/9879e868-78b2-4de5-b5fe-7d4c47174c2c" />

<img width="208" height="106" alt="image" src="https://github.com/user-attachments/assets/bd73b532-33bd-457a-ad46-af31c73280fe" />

Через описание заметки

<img width="274" height="119" alt="image" src="https://github.com/user-attachments/assets/efc635c8-bfb2-479f-b71e-7249b9b8fdb2" />

<img width="142" height="67" alt="image" src="https://github.com/user-attachments/assets/82464fff-f073-4dde-b417-67b4b41565d0" />



Как запустить:
PlatonovAr > dist > KanbanBoard.exe

Саму папку PlatonovAr можно кинуть в PyCharm чтобы посмотреть код, код очевидно в kanban.py

Как реализовывалось:

Для интерфейса использовался tkinter, он по факту использует встроенный интерфейс Windows который уже есть в 7, 8, 10 (про 11 незнаю, ей не пользуюсь). Есть три колонки сделанных через LabelFrame, каждая содержит Listbox которая поддерживает прокрутку, проктутка очевидно не появится пока всё видно.

Используется база данных, по факту вся база данных хранится в kanban.json, обычно всё сохраняется в него, его можно вообще вытащить из папки, после чего можно создать ещё один такой же.

Класс, отвечающий за хранение и логику работы с задачами.

```python
class KanbanModel:
    def __init__(self):
        self.columns = {
            "To Do": [],
            "In Progress": [],
            "Done": []
        }
```

Основные методы:

```add_task(column, title, description)``` cоздаёт новую задачу с уникальным UUID

```edit_task(column, task_id, new_title, new_description)``` изменяет существующую задачу по её ID

```delete_task(column, task_id)``` удаляет задачу

```move_task(from_col, to_col, task_id)``` перемещает задачу из одной колонки в другую

```get_all_tasks()``` возвращает список всех задач в формате (колонка, задача)

```save_to_json(filename)``` сохраняет текущее состояние колонок в json

```load_from_json(filename)``` загружает состояние из jsom если файл корректен

```export_to_md(filename)``` экспортирует доску в Markdown с заголовками ## колонки и ### задачи

```import_from_md(filename)``` парсит md и восстанавливает колонки и задачи

Каждая задача представлена словарём:

```python
{
    "id": "уникальный-uuid",
    "title": "Название задачи",
    "description": "Подробное описание"
}
```

При любом изменении данных вызывается ```refresh_column()``` или ```refresh_all_columns()```

Для получения id выбранной задачи используется ```get_selected_task_id()``` сопоставление индекса в Listbox с массивом id
