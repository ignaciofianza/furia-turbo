# Furia Turbo

Furia Turbo es un videojuego arcade local para dos jugadores desarrollado en Python con Pygame.

El proyecto fue realizado como apoyo para una actividad vinculada a IdMKids. No se trata de un proyecto personal ni de un producto comercial, sino de una implementación desarrollada para ser utilizada por otra persona dentro de ese contexto.

La propuesta busca ofrecer una experiencia simple, rápida y fácil de entender, especialmente pensada para público infantil.

## Características

- Juego local para 2 jugadores.
- Carreras cortas de estilo arcade.
- Selección de autos por color.
- Dos autos controlados por CPU.
- Los jugadores controlan únicamente el movimiento lateral.
- Avance automático durante la carrera.
- Power-ups de turbo y frenado.
- Las CPU no interactúan con los power-ups.
- El primer vehículo en cruzar la meta siempre es uno de los dos jugadores.
- Tabla de resultados con tiempos de llegada.
- Música y efectos de sonido.
- Secuencia de salida inspirada en las cinco luces de Fórmula 1.
- Interfaz y estética retro inspirada en videojuegos arcade y de 16 bits.
- Soporte para pantalla completa y escalado dinámico.
- Builds para Windows, macOS y Linux.

## Controles

### Jugador 1

Durante la selección de vehículo:

- `A` / `D`: cambiar de vehículo.
- `W`: confirmar selección.

Durante la carrera:

- `A`: mover hacia la izquierda.
- `D`: mover hacia la derecha.

### Jugador 2

Durante la selección de vehículo:

- Flecha izquierda / derecha: cambiar de vehículo.
- Flecha arriba: confirmar selección.

Durante la carrera:

- Flecha izquierda: mover hacia la izquierda.
- Flecha derecha: mover hacia la derecha.

## Power-ups

Actualmente existen dos tipos de elementos interactivos:

### Turbo

Aumenta temporalmente la velocidad del jugador que lo recoge.

### Bache

Reduce temporalmente la velocidad del jugador que lo atraviesa.

Los power-ups solo afectan a los jugadores. Los vehículos controlados por CPU los ignoran.

## Selección de vehículos

Los jugadores deben elegir vehículos distintos.

Una vez que Jugador 1 y Jugador 2 confirman sus elecciones, los dos colores restantes son asignados automáticamente a los vehículos controlados por CPU.

Colores disponibles:

- Rojo
- Azul
- Verde
- Amarillo

## Flujo del juego

1. Pantalla principal.
2. Selección de vehículo del Jugador 1.
3. Selección de vehículo del Jugador 2.
4. Pantalla de preparación.
5. Secuencia de cinco luces.
6. Carrera.
7. Pantalla de resultados.
8. Opción de volver a jugar o regresar al menú principal.

## Requisitos

- Python 3.13
- Pygame 2.6.1

Las dependencias del proyecto se encuentran en:

`requirements.txt`

## Ejecutar desde código fuente

Crear un entorno virtual:

`python3 -m venv .venv`

Activarlo en macOS o Linux:

`source .venv/bin/activate`

En Windows:

`.venv\Scripts\activate`

Instalar dependencias:

`pip install -r requirements.txt`

Ejecutar:

`python3 main.py`

En Windows también puede utilizarse:

`python main.py`

## Builds

El repositorio utiliza GitHub Actions para generar versiones ejecutables para:

- Windows
- macOS
- Linux

Los ejecutables compilados se publican en la sección Releases del repositorio.

## macOS

La versión para macOS no está firmada ni notarizada mediante Apple Developer.

Por este motivo, macOS puede mostrar una advertencia de seguridad al abrir la aplicación por primera vez.

En caso de ser necesario, puede abrirse utilizando clic derecho sobre la aplicación y seleccionando `Abrir`.

## Estructura del proyecto

`assets/`

Contiene imágenes, música, efectos de sonido e iconos.

`entities/`

Contiene las entidades principales del juego, como los vehículos.

`systems/`

Contiene la lógica de carrera y el sistema de power-ups.

`ui/`

Contiene las diferentes pantallas e interfaz del juego.

`game.py`

Gestiona la carrera, renderizado del circuito, vehículos y elementos interactivos.

`main.py`

Gestiona el loop principal, estados de la aplicación, fullscreen y escalado de resolución.

## Tecnologías

- Python
- Pygame
- PyInstaller
- GitHub Actions

## Contexto

Este proyecto fue desarrollado para ser utilizado en una actividad relacionada con IdMKids.

La implementación fue realizada específicamente para ese propósito y no representa un proyecto comercial ni un videojuego desarrollado para publicación profesional.

## Licencia

Actualmente el proyecto no posee una licencia específica.
