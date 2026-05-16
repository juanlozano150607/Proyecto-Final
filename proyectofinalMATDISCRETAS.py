import networkx as nx
import matplotlib.pyplot as plt

# Crear grafo
G = nx.Graph()

# Nodos
nodos = [
    "Casa Estudio",
    "Biblioteca",
    "Du Nord Plaza",
    "Bloque G",
    "Bloque I",
    "Bloque K",
    "Coliseo",
    "Bloque J"
]

G.add_nodes_from(nodos)

# Conexiones con pesos
conexiones = [
    ("Casa Estudio", "Biblioteca", 40),
    ("Biblioteca", "Du Nord Plaza", 80),
    ("Du Nord Plaza", "Bloque G", 60),
    ("Du Nord Plaza", "Bloque I", 120),
    ("Bloque G", "Bloque I", 130),
    ("Bloque G", "Coliseo", 50),
    ("Bloque I", "Coliseo", 30),
    ("Bloque I", "Bloque K", 40),
    ("Bloque K", "Bloque J", 70),
    ("Coliseo", "Bloque J", 100)
]

for origen, destino, distancia in conexiones:
    G.add_edge(origen, destino, weight=distancia)

# POSICIONES AJUSTADAS
pos = {
    "Casa Estudio": (0, 6),
    "Biblioteca": (0, 5),
    "Du Nord Plaza": (0, 3),
    "Bloque G": (-3, 1),
    "Bloque I": (3, 1),
    "Coliseo": (0, -1),
    "Bloque K": (5, 0),
    "Bloque J": (7, -1)
}

def mostrar_lugares():
    print("\n======================================")
    print("LUGARES DISPONIBLES EN EL CAMPUS")
    print("======================================\n")

    for nodo in nodos:
        print("-", nodo)

def mostrar_conexiones(lugar):
    print(f"\nUsted se encuentra en: {lugar}")
    print("\nLugares conectados disponibles:\n")

    vecinos = G[lugar]

    for vecino in vecinos:
        distancia = vecinos[vecino]['weight']
        print(f"- {vecino} ({distancia} metros)")

def calcular_ruta(inicio, destino):
    ruta = nx.shortest_path(G, source=inicio, target=destino, weight='weight')

    distancia_total = nx.shortest_path_length(
        G,
        source=inicio,
        target=destino,
        weight='weight'
    )

    print("\n======================================")
    print("RUTA MÁS CORTA ENCONTRADA")
    print("======================================")

    print("\nRuta:\n")

    for i in range(len(ruta)):
        if i < len(ruta) - 1:
            print(ruta[i], end=" -> ")
        else:
            print(ruta[i])

    print(f"\n\nDistancia total: {distancia_total} metros")

    plt.figure(figsize=(12, 10))

    nx.draw_networkx_nodes(G, pos, node_size=2500)
    nx.draw_networkx_labels(G, pos, font_size=9, font_weight='bold')
    nx.draw_networkx_edges(G, pos, width=2)

    labels = nx.get_edge_attributes(G, 'weight')
    nx.draw_networkx_edge_labels(G, pos, edge_labels=labels, font_size=9)

    ruta_aristas = list(zip(ruta, ruta[1:]))

    nx.draw_networkx_edges(
        G,
        pos,
        edgelist=ruta_aristas,
        width=5,
        edge_color='red'
    )

    plt.title(f"Ruta más corta entre {inicio} y {destino}", fontsize=14)
    plt.axis('off')
    plt.show()

# Menú
while True:
    print("\n======================================")
    print("GUÍA DE RUTAS - UNIVERSIDAD DEL NORTE")
    print("======================================")

    print("\n1. Ver lugares disponibles")
    print("2. Ver conexiones desde mi ubicación")
    print("3. Calcular ruta más corta")
    print("4. Salir")

    opcion = input("\nSeleccione una opción: ")

    if opcion == "1":
        mostrar_lugares()

    elif opcion == "2":
        lugar = input("\nIngrese su ubicación actual: ")

        if lugar in G.nodes:
            mostrar_conexiones(lugar)
        else:
            print("\nERROR: El lugar ingresado no existe.")

    elif opcion == "3":
        inicio = input("\nIngrese el punto de inicio: ")
        destino = input("Ingrese el punto de destino: ")

        if inicio not in G.nodes:
            print("\nERROR: El punto de inicio no existe.")
        elif destino not in G.nodes:
            print("\nERROR: El punto de destino no existe.")
        else:
            calcular_ruta(inicio, destino)

    elif opcion == "4":
        print("\nGracias por usar la guía de rutas.")
        break

    else:
        print("\nERROR: Opción inválida.")
