import requests
import networkx as nx
import matplotlib.pyplot as plt

#API-ключ
my_api_key = "f1a9fc68-da3c-4e08-b339-a101878e97d7"  

def get_route_data(api_key, start_coords, end_coords, vehicle):
    url = f'https://graphhopper.com/api/1/route?point={start_coords[0]},{start_coords[1]}&point={end_coords[0]},{end_coords[1]}&vehicle={vehicle}&key={api_key}'

    print(f"Запрашиваем URL: {url}")  

    res = requests.get(url)
    if res.status_code != 200:
        print(f"Ошибка при получении данных. Код ошибки: {res.status_code}")
        return None
    return res.json()

def build_graph(routes, vehicle):
    G = nx.Graph()

    print(f"Ответ от API для {vehicle}:", routes)  #Для отладки

    for i, route in enumerate(routes.get("paths", [])): 
        from_station = f"Start_{vehicle}_{i}"  #уникальное имя для начальной точки
        to_station = f"End_{vehicle}_{i}"      # уникальное имя для конечной точки
        duration = route['time'] / 1000 / 60  #время в минутах (API возвращает в миллисекундах)
        distance = route['distance'] / 1000   #расстояние в километрах

        G.add_edge(from_station, to_station, duration=duration, distance=distance, vehicle=vehicle)

    return G

def draw_graph(graph):
    if not graph:
        print("Граф не построен!")
        return

    pos = nx.spring_layout(graph, seed=42)  #Фиксируем seed для воспроизводимости
    plt.figure(figsize=(14, 10))

    vehicle_styles = {
        'car': {'color': 'blue', 'linewidth': 3, 'linestyle': '-', 'label': 'Машина'},
        'bike': {'color': 'green', 'linewidth': 2, 'linestyle': '--', 'label': 'Велосипед'},
        'foot': {'color': 'red', 'linewidth': 2, 'linestyle': ':', 'label': 'Пешком'}
    }

    nx.draw_networkx_nodes(graph, pos, node_size=2000, node_color='lightblue', edgecolors='black', alpha=0.8)

    edges = graph.edges(data=True)
    for u, v, d in edges:
        vehicle = d['vehicle']
        style = vehicle_styles.get(vehicle, {'color': 'black', 'linewidth': 2, 'linestyle': '-'})
        nx.draw_networkx_edges(graph, pos, edgelist=[(u, v)], width=style['linewidth'],
                               edge_color=style['color'], style=style['linestyle'], alpha=0.8)

    edge_labels = {(u, v): f"{d['duration']:.1f} мин\n{d['distance']:.1f} км" for u, v, d in edges}
    nx.draw_networkx_edge_labels(graph, pos, edge_labels=edge_labels, font_size=9, font_color='darkred')

    nx.draw_networkx_labels(graph, pos, font_size=12, font_weight='bold', font_color='darkblue')

    handles = [plt.Line2D([0], [0], color=style['color'], linewidth=style['linewidth'],
                          linestyle=style['linestyle'], label=style['label'])
               for style in vehicle_styles.values()]
    plt.legend(handles=handles, title="Тип транспорта", loc='upper right', fontsize=10)

    plt.title("Граф маршрутов для разных типов транспорта", fontsize=16, pad=20)
    plt.axis('off')  
    plt.tight_layout()
    plt.show()

#main
def main():
    #Ввод данных пользователем
    from_lat = float(input("Введите широту начальной точки: "))
    from_lon = float(input("Введите долготу начальной точки: "))
    to_lat = float(input("Введите широту конечной точки: "))
    to_lon = float(input("Введите долготу конечной точки: "))

    vehicles = ['car', 'bike', 'foot']
    G = nx.Graph()

    #получаем данные от API для каждого типа транспорта
    for vehicle in vehicles:
        route_data = get_route_data(my_api_key, (from_lat, from_lon), (to_lat, to_lon), vehicle)
        if not route_data:
            print(f"Нет данных для {vehicle}")
            continue
        vehicle_graph = build_graph(route_data, vehicle)
        #объединение графов
        G = nx.compose(G, vehicle_graph)
    draw_graph(G)

if __name__ == "__main__":
    main()