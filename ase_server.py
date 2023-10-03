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
            G.add_edge(planet["id"], portal["destinationId"], weight=portal["costs"], portal_id=portal["id"])
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


@app.post("/stage/3/")
def solve_three():
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
        if question["type"] == "CHEAPEST":
            answer = {"questionId": question["id"]}
            jumps = []
            if reachable(G, question["originId"], question["destinationId"]):
                stops = nx.shortest_path(G, source=question["originId"], target=question["destinationId"],
                                         weight="weight")
                for i in range(len(stops)-1):
                    origin = stops[i]
                    dest = stops[i+1]
                    jump = {
                        "portal": G.get_edge_data(origin, dest)['portal_id'],
                        "originPlanet": origin,
                        "destinationPlanet": dest
                    }
                    jumps.append(jump)
                answer["costs"] = nx.shortest_path_length(G, source=question["originId"],
                                                          target=question["destinationId"], weight="weight")
            else:
                answer["costs"] = -1
            answer["jumps"] = jumps
            answers.append(answer)
    all_reachable = (nx.edge_connectivity(G) > 0)
    return {"answers": answers, "allReachable": all_reachable}


@app.post("/stage/4/")
def solve_four():
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
        if question["type"] == "CHEAPEST":
            answer = {"questionId": question["id"]}
            jumps = []
            if reachable(G, question["originId"], question["destinationId"]):
                stops = nx.shortest_path(G, source=question["originId"], target=question["destinationId"],
                                         weight="weight")
                for i in range(len(stops)-1):
                    origin = stops[i]
                    dest = stops[i+1]
                    jump = {
                        "portal": G.get_edge_data(origin, dest)['portal_id'],
                        "originPlanet": origin,
                        "destinationPlanet": dest
                    }
                    jumps.append(jump)
                answer["costs"] = nx.shortest_path_length(G, source=question["originId"],
                                                          target=question["destinationId"], weight="weight")
            else:
                answer["costs"] = -1
            answer["jumps"] = jumps
            answers.append(answer)
    all_reachable = (nx.edge_connectivity(G) > 0)
    max = 0
    max_path = []
    for node in G.nodes():
        length, path = nx.single_source_bellman_ford(G, node, weight="weight")
        for node in length.keys():
            if max < length[node]:
                max = length[node]
                max_path = path[node]
    origin = max_path[0]
    dest = max_path[-1]
    costs = max
    jumps = []
    for i in range(len(max_path) - 1):
        jump = {
            "portal": G.get_edge_data(max_path[i], max_path[i + 1])['portal_id'],
            "originPlanet": max_path[i],
            "destinationPlanet":  max_path[i + 1]
        }
        jumps.append(jump)
    most_expensive = {"originId": origin, "destinationId": dest, "jumps": jumps, "costs": costs}
    return {"answers": answers, "allReachable": all_reachable, "mostExpensive": most_expensive}


if __name__ == '__main__':
    app.run(debug=True, port=8001)
