import datetime
from pathlib import Path


def singleton(cls):
    instances = {}

    def getinstance(*args, **kwargs):
        p1 = " ".join(args)
        p2 = " ".join(f"{k}={v}" for k, v in kwargs.items())
        key = f"{cls} {p1} {p2}"
        if key not in instances:
            inst = cls(*args, **kwargs)
            instances[key] = inst
            return inst
        return instances[key]

    return getinstance


def catch_exception(func):
    def action(*args, **kwargs):
        try:
            ret = func(*args, **kwargs)
            return ret
        except PermissionError as ex:
            print(f"Permission error: {ex} in {func}")
            exit(1)
        except Exception as ex:
            print(f"Error: {ex} in {func}")

    return action


@singleton
class Logger:
    class LoggerException(Exception):
        pass

    def __init__(self, path=""):
        self.base_path = Path.home() if not path else Path(path)
        self.file = None

    @catch_exception
    def __del__(self):
        if self.file and not self.file.closed:
            self.file.close()

    def __repr__(self):
        return f"{type(self)} {id(self)} path: {self.base_path}"

    @staticmethod
    def current_date() -> str:
        return datetime.datetime.now().strftime("%d.%m.%Y")

    @staticmethod
    def current_time() -> str:
        return datetime.datetime.now().strftime("%H:%M:%S")

    @catch_exception
    def __open_file_log(self, mode: str):
        fname = f"{self.base_path}{'' if self.base_path.name.endswith('/') else '/'}log_{self.current_date()}.log"
        if Path(fname).exists():
            self.file = open(fname, mode, encoding='utf-8')
        else:
            Path(fname).touch()
            self.file = open(fname, mode, encoding='utf-8')

    @catch_exception
    def write_log(self, msg: str):
        self.__open_file_log("a+")
        self.file.write(f"[{self.current_time()}] {msg}\n")
        self.file.close()

    @catch_exception
    def clear_log(self):
        self.__open_file_log("w+")
        self.file.close()

    @catch_exception
    def get_logs(self) -> list:
        self.__open_file_log("r")
        lst = [line.strip() for line in self.file.readlines()]
        self.file.close()
        return lst

    @catch_exception
    def get_last_events(self):
        lst = self.get_logs()
        return lst[-1] if len(lst) > 0 else ""

    @catch_exception
    def get_all_logs(self):
        return [line.name for line in self.base_path.glob("log_*.*.*.log")]


if __name__ == '__main__':
    l1 = Logger("")
    l2 = Logger("")
    print(l1, l2)

    l1.write_log("test test")
    print(l1.get_last_events())
    print(l1.get_logs())
    print(l2.get_all_logs())
    # l2.clear_log()
