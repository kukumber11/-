import tkinter as tk
from tkinter import ttk, messagebox
import json
import os

class BookTracker:
    def __init__(self, root):
        self.root = root
        self.root.title("Трекер прочитанных книг")
        self.root.geometry("850x600")

        self.data_file = "books.json"
        self.books = self.load_data()
        self.genres = ["Фантастика", "Фэнтези", "Детектив", "Классика", "Роман", "Научпоп", "Биография", "Другое"]

        # --- Фреймы ---
        input_frame = ttk.LabelFrame(root, text="Добавить книгу", padding=10)
        input_frame.pack(fill=tk.X, padx=10, pady=5)

        filter_frame = ttk.LabelFrame(root, text="Фильтрация", padding=10)
        filter_frame.pack(fill=tk.X, padx=10, pady=5)

        tree_frame = ttk.Frame(root, padding=10)
        tree_frame.pack(fill=tk.BOTH, expand=True)

        # --- Поля ввода (Добавление) ---
        ttk.Label(input_frame, text="Название:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.title_entry = ttk.Entry(input_frame, width=25)
        self.title_entry.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(input_frame, text="Автор:").grid(row=0, column=2, padx=5, pady=5, sticky="w")
        self.author_entry = ttk.Entry(input_frame, width=20)
        self.author_entry.grid(row=0, column=3, padx=5, pady=5)

        ttk.Label(input_frame, text="Жанр:").grid(row=0, column=4, padx=5, pady=5, sticky="w")
        self.genre_combo = ttk.Combobox(input_frame, values=self.genres, width=15)
        self.genre_combo.grid(row=0, column=5, padx=5, pady=5)

        ttk.Label(input_frame, text="Страниц:").grid(row=0, column=6, padx=5, pady=5, sticky="w")
        self.pages_entry = ttk.Entry(input_frame, width=8)
        self.pages_entry.grid(row=0, column=7, padx=5, pady=5)

        add_button = ttk.Button(input_frame, text="Добавить книгу", command=self.add_book)
        add_button.grid(row=0, column=8, padx=10, pady=5)

        # --- Поля ввода (Фильтры) ---
        ttk.Label(filter_frame, text="Жанр:").grid(row=0, column=0, padx=5, pady=5)
        self.filter_genre_combo = ttk.Combobox(filter_frame, values=["Все"] + self.genres, width=15)
        self.filter_genre_combo.grid(row=0, column=1, padx=5)
        self.filter_genre_combo.set("Все")

        ttk.Label(filter_frame, text="Минимум страниц:").grid(row=0, column=2, padx=5, pady=5)
        self.filter_pages_entry = ttk.Entry(filter_frame, width=8)
        self.filter_pages_entry.grid(row=0, column=3, padx=5)

        filter_button = ttk.Button(filter_frame, text="Применить", command=self.apply_filter)
        filter_button.grid(row=0, column=4, padx=10, pady=5)

        reset_button = ttk.Button(filter_frame, text="Сбросить", command=self.reset_filters)
        reset_button.grid(row=0, column=5, padx=5, pady=5)

        # --- Таблица ---
        self.tree = ttk.Treeview(tree_frame, columns=("title", "author", "genre", "pages"), show="headings")
        self.tree.heading("title", text="Название книги")
        self.tree.heading("author", text="Автор")
        self.tree.heading("genre", text="Жанр")
        self.tree.heading("pages", text="Количество страниц")

        self.tree.column("title", width=250)
        self.tree.column("author", width=200)
        self.tree.column("genre", width=150)
        self.tree.column("pages", width=120, anchor=tk.CENTER)

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.populate_table(self.books)

    def add_book(self):
        title = self.title_entry.get().strip()
        author = self.author_entry.get().strip()
        genre = self.genre_combo.get().strip()
        pages_str = self.pages_entry.get().strip()

        # Валидация пустых полей
        if not title or not author or not genre or not pages_str:
            messagebox.showerror("Ошибка ввода", "Все поля должны быть заполнены.")
            return

        # Валидация числа страниц
        try:
            pages = int(pages_str)
            if pages <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Ошибка ввода", "Количество страниц должно быть положительным числом.")
            return

        new_book = {"title": title, "author": author, "genre": genre, "pages": pages}
        self.books.append(new_book)
        self.save_data()
        self.apply_filter()

        # Очистка формы
        self.title_entry.delete(0, tk.END)
        self.author_entry.delete(0, tk.END)
        self.genre_combo.set('')
        self.pages_entry.delete(0, tk.END)

    def populate_table(self, data_to_show):
        for i in self.tree.get_children():
            self.tree.delete(i)
        
        for book in data_to_show:
            self.tree.insert("", tk.END, values=(book["title"], book["author"], book["genre"], book["pages"]))

    def apply_filter(self):
        genre_filter = self.filter_genre_combo.get()
        min_pages_str = self.filter_pages_entry.get().strip()

        filtered_data = self.books

        # Фильтр по жанру
        if genre_filter and genre_filter != "Все":
            filtered_data = [b for b in filtered_data if b['genre'] == genre_filter]

        # Фильтр по страницам
        if min_pages_str:
            try:
                min_pages = int(min_pages_str)
                filtered_data = [b for b in filtered_data if b['pages'] >= min_pages]
            except ValueError:
                messagebox.showwarning("Фильтр", "Минимум страниц должен быть числом. Фильтр по страницам проигнорирован.")

        self.populate_table(filtered_data)

    def reset_filters(self):
        self.filter_genre_combo.set("Все")
        self.filter_pages_entry.delete(0, tk.END)
        self.populate_table(self.books)

    def load_data(self):
        if not os.path.exists(self.data_file):
            return []
        try:
            with open(self.data_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return []

    def save_data(self):
        with open(self.data_file, "w", encoding="utf-8") as f:
            json.dump(self.books, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    root = tk.Tk()
    app = BookTracker(root)
    root.mainloop()