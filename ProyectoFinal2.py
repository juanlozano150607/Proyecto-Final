import tkinter as tk
from tkinter import ttk, messagebox
import networkx as nx
import matplotlib.pyplot as plt

# -------------------- GRAFO --------------------
G = nx.Graph()

nodos = [
    "Casa Estudio", "Biblioteca", "Du Nord Plaza",
    "Bloque G", "Bloque I", "Bloque K",
    "Coliseo", "Bloque J"
]
G.add_nodes_from(nodos)

conexiones = [
    ("Casa Estudio", "Biblioteca", 120),
    ("Biblioteca", "Du Nord Plaza", 70),
    ("Du Nord Plaza", "Bloque G", 80),
    ("Du Nord Plaza", "Bloque I", 140),
    ("Bloque G", "Bloque I", 130),
    ("Bloque G", "Coliseo", 60),
    ("Bloque I", "Coliseo", 50),
    ("Bloque I", "Bloque K", 70),
    ("Bloque K", "Bloque J", 90),
    ("Coliseo", "Bloque J", 110)
]

for o, d, w in conexiones:
    G.add_edge(o, d, weight=w)

# Posiciones tipo mapa
pos = {
    "Casa Estudio": (0, 5),
    "Biblioteca": (0, 4),
    "Du Nord Plaza": (0, 2.5),
    "Bloque G": (-2, 1),
    "Bloque I": (2, 1),
    "Coliseo": (0, -1),
    "Bloque K": (3, 0),
    "Bloque J": (2, -2)
}

historial = []

# -------------------- FUNCIONES --------------------
def calcular_ruta():
    origen = combo_origen.get()
    destino = combo_destino.get()

    if not origen or not destino:
        messagebox.showwarning("Aviso", "Seleccione origen y destino")
        return

    if origen not in G.nodes or destino not in G.nodes:
        messagebox.showerror("Error", "Nodo inválido")
        return

    try:
        ruta = nx.dijkstra_path(G, origen, destino, weight='weight')
        distancia = nx.dijkstra_path_length(G, origen, destino, weight='weight')

        resultado_var.set(f"Ruta: {' -> '.join(ruta)}\nDistancia: {distancia}")
        historial.append((origen, destino, ruta, distancia))

        dibujar_grafo(ruta)

    except nx.NetworkXNoPath:
        messagebox.showerror("Error", "No hay ruta entre los nodos")

def dibujar_grafo(ruta=None):
    plt.figure()
    nx.draw(G, pos, with_labels=True, node_size=2000, font_size=8)

    labels = nx.get_edge_attributes(G, 'weight')
    nx.draw_networkx_edge_labels(G, pos, edge_labels=labels)

    if ruta:
        edges_ruta = list(zip(ruta, ruta[1:]))
        nx.draw_networkx_edges(G, pos, edgelist=edges_ruta, width=3)

    plt.title("Grafo del campus")
    plt.show()

def ver_historial():
    ventana_hist = tk.Toplevel(root)
    ventana_hist.title("Historial")

    texto = tk.Text(ventana_hist, width=60, height=20)
    texto.pack()

    if not historial:
        texto.insert(tk.END, "No hay historial.\n")
    else:
        for i, (o, d, r, dist) in enumerate(historial, 1):
            texto.insert(tk.END, f"{i}. {o} -> {d}\n")
            texto.insert(tk.END, f"   Ruta: {r}\n")
            texto.insert(tk.END, f"   Distancia: {dist}\n\n")

# -------------------- INTERFAZ --------------------
root = tk.Tk()
root.title("Sistema de Rutas - Campus")

frame = tk.Frame(root, padx=20, pady=20)
frame.pack()

tk.Label(frame, text="Origen").grid(row=0, column=0)
combo_origen = ttk.Combobox(frame, values=nodos)
combo_origen.grid(row=0, column=1)

tk.Label(frame, text="Destino").grid(row=1, column=0)
combo_destino = ttk.Combobox(frame, values=nodos)
combo_destino.grid(row=1, column=1)

tk.Button(frame, text="Calcular Ruta", command=calcular_ruta).grid(row=2, column=0, columnspan=2, pady=10)
tk.Button(frame, text="Ver Historial", command=ver_historial).grid(row=3, column=0, columnspan=2)

resultado_var = tk.StringVar()
tk.Label(frame, textvariable=resultado_var, justify="left").grid(row=4, column=0, columnspan=2, pady=10)

tk.Button(frame, text="Mostrar Grafo Completo", command=lambda: dibujar_grafo()).grid(row=5, column=0, columnspan=2)

root.mainloop()
