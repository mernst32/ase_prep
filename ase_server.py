from flask import Flask
from flask import request
import psycopg2

app = Flask(__name__)


def connect():
    conn = psycopg2.connect(
        host="localhost",
        database="ase_prep_db",
        user="mernst",
        password="")
    return conn


@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"


@app.route("/solution_one/<user>")
def solution_one(user):
    return f'User {user}'


@app.route("/solution_two/", methods=['GET', 'POST'])
def solution_two():
    if request.method == 'GET':
        conn = connect()
        users = []
        cur = conn.cursor()
        cur.execute("SELECT user_id, user_name FROM prep_users")
        row = cur.fetchone()
        while row is not None:
            user_id, user_name = row
            user = {'user_id': user_id, 'user_name': user_name}
            users.append(user)
            row = cur.fetchone()
        cur.close()
        conn.close()
        return users
    if request.method == 'POST':
        new_user = request.json
        conn = connect()
        cur = conn.cursor()
        sql = "INSERT INTO prep_users(user_name) VALUES (%s) RETURNING user_id"
        cur.execute(sql, (new_user["user_name"],))
        user_id = cur.fetchone()
        print(f"new user_id = {user_id}")
        conn.commit()
        cur.close()
        conn.close()
        return f"<p>New User: {user_id}</p>"


if __name__ == '__main__':
    app.run(debug=True, port=8001)