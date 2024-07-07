import redis


class RedisDB:
    def __init__(
        self, host: str, port: int = 6379, db: int = 0, decode: bool = False
    ) -> object:
        self.conn = redis.StrictRedis(
            host=host, port=port, db=db, decode_responses=decode
        )

    def save_record(self, record: dict) -> None:
        """Создаём запись хеша (в ОЗУ)"""
        for k, v in record.items():
            self.conn.hset(record["username"], k, v)

    def load_kv(self, name: str, key: str) -> str:
        """Считываем значение определённого ключа.
        При отсутствии внешнего ключа name возвращает None
        """
        return self.conn.hget(name, key)

    def load_hash(self, name: str) -> dict:
        """Считываем все ключи=значения хеша"""
        return self.conn.hgetall(name)

    def get_size(self) -> int:
        """Выводим количество пар ключ=значение в БД"""
        return self.conn.dbsize()

    def write_db(self) -> None:
        """Сохраняем все данные в памяти на диск.
        создаётся форк БД: родительский процесс продолжит обслуживание клиентов, а дочерний выгрузит
        бэкап базы данных. Если в период обработки команды bgsave будут выполняться изменения,
        они не попадут в снапшот."""
        self.conn.bgsave()

    def flush_db(self) -> None:
        """очистить всю выбраную базу"""
        self.conn.flushdb()

    def get_keys(self) -> list:
        """Выводим ключи (внешние) в БД"""
        return self.conn.keys()

    def all_key_value(self) -> list:
        """Выводит все key=value из БД, кроме пароля."""
        all_hash = []
        for i in self.get_keys():
            record = self.load_hash(i)
            all_hash.append({"username": record["username"], "role": record["role"]})
        return all_hash
