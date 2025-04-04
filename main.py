import sys
import tkinter as tk
from tkinter import filedialog, messagebox
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class GraphApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Visualizador de Grafos")
        self.root.geometry("900x600")  # Tamaño inicial de la ventana
        
        self.graph = nx.Graph()
        self.pos = {}  
        self.start_node = tk.StringVar()
        self.end_node = tk.StringVar()
        self.edges_drawn = []
        self.heuristics = {}

        self.algorithm_selected = tk.StringVar(value="BFS")  # Algoritmo por defecto

        self.create_layout()
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def on_close(self):
        """Maneja el evento de cierre de la ventana"""
        if messagebox.askokcancel("Salir", "¿Estás seguro de que deseas cerrar el programa?"):
            self.root.destroy()  # Cierra la ventana
            sys.exit(0)  # Termina el programa
    
    def create_layout(self):
        """Crea la interfaz con panel lateral izquierdo y área de visualización a la derecha"""

        # Crear un marco lateral para los controles
        control_frame = tk.Frame(self.root, padx=10, pady=10)
        control_frame.grid(row=0, column=0, sticky="ns")

        # Botón para cargar archivo
        tk.Button(control_frame, text="Cargar Archivo", command=self.load_file).pack(fill="x", pady=5)

        # Entrada para Nodo Inicial
        tk.Label(control_frame, text="Nodo Inicio:").pack(anchor="w")
        tk.Entry(control_frame, textvariable=self.start_node).pack(fill="x", pady=2)

        # Entrada para Nodo Final
        tk.Label(control_frame, text="Nodo Fin:").pack(anchor="w")
        tk.Entry(control_frame, textvariable=self.end_node).pack(fill="x", pady=2)

        # Dropdown de Algoritmos
        tk.Label(control_frame, text="Algoritmo:").pack(anchor="w")
        opciones = ["BFS", "DFS", "Djikstra", "Bellman-Ford", "Greedy", "Hill Climbing", "Recocido Simulado"]
        self.algorithm_selected.set(opciones[0])  # Establecer el algoritmo por defecto
        dropdown = tk.OptionMenu(control_frame, self.algorithm_selected, *opciones)
        dropdown.pack(fill="x", pady=5)

        # Botón para ejecutar
        tk.Button(control_frame, text="Ejecutar", command=self.run_algorithm).pack(fill="x", pady=10)

        # Botón para calcular heurísticas
        tk.Button(control_frame, text="Calcular Heurísticas", command=lambda: self.calculate_heuristics(self.end_node.get())).pack(fill="x", pady=5)
        tk.Label(control_frame, text="Heurísticas:").pack(anchor="w")
        self.heuristics_text = tk.Text(control_frame, height=10, width=30)
        self.heuristics_text.pack(fill="x", pady=5)

        # Crear un marco para la visualización del grafo (lado derecho)
        graph_frame = tk.Frame(self.root, bg="white")
        graph_frame.grid(row=0, column=1, sticky="nsew")

        # Configurar la expansión de las columnas y filas
        self.root.columnconfigure(1, weight=1)  # Permite que el grafo se expanda
        self.root.rowconfigure(0, weight=1)

        
        self.figure, self.ax = plt.subplots(figsize=(5, 4))
            
            # Configurar el fondo blanco y ocultar los ejes
        self.ax.set_facecolor("white")  # Fondo blanco para la figura
        self.ax.set_xticks([])  # Ocultar eje X
        self.ax.set_yticks([])  # Ocultar eje Y
        self.ax.set_frame_on(False)  # Eliminar el borde del gráfico

        self.canvas = FigureCanvasTkAgg(self.figure, master=graph_frame)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

    def load_file(self):
        """Carga un archivo de texto con la estructura del grafo"""
        file_path = filedialog.askopenfilename(filetypes=[("Archivos de Texto", "*.txt")])
        if file_path:
            self.graph.clear()
            try:
                with open(file_path, 'r') as file:
                    for line in file:
                        if line.strip():
                            parts = line.strip().split()
                            if len(parts) == 3:
                                node1, node2, weight = parts
                                self.graph.add_edge(node1, node2, weight=float(weight))
                            else:
                                messagebox.showerror("Error", "Formato de archivo incorrecto. Debe ser 'nodo1 nodo2 peso' o 'nodo1 nodo2'.")
                                return
                self.pos = nx.spring_layout(self.graph)  # Calcular posiciones solo una vez
                self.draw_graph()
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo cargar el archivo: {e}")

    def draw_graph(self):
        """Dibuja el grafo sin rutas resaltadas"""
        self.ax.clear()
        self.ax.set_xticks([])
        self.ax.set_yticks([])
        self.ax.set_frame_on(False)

        nx.draw(self.graph, self.pos, with_labels=True, node_color='skyblue',
                node_size=500, font_size=10, font_weight='bold', ax=self.ax)
        
        edge_labels = nx.get_edge_attributes(self.graph, 'weight')
        nx.draw_networkx_edge_labels(self.graph, self.pos, edge_labels=edge_labels, ax=self.ax)

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
        """Ejecuta el algoritmo seleccionado y colorea la ruta"""
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
                path = nx.shortest_path(self.graph, source=start_node, target=end_node)
            if algorithm == "Djikstra":
                path = nx.dijkstra_path(self.graph, source=start_node, target=end_node)
            if algorithm == "Bellman-Ford":
                path = nx.bellman_ford_path(self.graph, source=start_node, target=end_node)
            if algorithm == "DFS":
                path = list(nx.dfs_preorder_nodes(self.graph, source=start_node))
                if end_node in path:
                    path = path[:path.index(end_node) + 1]
                else:
                    raise nx.NetworkXNoPath
            if algorithm == "Greedy":
                path = self.greedy_algorithm(start_node, end_node)
            if algorithm == "Hill Climbing":
                path = self.hill_climbing_algorithm(start_node, end_node)
            if algorithm == "Recocido Simulado":
                path = self.simulated_annealing(start_node, end_node)
             
            self.highlight_path(path)

        except nx.NetworkXNoPath:
            messagebox.showwarning("Sin Ruta", f"No hay camino entre {start_node} y {end_node}.")

    def greedy_algorithm(self, start_node, end_node):
        visited = set()  # Conjunto de nodos visitados
        path = [start_node]  # Ruta inicial
        current_node = start_node

        while current_node != end_node:
            visited.add(current_node)
            neighbors = self.graph[current_node]  # Vecinos del nodo actual

            # Encontrar el vecino con el menor peso que no haya sido visitado
            next_node = None
            min_weight = float('inf')
            for neighbor, attributes in neighbors.items():
                if neighbor not in visited and attributes.get('weight', 1) < min_weight:
                    next_node = neighbor
                    min_weight = attributes.get('weight', 1)

            if next_node is None:
                raise nx.NetworkXNoPath

            path.append(next_node)
            current_node = next_node

        return path

    def hill_climbing_algorithm(self, start_node, end_node):
        if self.heuristics is None:
            messagebox.showerror("Error", "Primero calcula las heurísticas.")
            return
        visited = set()  # Conjunto de nodos visitados
        path = [start_node]  # Ruta inicial
        current_node = start_node

        while current_node != end_node:
            visited.add(current_node)
            neighbors = self.graph[current_node]  # Vecinos del nodo actual

            # Seleccionar el vecino más prometedor según la heurística
            next_node = None
            best_heuristic = float('inf')
            for neighbor in neighbors:
                if neighbor not in visited:
                    # Obtener la heurística del nodo vecino
                    heuristic = self.heuristics.get(neighbor, float('inf'))
                    if heuristic < best_heuristic:

                        next_node = neighbor
                        best_heuristic = heuristic

            if next_node is None:
                raise nx.NetworkXNoPath  # No hay camino al nodo final

            path.append(next_node)
            current_node = next_node

        return path
    
    def simulated_annealing(self, start_node, end_node):
        if self.heuristics is None:
            messagebox.showerror("Error", "Primero calcula las heurísticas.")
            return

        current_node = start_node
        current_heuristic = self.heuristics.get(current_node, float('inf'))
        path = [current_node]  # Ruta inicial
        temperature = 100  # Temperatura inicial
        cooling_rate = 0.95  # Tasa de enfriamiento

        while temperature > 1:
            neighbors = list(self.graph[current_node])  # Obtener los vecinos del nodo actual

            if not neighbors:
                messagebox.showwarning("Sin Ruta", "No hay vecinos disponibles para continuar.")
                return path

            # Seleccionar un vecino aleatorio
            next_node = random.choice(neighbors)
            next_heuristic = self.heuristics.get(next_node, float('inf'))

            # Calcular el cambio en la heurística
            delta_heuristic = next_heuristic - current_heuristic

            # Decidir si moverse al vecino
            if delta_heuristic < 0 or random.uniform(0, 1) < math.exp(-delta_heuristic / temperature):
                current_node = next_node
                current_heuristic = next_heuristic
                path.append(current_node)

            # Si se alcanza el nodo objetivo, terminar
            if current_node == end_node:
                return path

            # Reducir la temperatura
            temperature *= cooling_rate

        messagebox.showwarning("Sin Ruta", "No se encontró un camino al nodo objetivo dentro del límite de temperatura.")
        return path
    
    def calculate_heuristics(self, target_node):
        if target_node not in self.graph:
            messagebox.showerror("Error", f"El nodo objetivo '{target_node}' no existe en el grafo.")
            return

        # Calcular la heurística como la distancia más corta al nodo objetivo
        self.heuristics = {}  # Reiniciar el diccionario de heurísticas
        for node in self.graph.nodes:
            try:
                # Usar la distancia más corta como heurística
                distance = nx.shortest_path_length(self.graph, source=node, target=target_node, weight='weight')
                self.heuristics[node] = distance
            except nx.NetworkXNoPath:
                # Si no hay camino al nodo objetivo, asignar una heurística infinita
                self.heuristics[node] = float('inf')

        # Mostrar las heurísticas en el área de texto
        self.heuristics_text.delete(1.0, tk.END)  # Limpiar el contenido previo
        for node, heuristic in self.heuristics.items():
            self.heuristics_text.insert(tk.END, f"{node}: {heuristic}\n")  # Insertar nodo y heurística

        messagebox.showinfo("Heurística Calculada", "Se han calculado las heurísticas para todos los nodos.")

import math
import random



if __name__ == "__main__":
    root = tk.Tk()
    app = GraphApp(root)
    root.mainloop()
