"""
The SQL query templates for base statements.
"""

CREATE_TABLE = 'CREATE TABLE IF NOT EXISTS %s (%s);'
DROP_TABLE = 'DROP TABLE %s;'

SELECT_ALL = 'SELECT * FROM %s %s;'
SELECT = 'SELECT %s FROM %s %s WHERE %s;'

JOIN = 'INNER JOIN %s ON %s.%s = %s.%s'

INSERT_COLUMNS = 'INSERT INTO %s (%s) VALUES (%s);'

UPDATE = 'UPDATE %s SET %s WHERE %s;'
UPDATE_ALL = 'UPDATE %s SET %s;'

DELETE = 'DELETE FROM %s WHERE %s;'
DELETE_ALL = 'DELETE FROM %s;'

