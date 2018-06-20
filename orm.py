from templates import CREATE_TABLE, DROP_TABLE
from templates import SELECT_ALL, SELECT
from templates import INSERT_COLUMNS


class HelperMixin(object):
    def join(self, to_join, sep=', '):
        return sep.join(to_join)


class Base(HelperMixin, object):
    __tablename__ = ''

    def __init__(self, connection, **kwargs):
        self.conn = connection
        self.kwargs = kwargs
        self.fields = self.get_fields()
        self._create_table_if_not_exist(self.table)

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.conn.close()

    @property
    def table(self):
        return self.__class__.__tablename__

    def get_fields(self):
        old_dict = self.__class__.__dict__
        return {key: value for (key, value) in old_dict.items()
                if not key.startswith('__') or None}

    def _create_table_if_not_exist(self, table):
        params = []

        for name, (f_type, null_or_key) in self.fields.items():
            if null_or_key == 'required':
                field = "%s %s %s" % (name, f_type, 'NOT NULL')
            elif null_or_key == 'pk':
                field = "%s %s %s" % (name, f_type, 'PRIMARY KEY')
            else:
                field = "%s %s" % (name, f_type)
            params.append(field)

        c = self.conn.cursor()
        c.execute(CREATE_TABLE % (table, self.join(params)))
        self.conn.commit()

    def create_table(self, table):
        c = self.conn.cursor()
        c.execute(DROP_TABLE % table)
        self.conn.commit()

    def drop_table(self, table):
        c = self.conn.cursor()
        c.execute(DROP_TABLE % table)
        self.conn.commit()

    def select_all(self):
        field_names = self.fields.keys()
        command = SELECT_ALL % (self.join(field_names), self.table)
        c = self.conn.cursor()
        c.execute(command)
        return c.fetchall()

    def select_by(self, **args):
        field_names = self.fields.keys()
        params = ["%s='%s'" % (key, value) if isinstance(value, str)
                  else "%s=%s" % (key, value) for (key, value) in args.items()]
        command = SELECT % (self.join(field_names), self.table, self.join(params, ' AND '))
        c = self.conn.cursor()
        c.execute(command)
        return c.fetchall()

    def _insert(self, kwargs):
        values = ["'%s'" % str(x) if isinstance(x, str) else str(x) for x in kwargs.values()]
        command = INSERT_COLUMNS % (self.table,
                                    self.join(kwargs.keys()),
                                    self.join(values))
        c = self.conn.cursor()
        c.execute(command)
        self.conn.commit()

    def save(self):
        if len(self.kwargs) > 1:
            self._insert(self.kwargs)
