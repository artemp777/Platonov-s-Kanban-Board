import json
import os
import uuid
import re
from tkinter import *
from tkinter import ttk, messagebox, filedialog, simpledialog

# ---------------------------- МОДЕЛЬ ДАННЫХ ----------------------------
class KanbanModel:
    def __init__(self):
        self.columns = {
            "To Do": [],
            "In Progress": [],
            "Done": []
        }

    def add_task(self, column, title, description):
        """Добавить задачу в колонку."""
        task = {
            "id": str(uuid.uuid4()),
            "title": title,
            "description": description
        }
        self.columns[column].append(task)
        return task

    def edit_task(self, column, task_id, new_title, new_description):
        """Изменить задачу по ID."""
        for task in self.columns[column]:
            if task["id"] == task_id:
                task["title"] = new_title
                task["description"] = new_description
                return True
        return False

    def delete_task(self, column, task_id):
        """Удалить задачу по ID."""
        for i, task in enumerate(self.columns[column]):
            if task["id"] == task_id:
                del self.columns[column][i]
                return True
        return False

    def move_task(self, from_col, to_col, task_id):
        """Переместить задачу из одной колонки в другую."""
        task = None
        for i, t in enumerate(self.columns[from_col]):
            if t["id"] == task_id:
                task = self.columns[from_col].pop(i)
                break
        if task:
            self.columns[to_col].append(task)
            return True
        return False

    def get_all_tasks(self):
        """Вернуть все задачи для поиска (колонка, задача)."""
        tasks = []
        for col, task_list in self.columns.items():
            for task in task_list:
                tasks.append((col, task))
        return tasks

    def save_to_json(self, filename="kanban.json"):
        """Сохранить доску в JSON."""
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(self.columns, f, ensure_ascii=False, indent=2)

    def load_from_json(self, filename="kanban.json"):
        """Загрузить доску из JSON."""
        if not os.path.exists(filename):
            return False
        with open(filename, "r", encoding="utf-8") as f:
            data = json.load(f)
        # Проверка структуры
        if set(data.keys()) == {"To Do", "In Progress", "Done"}:
            self.columns = data
            return True
        return False

    def export_to_md(self, filename="kanban_export.md"):
        """Экспорт в Markdown (формат с заголовками h2 и h3)."""
        with open(filename, "w", encoding="utf-8") as f:
            f.write("# Kanban Board\n\n")
            for col_name, tasks in self.columns.items():
                f.write(f"## {col_name}\n\n")
                for task in tasks:
                    f.write(f"### {task['title']}\n")
                    if task['description'].strip():
                        f.write(f"{task['description']}\n")
                    f.write("\n")
                f.write("\n")

    def import_from_md(self, filename):
        """Импорт из Markdown (формат с h2 и h3)."""
        with open(filename, "r", encoding="utf-8") as f:
            content = f.read()

        # Регулярное выражение для поиска заголовков h2 и h3
        # Разбиваем на блоки по заголовкам h2
        pattern = r"## (.+?)\n(.*?)(?=\n## |\Z)"
        matches = re.findall(pattern, content, re.DOTALL)

        new_columns = {"To Do": [], "In Progress": [], "Done": []}

        for col_name, col_content in matches:
            col_name = col_name.strip()
            if col_name not in new_columns:
                continue  # игнорируем неизвестные колонки
            # Ищем задачи: ### Заголовок\nописание
            task_pattern = r"### (.+?)\n(.*?)(?=\n### |\n## |\Z)"
            tasks = re.findall(task_pattern, col_content, re.DOTALL)
            for title, desc in tasks:
                title = title.strip()
                desc = desc.strip()
                new_columns[col_name].append({
                    "id": str(uuid.uuid4()),
                    "title": title,
                    "description": desc
                })
        self.columns = new_columns


# ---------------------------- ГРАФИЧЕСКИЙ ИНТЕРФЕЙС ----------------------------
class KanbanApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Kanban Board")
        self.root.geometry("1000x600")

        self.model = KanbanModel()
        # Загружаем последнюю доску, если есть
        if not self.model.load_from_json("kanban.json"):
            # Создаём тестовые данные для примера
            self.model.add_task("To Do", "Пример задачи", "Это описание тестовой задачи.")
            self.model.add_task("In Progress", "Работа над проектом", "Пишем код канбан-доски.")
            self.model.add_task("Done", "Завершённая задача", "Ура, работает!")

        # Переменные для хранения ссылок на listbox'ы и списки ID задач
        self.listboxes = {}
        self.task_ids = {}  # {column: [list of task ids]}

        # Создаём интерфейс
        self.create_widgets()
        self.refresh_all_columns()

    def create_widgets(self):
        # Верхняя панель с кнопками
        top_frame = ttk.Frame(self.root)
        top_frame.pack(fill=X, padx=5, pady=5)

        ttk.Button(top_frame, text="Сохранить доску", command=self.save_board).pack(side=LEFT, padx=2)
        ttk.Button(top_frame, text="Загрузить доску", command=self.load_board).pack(side=LEFT, padx=2)
        ttk.Button(top_frame, text="Экспорт в MD", command=self.export_md).pack(side=LEFT, padx=2)
        ttk.Button(top_frame, text="Импорт из MD", command=self.import_md).pack(side=LEFT, padx=2)
        ttk.Button(top_frame, text="Поиск", command=self.search_tasks).pack(side=LEFT, padx=2)

        # Основная область с тремя колонками
        columns_frame = ttk.Frame(self.root)
        columns_frame.pack(fill=BOTH, expand=True, padx=5, pady=5)

        self.columns = ["To Do", "In Progress", "Done"]
        for idx, col_name in enumerate(self.columns):
            frame = ttk.LabelFrame(columns_frame, text=col_name)
            frame.grid(row=0, column=idx, sticky=NSEW, padx=5, pady=5)
            columns_frame.columnconfigure(idx, weight=1)
        columns_frame.rowconfigure(0, weight=1)

        # Для каждой колонки создаём listbox и кнопки
        for col_name in self.columns:
            container = ttk.Frame(columns_frame)
            # Привязываем к grid-позиции, но лучше использовать отдельные фреймы внутри LabelFrame
            # Упростим: создаём фрейм внутри каждого LabelFrame
            parent = None
            for child in columns_frame.winfo_children():
                if child.cget("text") == col_name:
                    parent = child
                    break
            if parent:
                # Listbox с прокруткой
                listbox_frame = ttk.Frame(parent)
                listbox_frame.pack(fill=BOTH, expand=True, padx=5, pady=5)
                scrollbar = ttk.Scrollbar(listbox_frame)
                scrollbar.pack(side=RIGHT, fill=Y)
                lb = Listbox(listbox_frame, yscrollcommand=scrollbar.set, font=("Arial", 10))
                lb.pack(side=LEFT, fill=BOTH, expand=True)
                scrollbar.config(command=lb.yview)
                self.listboxes[col_name] = lb

                # Кнопки управления
                btn_frame = ttk.Frame(parent)
                btn_frame.pack(fill=X, padx=5, pady=5)

                ttk.Button(btn_frame, text="Добавить",
                           command=lambda c=col_name: self.add_task(c)).pack(side=LEFT, padx=2)
                ttk.Button(btn_frame, text="Изменить",
                           command=lambda c=col_name: self.edit_task(c)).pack(side=LEFT, padx=2)
                ttk.Button(btn_frame, text="Удалить",
                           command=lambda c=col_name: self.delete_task(c)).pack(side=LEFT, padx=2)

                # Кнопки перемещения (влево/вправо)
                move_frame = ttk.Frame(parent)
                move_frame.pack(fill=X, padx=5, pady=5)
                if col_name != self.columns[0]:  # не первая колонка -> кнопка влево
                    ttk.Button(move_frame, text="←",
                               command=lambda c=col_name, direction="left": self.move_task(c, direction)).pack(side=LEFT, padx=2)
                if col_name != self.columns[-1]:  # не последняя -> кнопка вправо
                    ttk.Button(move_frame, text="→",
                               command=lambda c=col_name, direction="right": self.move_task(c, direction)).pack(side=LEFT, padx=2)

    def refresh_column(self, col_name):
        """Обновить отображение одной колонки."""
        lb = self.listboxes[col_name]
        lb.delete(0, END)
        tasks = self.model.columns[col_name]
        ids = []
        for task in tasks:
            lb.insert(END, task["title"])
            ids.append(task["id"])
        self.task_ids[col_name] = ids

    def refresh_all_columns(self):
        """Обновить все колонки."""
        for col in self.columns:
            self.refresh_column(col)

    def get_selected_task_id(self, col_name):
        """Получить ID выбранной задачи в колонке."""
        lb = self.listboxes[col_name]
        selection = lb.curselection()
        if not selection:
            messagebox.showwarning("Выбор", "Сначала выберите задачу.")
            return None
        idx = selection[0]
        if idx < len(self.task_ids.get(col_name, [])):
            return self.task_ids[col_name][idx]
        return None

    def add_task(self, col_name):
        """Открыть диалог добавления задачи."""
        dialog = Toplevel(self.root)
        dialog.title("Новая задача")
        dialog.geometry("400x300")
        dialog.grab_set()

        ttk.Label(dialog, text="Заголовок:").pack(pady=(10,0), anchor=W, padx=10)
        title_entry = ttk.Entry(dialog, width=50)
        title_entry.pack(padx=10, pady=5, fill=X)

        ttk.Label(dialog, text="Описание:").pack(anchor=W, padx=10)
        desc_text = Text(dialog, height=10, width=50)
        desc_text.pack(padx=10, pady=5, fill=BOTH, expand=True)

        def save():
            title = title_entry.get().strip()
            if not title:
                messagebox.showerror("Ошибка", "Заголовок не может быть пустым.")
                return
            desc = desc_text.get("1.0", END).strip()
            self.model.add_task(col_name, title, desc)
            self.refresh_column(col_name)
            dialog.destroy()

        ttk.Button(dialog, text="Сохранить", command=save).pack(pady=10)

    def edit_task(self, col_name):
        """Редактировать выбранную задачу."""
        task_id = self.get_selected_task_id(col_name)
        if not task_id:
            return
        # Найдём задачу
        task = None
        for t in self.model.columns[col_name]:
            if t["id"] == task_id:
                task = t
                break
        if not task:
            return

        dialog = Toplevel(self.root)
        dialog.title("Редактировать задачу")
        dialog.geometry("400x300")
        dialog.grab_set()

        ttk.Label(dialog, text="Заголовок:").pack(pady=(10,0), anchor=W, padx=10)
        title_entry = ttk.Entry(dialog, width=50)
        title_entry.insert(0, task["title"])
        title_entry.pack(padx=10, pady=5, fill=X)

        ttk.Label(dialog, text="Описание:").pack(anchor=W, padx=10)
        desc_text = Text(dialog, height=10, width=50)
        desc_text.insert("1.0", task["description"])
        desc_text.pack(padx=10, pady=5, fill=BOTH, expand=True)

        def save():
            new_title = title_entry.get().strip()
            if not new_title:
                messagebox.showerror("Ошибка", "Заголовок не может быть пустым.")
                return
            new_desc = desc_text.get("1.0", END).strip()
            self.model.edit_task(col_name, task_id, new_title, new_desc)
            self.refresh_column(col_name)
            dialog.destroy()

        ttk.Button(dialog, text="Сохранить", command=save).pack(pady=10)

    def delete_task(self, col_name):
        """Удалить выбранную задачу."""
        task_id = self.get_selected_task_id(col_name)
        if not task_id:
            return
        if messagebox.askyesno("Удаление", "Вы уверены, что хотите удалить задачу?"):
            self.model.delete_task(col_name, task_id)
            self.refresh_column(col_name)

    def move_task(self, col_name, direction):
        """Переместить задачу в соседнюю колонку."""
        task_id = self.get_selected_task_id(col_name)
        if not task_id:
            return
        col_idx = self.columns.index(col_name)
        if direction == "left" and col_idx > 0:
            to_col = self.columns[col_idx - 1]
        elif direction == "right" and col_idx < len(self.columns) - 1:
            to_col = self.columns[col_idx + 1]
        else:
            return
        if self.model.move_task(col_name, to_col, task_id):
            self.refresh_all_columns()
        else:
            messagebox.showerror("Ошибка", "Не удалось переместить задачу.")

    def save_board(self):
        """Сохранить текущую доску в JSON."""
        self.model.save_to_json("kanban.json")
        messagebox.showinfo("Сохранение", "Доска сохранена в kanban.json")

    def load_board(self):
        """Загрузить доску из JSON."""
        if self.model.load_from_json("kanban.json"):
            self.refresh_all_columns()
            messagebox.showinfo("Загрузка", "Доска загружена из kanban.json")
        else:
            messagebox.showerror("Ошибка", "Не удалось загрузить файл kanban.json")

    def export_md(self):
        """Экспорт в Markdown."""
        filename = filedialog.asksaveasfilename(defaultextension=".md", filetypes=[("Markdown", "*.md")])
        if filename:
            self.model.export_to_md(filename)
            messagebox.showinfo("Экспорт", f"Доска экспортирована в {filename}")

    def import_md(self):
        """Импорт из Markdown."""
        filename = filedialog.askopenfilename(filetypes=[("Markdown", "*.md")])
        if filename:
            try:
                self.model.import_from_md(filename)
                self.refresh_all_columns()
                messagebox.showinfo("Импорт", f"Доска импортирована из {filename}")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось импортировать: {str(e)}")

    def search_tasks(self):
        """Поиск по заголовку и описанию всех задач."""
        query = simpledialog.askstring("Поиск", "Введите текст для поиска:")
        if not query:
            return
        query = query.lower()
        results = []
        for col, task in self.model.get_all_tasks():
            if query in task["title"].lower() or query in task["description"].lower():
                results.append((col, task))

        if not results:
            messagebox.showinfo("Поиск", "Ничего не найдено.")
            return

        # Окно результатов
        win = Toplevel(self.root)
        win.title("Результаты поиска")
        win.geometry("600x400")
        win.grab_set()

        frame = ttk.Frame(win)
        frame.pack(fill=BOTH, expand=True, padx=10, pady=10)

        scroll = ttk.Scrollbar(frame)
        scroll.pack(side=RIGHT, fill=Y)
        listbox = Listbox(frame, yscrollcommand=scroll.set, font=("Arial", 10))
        listbox.pack(side=LEFT, fill=BOTH, expand=True)
        scroll.config(command=listbox.yview)

        # Заполняем список
        for col, task in results:
            display = f"[{col}] {task['title']}"
            listbox.insert(END, display)
        # Двойной клик для просмотра задачи
        def on_select(event):
            selection = listbox.curselection()
            if selection:
                idx = selection[0]
                col, task = results[idx]
                messagebox.showinfo("Задача", f"Колонка: {col}\nЗаголовок: {task['title']}\n\nОписание:\n{task['description']}")
        listbox.bind("<Double-Button-1>", on_select)

# ---------------------------- ЗАПУСК ----------------------------
if __name__ == "__main__":
    root = Tk()
    app = KanbanApp(root)
    root.mainloop()