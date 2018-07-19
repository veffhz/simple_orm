from orm import Base
import sqlite3

conn = sqlite3.connect('example.db')


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
    print("users -", [one.username for one in all_users])

    user1 = user.select_by(id=1)
    print("user id 1 -", user1[0].username)

    user2 = user.select_by(id=2, username='joe')
    print("user id 2 and name joe -", user2[0].id)

    user.update_by_id(id=1, username='yyy')

    all_users = user.select_all()
    print("users -", [one.username for one in all_users])

    user.update_all(username='xxx')

    user2 = user.select_by(id=2, condition='OR', username='xxx')
    print("user id 2 or name xxx -", user2[0].id, user2[1].id)

    user.update_by_id(id=1, username='zzz')

    all_users = user.select_all()
    print("users -", [one.username for one in all_users])


def account_test(account):
    all_accounts = account.select_all()
    print("accounts no -", [one.no for one in all_accounts])
    print("accounts joined users -", [one.username for one in all_accounts])

    accounts = account.select_by(id=4)
    print("account id 4 no -", accounts[0].no)

    account.update_by_id(id=4, no=555)

    all_accounts = account.select_all()
    print("accounts -", [one.no for one in all_accounts])

    account.update_all(no=777)

    all_accounts = account.select_all()
    print("accounts -", [one.no for one in all_accounts])

    account.delete_by(id=4)
    account.delete_all()


def run_test():
    user = User(connection=conn, id=1, username='doe')
    user.save()

    user = User(connection=conn, id=2, username='joe')
    user.save()

    user_test(user)

    account = Account(connection=conn, id=4, user_id=1, no=123)
    account.save()

    account = Account(connection=conn, id=5, user_id=2, no=456)
    account.save()

    account_test(account)

    user.drop_table()
    account.drop_table()


if __name__ == "__main__":
    run_test()
