from sqlite3 import OperationalError

from exceptions import SqlException
from templates import CREATE_TABLE, DROP_TABLE
from templates import SELECT_ALL, SELECT
from templates import INSERT_COLUMNS
from templates import UPDATE, UPDATE_ALL
from templates import DELETE, DELETE_ALL
from templates import JOIN

import helpers


class Base:
    __tablename__ = ''

    def __init__(self, connection, **kwargs):
        fields = helpers.get_fields(self.__class__.__dict__, kwargs)
        helpers.validate_fields(fields)
        self.conn = connection
        self.fields = fields
        self.foreign_keys = []

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.conn.close()

    @property
    def table(self):
        return self.__class__.__tablename__

    def execute_command(self, command):
        c = self.conn.cursor()
        try:
            c.execute(command)
        except OperationalError as error:
            raise SqlException(error)
        else:
            result = c.fetchall()
            self.conn.commit()
            return result

    def execute_and_fetch(self, command):
        c = self.conn.cursor()
        try:
            c.execute(command)
        except OperationalError as error:
            raise SqlException(error)
        else:
            result = c.fetchall(), next(zip(*c.description))
            self.conn.commit()
            return result

    def __create_table_if_not_exist(self, table):
        items = self.fields.items()
        params = helpers.iterate_fields(helpers.parse_column_param, items)
        self.foreign_keys = [key for key in helpers.iterate_fields(helpers.parse_foreign_keys, items) if key]
        foreign_keys_string = [helpers.template_foreign_keys(name, other_table, other_field)
                               for name, other_table, other_field in self.foreign_keys]
        params.extend(foreign_keys_string)
        self.execute_command(CREATE_TABLE % (table, helpers.join_str(params)))

    def create_table(self, table, columns):
        self.execute_command(CREATE_TABLE % (table, columns))

    def drop_table(self):
        self.__drop_table(self.table)

    def __drop_table(self, table):
        self.execute_command(DROP_TABLE % table)

    def select_all(self):
        join_tables = []
        if len(self.foreign_keys) > 0:
            join_tables = [JOIN % (table, table, field, self.table, name)
                           for name, table, field in self.foreign_keys]

        command = SELECT_ALL % (self.table, helpers.join_str(join_tables))
        rows = self.execute_and_fetch(command)
        return [self.mapped_row_on_object(row, rows[1]) for row in rows[0]]

    def select_by(self, condition='AND', **args):
        field_names = list(self.fields.keys())
        params = ["%s.%s='%s'" % (self.table, key, value) if isinstance(value, str)
                  else "%s.%s=%s" % (self.table, key, value) for (key, value) in args.items()]

        command = SELECT % ('%s.%s' % (self.table, helpers.join_str(field_names)), self.table,
                            '', helpers.join_str(params, ' %s ' % condition))
        rows = self.execute_and_fetch(command)
        return [self.mapped_row_on_object(row, rows[1]) for row in rows[0]]

    def update_all(self, **args):
        params = ["%s='%s'" % (key, value) if isinstance(value, str)
                  else "%s=%s" % (key, value) for (key, value) in args.items()]
        command = UPDATE_ALL % (self.table, helpers.join_str(params))
        self.execute_command(command)

    def update_by_id(self, id, **args):
        params = ["%s='%s'" % (key, value) if isinstance(value, str)
                  else "%s=%s" % (key, value) for (key, value) in args.items()]
        command = UPDATE % (self.table, helpers.join_str(params), 'id={}'.format(id))
        self.execute_command(command)

    def __insert(self, fields):
        values = ["'%s'" % str(value[1]) if isinstance(value[1], str)
                  else str(value[1]) for value in fields.values()]
        command = INSERT_COLUMNS % (self.table,
                                    helpers.join_str(fields.keys()),
                                    helpers.join_str(values))
        self.execute_command(command)

    def delete_all(self):
        self.execute_command(DELETE_ALL % self.table)

    def delete_by(self, condition='AND', **args):
        params = ["%s.%s='%s'" % (self.table, key, value) if isinstance(value, str)
                  else "%s.%s=%s" % (self.table, key, value) for (key, value) in args.items()]

        command = DELETE % (self.table, helpers.join_str(params, ' %s ' % condition))
        self.execute_command(command)

    def save(self):
        self.__create_table_if_not_exist(self.table)
        self.__insert(self.fields)

    def mapped_row_on_object(self, row, field_names):
        count = 0
        arr = {key: None for key in field_names}
        obj = self.__class__(self.conn, **arr)
        for name in field_names:
            setattr(obj, name, row[count])
            count = count + 1
        return obj


