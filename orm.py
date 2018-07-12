from templates import CREATE_TABLE, DROP_TABLE
from templates import SELECT_ALL, SELECT
from templates import INSERT_COLUMNS
from templates import UPDATE, UPDATE_ALL

import helpers


class Base:
    __tablename__ = ''

    def __init__(self, connection, **kwargs):
        fields = helpers.get_fields(self.__class__.__dict__, kwargs)
        helpers.validate_fields(fields)
        self.conn = connection
        self.fields = fields

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
        items = self.fields.items()
        params = helpers.iterate_fields(helpers.parse_column_param, items)
        foreing_keys = [key for key in helpers.iterate_fields(helpers.parse_foreign_keys, items) if key]
        params.extend(foreing_keys)
        self.execute_command(CREATE_TABLE % (table, helpers.join(params)))

    def create_table(self, table, colums):
        self.execute_command(CREATE_TABLE % (table, colums))

    def drop_table(self, table):
        self.execute_command(DROP_TABLE % table)

    def select_all(self):
        field_names = self.fields.keys()
        command = SELECT_ALL % (helpers.join(field_names), self.table)
        rows = self.execute_and_fetch(command)
        return [self.mapped_row_on_object(row, field_names) for row in rows]

    def select_by(self, **args):
        field_names = self.fields.keys()
        params = ["%s='%s'" % (key, value) if isinstance(value, str)
                  else "%s=%s" % (key, value) for (key, value) in args.items()]
        command = SELECT % (helpers.join(field_names), self.table, helpers.join(params, ' AND '))
        rows = self.execute_and_fetch(command)
        return [self.mapped_row_on_object(row, field_names) for row in rows]

    def update_all(self, **args):
        params = ["%s='%s'" % (key, value) if isinstance(value, str)
                  else "%s=%s" % (key, value) for (key, value) in args.items()]
        command = UPDATE_ALL % (self.table, helpers.join(params))
        self.execute_command(command)

    def update_by_id(self, id, **args):
        params = ["%s='%s'" % (key, value) if isinstance(value, str)
                  else "%s=%s" % (key, value) for (key, value) in args.items()]
        command = UPDATE % (self.table, helpers.join(params), 'id={}'.format(id))
        self.execute_command(command)

    def _insert(self, fields):
        values = ["'%s'" % str(x[1]) if isinstance(x[1], str) else str(x[1]) for x in fields.values()]
        command = INSERT_COLUMNS % (self.table,
                                    helpers.join(fields.keys()),
                                    helpers.join(values))
        self.execute_command(command)

    def save(self):
        self._create_table_if_not_exist(self.table)
        self._insert(self.fields)

    def mapped_row_on_object(self, row, field_names):
        count = 0
        arr = {key: None for key in field_names}
        obj = self.__class__(self.conn, **arr)
        for name in field_names:
            setattr(obj, name, row[count])
            count = count + 1
        return obj


