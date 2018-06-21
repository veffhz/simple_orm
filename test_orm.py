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
    all = user.select_all()
    print(all)
    data = user.select_by(id=1)
    print(data)
    data = user.select_by(id=1, username='doe')
    print(data[0].id)
    user.drop_table('posts')
