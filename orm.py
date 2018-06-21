from exceptions import SqlRequiredException

from templates import CREATE_TABLE, DROP_TABLE
from templates import SELECT_ALL, SELECT
from templates import INSERT_COLUMNS
from templates import UPDATE, UPDATE_ALL


class Helper:
    @staticmethod
    def join(to_join, sep=', '):
        return sep.join(to_join)

    @staticmethod
    def parse_column_param(name, param):
        column_type = param[0]
        if len(param) == 2 and 'required' in param[1]:
            return "%s %s %s" % (name, column_type, 'NOT NULL')
        elif len(param) == 2 and 'pk' in param:
            return "%s %s %s" % (name, column_type, 'PRIMARY KEY')
        else:
            return "%s %s" % (name, column_type)

    @staticmethod
    def validate_fields(fields):
        for name, (param, value) in fields.items():
            if 'required' in param[0][1] and value is None:
                raise SqlRequiredException('Required value {} is not present!'.format(name))

    @staticmethod
    def get_fields(full_dict, kwargs):
        return {key: (column_type, kwargs[key]) for (key, column_type) in full_dict.items()
                if not key.startswith('__') or None}


class Base:
    __tablename__ = ''

    def __init__(self, connection, **kwargs):
        fields = Helper.get_fields(self.__class__.__dict__, kwargs)
        Helper.validate_fields(fields)
        self.conn = connection
        self.fields = fields
        self._create_table_if_not_exist(self.table)

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.conn.close()

    @property
    def table(self):
        return self.__class__.__tablename__

    def execute_command(self, command):
        c = self.conn.cursor()
        c.execute(command)
        self.conn.commit()

    def execute_and_fetch(self, command):
        c = self.conn.cursor()
        c.execute(command)
        return c.fetchall()

    def _create_table_if_not_exist(self, table):
        params = [Helper.parse_column_param(name, param) for name, (param, value) in self.fields.items()]
        self.execute_command(CREATE_TABLE % (table, Helper.join(params)))

    def create_table(self, table, colums):
        self.execute_command(CREATE_TABLE % (table, colums))

    def drop_table(self, table):
        self.execute_command(DROP_TABLE % table)

    def select_all(self):
        field_names = self.fields.keys()
        command = SELECT_ALL % (Helper.join(field_names), self.table)
        rows = self.execute_and_fetch(command)
        return [self.mapped_row_on_object(row, field_names) for row in rows]

    def select_by(self, **args):
        field_names = self.fields.keys()
        params = ["%s='%s'" % (key, value) if isinstance(value, str)
                  else "%s=%s" % (key, value) for (key, value) in args.items()]
        command = SELECT % (Helper.join(field_names), self.table, Helper.join(params, ' AND '))
        rows = self.execute_and_fetch(command)
        return [self.mapped_row_on_object(row, field_names) for row in rows]

    def update_all(self, **args):
        params = ["%s='%s'" % (key, value) if isinstance(value, str)
                  else "%s=%s" % (key, value) for (key, value) in args.items()]
        command = UPDATE_ALL % (self.table, Helper.join(params))
        self.execute_command(command)

    def update_by_id(self, id, **args):
        params = ["%s='%s'" % (key, value) if isinstance(value, str)
                  else "%s=%s" % (key, value) for (key, value) in args.items()]
        command = UPDATE % (self.table, Helper.join(params), 'id={}'.format(id))
        self.execute_command(command)

    def _insert(self, fields):
        values = ["'%s'" % str(x[1]) if isinstance(x[1], str) else str(x[1]) for x in fields.values()]
        command = INSERT_COLUMNS % (self.table,
                                    Helper.join(fields.keys()),
                                    Helper.join(values))
        self.execute_command(command)

    def save(self):
        self._insert(self.fields)

    def mapped_row_on_object(self, row, field_names):
        count = 0
        arr = {key: None for key in field_names}
        obj = self.__class__(self.conn, **arr)
        for name in field_names:
            setattr(obj, name, row[count])
            count = count + 1
        return obj


