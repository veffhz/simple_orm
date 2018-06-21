from orm import Base
import sqlite3

conn = sqlite3.connect('example.db')


class User(Base):
    __tablename__ = 'posts'
    id = ('int', 'pk')
    username = ('char(256)', 'required')


if __name__ == "__main__":
    user = User(connection=conn, id=1, username='doe')
    user.save()

    user = User(connection=conn, id=2, username='joe')
    user.save()

    all = user.select_all()
    print(all)
    data = user.select_by(id=1)
    print(data)
    data = user.select_by(id=2, username='joe')
    print(data[0].id)
    user.update_by_id(id=1, username='yyy')
    user.update_all(username='xxx')
    user.drop_table('posts')
