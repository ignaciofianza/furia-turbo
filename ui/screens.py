import os

import pygame

from config import WIDTH, HEIGHT

CAR_COLORS = {
    "rojo": {
        "rgb": (235, 55, 70),
        "showroom": "showroom_rojo.png",
    },
    "azul": {
        "rgb": (55, 135, 235),
        "showroom": "showroom_azul.png",
    },
    "verde": {
        "rgb": (60, 200, 105),
        "showroom": "showroom_verde.png",
    },
    "amarillo": {
        "rgb": (245, 205, 55),
        "showroom": "showroom_amarillo.png",
    },
}

COLOR_ORDER = [
    "rojo",
    "azul",
    "verde",
    "amarillo",
]


class ScreenManager:
    def __init__(self, screen):
        self.screen = screen

        self.font_cache = {}
        self.showroom_images = self._load_showroom_images()

        # --------------------------------------------------------
        # Audio
        # --------------------------------------------------------

        self.select_sound = self._load_sound("select.wav")
        self.confirm_sound = self._load_sound("confirm.wav")
        self.f1_sound = self._load_sound("f1lights.wav")

        # --------------------------------------------------------
        # Estado
        # --------------------------------------------------------

        self.state = "title"

        self.player_1_color = None
        self.player_2_color = None

        self.selection_index = 0

        # --------------------------------------------------------
        # Fade
        # --------------------------------------------------------

        self.fade_alpha = 0.0
        self.fade_direction = 0
        self.fade_target_state = None

        # --------------------------------------------------------
        # Loading
        # --------------------------------------------------------

        self.loading_timer = 0.0

        # --------------------------------------------------------
        # Countdown
        # --------------------------------------------------------

        self.countdown_timer = 0.0

        # 1 segundo por luz
        self.light_interval = 1.0

        # Tiempo con las cinco luces prendidas
        self.all_lights_hold = 1.15

        # Total:
        # 5 s encendiendo + 1.15 s esperando
        self.countdown_total = self.light_interval * 5 + self.all_lights_hold

        # --------------------------------------------------------
        # Resultados
        # --------------------------------------------------------

        self.results_selection = 0
        self.results_data = None

        self._play_music("menu.ogg")

    # ============================================================
    # ASSETS
    # ============================================================

    def _load_showroom_images(self):
        images = {}

        base_path = os.path.join(
            "assets",
            "imagenes",
        )

        for color, data in CAR_COLORS.items():
            path = os.path.join(
                base_path,
                data["showroom"],
            )

            image = pygame.image.load(path).convert_alpha()

            # No deformamos tanto la imagen.
            # Se escala manteniendo buena presencia.
            image = pygame.transform.smoothscale(
                image,
                (540, 310),
            )

            images[color] = image

        return images

    def _load_sound(self, filename):
        path = os.path.join(
            "assets",
            "audio",
            filename,
        )

        if not os.path.exists(path):
            return None

        return pygame.mixer.Sound(path)

    # ============================================================
    # FUENTES
    # ============================================================

    def _font(self, size):
        if size not in self.font_cache:
            self.font_cache[size] = pygame.font.Font(
                None,
                size,
            )

        return self.font_cache[size]

    # ============================================================
    # AUDIO
    # ============================================================

    def _play_music(self, filename):
        path = os.path.join(
            "assets",
            "audio",
            filename,
        )

        if not os.path.exists(path):
            return

        pygame.mixer.music.stop()
        pygame.mixer.music.load(path)
        pygame.mixer.music.play(-1)

    def _fade_music_out(self):
        pygame.mixer.music.fadeout(500)

    # ============================================================
    # TRANSICIONES
    # ============================================================

    def start_fade(self, target_state):
        if self.fade_direction != 0:
            return

        self.fade_direction = 1
        self.fade_target_state = target_state

    def _update_fade(self, dt):
        if self.fade_direction == 0:
            return

        speed = 400

        self.fade_alpha += speed * dt * self.fade_direction

        # Se llegó a negro.
        if self.fade_direction == 1 and self.fade_alpha >= 255:
            self.fade_alpha = 255

            self.state = self.fade_target_state

            self._on_state_enter(self.state)

            self.fade_direction = -1

        # Terminó de aparecer la nueva pantalla.
        elif self.fade_direction == -1 and self.fade_alpha <= 0:
            self.fade_alpha = 0
            self.fade_direction = 0
            self.fade_target_state = None

    def _draw_fade(self):
        if self.fade_alpha <= 0:
            return

        overlay = pygame.Surface((WIDTH, HEIGHT))

        overlay.fill((0, 0, 0))

        overlay.set_alpha(int(self.fade_alpha))

        self.screen.blit(
            overlay,
            (0, 0),
        )

    # ============================================================
    # ESTADOS
    # ============================================================

    def _on_state_enter(self, state):
        if state == "title":
            self.player_1_color = None
            self.player_2_color = None

            self.selection_index = 0

            self._play_music("menu.ogg")

        elif state == "showroom_p1":
            self.player_1_color = None
            self.player_2_color = None

            self.selection_index = 0

            self._play_music("showroom.ogg")

        elif state == "showroom_p2":
            self.selection_index = 0

        elif state == "loading":
            self.loading_timer = 0.0

            self._fade_music_out()

        elif state == "countdown":
            self.countdown_timer = 0.0

            if self.f1_sound:
                self.f1_sound.play()

        elif state == "race":
            self._play_music("race.ogg")

        elif state == "results":
            self.results_selection = 0

            self._play_music("podium.ogg")

    # ============================================================
    # INPUT
    # ============================================================

    def handle_event(self, event):
        if event.type != pygame.KEYDOWN:
            return

        # --------------------------------------------------------
        # HOME
        # --------------------------------------------------------

        if self.state == "title":
            self.start_fade("showroom_p1")

        # --------------------------------------------------------
        # JUGADOR 1
        # --------------------------------------------------------

        elif self.state == "showroom_p1":
            if event.key == pygame.K_a:
                self.selection_index -= 1
                self.selection_index %= len(COLOR_ORDER)

                if self.select_sound:
                    self.select_sound.play()

            elif event.key == pygame.K_d:
                self.selection_index += 1
                self.selection_index %= len(COLOR_ORDER)

                if self.select_sound:
                    self.select_sound.play()

            elif event.key == pygame.K_w:
                self.player_1_color = COLOR_ORDER[self.selection_index]

                if self.confirm_sound:
                    self.confirm_sound.play()

                self.start_fade("showroom_p2")

        # --------------------------------------------------------
        # JUGADOR 2
        # --------------------------------------------------------

        elif self.state == "showroom_p2":
            available = self._available_colors_for_p2()

            if event.key == pygame.K_LEFT:
                self.selection_index -= 1
                self.selection_index %= len(available)

                if self.select_sound:
                    self.select_sound.play()

            elif event.key == pygame.K_RIGHT:
                self.selection_index += 1
                self.selection_index %= len(available)

                if self.select_sound:
                    self.select_sound.play()

            elif event.key == pygame.K_UP:
                self.player_2_color = available[self.selection_index]

                if self.confirm_sound:
                    self.confirm_sound.play()

                self.start_fade("loading")

        # --------------------------------------------------------
        # RESULTADOS
        # --------------------------------------------------------

        elif self.state == "results":
            if event.key in (
                pygame.K_UP,
                pygame.K_w,
            ):
                self.results_selection = 0

                if self.select_sound:
                    self.select_sound.play()

            elif event.key in (
                pygame.K_DOWN,
                pygame.K_s,
            ):
                self.results_selection = 1

                if self.select_sound:
                    self.select_sound.play()

            elif event.key in (
                pygame.K_RETURN,
                pygame.K_SPACE,
            ):
                if self.confirm_sound:
                    self.confirm_sound.play()

                if self.results_selection == 0:
                    # Volver directamente al concesionario.
                    self.start_fade("showroom_p1")

                else:
                    # Volver a portada.
                    self.start_fade("title")

    # ============================================================
    # UPDATE
    # ============================================================

    def update(self, dt):
        self._update_fade(dt)

        if self.state == "loading":
            self.loading_timer += dt

            if self.loading_timer >= 1.6:
                self.state = "countdown"

                self._on_state_enter("countdown")

        elif self.state == "countdown":
            self.countdown_timer += dt

    # ============================================================
    # HELPERS
    # ============================================================

    def _available_colors_for_p2(self):
        return [color for color in COLOR_ORDER if color != self.player_1_color]

    def get_selected_colors(self):
        return (
            self.player_1_color,
            self.player_2_color,
        )

    def countdown_finished(self):
        return (
            self.state == "countdown" and self.countdown_timer >= self.countdown_total
        )

    # ============================================================
    # RESULTADOS
    # ============================================================

    def set_results(self, game):
        players = [
            game.player_1,
            game.player_2,
        ]

        players.sort(
            key=lambda car: (
                car.finish_time if car.finish_time is not None else float("inf")
            )
        )

        self.results_data = {
            "winner": game.race.winner,
            "players": players,
        }

    def go_to_results(self, game):
        self.set_results(game)

        self.state = "results"

        self._on_state_enter("results")

    # ============================================================
    # DRAW GENERAL
    # ============================================================

    def draw(self):
        if self.state == "title":
            self._draw_title()

        elif self.state == "showroom_p1":
            self._draw_showroom(player=1)

        elif self.state == "showroom_p2":
            self._draw_showroom(player=2)

        elif self.state == "loading":
            self._draw_loading()

        elif self.state == "countdown":
            self._draw_countdown()

        elif self.state == "results":
            self._draw_results()

        self._draw_crt_overlay()
        self._draw_fade()

    # ============================================================
    # HOME
    # ============================================================

    def _draw_title(self):
        # --------------------------------------------------------
        # Fondo
        # --------------------------------------------------------

        self.screen.fill((8, 10, 16))

        # Ciudad pixelada al fondo.
        skyline_y = 345

        buildings = [
            (0, 160, 85),
            (90, 120, 115),
            (215, 145, 90),
            (320, 95, 140),
            (430, 175, 60),
            (500, 125, 110),
            (620, 155, 80),
            (715, 100, 135),
            (825, 170, 65),
            (900, 115, 120),
            (1030, 150, 85),
            (1130, 105, 130),
        ]

        for x, width, height in buildings:
            rect = pygame.Rect(
                x,
                skyline_y - height,
                width,
                height,
            )

            pygame.draw.rect(
                self.screen,
                (20, 24, 38),
                rect,
            )

            # Ventanas
            for wx in range(
                x + 12,
                x + width - 8,
                24,
            ):
                for wy in range(
                    skyline_y - height + 14,
                    skyline_y - 12,
                    26,
                ):
                    if (wx // 24 + wy // 26) % 3 == 0:
                        pygame.draw.rect(
                            self.screen,
                            (255, 185, 65),
                            (
                                wx,
                                wy,
                                6,
                                8,
                            ),
                        )

        # --------------------------------------------------------
        # Carretera entrando desde abajo
        # --------------------------------------------------------

        road = [
            (
                WIDTH // 2 - 135,
                skyline_y,
            ),
            (
                WIDTH // 2 + 135,
                skyline_y,
            ),
            (
                WIDTH - 60,
                HEIGHT,
            ),
            (
                60,
                HEIGHT,
            ),
        ]

        pygame.draw.polygon(
            self.screen,
            (35, 37, 45),
            road,
        )

        # Bordes neón.
        pygame.draw.line(
            self.screen,
            (235, 55, 150),
            (
                WIDTH // 2 - 135,
                skyline_y,
            ),
            (
                60,
                HEIGHT,
            ),
            6,
        )

        pygame.draw.line(
            self.screen,
            (45, 220, 220),
            (
                WIDTH // 2 + 135,
                skyline_y,
            ),
            (
                WIDTH - 60,
                HEIGHT,
            ),
            6,
        )

        # Líneas de carril.
        for i in range(6):
            y = skyline_y + 35 + i * 60

            width = 20 + i * 14

            pygame.draw.rect(
                self.screen,
                (235, 235, 225),
                (
                    WIDTH // 2 - width // 2,
                    y,
                    width,
                    20,
                ),
            )

        # --------------------------------------------------------
        # Logo
        # --------------------------------------------------------

        logo_x = WIDTH // 2
        logo_y = 145

        # Shadow / bloque trasero
        shadow_font = self._font(124)

        title_font = self._font(124)

        furia_shadow = shadow_font.render(
            "FURIA",
            True,
            (0, 0, 0),
        )

        furia = title_font.render(
            "FURIA",
            True,
            (255, 70, 75),
        )

        turbo_shadow = shadow_font.render(
            "TURBO",
            True,
            (0, 0, 0),
        )

        turbo = title_font.render(
            "TURBO",
            True,
            (255, 220, 55),
        )

        self.screen.blit(
            furia_shadow,
            furia_shadow.get_rect(
                center=(
                    logo_x + 6,
                    logo_y + 6,
                )
            ),
        )

        self.screen.blit(
            furia,
            furia.get_rect(
                center=(
                    logo_x,
                    logo_y,
                )
            ),
        )

        self.screen.blit(
            turbo_shadow,
            turbo_shadow.get_rect(
                center=(
                    logo_x + 6,
                    logo_y + 101,
                )
            ),
        )

        self.screen.blit(
            turbo,
            turbo.get_rect(
                center=(
                    logo_x,
                    logo_y + 95,
                )
            ),
        )

        # Línea bajo el logo
        pygame.draw.rect(
            self.screen,
            (45, 220, 220),
            (
                WIDTH // 2 - 240,
                275,
                480,
                5,
            ),
        )

        pygame.draw.rect(
            self.screen,
            (235, 55, 150),
            (
                WIDTH // 2 - 120,
                286,
                240,
                4,
            ),
        )

        # --------------------------------------------------------
        # Prompt
        # --------------------------------------------------------

        blink = (pygame.time.get_ticks() // 550) % 2

        if blink == 0:
            prompt = self._font(34).render(
                "PRESIONÁ CUALQUIER BOTÓN",
                True,
                (245, 245, 240),
            )

            prompt_rect = prompt.get_rect(
                center=(
                    WIDTH // 2,
                    500,
                )
            )

            self.screen.blit(
                prompt,
                prompt_rect,
            )

        subtitle = self._font(22).render(
            "2 JUGADORES  •  TURBOS  •  CAOS",
            True,
            (125, 130, 145),
        )

        subtitle_rect = subtitle.get_rect(
            center=(
                WIDTH // 2,
                548,
            )
        )

        self.screen.blit(
            subtitle,
            subtitle_rect,
        )

        # --------------------------------------------------------
        # Barra inferior
        # --------------------------------------------------------

        pygame.draw.rect(
            self.screen,
            (8, 10, 16),
            (
                0,
                HEIGHT - 44,
                WIDTH,
                44,
            ),
        )

        footer = self._font(20).render(
            "FURIA TURBO  •  ARCADE EDITION",
            True,
            (85, 90, 110),
        )

        footer_rect = footer.get_rect(
            center=(
                WIDTH // 2,
                HEIGHT - 22,
            )
        )

        self.screen.blit(
            footer,
            footer_rect,
        )

    # ============================================================
    # SHOWROOM
    # ============================================================

    def _draw_showroom(self, player):
        self.screen.fill((12, 14, 22))

        if player == 1:
            available = COLOR_ORDER

            selected_color = available[self.selection_index]

            player_title = "JUGADOR 1"

            controls = "A / D  CAMBIAR     W  CONFIRMAR"

        else:
            available = self._available_colors_for_p2()

            selected_color = available[self.selection_index]

            player_title = "JUGADOR 2"

            controls = "FLECHAS IZQ/DER CAMBIAR     FLECHA ARRIBA CONFIRMAR"

        rgb = CAR_COLORS[selected_color]["rgb"]

        # --------------------------------------------------------
        # Cabecera
        # --------------------------------------------------------

        pygame.draw.rect(
            self.screen,
            (8, 10, 17),
            (
                0,
                0,
                WIDTH,
                92,
            ),
        )

        pygame.draw.rect(
            self.screen,
            rgb,
            (
                0,
                88,
                WIDTH,
                4,
            ),
        )

        title = self._font(52).render(
            "CONCESIONARIO",
            True,
            (245, 245, 245),
        )

        self.screen.blit(
            title,
            (
                42,
                21,
            ),
        )

        player_label = self._font(32).render(
            player_title,
            True,
            rgb,
        )

        self.screen.blit(
            player_label,
            (
                WIDTH - player_label.get_width() - 42,
                32,
            ),
        )

        # --------------------------------------------------------
        # Card principal
        # --------------------------------------------------------

        panel = pygame.Rect(
            90,
            125,
            WIDTH - 180,
            430,
        )

        pygame.draw.rect(
            self.screen,
            (23, 25, 35),
            panel,
        )

        pygame.draw.rect(
            self.screen,
            rgb,
            panel,
            4,
        )

        # Piso del showroom
        pygame.draw.rect(
            self.screen,
            (34, 35, 44),
            (
                panel.x + 4,
                panel.bottom - 90,
                panel.width - 8,
                86,
            ),
        )

        # Sombras diagonales
        for x in range(
            panel.x + 20,
            panel.right,
            80,
        ):
            pygame.draw.line(
                self.screen,
                (42, 44, 55),
                (
                    x,
                    panel.bottom - 88,
                ),
                (
                    x + 50,
                    panel.bottom - 4,
                ),
                3,
            )

        # --------------------------------------------------------
        # Auto lateral
        # --------------------------------------------------------

        image = self.showroom_images[selected_color]

        image_rect = image.get_rect(
            center=(
                WIDTH // 2,
                315,
            )
        )

        self.screen.blit(
            image,
            image_rect,
        )

        # --------------------------------------------------------
        # Nombre del color
        # --------------------------------------------------------

        color_surface = self._font(54).render(
            selected_color.upper(),
            True,
            rgb,
        )

        color_rect = color_surface.get_rect(
            center=(
                WIDTH // 2,
                490,
            )
        )

        self.screen.blit(
            color_surface,
            color_rect,
        )

        # --------------------------------------------------------
        # Flechas
        # --------------------------------------------------------

        left_surface = self._font(80).render(
            "<",
            True,
            (245, 245, 245),
        )

        right_surface = self._font(80).render(
            ">",
            True,
            (245, 245, 245),
        )

        self.screen.blit(
            left_surface,
            (
                115,
                290,
            ),
        )

        self.screen.blit(
            right_surface,
            (
                WIDTH - right_surface.get_width() - 115,
                290,
            ),
        )

        # --------------------------------------------------------
        # Colores disponibles
        # --------------------------------------------------------

        dot_spacing = 60
        dot_start = WIDTH // 2 - (len(available) - 1) * dot_spacing // 2

        for index, color in enumerate(available):
            dot_rgb = CAR_COLORS[color]["rgb"]

            x = dot_start + index * dot_spacing

            selected = index == self.selection_index

            radius = 16 if selected else 10

            pygame.draw.circle(
                self.screen,
                dot_rgb,
                (
                    x,
                    535,
                ),
                radius,
            )

            if selected:
                pygame.draw.circle(
                    self.screen,
                    (255, 255, 255),
                    (
                        x,
                        535,
                    ),
                    radius + 5,
                    2,
                )

        # --------------------------------------------------------
        # Controles
        # --------------------------------------------------------

        controls_surface = self._font(27).render(
            controls,
            True,
            (220, 220, 225),
        )

        controls_rect = controls_surface.get_rect(
            center=(
                WIDTH // 2,
                615,
            )
        )

        self.screen.blit(
            controls_surface,
            controls_rect,
        )

        if player == 2 and self.player_1_color:
            locked_rgb = CAR_COLORS[self.player_1_color]["rgb"]

            j1_locked = self._font(22).render(
                ("J1: " + self.player_1_color.upper() + "  •  AUTO OCUPADO"),
                True,
                locked_rgb,
            )

            self.screen.blit(
                j1_locked,
                (
                    32,
                    HEIGHT - 34,
                ),
            )

    # ============================================================
    # LOADING
    # ============================================================

    def _draw_loading(self):
        self.screen.fill((8, 10, 16))

        # Franjas
        for y in range(
            0,
            HEIGHT,
            48,
        ):
            pygame.draw.rect(
                self.screen,
                (
                    13 if y % 96 == 0 else 10,
                    13,
                    22,
                ),
                (
                    0,
                    y,
                    WIDTH,
                    48,
                ),
            )

        title = self._font(62).render(
            "PREPARANDO LA PISTA",
            True,
            (245, 245, 245),
        )

        title_rect = title.get_rect(
            center=(
                WIDTH // 2,
                280,
            )
        )

        self.screen.blit(
            title,
            title_rect,
        )

        # Barra animada
        bar = pygame.Rect(
            WIDTH // 2 - 250,
            365,
            500,
            24,
        )

        pygame.draw.rect(
            self.screen,
            (35, 38, 50),
            bar,
        )

        progress = min(
            self.loading_timer / 1.6,
            1.0,
        )

        pygame.draw.rect(
            self.screen,
            (45, 220, 220),
            (
                bar.x,
                bar.y,
                int(bar.width * progress),
                bar.height,
            ),
        )

        pygame.draw.rect(
            self.screen,
            (245, 245, 245),
            bar,
            2,
        )

        status = self._font(24).render(
            "CARGANDO AUTOS...",
            True,
            (130, 135, 150),
        )

        status_rect = status.get_rect(
            center=(
                WIDTH // 2,
                425,
            )
        )

        self.screen.blit(
            status,
            status_rect,
        )

    # ============================================================
    # COUNTDOWN F1
    # ============================================================

    def _draw_countdown(self):
        self.screen.fill((7, 8, 11))

        title = self._font(48).render(
            "SALIDA",
            True,
            (235, 235, 235),
        )

        title_rect = title.get_rect(
            center=(
                WIDTH // 2,
                135,
            )
        )

        self.screen.blit(
            title,
            title_rect,
        )

        # --------------------------------------------------------
        # Estructura del semáforo
        # --------------------------------------------------------

        housing = pygame.Rect(
            WIDTH // 2 - 345,
            230,
            690,
            180,
        )

        pygame.draw.rect(
            self.screen,
            (22, 23, 29),
            housing,
        )

        pygame.draw.rect(
            self.screen,
            (75, 77, 88),
            housing,
            5,
        )

        # Cuántas luces están prendidas.
        lights_on = min(
            5,
            int(self.countdown_timer // self.light_interval) + 1,
        )

        # Antes de 1 segundo, todavía ninguna.
        if self.countdown_timer < 1.0:
            lights_on = 0

        spacing = 125

        start_x = WIDTH // 2 - spacing * 2

        for index in range(5):
            x = start_x + index * spacing

            active = index < lights_on

            # Recuadro individual
            lamp_box = pygame.Rect(
                x - 46,
                260,
                92,
                120,
            )

            pygame.draw.rect(
                self.screen,
                (10, 10, 13),
                lamp_box,
            )

            pygame.draw.rect(
                self.screen,
                (53, 54, 62),
                lamp_box,
                3,
            )

            # Glow
            if active:
                pygame.draw.circle(
                    self.screen,
                    (120, 15, 20),
                    (
                        x,
                        320,
                    ),
                    45,
                )

                light_color = (
                    255,
                    40,
                    45,
                )
            else:
                light_color = (
                    48,
                    18,
                    20,
                )

            pygame.draw.circle(
                self.screen,
                light_color,
                (
                    x,
                    320,
                ),
                33,
            )

            pygame.draw.circle(
                self.screen,
                (105, 105, 115),
                (
                    x,
                    320,
                ),
                33,
                3,
            )

        # --------------------------------------------------------
        # Estado inferior
        # --------------------------------------------------------

        if self.countdown_timer < self.light_interval * 5:
            status_text = "PREPARATE"

            status_color = (
                180,
                180,
                190,
            )

        elif self.countdown_timer < self.countdown_total:
            status_text = "..."

            status_color = (
                255,
                65,
                65,
            )

        else:
            status_text = "¡YA!"

            status_color = (
                60,
                235,
                130,
            )

        status = self._font(60).render(
            status_text,
            True,
            status_color,
        )

        status_rect = status.get_rect(
            center=(
                WIDTH // 2,
                500,
            )
        )

        self.screen.blit(
            status,
            status_rect,
        )

        hint = self._font(22).render(
            "NO HACE FALTA ACELERAR",
            True,
            (110, 115, 130),
        )

        hint_rect = hint.get_rect(
            center=(
                WIDTH // 2,
                570,
            )
        )

        self.screen.blit(
            hint,
            hint_rect,
        )

    # ============================================================
    # RESULTADOS
    # ============================================================

    def _draw_results(self):
        self.screen.fill((10, 12, 18))

        title = self._font(70).render(
            "RESULTADOS",
            True,
            (245, 245, 245),
        )

        title_rect = title.get_rect(
            center=(
                WIDTH // 2,
                72,
            )
        )

        self.screen.blit(
            title,
            title_rect,
        )

        if not self.results_data:
            return

        winner = self.results_data["winner"]

        if winner:
            rgb = CAR_COLORS[winner.color]["rgb"]

            winner_surface = self._font(52).render(
                ("¡GANA JUGADOR " f"{winner.player_id}!"),
                True,
                rgb,
            )

            winner_rect = winner_surface.get_rect(
                center=(
                    WIDTH // 2,
                    148,
                )
            )

            self.screen.blit(
                winner_surface,
                winner_rect,
            )

        players = self.results_data["players"]

        y = 230

        for position, car in enumerate(
            players,
            start=1,
        ):
            rgb = CAR_COLORS[car.color]["rgb"]

            panel = pygame.Rect(
                WIDTH // 2 - 300,
                y,
                600,
                92,
            )

            pygame.draw.rect(
                self.screen,
                (25, 27, 37),
                panel,
            )

            pygame.draw.rect(
                self.screen,
                rgb,
                panel,
                4,
            )

            pos = self._font(48).render(
                f"{position}°",
                True,
                (245, 245, 245),
            )

            self.screen.blit(
                pos,
                (
                    panel.x + 22,
                    panel.y + 22,
                ),
            )

            player = self._font(32).render(
                f"JUGADOR {car.player_id}",
                True,
                rgb,
            )

            self.screen.blit(
                player,
                (
                    panel.x + 120,
                    panel.y + 14,
                ),
            )

            color_surface = self._font(22).render(
                car.color.upper(),
                True,
                (165, 170, 185),
            )

            self.screen.blit(
                color_surface,
                (
                    panel.x + 122,
                    panel.y + 51,
                ),
            )

            if car.finish_time is not None:
                time_text = f"{car.finish_time:.2f} s"
            else:
                time_text = "--"

            time = self._font(34).render(
                time_text,
                True,
                (245, 245, 245),
            )

            time_rect = time.get_rect(
                midright=(
                    panel.right - 24,
                    panel.centery,
                )
            )

            self.screen.blit(
                time,
                time_rect,
            )

            y += 112

        # --------------------------------------------------------
        # Opciones
        # --------------------------------------------------------

        options = [
            "VOLVER A JUGAR",
            "MENÚ PRINCIPAL",
        ]

        start_y = 500

        for index, option in enumerate(options):
            selected = index == self.results_selection

            if selected:
                color = (
                    45,
                    225,
                    220,
                )

                prefix = "> "
            else:
                color = (
                    145,
                    150,
                    165,
                )

                prefix = " "

            surface = self._font(32).render(
                prefix + option,
                True,
                color,
            )

            rect = surface.get_rect(
                center=(
                    WIDTH // 2,
                    start_y + index * 50,
                )
            )

            self.screen.blit(
                surface,
                rect,
            )

        instructions = self._font(20).render(
            ("W/S o ARRIBA/ABAJO  ELEGIR   •   ENTER  CONFIRMAR"),
            True,
            (100, 105, 120),
        )

        instructions_rect = instructions.get_rect(
            center=(
                WIDTH // 2,
                HEIGHT - 35,
            )
        )

        self.screen.blit(
            instructions,
            instructions_rect,
        )

    # ============================================================
    # CRT / RETRO
    # ============================================================

    def _draw_crt_overlay(self):
        overlay = pygame.Surface(
            (
                WIDTH,
                HEIGHT,
            ),
            pygame.SRCALPHA,
        )

        # Scanlines suaves
        for y in range(
            0,
            HEIGHT,
            4,
        ):
            pygame.draw.line(
                overlay,
                (
                    0,
                    0,
                    0,
                    20,
                ),
                (
                    0,
                    y,
                ),
                (
                    WIDTH,
                    y,
                ),
            )

        # Viñeta lateral muy ligera
        pygame.draw.rect(
            overlay,
            (
                0,
                0,
                0,
                22,
            ),
            (
                0,
                0,
                15,
                HEIGHT,
            ),
        )

        pygame.draw.rect(
            overlay,
            (
                0,
                0,
                0,
                22,
            ),
            (
                WIDTH - 15,
                0,
                15,
                HEIGHT,
            ),
        )

        self.screen.blit(
            overlay,
            (0, 0),
        )
