from tkinter import ttk, scrolledtext, Tk, END, Toplevel
import threading
import time
from tkinter import messagebox
import psutil
from db_config import DB_config
import re


write_en, stop, check = False, False, 0


def is_valid(newval):
    return re.match(r"^\d{0,3}$", newval) is not None


def error(text_send):
    message = text_send
    messagebox.showerror("Ошибка", message=message)


def second_thread(thread, func):
    if not thread.is_alive():
        a_thread = None
        a_thread = threading.Thread(target=func)
        a_thread.start()


def journal():
    jrl = Journal()
    db = DB_config()
    try:
        read, area = db.read()
        jrl.journal_place()
        jrl.completion_journal(read, area)
    except TypeError:
        jrl.journal_window.destroy()
        error("В схеме базы данных нет таблиц")


class Main_page:

    def __init__(self):
        self.update_cpu_thread = threading.Thread(target=self.processor)
        self.update_memory_thread = threading.Thread(target=self.memory_all)
        self.update_hdd_thread = threading.Thread(target=self.hdd_all)
        self.timer_thread = threading.Thread(target=self.timer)
        self.page_loading_thread = threading.Thread(target=self.page_loading)
        self.root = Tk()
        self.root.title('System_monitor')
        self.root.geometry('1150x700')
        self.root.resizable(0, 0)
        self.title_label = ttk.Label(
            text="Уровень загруженности:",
            font=("Courier New", 11)
        )
        self.close_button = ttk.Button(
            self.root,
            text='Выход',
            command=self.on_close
        )
        self.close_button.place(x=1015, y=15)
        self.write_button = ttk.Button(
            self.root,
            text='Начать запись',
            command=self.write_to_db
        )
        self.journal_button = ttk.Button(
            self.root,
            text='Журнал',
            command=journal
        )
        self.journal_button.place(x=920, y=15)
        int_check = (self.root.register(is_valid), "%P")
        self.update_label = ttk.Label(
            text="Обновление:",
            font=("Courier New", 11)
        )
        self.update_entry = ttk.Entry(
            validate="key",
            validatecommand=int_check,
            width=4,
            font=("Courier New", 11)
        )
        self.update_lab_sec = ttk.Label(
            text="сек.",
            font=("Courier New", 11)
        )
        self.timer_label = ttk.Label(
            font=("Courier New", 11),
            compound="left"
        )
        self.loading_label = ttk.Label(
            font=("Courier New", 11),
            compound="left"
        )
        self.proc_label = ttk.Label(self.root, font=("Courier New", 11))
        self.proc_label.place(x=170, y=100)
        self.ram_label = ttk.Label(font=("Courier New", 11))
        self.ram_label.place(x=170, y=150)
        self.rom_label = ttk.Label(font=("Courier New", 11))
        self.rom_label.place(x=170, y=200)
        self.update_entry.insert(0, "1")
        self.db = DB_config()
        self.start_threads()
        self.root.mainloop()

    def page_loading(self):
        while not self.proc_label['text']:
            self.loading_label.place(x=500, y=360)
            self.journal_button.configure(state="disabled")
            self.loading_label['text'] = 'Собираем информацию . . .'
        else:
            self.update_label.place(x=650, y=23)
            self.update_entry.place(x=760, y=23)
            self.update_lab_sec.place(x=800, y=23)
            self.title_label.place(x=170, y=50)
            self.write_button.place(x=450, y=600)
            self.journal_button.configure(state="active")
            self.loading_label.place_forget()

    def processor(self):
        while True:
            try:
                update_second = int(self.update_entry.get())
            except ValueError:
                update_second = 1
            proc = psutil.cpu_percent(4)
            time.sleep(update_second)
            self.proc_label.config(text=f"ЦПУ: {proc}")

    def memory_all(self):
        global write_en
        while True:
            try:
                update_second = int(self.update_entry.get())
            except ValueError:
                update_second = 1
            memory = psutil.virtual_memory()
            time.sleep(update_second)
            self.ram_label.config(
                text=f"ОЗУ: "
                     f"{memory.available // 1000000000}"
                     f" GB  /  "
                     f"{memory.total // 1000000000}"
                     f" GB"
            )
            if write_en is True:
                write = DB_config().write(
                    cpu=self.proc_label['text'],
                    ram=self.ram_label['text'],
                    rom=self.rom_label['text']
                )
                if write is False:
                    error("Ошибка записи в БД")
                    self.stop_write()

    def hdd_all(self):
        while True:
            try:
                update_second = int(self.update_entry.get())
            except ValueError:
                update_second = 1
            time.sleep(update_second)
            hdd = psutil.disk_usage('/')
            self.rom_label.config(
                text=f"ПЗУ: {hdd.free // 1000000000} GB / "
                     f"{hdd.total // 1000000000} GB"
            )

    def on_close(self):
        message = "Вы уверены, что хотите закрыть это окно?"
        if messagebox.askokcancel("Выход из программы", message=message):
            self.root.destroy()

    def write_to_db(self):
        global check
        if check == 0:
            self.db.close_connect()
            self.start_write()
        elif check == 1:
            self.db.close_connect()
            self.stop_write()

    def start_write(self):
        global write_en, stop, check
        write_en, stop, check = True, False, 1
        self.write_button.config(text="Остановить запись")
        self.journal_button.configure(state="disabled")
        self.start_timer_threads()

    def stop_write(self):
        global write_en, stop, check
        write_en, stop, check = False, True, 0
        self.write_button.config(text="Начать запись")
        self.journal_button.configure(state="active")
        self.timer_label.config(text="")
        self.timer_label.place_forget()

    def timer(self):
        self.timer_label.place(x=500, y=560)
        self.timer_label.config(text="")
        m, s = 0, 0
        global stop, check
        while stop is False:
            time.sleep(1)
            s += 1
            if s == 60:
                m += 1
                s = 0
            min_sec_format = '{:02d}:{:02d}'.format(m, s)
            self.timer_label.config(text=min_sec_format)

    def start_threads(self):
        print('yes')
        second_thread(self.page_loading_thread, self.page_loading)
        second_thread(self.update_cpu_thread, self.processor)
        second_thread(self.update_memory_thread, self.memory_all)
        second_thread(self.update_hdd_thread, self.hdd_all)

    def start_timer_threads(self):
        second_thread(self.timer_thread, self.timer)


class Journal:

    def __init__(self):
        self.journal_window = Toplevel()
        self.journal_window.title('System_monitor')
        self.journal_window.geometry('900x500')
        self.journal_window.resizable(0, 0)
        self.journal_text = scrolledtext.ScrolledText(
            self.journal_window,
            width=83,
            height=17,
            font=("Times New Roman", 15)
        )
        ttk.Button(
            self.journal_window,
            text='Закрыть',
            command=self.journal_window.destroy
        ).place(x=795, y=15)
        ttk.Button(
            self.journal_window,
            text='Очистить',
            command=self.clear_journal
        ).place(x=595, y=15)
        ttk.Label(
            self.journal_window,
            text="Журнал",
            font=("Times New Roman", 15),
            background='yellow',
            foreground="black"
        ).place(x=410, y=15)
        self.db = DB_config()

    def journal_place(self):
        self.journal_text.place(x=25, y=65)

    def completion_journal(self, read, items):
        if read is True:
            for i in range(0, len(items)):
                item = items[i]
                self.journal_text.insert(
                    END,
                    f"{item[0]} -  "
                    f"{item[1]}  |  "
                    f"{item[2]}  |  "
                    f"{item[3]}\n")
            self.journal_text.configure(state='disabled')
        else:
            error("Ошибка загрузки БД")
            self.journal_window.destroy()

    def clear_journal(self):
        self.journal_text.place_forget()
        if self.db.delete() is True:
            self.journal_text.delete(END, "")
        else:
            self.journal_window.destroy()
            error("В схеме базы данных нет таблиц")


Main_page()
