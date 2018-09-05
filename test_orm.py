import logging
import sqlite3

from orm import Base


class User(Base):
    __tablename__ = 'users'

    id = ('int', 'pk')
    username = ('char(256)', 'required')


class Account(Base):
    __tablename__ = 'accounts'

    id = ('int', 'pk')
    user_id = ('int', 'required', ('fk', 'id', 'users'))
    no = ('int', 'required')


def user_test(user):
    all_users = user.select_all()
    logging.info("users - %s" % [user.username for user in all_users])

    user1 = user.select_by(id=1)
    logging.info("user id 1 - %s" % user1[0].username)

    user2 = user.select_by(id=2, username='joe')
    logging.info("user id 2 and name joe - %s" % user2[0].id)

    user.update_by_id(id=1, username='yyy')

    all_users = user.select_all()
    logging.info("users - %s" % [one.username for one in all_users])

    user.update_all(username='xxx')

    user2 = user.select_by(id=2, condition='OR', username='xxx')
    logging.info("user id 2 or name xxx - %s %s" % (user2[0].id, user2[1].id))

    user.update_by_id(id=1, username='zzz')

    all_users = user.select_all()
    logging.info("users - %s " % [one.username for one in all_users])


def account_test(account):
    all_accounts = account.select_all()
    logging.info("accounts no - %s" % [one.no for one in all_accounts])
    logging.info("accounts joined users - %s" % [one.username for one in all_accounts])

    accounts = account.select_by(id=4)
    logging.info("account id 4 no - %s" % accounts[0].no)

    account.update_by_id(id=4, no=555)

    all_accounts = account.select_all()
    logging.info("accounts - %s" % [one.no for one in all_accounts])

    account.update_all(no=777)

    all_accounts = account.select_all()
    logging.info("accounts - %s" % [one.no for one in all_accounts])

    account.delete_by(id=4)
    account.delete_all()


def run_test():
    user = User(id=1, username='doe')
    user.create_table_by_fields()
    user.save()

    user = User(id=2, username='joe')
    user.save()

    user_test(user)

    account = Account(id=4, user_id=1, no=123)
    account.create_table_by_fields()
    account.save()

    account = Account(id=5, user_id=2, no=456)
    account.save()

    account_test(account)

    user.drop_table()
    account.drop_table()


def init_db_connection():
    connection = sqlite3.connect('example.db')
    Base.set_connection(connection)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(message)s')
    init_db_connection()
    run_test()
