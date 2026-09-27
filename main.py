import os
import sys

import pygame

from config import WIDTH, HEIGHT, FPS

# ================================================================
# PYINSTALLER / RUTAS
# ================================================================
#
# Cuando corre empaquetado con PyInstaller, los assets se extraen
# temporalmente en sys._MEIPASS.
#
# Hacemos chdir ahí para que todas las rutas relativas del proyecto
# sigan funcionando igual que en desarrollo.
# ================================================================

if getattr(sys, "frozen", False):
    os.chdir(sys._MEIPASS)


from game import Game
from ui.screens import ScreenManager

# ================================================================
# DISPLAY
# ================================================================


def create_display(fullscreen):
    if fullscreen:
        return pygame.display.set_mode(
            (0, 0),
            pygame.FULLSCREEN,
        )

    return pygame.display.set_mode(
        (WIDTH, HEIGHT),
        pygame.RESIZABLE,
    )


# ================================================================
# MAIN
# ================================================================


def main():
    pygame.init()

    # ------------------------------------------------------------
    # Audio
    # ------------------------------------------------------------

    if not pygame.mixer.get_init():
        pygame.mixer.init()

    # ------------------------------------------------------------
    # Ventana real
    # ------------------------------------------------------------

    fullscreen = True

    display = create_display(fullscreen)

    pygame.display.set_caption("Furia Turbo")

    # ------------------------------------------------------------
    # Icono
    # ------------------------------------------------------------

    icon_path = os.path.join(
        "assets",
        "imagenes",
        "icon.png",
    )

    if os.path.exists(icon_path):
        icon = pygame.image.load(icon_path).convert_alpha()

        pygame.display.set_icon(icon)

    # ------------------------------------------------------------
    # Superficie interna
    #
    # Todo el juego se dibuja SIEMPRE en 1280x720.
    # Después se escala a la resolución real.
    # ------------------------------------------------------------

    game_surface = pygame.Surface(
        (
            WIDTH,
            HEIGHT,
        )
    )

    clock = pygame.time.Clock()

    # ------------------------------------------------------------
    # UI / Estados
    # ------------------------------------------------------------

    screens = ScreenManager(game_surface)

    # El objeto Game recién se crea
    # después de que J1 y J2 eligen autos.
    game = None

    running = True

    # ============================================================
    # LOOP PRINCIPAL
    # ============================================================

    while running:
        dt = clock.tick(FPS) / 1000.0

        # ========================================================
        # EVENTOS
        # ========================================================

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN:

                # ------------------------------------------------
                # ESC = salir
                # ------------------------------------------------

                if event.key == pygame.K_ESCAPE:
                    running = False

                # ------------------------------------------------
                # F11 = fullscreen / ventana
                # ------------------------------------------------

                elif event.key == pygame.K_F11:
                    fullscreen = not fullscreen

                    display = create_display(fullscreen)

            # Las pantallas manejan input propio
            # mientras no estamos corriendo.
            if screens.state != "race":
                screens.handle_event(event)

        # ========================================================
        # MENÚ / SHOWROOM / LOADING / COUNTDOWN / RESULTS
        # ========================================================

        if screens.state != "race":
            screens.update(dt)

            # ----------------------------------------------------
            # Cuando termina el semáforo:
            # creamos la carrera con los autos elegidos.
            # ----------------------------------------------------

            if screens.countdown_finished():
                (
                    player_1_color,
                    player_2_color,
                ) = screens.get_selected_colors()

                game = Game(
                    game_surface,
                    player_1_color=player_1_color,
                    player_2_color=player_2_color,
                )

                screens.state = "race"

                screens._on_state_enter("race")

            screens.draw()

        # ========================================================
        # CARRERA
        # ========================================================

        else:
            # Seguridad:
            # si por alguna razón estamos en race
            # sin Game creado, volvemos al título.
            if game is None:
                screens.state = "title"

                screens._on_state_enter("title")

            else:
                game.update(dt)

                game.draw()

                # ------------------------------------------------
                # Fin de carrera
                # ------------------------------------------------

                if game.race.finished:
                    screens.go_to_results(game)

        # ========================================================
        # ESCALADO A PANTALLA REAL
        # ========================================================

        display_width = display.get_width()

        display_height = display.get_height()

        # Mantener proporción 16:9.
        scale = min(
            display_width / WIDTH,
            display_height / HEIGHT,
        )

        scaled_width = int(WIDTH * scale)

        scaled_height = int(HEIGHT * scale)

        scaled_surface = pygame.transform.smoothscale(
            game_surface,
            (
                scaled_width,
                scaled_height,
            ),
        )

        # Fondo negro para letterboxing.
        display.fill((0, 0, 0))

        offset_x = (display_width - scaled_width) // 2

        offset_y = (display_height - scaled_height) // 2

        display.blit(
            scaled_surface,
            (
                offset_x,
                offset_y,
            ),
        )

        pygame.display.flip()

    # ============================================================
    # CIERRE
    # ============================================================

    pygame.quit()


if __name__ == "__main__":
    main()
