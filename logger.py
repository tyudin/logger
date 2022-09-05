import datetime
from pathlib import Path
from typing import Callable


def singleton(cls: Callable):
    """ Декоратор синглтон - один инстанс для всех объектов класса cls """
    instances = {}  # хранилище объектов класса

    def getinstance(*args, **kwargs):
        p1 = " ".join(args)
        p2 = " ".join(f"{k}={v}" for k, v in kwargs.items())
        key = f"{cls} {p1} {p2}"  # ключ для хранилища содержит список всех параметров инициализации
        if key not in instances:
            inst = cls(*args, **kwargs)  # создали объект класса cls
            instances[key] = inst
            return inst
        return instances[key]

    return getinstance


def catch_exception(func: Callable):
    """ Декоратор - перехватчик ошибок """
    def action(*args, **kwargs):
        try:
            ret = func(*args, **kwargs)
            return ret
        except PermissionError as ex:
            print(f"Permission error: {ex} in {func}")
            exit(1)  # Выходим с кодом 1 при ошибке доступа
        except Exception as ex:
            print(f"Error: {ex} in {func}")

    return action


@singleton
class Logger:
    @catch_exception
    def __init__(self, base_path: str = ""):
        """ base_path: str - каталог в котором создавать файлы логов """
        self.base_path = Path.home() if not base_path else Path(base_path)
        self.file = None
        self.last_event = ""

    @catch_exception
    def __del__(self):
        if self.file and not self.file.closed:
            # Если файл еще открыт, то закроем его
            self.file.close()

    def __repr__(self):
        return f"type: {type(self)} id: {id(self)} base path: {self.base_path}"

    @staticmethod
    def current_date() -> str:
        return datetime.datetime.now().strftime("%d.%m.%Y")

    @staticmethod
    def current_time() -> str:
        return datetime.datetime.now().strftime("%H:%M:%S")

    @catch_exception
    def __open_file_log(self, mode: str):
        """ Открываем файл лога с нужным режимом (mode) """
        fname = f"{self.base_path}{'' if self.base_path.name.endswith('/') else '/'}log_{self.current_date()}"
        if Path(fname).exists():
            self.file = open(fname, mode, encoding='utf-8')
        else:
            # если файла лога еще нет, то создадим пустой
            Path(fname).touch()
            self.file = open(fname, mode, encoding='utf-8')

    @catch_exception
    def write_log(self, msg: str):
        """ Запись события в файл лога """
        self.last_event = f"[{self.current_time()}] {msg}"
        self.__open_file_log("a+")
        self.file.write(f"{self.last_event}\n")
        self.file.close()

    @catch_exception
    def clear_log(self):
        """ Очистка файла - лога """
        self.__open_file_log("w+")
        self.file.close()

    @catch_exception
    def get_logs(self) -> list:
        """ Получение записей из текщего файла-лога в виде списка """
        self.__open_file_log("r")
        lst = [line.strip() for line in self.file.readlines()]  # уберем символ перевода каретки вконце строки
        self.file.close()
        return lst

    @catch_exception
    def get_last_event(self) -> str:
        """ Выдача последнего события """
        return self.last_event

    @catch_exception
    def get_all_logs(self) -> list:
        """ Выдача списка файлов-логов """
        return [line.name for line in self.base_path.glob("log_??.??.????")]


if __name__ == '__main__':
    # l1 = Logger("..")
    l1 = Logger()
    l2 = Logger()
    print(l1, l2)  # id объектов должны совпадать (если применен декоратор singleton)

    # еще один вариант проверки
    assert id(l1) == id(l2), "Тест не пройден: Объекты разные!"
    print("Тест пройден - объекты одинаковые")

    l1.write_log("test test")
    print(l1.get_last_event())
    print(l1.get_logs())
    print(l2.get_all_logs())
    # l2.clear_log()
