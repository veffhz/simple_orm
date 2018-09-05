import logging
from exceptions import SqlRequiredException


def join_str(to_join, sep=', '):
    return sep.join(to_join)


def parse_column_param(name, param):
    if len(param) == 0:
        logging.error('Empty param in parse_column_param!')
        return None
    column_type = param[0]
    if len(param) == 1:
        return "%s %s" % (name, column_type)
    elif len(param) > 1:
        column_option = ''
        if 'required' in param[1]:
            column_option = 'NOT NULL'
        elif 'pk' in param:
            column_option = 'PRIMARY KEY'
        return "%s %s %s" % (name, column_type, column_option)


def template_foreign_keys(name, other_table, other_field):
    return 'FOREIGN KEY(%s) REFERENCES %s(%s)' % (name, other_table, other_field)


def parse_foreign_keys(name, param):
    try:
        if len(param) == 3 and 'fk' in param[2][0]:
            other_table = param[2][2]
            other_field = param[2][1]
            return name, other_table, other_field
    except IndexError as e:
        logging.error('Error at parse', exc_info=e)


def iterate_fields(func, items):
    return [func(name, param) for name, (param, value) in items]


def validate_fields(fields):
    for name, (param, value) in fields.items():
        if 'required' in param[0][1] and value is None:
            raise SqlRequiredException('Required value %s is not present!' % name)


def get_fields(full_dict, kwargs):
    return {key: (column_type, kwargs[key]) for (key, column_type) in full_dict.items()
            if not key.startswith('__') or None}
