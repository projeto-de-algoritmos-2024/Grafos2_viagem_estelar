from flask import Flask, jsonify, render_template, request
import pandas as pd
import heapq

app = Flask(__name__)

# Carregar dados do CSV e criar o grafo
df = pd.read_csv('Grafo2_stars.csv')
G = {}

for _, row in df.iterrows():
    star = row['Name']
    constellation = row['Constellation']
    distance = row['Distance (ly)']
    if star not in G:
        G[star] = []
    if constellation not in G:
        G[constellation] = []
    G[star].append((constellation, distance))
    G[constellation].append((star, distance))


# Algoritmo de Dijkstr
def dijkstra(graph, start, end):
    queue = [(0, start, [])]
    seen = set()
    mins = {start: 0}

    while queue:
        (cost, node, path) = heapq.heappop(queue)

        if node in seen:
            continue

        path = path + [node]
        seen.add(node)

        if node == end:
            return (cost, path)

        for next_node, weight in graph.get(node, []):
            if next_node in seen:
                continue
            prev = mins.get(next_node, None)
            next_cost = cost + weight
            if prev is None or next_cost < prev:
                mins[next_node] = next_cost
                heapq.heappush(queue, (next_cost, next_node, path))

    return float("inf"), []


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/graph-data')
def get_graph_data():
    nodes = [{'id': node, 'type': 'star' if any(star == node for star in df['Name']) else 'constellation'} for node in G.keys()]
    edges = [{'source': u, 'target': v, 'distance': w} for u in G for v, w in G[u]]
    return jsonify({'nodes': nodes, 'edges': edges})


@app.route('/shortest-path', methods=['POST'])
def get_shortest_path():
    data = request.json
    source = data['source']
    target = data['target']

    try:
        distance, path = dijkstra(G, source, target)
        path_edges = list(zip(path, path[1:]))
        path_info = [{'source': path[i], 'target': path[i + 1], 'distance': dict(G[path[i]])[path[i + 1]]} for i in range(len(path) - 1)]
        return jsonify({'path': path, 'path_edges': path_edges, 'path_info': path_info, 'distance': distance})
    except Exception as e:
        return jsonify({'error': str(e)}), 404


if __name__ == '__main__':
    app.run(debug=True)
