class SqlException(Exception):
    """
    Base simple orm exception
    """
    def __init__(self, message=None):
        self.message = 'Sqlite exception: %s' % message

    def __str__(self):
        return self.message


class SqlRequiredException(SqlException):
    """
    Not found required value exception
    """
    def __init__(self, message=None):
        self.message = 'Sqlite exception: %s' % message

    def __str__(self):
        return self.message


class SqlColumnException(SqlException):
    def __init__(self, message=None):
        self.message = 'Sqlite exception: %s' % message

    def __str__(self):
        return self.message
