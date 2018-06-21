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
        self.fields = self.get_fields(kwargs)
        self._create_table_if_not_exist(self.table)

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.conn.close()

    @property
    def table(self):
        return self.__class__.__tablename__

    def get_fields(self, kwargs):
        full_dict = self.__class__.__dict__
        return {key: (value, kwargs[key]) for (key, value) in full_dict.items()
                if not key.startswith('__') or None}

    def _create_table_if_not_exist(self, table):
        params = []

        for name, param in self.fields.items():
            field = self.parse_column_param(name, param)
            params.append(field)

        c = self.conn.cursor()
        c.execute(CREATE_TABLE % (table, self.join(params)))
        self.conn.commit()

    def parse_column_param(self, name, param):
        column_type = self.join(param[0])
        if len(param) == 2 and 'required' in param:
            return "%s %s %s" % (name, column_type, 'NOT NULL')
        elif len(param) == 2 and 'pk' in param:
            return "%s %s %s" % (name, column_type, 'PRIMARY KEY')
        else:
            return "%s %s" % (name, column_type)

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

    def _insert(self, fields):
        values = ["'%s'" % str(x[1]) if isinstance(x[1], str) else str(x[1]) for x in fields.values()]
        command = INSERT_COLUMNS % (self.table,
                                    self.join(fields.keys()),
                                    self.join(values))
        c = self.conn.cursor()
        c.execute(command)
        self.conn.commit()

    def save(self):
        self._insert(self.fields)
