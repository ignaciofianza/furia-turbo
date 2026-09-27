import pygame

from config import WIDTH, HEIGHT, FPS
from game import Game
from ui.screens import ScreenManager


def create_display(fullscreen):
    if fullscreen:
        return pygame.display.set_mode((0, 0), pygame.FULLSCREEN)

    return pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)


def main():
    pygame.init()

    if not pygame.mixer.get_init():
        pygame.mixer.init()

    # ---------------------------------------------------------
    # Pantalla real
    # ---------------------------------------------------------

    fullscreen = True
    display = create_display(fullscreen)

    # Ahora que YA existe un modo de video,
    # podemos usar convert_alpha().
    icon = pygame.image.load("assets/imagenes/icon.png").convert_alpha()

    pygame.display.set_icon(icon)
    pygame.display.set_caption("Furia Turbo")

    # ---------------------------------------------------------
    # Superficie interna del juego
    # ---------------------------------------------------------

    game_surface = pygame.Surface((WIDTH, HEIGHT))

    clock = pygame.time.Clock()

    screens = ScreenManager(game_surface)

    game = None

    running = True
    pygame.init()

    if not pygame.mixer.get_init():
        pygame.mixer.init()

    pygame.display.set_caption("Furia Turbo")
    icon = pygame.image.load("assets/imagenes/icon.png").convert_alpha()

    pygame.display.set_icon(icon)

    # ---------------------------------------------------------
    # Pantalla real
    # ---------------------------------------------------------

    fullscreen = True

    display = create_display(fullscreen)

    # ---------------------------------------------------------
    # Superficie interna del juego
    #
    # TODO se dibuja siempre en 1280x720.
    # Después lo escalamos a la pantalla real.
    # ---------------------------------------------------------

    game_surface = pygame.Surface((WIDTH, HEIGHT))

    clock = pygame.time.Clock()

    screens = ScreenManager(game_surface)

    game = None

    running = True

    while running:
        dt = clock.tick(FPS) / 1000.0

        # =====================================================
        # EVENTOS
        # =====================================================

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN:
                # ---------------------------------------------
                # ESC
                # ---------------------------------------------

                if event.key == pygame.K_ESCAPE:
                    running = False

                # ---------------------------------------------
                # F11
                # Fullscreen / ventana
                # ---------------------------------------------

                elif event.key == pygame.K_F11:
                    fullscreen = not fullscreen

                    display = create_display(fullscreen)

            # Las pantallas manejan su input
            # excepto durante la carrera.
            if screens.state != "race":
                screens.handle_event(event)

        # =====================================================
        # UI / MENÚS
        # =====================================================

        if screens.state != "race":
            screens.update(dt)

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

        # =====================================================
        # CARRERA
        # =====================================================

        else:
            if game is None:
                screens.state = "title"

                screens._on_state_enter("title")

            else:
                game.update(dt)

                game.draw()

                if game.race.finished:
                    screens.go_to_results(game)

        # =====================================================
        # ESCALADO A PANTALLA REAL
        # =====================================================

        display_width = display.get_width()

        display_height = display.get_height()

        # Escalamos manteniendo proporción 16:9.
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

    pygame.quit()


if __name__ == "__main__":
    main()
