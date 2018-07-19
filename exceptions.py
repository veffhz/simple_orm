
class SqlException(Exception):
    def __init__(self, message=None):
        self.message = 'Ошибка Sqlite: {}'.format(message)

    def __str__(self):
        return self.message


class SqlRequiredException(SqlException):
    def __init__(self, message=None):
        self.message = 'Ошибка Sqlite: {}'.format(message)

    def __str__(self):
        return self.message


class SqlColumnException(SqlException):
    def __init__(self, message=None):
        self.message = 'Ошибка Sqlite: {}'.format(message)

    def __str__(self):
        return self.message
