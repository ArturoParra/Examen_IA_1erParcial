import tkinter as tk
from tkinter import filedialog, messagebox
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class GraphApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Graph Algorithms App")

        self.graph = nx.Graph()
        self.pos = {}  # Posiciones de los nodos
        self.start_node = tk.StringVar()
        self.end_node = tk.StringVar()
        self.edges_drawn = []

        self.algorithm_selected = tk.StringVar(value="BFS")  # Valor inicial

        self.create_widgets()

    def create_widgets(self):
        control_frame = tk.Frame(self.root)
        control_frame.pack(pady=10)

        # Botón para cargar archivo
        load_button = tk.Button(control_frame, text="Cargar Archivo", command=self.load_file)
        load_button.grid(row=0, column=0, padx=10)

        # Campos para ingresar nodo inicial y final
        tk.Label(control_frame, text="Inicio:").grid(row=0, column=1)
        tk.Entry(control_frame, textvariable=self.start_node, width=5).grid(row=0, column=2, padx=5)

        tk.Label(control_frame, text="Fin:").grid(row=0, column=3)
        tk.Entry(control_frame, textvariable=self.end_node, width=5).grid(row=0, column=4, padx=5)

        # Dropdown para seleccionar algoritmo
        tk.Label(control_frame, text="Algoritmo:").grid(row=0, column=5)
        opciones = ["BFS", "DFS"]
        dropdown = tk.OptionMenu(control_frame, self.algorithm_selected, *opciones)
        dropdown.grid(row=0, column=6, padx=10)

        # Botón para ejecutar algoritmo seleccionado
        run_button = tk.Button(control_frame, text="Ejecutar", command=self.run_algorithm)
        run_button.grid(row=0, column=7, padx=10)

        # Frame para el gráfico del grafo
        self.figure, self.ax = plt.subplots(figsize=(5, 4))
        self.canvas = FigureCanvasTkAgg(self.figure, master=self.root)
        self.canvas.get_tk_widget().pack()

    def load_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("Archivos de Texto", "*.txt")])
        if file_path:
            self.graph.clear()
            try:
                with open(file_path, 'r') as file:
                    for line in file:
                        if line.strip():
                            node1, node2 = line.strip().split()
                            self.graph.add_edge(node1, node2)
                self.pos = nx.spring_layout(self.graph)  # Calcular posiciones solo una vez
                self.draw_graph()
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo cargar el archivo: {e}")

    def draw_graph(self):
        """Dibuja el grafo solo una vez sin ruta resaltada"""
        self.ax.clear()
        nx.draw(self.graph, self.pos, with_labels=True, node_color='skyblue',
                node_size=500, font_size=10, font_weight='bold', ax=self.ax)
        self.edges_drawn = []
        for edge in self.graph.edges():
            line, = self.ax.plot([], [], color="black", linewidth=1)
            self.edges_drawn.append((edge, line))
        self.canvas.draw()

    def highlight_path(self, path):
        """Colorea solo las aristas de la ruta sin redibujar todo"""
        if not path:
            return
        path_edges = set(zip(path, path[1:]))

        for edge, line in self.edges_drawn:
            x_values = [self.pos[edge[0]][0], self.pos[edge[1]][0]]
            y_values = [self.pos[edge[0]][1], self.pos[edge[1]][1]]

            if edge in path_edges or (edge[1], edge[0]) in path_edges:
                line.set_data(x_values, y_values)
                line.set_color("red")
                line.set_linewidth(2)
            else:
                line.set_color("black")
                line.set_linewidth(1)

        self.canvas.draw()

    def run_algorithm(self):
        if not self.graph.nodes:
            messagebox.showwarning("Advertencia", "Carga un archivo primero.")
            return

        start_node = self.start_node.get().strip()
        end_node = self.end_node.get().strip()

        if not start_node or not end_node:
            messagebox.showwarning("Advertencia", "Ingresa los nodos de inicio y fin.")
            return
        if start_node not in self.graph or end_node not in self.graph:
            messagebox.showwarning("Error", "Uno o ambos nodos no existen en el grafo.")
            return

        algorithm = self.algorithm_selected.get()

        try:
            if algorithm == "BFS":
                path = nx.shortest_path(self.graph, source=start_node, target=end_node, method='bfs')
            elif algorithm == "DFS":
                path = list(nx.dfs_preorder_nodes(self.graph, source=start_node))
                if end_node in path:
                    path = path[:path.index(end_node) + 1]
                else:
                    raise nx.NetworkXNoPath

            self.highlight_path(path)

        except nx.NetworkXNoPath:
            messagebox.showwarning("Sin Ruta", f"No hay camino entre {start_node} y {end_node}.")

if __name__ == "__main__":
    root = tk.Tk()
    app = GraphApp(root)
    root.mainloop()
