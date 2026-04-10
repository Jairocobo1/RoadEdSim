import json
import matplotlib.pyplot as plt
import matplotlib.patches as patches

class DraggableElement:
    def __init__(self, patch, tipo, editor_ref):
        self.patch = patch
        self.tipo = tipo
        self.editor = editor_ref
        self.press = None
        self.canvas = patch.figure.canvas
        self.connect()

    def connect(self):
        self.cidpress = self.canvas.mpl_connect('button_press_event', self.on_press)
        self.cidrelease = self.canvas.mpl_connect('button_release_event', self.on_release)
        self.cidmotion = self.canvas.mpl_connect('motion_notify_event', self.on_motion)

    def on_press(self, event):
        if event.inaxes != self.patch.axes: return
        contains, _ = self.patch.contains(event)
        if not contains: return
        
        # --- NUEVA LÓGICA DE BORRADO (Clic Derecho = 3) ---
        if event.button == 3: 
            self.borrar_elemento()
            return
        
        x0, y0 = self.patch.get_xy()
        
        # Si clicamos en la FÁBRICA (x < 0), clonamos
        if x0 < 0:
            self.clonar_y_activar(event)
            return

        self.press = x0, y0, event.xdata, event.ydata
    
    def borrar_elemento(self):
        # Solo permitimos borrar si NO está en la fábrica (x >= 0)
        x_actual, _ = self.patch.get_xy()
        if x_actual >= 0:
            self.patch.remove() # Lo quita del dibujo
            if self in self.editor.elementos:
                self.editor.elementos.remove(self) # Lo quita de la lista de memoria
            self.canvas.draw()
            print(f"Elemento {self.tipo} eliminado.")
    
    def clonar_y_activar(self, event):
        nuevo_patch = None
        
        # Lógica de creación de piezas reales
        if self.tipo == "cebra":
            nuevo_patch = patches.Rectangle((event.xdata-10, event.ydata-20), 20, 40, 
                                          facecolor='none', edgecolor='white', 
                                          hatch='---', lw=2, zorder=2)
        elif self.tipo == "slot":
            nuevo_patch = patches.Rectangle((event.xdata-10, event.ydata-5), 20, 10, 
                                          color='blue', alpha=0.6, zorder=1)
        elif self.tipo == "barrera":
            nuevo_patch = patches.Rectangle((event.xdata-1, event.ydata-15), 2, 38, 
                                          color='red', zorder=5)
        elif self.tipo == "linea_central":
            nuevo_patch = patches.Rectangle((event.xdata-15, event.ydata-1), 30, 2, 
                                          color='yellow', ls='--', zorder=3)
        
        if nuevo_patch:
            self.patch.axes.add_patch(nuevo_patch)
            nuevo_obj = DraggableElement(nuevo_patch, self.tipo, self.editor)
            self.editor.elementos.append(nuevo_obj)
            
            # Activación inmediata para arrastre
            nuevo_obj.press = nuevo_patch.get_xy()[0], nuevo_patch.get_xy()[1], event.xdata, event.ydata
            self.canvas.draw()

    def on_motion(self, event):
        if self.press is None or event.inaxes != self.patch.axes: return
        x0, y0, xpress, ypress = self.press
        dx = event.xdata - xpress
        dy = event.ydata - ypress
        self.patch.set_xy((x0 + dx, y0 + dy))
        self.canvas.draw_idle()

    def on_release(self, event):
        if self.press is not None:
            # Snap-to-Grid (Ajuste a 10 unidades)
            x, y = self.patch.get_xy()
            self.patch.set_xy((round(x/10)*10, round(y/5)*5))
            self.canvas.draw_idle()
        self.press = None

class EditorEDSIM:
    def __init__(self):
        self.fig, self.ax = plt.subplots(figsize=(14, 6))
        self.ax.set_xlim(-100, 500)
        self.ax.set_ylim(-100, 100)

        self.ax.set_aspect('equal', adjustable='box')
        self.elementos = []
        self.setup_escenario()

        # Conectar tecla 'S' para guardar y 'L' para cargar
        self.fig.canvas.mpl_connect('key_press_event', self.on_key)

    def on_key(self, event):
        if event.key == 's':
            self.guardar_mapa()
        elif event.key == 'l':
            self.cargar_mapa()

    def guardar_mapa(self):
        datos_mapa = []
        for el in self.elementos:
            x, y = el.patch.get_xy()
            # Solo guardamos lo que esté en el área de trabajo (x >= 0)
            if x >= 0:
                datos_mapa.append({
                    'tipo': el.tipo,
                    'x': x,
                    'y': y
                })
        
        with open('data/mapa_popayan.json', 'w') as f:
            json.dump(datos_mapa, f, indent=4)
        print("¡Mapa guardado con éxito en data/mapa_popayan.json!")

    def cargar_mapa(self):
        try:
            with open('data/mapa_popayan.json', 'r') as f:
                datos = json.load(f)
            
            for d in datos:
                # Recreamos el patch según el tipo guardado
                if d['tipo'] == "cebra":
                    p = patches.Rectangle((d['x'], d['y']), 20, 40, facecolor='none', edgecolor='white', hatch='|||', lw=2)
                elif d['tipo'] == "slot":
                    p = patches.Rectangle((d['x'], d['y']), 20, 10, color='blue', alpha=0.4)
                # ... (añadir los otros tipos aquí)
                elif d['tipo'] == "barrera":
                    p = patches.Rectangle((d['x'], d['y']), 2, 30, color='red', zorder=5)
                elif d['tipo'] == "linea_central":
                    p = patches.Rectangle((d['x'], d['y']), 30, 2, color='yellow', ls='--', zorder=3)

                if p:    
                    self.ax.add_patch(p)
                    self.elementos.append(DraggableElement(p, d['tipo'], self))
            
            self.fig.canvas.draw()
            print("Mapa cargado correctamente.")
        except FileNotFoundError:
            print("No se encontró ningún mapa guardado.")

    def setup_escenario(self):
        self.ax.set_ylim(-100, 100)

       
        # Fondo y línea divisoria
        self.ax.add_patch(patches.Rectangle((-100, -100), 100, 200, color="#298b2084", zorder=0))
        self.ax.axvline(0, color='black', lw=3, zorder=10)
        self.ax.text(-85, 85, "FÁBRICA", fontweight='bold', fontsize=10)
        # ASFALTO: Asegúrate de que el alto sea coherente (ej: de -40 a 40)
        # Rectangle((x, y), ancho, alto)
        self.ax.add_patch(patches.Rectangle((0, -40), 500, 80, color='#333333', zorder=1))
                
        # Muestras estáticas en la fábrica
        # (Aquí NO usamos hatch ni lógica compleja, solo la muestra visual)
        muestras = [
            ("cebra", 50, "Cebra", 'white'),
            ("slot", 10, "Slot P.", 'blue'),
            ("barrera", -40, "Barrera", 'red'),
            ("linea_central", -80, "L. Central", 'yellow')
        ]
        
        for tipo, y, etiqueta, color in muestras:
            if tipo == "linea_central":
                p = patches.Rectangle((-80, y), 30, 2, color=color)
            elif tipo == "barrera":
                p = patches.Rectangle((-65, y), 2, 25, color=color)
            else:
                p = patches.Rectangle((-75, y), 20, 10, color=color, alpha=0.7)
            
            self.ax.add_patch(p)
            self.elementos.append(DraggableElement(p, tipo, self))
            self.ax.text(-85, y-10, etiqueta, fontsize=8, zorder=10, fontweight='bold')

        # Asfalto del área de trabajo
        self.ax.add_patch(patches.Rectangle((0, -40), 500, 80, color='#333333', zorder=0))
        self.ax.set_aspect('equal') # Mantiene los cuadrados como cuadrados
        self.ax.set_ylim(-100, 100) # Fija el límite vertical
        plt.title("EDSIM v0.3 - Editor Popayán (Fábrica Corregida)")
        plt.grid(True, which='both', color='gray', linestyle='--', linewidth=0.3)

editor = EditorEDSIM()
plt.show()