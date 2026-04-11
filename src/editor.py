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
        # 1. Quitar del eje visual
        if self.patch in self.patch.axes.patches:
            self.patch.remove()
        
        # 2. Quitar de la lista lógica del editor
        if self in self.editor.elementos:
            self.editor.elementos.remove(self)
        
        # 3. Si era un LED, quitarlo del diccionario de control
        if hasattr(self.editor, 'segmentos_led'):
            # Buscamos si este patch está en el diccionario y lo borramos
            claves_a_eliminar = [k for k, v in self.editor.segmentos_led.items() if v == self.patch]
            for k in claves_a_eliminar:
                del self.editor.segmentos_led[k]

        self.canvas.draw()
        print(f"Sistema: {self.tipo} eliminado por completo.")
    
    def clonar_y_activar(self, event):
        nuevo_patch = None
        tipo_final = self.tipo

        # 1. Definición del Patch según el tipo
        if self.tipo == "cebra":
            nuevo_patch = patches.Rectangle((event.xdata-10, event.ydata-20), 20, 40, 
                                          facecolor='none', edgecolor='white', 
                                          hatch='---', lw=2, zorder=2)
        
        elif self.tipo == "slot":
            # Autonumeración de slots
            num = len([e for e in self.editor.elementos if "slot" in e.tipo]) + 1
            tipo_final = f"slot_{num}"
            nuevo_patch = patches.Rectangle((event.xdata-10, event.ydata-5), 20, 10, 
                                          color='blue', alpha=0.6, zorder=1)
            
        elif self.tipo == "barrera": # Línea de pare roja
            nuevo_patch = patches.Rectangle((event.xdata-1, event.ydata-15), 2, 38, 
                                          color='red', zorder=5)
            
        elif self.tipo == "linea_central":
            nuevo_patch = patches.Rectangle((event.xdata-15, event.ydata-1), 30, 2, 
                                          color='yellow', zorder=3)
            # No hay "guia_led", es una linea real desde que nace

        # 2. Creación y Activación Universal
        if nuevo_patch:
            self.patch.axes.add_patch(nuevo_patch)
            nuevo_obj = DraggableElement(nuevo_patch, tipo_final, self.editor)
            self.editor.elementos.append(nuevo_obj)
            
            # Esto es lo que permite que se "pegue" al ratón de inmediato:
            nuevo_obj.press = nuevo_patch.get_xy()[0], nuevo_patch.get_xy()[1], event.xdata, event.ydata
            
            self.canvas.draw()
            print(f"Instalando: {tipo_final}")

    def on_motion(self, event):
        if self.press is None or event.inaxes != self.patch.axes: return
        x0, y0, xpress, ypress = self.press
        dx = event.xdata - xpress
        dy = event.ydata - ypress
        self.patch.set_xy((x0 + dx, y0 + dy))
        self.canvas.draw_idle()

    def on_release(self, event):
        if self.press is None: return
        
        # Snap-to-grid normal
        x, y = self.patch.get_xy()
        if x < 0:
            print("Elemento en área de fábrica, eliminado")
            self.borrar_elemento()
            self.press = None
            return
        # Snap-to-grid ajuste a la rejilla
        self.patch.set_xy((round(x/10)*10, round(y/5)*5))

        self.press = None
        self.canvas.draw_idle()
        self.canvas.draw_idle()

    def explotar_en_leds(self, x_base, y_base):
        # 1. Limpieza de la guía
        self.patch.remove()
        if self in self.editor.elementos:
            self.editor.elementos.remove(self)
        
        # 2. Inicializar el contenedor si no existe
        if not hasattr(self.editor, 'segmentos_led'):
            self.editor.segmentos_led = {}

        distancia = 60 
        for n in range(1, 8):
            x_seg = x_base + (n-1) * distancia
            p = patches.Rectangle((x_seg, y_base), 35, 2, color='yellow', zorder=3)
            
            # ¡CLAVE!: Añadirlo al AXES antes de crear el objeto Draggable
            self.patch.axes.add_patch(p)
            
            # Guardar la referencia para el control de teclas (2-7)
            self.editor.segmentos_led[n] = p
            
            # CREAR EL OBJETO Y GUARDARLO EN LA LISTA PRINCIPAL
            # Esto evita que desaparezca al redibujar
            nuevo_led = DraggableElement(p, f"led_{n}", self.editor)
            self.editor.elementos.append(nuevo_led)
        
        self.canvas.draw()
        print(f"Infraestructura: {len(self.editor.segmentos_led)} LEDs fijados en el sistema.")

class EditorEDSIM:
    
    def __init__(self):
        self.version = "v0.7 - Base Dinámica" # <--- Define aquí tu versión
        self.fig, self.ax = plt.subplots(figsize=(14, 6))
        
        # Configuramos el título de la ventana de Windows/Linux
        self.fig.canvas.manager.set_window_title(f"EDSIM {self.version} - Popayán Smart City")
        
        # ... resto de tu código ...

    def multiplicar_serie_led(self):
        # Buscamos la última línea central que pusiste
        lineas = [el for el in self.elementos if el.tipo == "linea_central"]
        if not lineas: return
        
        ultima_linea = lineas[-1]
        x_base, y_base = ultima_linea.patch.get_xy()
        distancia = 60
        
        if not hasattr(self, 'segmentos_led'):
            self.segmentos_led = {}
        
        # El primero ya existe, creamos del 2 al 7
        self.segmentos_led[1] = ultima_linea.patch
        for n in range(2, 8):
            x_nuevo = x_base + (n-1) * distancia
            p = patches.Rectangle((x_nuevo, y_base), 30, 2, color='yellow', zorder=3)
            self.ax.add_patch(p)
            
            # Los guardamos con ID para tus comandos 2-7
            nuevo_obj = DraggableElement(p, f"led_{n}", self)
            self.elementos.append(nuevo_obj)
            self.segmentos_led[n] = p
            
        self.fig.canvas.draw()
        print("Serie de 7 LEDs generada correctamente.")

    def set_semaforo(self, color):
        for el in self.elementos:
            if "cebra" in el.tipo:
                # La cebra se pone verde si el semáforo está rojo (Peatón pasa)
                el.patch.set_edgecolor('green' if color == 'red' else 'white')
            if "barrera" in el.tipo:
                el.patch.set_color(color)
        self.fig.canvas.draw()
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
        if event.key == 'm': # M para Multiplicar la línea
            self.multiplicar_serie_led()
        if event.key == 's':
            self.guardar_mapa()
        elif event.key == 'l':
            self.cargar_mapa()
        # Comandos de Parqueo Inteligente (Teclas 2 al 7)
        if event.key in ['2', '3', '4', '5', '6', '7']:
            n = int(event.key)
            self.controlar_infraestructura(n)
    
        # Comandos de Semáforo LED
        elif event.key == 'r': self.set_semaforo('red')
        elif event.key == 'n': self.set_semaforo('orange')
        elif event.key == 'v': self.set_semaforo('green') 

    def controlar_infraestructura(self, n):
        """Apaga LED y enciende Slot en verde de forma segura"""
        is_on = False  # Valor por defecto para evitar el UnboundLocalError
        
        # 1. Control del LED
        if hasattr(self, 'segmentos_led') and n in self.segmentos_led:
            led = self.segmentos_led[n]
            # Verificamos si es amarillo (on)
            # Nota: Comparar colores en Matplotlib puede ser truculento, 
            # así que usamos una bandera o comparamos el primer valor (Red)
            color_actual = led.get_facecolor()
            is_on = color_actual[0] > 0.5 and color_actual[1] > 0.5 # Es amarillo
            
            # Si está encendido (amarillo), lo "apagamos" (gris oscuro)
            nuevo_color = '#333333' if is_on else 'yellow'
            led.set_color(nuevo_color)
        
        # 2. Control del Slot (Buscamos el slot_n)
        for el in self.elementos:
            if el.tipo == f"slot_{n}":
                # Si el LED estaba ON, ahora el slot se pone VERDE (Abierto)
                # Si el LED estaba OFF, el slot vuelve a AZUL
                el.patch.set_color('green' if is_on else 'blue')
                el.patch.set_alpha(0.8 if is_on else 0.4)
        
        self.fig.canvas.draw_idle()

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

    def on_hover(self, event):
        if event.inaxes == self.ax:
            for el in self.elementos:
                cont, _ = el.patch.contains(event)
                if cont:
                    # Cambia el título del gráfico temporalmente
                    self.ax.set_title(f"Elemento detectado: {el.tipo}")
                    self.fig.canvas.draw_idle()
                    return
            self.ax.set_title(f"EDSIM {self.version} - Editor de Infraestructura")
            self.fig.canvas.draw_idle()

        # Y en el __init__ conectas el evento:
        self.fig.canvas.mpl_connect('motion_notify_event', self.on_hover)

editor = EditorEDSIM()
plt.show()