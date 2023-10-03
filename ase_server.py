from flask import Flask
from flask import request
import psycopg2
import networkx as nx

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


def populate_graph(planets):
    G = nx.DiGraph()
    for planet in planets:
        for portal in planet["portals"]:
            G.add_edge(planet["id"], portal["destinationId"], weight=portal["costs"])
    return G


def reachable(G, origin, destination):
    return nx.has_path(G, origin, destination)


@app.post("/stage/1/")
def solve_one():
    answers = []
    planets = request.json["planets"]
    G = populate_graph(planets)
    questions = request.json["questions"]
    for question in questions:
        if question["type"] == "REACHABLE":
            answer = {"questionId": question["id"],
                      "reachable": reachable(G, question["originId"], question["destinationId"])
                      }
            answers.append(answer)
    return {"answers": answers}


@app.post("/stage/2/")
def solve_two():
    answers = []
    planets = request.json["planets"]
    G = populate_graph(planets)
    questions = request.json["questions"]
    for question in questions:
        if question["type"] == "REACHABLE":
            answer = {"questionId": question["id"],
                      "reachable": reachable(G, question["originId"], question["destinationId"])
                      }
            answers.append(answer)
    all_reachable = (nx.edge_connectivity(G) > 0)
    return {"answers": answers, "allReachable": all_reachable}


if __name__ == '__main__':
    app.run(debug=True, port=8001)
