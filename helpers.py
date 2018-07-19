from exceptions import SqlRequiredException


def join_str(to_join, sep=', '):
    return sep.join(to_join)


def parse_column_param(name, param):
    column_type = param[0]
    if len(param) > 1 and 'required' in param[1]:
        return "%s %s %s" % (name, column_type, 'NOT NULL')
    elif len(param) > 1 and 'pk' in param:
        return "%s %s %s" % (name, column_type, 'PRIMARY KEY')
    else:
        return "%s %s" % (name, column_type)


def template_foreign_keys(name, other_table, other_field):
    return 'FOREIGN KEY(%s) REFERENCES %s(%s)' % (name, other_table, other_field)


def parse_foreign_keys(name, param):
    if len(param) == 3 and 'fk' in param[2][0]:
        other_table = param[2][2]
        other_field = param[2][1]
        return name, other_table, other_field


def iterate_fields(func, items):
    return [func(name, param) for name, (param, value) in items]


def validate_fields(fields):
    for name, (param, value) in fields.items():
        if 'required' in param[0][1] and value is None:
            raise SqlRequiredException('Required value {} is not present!'.format(name))


def get_fields(full_dict, kwargs):
    return {key: (column_type, kwargs[key]) for (key, column_type) in full_dict.items()
            if not key.startswith('__') or None}
