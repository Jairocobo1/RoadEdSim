# Proyecto EDSIM - v0.1
**Fecha:** 05/04/2026
**Ubicación:** Popayán, Colombia

## Objetivo
Desarrollar un editor de mapas urbanos modulares con capacidad de simulación de tráfico inteligente.

## Especificaciones de Módulos
- **ModuloRecto:** Tramo de 200 unidades.
- **Cebra:** Sensor de parada y zona peatonal.
- **Slot Parqueo:** 20 unidades, color azul con degradado.
- **Semáforo:** Lógica de 4 colores (Rojo, Naranja, Verde, Azul).

## Control de Versiones
- Repositorio: [Aquí pondrás tu link de GitHub luego]

## Flujo de trabajo
Diseñar el mapa arrastrando las piezas desde la fábrica (Menú izquierdo).

1. Alinear usando el Snap-to-Grid (que ya está configurado a 20 unidades).

2. Guardar (esta será nuestra siguiente función, para que la 3. estructura no se pierda al cerrar el programa).

---
## Actualización de Avance - Miércoles 08/04/2026
- **Versión:** 0.5 (Estabilidad Visual y Persistencia)
- **Cambios realizados:**
    - **Corrección de Proporciones:** Implementación de `set_aspect('equal')` para evitar deformación de piezas.
    - **Persistencia JSON:** Sistema de guardado (tecla 'S') y carga (tecla 'L') operativo en la carpeta `data/`.
    - **Interfaz de Fábrica:** Limpieza de la zona de diseño y corrección de etiquetas.
    - **Nuevas Piezas:** Inclusión de Línea Central Amarilla y Barreras Rojas con proporciones reales.
- **Estado del Repositorio:** Sincronizado con cuenta Jairocobo1.

---
## Actualización de Avance - Jueves 09/04/2026 (Sesión 1)
- **Versión:** 0.6 (Editor Perfeccionado)
- **Cambios realizados:**
    - **Función de Borrado:** Implementado clic derecho para eliminar elementos del escenario.
    - **Optimización de Memoria:** Los elementos borrados se eliminan tanto visualmente como de la lista lógica de Python.
    - **Preparación de Infraestructura:** Ajuste de clases para recibir controladores de señalización dinámica (LEDs). 
    ---
#
- **Versión:** 0.6 (Infraestructura Estática Finalizada)
- **Hitos alcanzados:**
    - **Optimización del Editor:** Implementación de borrado selectivo de objetos mediante clic derecho, asegurando la limpieza de memoria en la lista de elementos.
    - **Cierre de Fase Estática:** Se completa la versión mínima funcional de la infraestructura física (asfalto, cebras, slots y líneas).
- **Próximos Pasos (Fase Dinámica):**
    - Evolución de la infraestructura hacia un sistema interactivo.
    - Implementación de controladores para la señalización LED dinámica en línea central y zonas de parqueo.
    - Preparación del entorno para la simulación de flujo vehicular.hasta aqui la  version minima estatica de la infraestructura y del editor en la proxima empezaremos con la base dinamica de la infraestructura para poder hacer la simulacion del sistema