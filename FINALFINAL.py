"""
UNINORTE · CAMPUS NAVIGATION — Algoritmo de Dijkstra
Matematicas Discretas — Juan Lozano & Sergio Cuello
"""

import tkinter as tk
from tkinter import ttk
import networkx as nx
import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# ─────────────── PALETA DE COLORES ───────────────────
BG        = "#0D0F1A"
PANEL     = "#1A1E35"
PANEL2    = "#1E2340"
ACCENT    = "#4F8FFF"
ACCENT2   = "#7B5EFF"
GOLD      = "#FFD166"
GREEN     = "#06D6A0"
RED_HIGH  = "#EF476F"
TEXT      = "#E8EAF6"
TEXT2     = "#8892B0"
BORDER    = "#2D3561"
GRAPH_BG  = "#0F1220"

# ─────────────── GRAFO DEL CAMPUS ────────────────────
NODOS = [
    "Casa Estudio",
    "Biblioteca",
    "Du Nord Plaza",
    "Bloque G",
    "Bloque I",
    "Bloque K",
    "Coliseo",
    "Bloque J",
]

CONEXIONES = [
    ("Casa Estudio",  "Biblioteca",    20),
    ("Biblioteca",    "Du Nord Plaza", 80),
    ("Du Nord Plaza", "Bloque G",      90),
    ("Du Nord Plaza", "Bloque I",     140),
    ("Bloque G",      "Bloque I",     130),
    ("Bloque G",      "Coliseo",       60),
    ("Bloque I",      "Coliseo",       50),
    ("Bloque I",      "Bloque K",      70),
    ("Bloque K",      "Bloque J",      90),
    ("Coliseo",       "Bloque J",     110),
]

# ──────────────────────────────────────────────────────
# POSICIONES: layout fiel a la imagen (top-center → expand)
# Escala proporcional: eje Y va de arriba (0.95) hacia abajo (0.05)
# Eje X centrado en 0.5, se expande según la posición lateral
#
# Mapa de distancias acumuladas desde Casa Estudio (columna vertical):
#   Casa Estudio  y=0.93  (top)
#   Biblioteca    y=0.93 - prop(20)
#   Du Nord Plaza y anterior - prop(80)
#   luego se bifurca horizontalmente
# ──────────────────────────────────────────────────────
# Escala vertical: distancia total vertical usable = 0.80 unidades
# Distancia max acumulada en el eje principal = 20+80 = 100m → ocupa ~0.20
# Luego la expansión horizontal lleva los nodos más abajo

POSICIONES = {
    # Columna central (de arriba abajo)
    "Casa Estudio":  (0.50, 0.92),
    "Biblioteca":    (0.50, 0.78),   # 20m abajo → pequeño gap
    "Du Nord Plaza": (0.50, 0.58),   # 80m abajo → gap mayor ~4x el anterior

    # Expansión lateral proporcional a las distancias desde Du Nord Plaza
    # Du Nord Plaza -> Bloque G: 90m  → izquierda moderada
    # Du Nord Plaza -> Bloque I: 140m → derecha, más lejos
    "Bloque G":      (0.15, 0.40),   # izquierda
    "Bloque I":      (0.82, 0.40),   # derecha (140 > 90 → más separado)

    # Segundo nivel de expansión
    # Bloque G -> Coliseo: 60m       → centro-bajo izquierda
    # Bloque I -> Coliseo: 50m       → convergen al centro
    "Coliseo":       (0.50, 0.20),   # centro bajo

    # Bloque I -> Bloque K: 70m      → extremo derecho, un poco más abajo
    "Bloque K":      (0.92, 0.22),   # extremo derecho

    # Bloque K -> Bloque J: 90m / Coliseo -> Bloque J: 110m → convergen abajo
    "Bloque J":      (0.76, 0.04),   # bajo derecha
}

MARCADORES = {
    "Casa Estudio":  "[H]",
    "Biblioteca":    "[B]",
    "Du Nord Plaza": "[P]",
    "Bloque G":      "[G]",
    "Bloque I":      "[I]",
    "Bloque K":      "[K]",
    "Coliseo":       "[C]",
    "Bloque J":      "[J]",
}


class CampusApp:
    def __init__(self, root):
        self.root = root
        self.root.title("UNINORTE  |  Rutas del Campus  |  Algoritmo de Dijkstra")
        self.root.configure(bg=BG)
        self.root.geometry("1280x800")
        self.root.minsize(1100, 720)

        self.G = nx.Graph()
        self.G.add_nodes_from(NODOS)
        for o, d, w in CONEXIONES:
            self.G.add_edge(o, d, weight=w)

        self.pos = POSICIONES
        self.ruta_actual = []
        self.distancia_actual = 0

        self._build_ui()
        self._draw_graph()

    # ─── UI ──────────────────────────────────────────
    def _build_ui(self):
        header = tk.Frame(self.root, bg=PANEL, height=64)
        header.pack(fill="x")
        header.pack_propagate(False)

        title_frame = tk.Frame(header, bg=PANEL)
        title_frame.pack(side="left", padx=24)

        tk.Label(title_frame, text="UNINORTE  |  CAMPUS NAVIGATOR",
                 bg=PANEL, fg=ACCENT, font=("Courier", 16, "bold")).pack(anchor="w", pady=(12, 0))
        tk.Label(title_frame,
                 text="Navegacion Optima via Algoritmo de Dijkstra  —  Matematicas Discretas",
                 bg=PANEL, fg=TEXT2, font=("Courier", 9)).pack(anchor="w")

        tk.Label(header, text="Juan Lozano  &  Sergio Cuello",
                 bg=PANEL, fg=TEXT2, font=("Courier", 9)).pack(side="right", padx=24, pady=14)

        tk.Frame(self.root, bg=ACCENT, height=2).pack(fill="x")

        body = tk.Frame(self.root, bg=BG)
        body.pack(fill="both", expand=True)

        self._build_left_panel(body)
        self._build_graph_panel(body)

    def _build_left_panel(self, parent):
        lp = tk.Frame(parent, bg=PANEL, width=316)
        lp.pack(side="left", fill="y")
        lp.pack_propagate(False)

        canvas_s = tk.Canvas(lp, bg=PANEL, highlightthickness=0)
        canvas_s.pack(fill="both", expand=True)
        inner = tk.Frame(canvas_s, bg=PANEL)
        canvas_s.create_window((0, 0), window=inner, anchor="nw", width=316)

        self._divider(inner, "ORIGEN")
        self.origen_var = tk.StringVar(value=NODOS[0])
        self._dropdown(inner, self.origen_var)

        self._divider(inner, "DESTINO")
        self.destino_var = tk.StringVar(value=NODOS[6])
        self._dropdown(inner, self.destino_var)

        btn_area = tk.Frame(inner, bg=PANEL)
        btn_area.pack(fill="x", padx=16, pady=12)

        tk.Button(btn_area, text="CALCULAR RUTA OPTIMA  >>",
                  bg=ACCENT, fg="white", activebackground=ACCENT2, activeforeground="white",
                  font=("Courier", 11, "bold"), bd=0, relief="flat", cursor="hand2",
                  padx=12, pady=11, command=self._calcular).pack(fill="x")

        tk.Button(btn_area, text="LIMPIAR",
                  bg=PANEL2, fg=TEXT2, activebackground=BORDER, activeforeground=TEXT,
                  font=("Courier", 10), bd=0, relief="flat", cursor="hand2",
                  padx=10, pady=7, command=self._limpiar).pack(fill="x", pady=(6, 0))

        self._divider(inner, "RESULTADO")
        result_box = tk.Frame(inner, bg=PANEL2)
        result_box.pack(fill="x", padx=16, pady=6)

        tk.Label(result_box, text="DISTANCIA MINIMA", bg=PANEL2, fg=TEXT2,
                 font=("Courier", 8, "bold")).pack(pady=(12, 0))
        self.lbl_distancia = tk.Label(result_box, text="---", bg=PANEL2, fg=GOLD,
                                      font=("Courier", 36, "bold"))
        self.lbl_distancia.pack()
        tk.Label(result_box, text="metros", bg=PANEL2, fg=TEXT2,
                 font=("Courier", 10)).pack(pady=(0, 12))

        self._divider(inner, "RUTA OPTIMA")
        self.steps_frame = tk.Frame(inner, bg=PANEL)
        self.steps_frame.pack(fill="x", padx=16, pady=4)

        self._divider(inner, "INFORMACION DEL GRAFO")
        self._stat_row(inner, "Nodos totales",   str(self.G.number_of_nodes()))
        self._stat_row(inner, "Aristas totales", str(self.G.number_of_edges()))
        self._stat_row(inner, "Tipo de grafo",   "No dirigido / Ponderado")
        self._stat_row(inner, "Algoritmo",       "Dijkstra (O((V+E) log V))")

        self._divider(inner, "CONEXIONES Y PESOS")
        for o, d, w in CONEXIONES:
            row = tk.Frame(inner, bg=PANEL)
            row.pack(fill="x", padx=16, pady=1)
            tk.Label(row, text=f"{MARCADORES[o]}-{MARCADORES[d]}",
                     bg=PANEL, fg=TEXT2, font=("Courier", 8), width=9, anchor="w").pack(side="left")
            tk.Label(row, text=f"{o[:11]} <-> {d[:11]}",
                     bg=PANEL, fg=TEXT, font=("Courier", 8), anchor="w").pack(side="left", expand=True)
            tk.Label(row, text=f"{w}m",
                     bg=PANEL, fg=GREEN, font=("Courier", 8, "bold"), width=5, anchor="e").pack(side="right")

    def _divider(self, parent, text):
        frame = tk.Frame(parent, bg=PANEL)
        frame.pack(fill="x", pady=(8, 2))
        tk.Frame(frame, bg=BORDER, height=1).pack(fill="x", padx=16)
        tk.Label(frame, text=f"  {text}  ", bg=PANEL, fg=ACCENT2,
                 font=("Courier", 9, "bold")).pack(anchor="w", padx=16, pady=(3, 0))

    def _dropdown(self, parent, var):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Dark.TCombobox", fieldbackground=PANEL2, background=PANEL2,
                        foreground=TEXT, selectbackground=ACCENT, selectforeground="white",
                        bordercolor=BORDER, arrowcolor=ACCENT)
        style.map("Dark.TCombobox", fieldbackground=[("readonly", PANEL2)])
        cb = ttk.Combobox(parent, textvariable=var, values=NODOS, state="readonly",
                          style="Dark.TCombobox", font=("Courier", 11))
        cb.pack(fill="x", padx=16, pady=4)
        return cb

    def _stat_row(self, parent, label, value):
        row = tk.Frame(parent, bg=PANEL)
        row.pack(fill="x", padx=16, pady=1)
        tk.Label(row, text=label, bg=PANEL, fg=TEXT2,
                 font=("Courier", 9), anchor="w", width=22).pack(side="left")
        tk.Label(row, text=value, bg=PANEL, fg=GREEN,
                 font=("Courier", 9, "bold"), anchor="w").pack(side="left")

    def _build_graph_panel(self, parent):
        gp = tk.Frame(parent, bg=GRAPH_BG)
        gp.pack(side="left", fill="both", expand=True)
        self.fig, self.ax = plt.subplots(figsize=(9, 6.8))
        self.fig.patch.set_facecolor(GRAPH_BG)
        self.ax.set_facecolor(GRAPH_BG)
        self.canvas_mpl = FigureCanvasTkAgg(self.fig, master=gp)
        self.canvas_mpl.get_tk_widget().pack(fill="both", expand=True)

    # ─── DIBUJO ──────────────────────────────────────
    def _draw_graph(self, ruta=None):
        self.ax.clear()
        self.ax.set_facecolor(GRAPH_BG)
        self.fig.patch.set_facecolor(GRAPH_BG)
        self.ax.axis("off")

        # Grid de fondo
        for x in [i * 0.1 for i in range(11)]:
            self.ax.axvline(x, color="#161B33", lw=0.5, alpha=0.7)
        for y in [i * 0.1 for i in range(11)]:
            self.ax.axhline(y, color="#161B33", lw=0.5, alpha=0.7)

        # Borde campus
        campus_rect = mpatches.FancyBboxPatch(
            (0.02, 0.02), 0.96, 0.96,
            boxstyle="round,pad=0.01", linewidth=1.5,
            edgecolor=BORDER, facecolor="#0C1124", alpha=0.5, zorder=0)
        self.ax.add_patch(campus_rect)

        pos_disp = {n: (x, y) for n, (x, y) in self.pos.items()}

        # Aristas en ruta
        ruta_edges = set()
        if ruta and len(ruta) > 1:
            for i in range(len(ruta) - 1):
                ruta_edges.add((ruta[i], ruta[i+1]))
                ruta_edges.add((ruta[i+1], ruta[i]))

        otras = [(u, v) for u, v in self.G.edges() if (u, v) not in ruta_edges]
        ruta_e = [(u, v) for u, v in self.G.edges() if (u, v) in ruta_edges]

        nx.draw_networkx_edges(self.G, pos_disp, edgelist=otras,
                               edge_color=BORDER, width=2, alpha=0.55, ax=self.ax)
        if ruta_e:
            nx.draw_networkx_edges(self.G, pos_disp, edgelist=ruta_e,
                                   edge_color=GREEN, width=10, alpha=0.18, ax=self.ax)
            nx.draw_networkx_edges(self.G, pos_disp, edgelist=ruta_e,
                                   edge_color=GREEN, width=4, alpha=0.95, ax=self.ax)

        # Pesos en aristas
        labels_peso = {(u, v): f"{d['weight']}m" for u, v, d in self.G.edges(data=True)}
        nx.draw_networkx_edge_labels(
            self.G, pos_disp, edge_labels=labels_peso,
            font_color=TEXT2, font_size=7.5, font_family="monospace",
            bbox=dict(boxstyle="round,pad=0.18", fc=GRAPH_BG, ec="none", alpha=0.85),
            ax=self.ax)

        # Colores de nodos
        node_colors, node_sizes, border_colors = [], [], []
        for n in self.G.nodes():
            if ruta and n == ruta[0]:
                node_colors.append(ACCENT); node_sizes.append(1100); border_colors.append("#FFFFFF")
            elif ruta and n == ruta[-1]:
                node_colors.append(RED_HIGH); node_sizes.append(1100); border_colors.append("#FFFFFF")
            elif ruta and n in ruta:
                node_colors.append(GREEN); node_sizes.append(800); border_colors.append(GREEN)
            else:
                node_colors.append(PANEL2); node_sizes.append(620); border_colors.append(BORDER)

        # Halos
        for n in self.G.nodes():
            if ruta and n in ruta:
                x, y = pos_disp[n]
                col = ACCENT if n == ruta[0] else (RED_HIGH if n == ruta[-1] else GREEN)
                self.ax.add_patch(plt.Circle((x, y), 0.055, color=col, alpha=0.15, zorder=1))

        nx.draw_networkx_nodes(self.G, pos_disp,
                               node_color=node_colors, node_size=node_sizes,
                               linewidths=2.2, edgecolors=border_colors, ax=self.ax)

        # Etiquetas
        for n in self.G.nodes():
            x, y = pos_disp[n]
            color_txt = TEXT if (ruta and n in ruta) else TEXT2
            peso = "bold" if (ruta and n in ruta) else "normal"
            self.ax.text(x, y, MARCADORES.get(n, "?"),
                         ha="center", va="center", fontsize=8, fontweight="bold",
                         color="#FFFFFF", fontfamily="monospace", zorder=10)
            self.ax.text(x, y - 0.075, n,
                         ha="center", va="top", fontsize=9, fontweight=peso,
                         color=color_txt, fontfamily="monospace", zorder=5)

        # Leyenda
        legend_items = [
            mpatches.Patch(color=ACCENT,   label="Origen"),
            mpatches.Patch(color=RED_HIGH, label="Destino"),
            mpatches.Patch(color=GREEN,    label="Ruta optima"),
            mpatches.Patch(color=PANEL2,   label="Nodo inactivo"),
        ]
        self.ax.legend(handles=legend_items, loc="lower left",
                       facecolor=PANEL, edgecolor=BORDER,
                       labelcolor=TEXT, fontsize=8.5, framealpha=0.95)

        if ruta:
            titulo = f"Ruta: {chr(8594).join(ruta)}"
            subtitulo = f"Distancia total: {self.distancia_actual} metros"
            color_t = GREEN
        else:
            titulo = "Campus Universidad del Norte  —  Grafo Ponderado"
            subtitulo = "Selecciona origen y destino para calcular la ruta optima"
            color_t = TEXT2

        self.ax.text(0.02, 1.01, titulo, transform=self.ax.transAxes,
                     color=color_t, fontsize=9, fontfamily="monospace",
                     va="bottom", fontweight="bold")
        self.ax.text(0.02, 0.99, subtitulo, transform=self.ax.transAxes,
                     color=TEXT2, fontsize=8, fontfamily="monospace", va="top")

        self.ax.set_xlim(-0.04, 1.04)
        self.ax.set_ylim(-0.05, 1.08)
        self.canvas_mpl.draw()

    # ─── DIJKSTRA ────────────────────────────────────
    def _calcular(self):
        origen  = self.origen_var.get()
        destino = self.destino_var.get()

        if origen == destino:
            self._mostrar_error("Origen y destino son el mismo lugar.")
            return
        try:
            ruta = nx.shortest_path(self.G, source=origen, target=destino, weight="weight")
            dist = nx.shortest_path_length(self.G, source=origen, target=destino, weight="weight")
        except nx.NetworkXNoPath:
            self._mostrar_error("No existe ruta entre estos nodos.")
            return

        self.ruta_actual      = ruta
        self.distancia_actual = dist
        self.lbl_distancia.config(text=str(dist), fg=GOLD)
        self._draw_graph(ruta)
        self._mostrar_pasos(ruta)

    def _mostrar_pasos(self, ruta):
        for w in self.steps_frame.winfo_children():
            w.destroy()
        for i, nodo in enumerate(ruta):
            step_row = tk.Frame(self.steps_frame, bg=PANEL)
            step_row.pack(fill="x", pady=1)
            dot_color = ACCENT if i == 0 else (RED_HIGH if i == len(ruta)-1 else GREEN)
            suffix    = "  INICIO" if i == 0 else ("  FIN" if i == len(ruta)-1 else "")
            tk.Label(step_row, text="●", bg=PANEL, fg=dot_color,
                     font=("Courier", 10)).pack(side="left", padx=(4, 4))
            tk.Label(step_row, text=f"{MARCADORES.get(nodo,'?')} {nodo}{suffix}",
                     bg=PANEL, fg=TEXT, font=("Courier", 9, "bold")).pack(side="left")
            if i < len(ruta) - 1:
                w = self.G[ruta[i]][ruta[i+1]]["weight"]
                conn = tk.Frame(self.steps_frame, bg=PANEL)
                conn.pack(fill="x")
                tk.Label(conn, text="  |", bg=PANEL, fg=BORDER,
                         font=("Courier", 8)).pack(side="left", padx=6)
                tk.Label(conn, text=f"  {w} metros", bg=PANEL, fg=TEXT2,
                         font=("Courier", 8)).pack(side="left")

    def _limpiar(self):
        self.ruta_actual      = []
        self.distancia_actual = 0
        self.lbl_distancia.config(text="---", fg=GOLD)
        for w in self.steps_frame.winfo_children():
            w.destroy()
        self._draw_graph()

    def _mostrar_error(self, msg):
        self.lbl_distancia.config(text="!", fg=RED_HIGH)
        for w in self.steps_frame.winfo_children():
            w.destroy()
        tk.Label(self.steps_frame, text=f"  ERROR: {msg}",
                 bg=PANEL, fg=RED_HIGH, font=("Courier", 9),
                 wraplength=260, justify="left").pack(anchor="w")
        self._draw_graph()


if __name__ == "__main__":
    root = tk.Tk()
    try:
        root.state("zoomed")
    except Exception:
        try:
            root.attributes("-zoomed", True)
        except Exception:
            pass
    CampusApp(root)
    root.mainloop()
