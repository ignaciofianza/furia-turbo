import math
import os
import random

import pygame

from config import (
    WIDTH,
    HEIGHT,
    LANE_LIMIT,
    RACE_DISTANCE,
)

from entities.car import Car
from systems.race import RaceManager
from systems.powerups import PowerUpManager

# ================================================================
# IDENTIDAD DE LOS AUTOS
# ================================================================

CAR_COLORS = {
    "rojo": {
        "file": "auto_rojo.png",
        "rgb": (255, 70, 85),
    },
    "azul": {
        "file": "auto_azul.png",
        "rgb": (70, 160, 255),
    },
    "verde": {
        "file": "auto_verde.png",
        "rgb": (70, 230, 130),
    },
    "amarillo": {
        "file": "auto_amarillo.png",
        "rgb": (255, 220, 70),
    },
}


class Game:
    def __init__(
        self,
        screen,
        player_1_color="rojo",
        player_2_color="azul",
    ):
        self.screen = screen

        # --------------------------------------------------------
        # Fuentes
        # --------------------------------------------------------

        self.font_cache = {}

        # --------------------------------------------------------
        # Selección de autos
        # --------------------------------------------------------

        self.player_1_color = player_1_color
        self.player_2_color = player_2_color

        self._validate_selected_colors()

        remaining_colors = [
            color
            for color in CAR_COLORS
            if color
            not in (
                self.player_1_color,
                self.player_2_color,
            )
        ]

        # En el futuro podemos hacer random.shuffle()
        # si queremos variar qué CPU recibe cada color.
        self.cpu_1_color = remaining_colors[0]
        self.cpu_2_color = remaining_colors[1]

        # --------------------------------------------------------
        # PERSPECTIVA / PISTA
        # --------------------------------------------------------

        self.horizon_y = 105
        self.road_bottom_y = HEIGHT + 35

        self.road_top_width = 220
        self.road_bottom_width = 1080

        self.visible_distance = 1900.0
        self.camera_offset = 420.0

        # --------------------------------------------------------
        # ASSETS
        # --------------------------------------------------------

        self.car_images = self._load_car_images()

        # --------------------------------------------------------
        # AUTOS
        # --------------------------------------------------------

        self.player_1 = self._create_car(
            name="Jugador 1",
            color=self.player_1_color,
            player_id=1,
        )

        self.player_2 = self._create_car(
            name="Jugador 2",
            color=self.player_2_color,
            player_id=2,
        )

        self.cpu_1 = self._create_car(
            name="CPU 1",
            color=self.cpu_1_color,
            player_id=None,
        )

        self.cpu_2 = self._create_car(
            name="CPU 2",
            color=self.cpu_2_color,
            player_id=None,
        )

        self.cars = [
            self.player_1,
            self.player_2,
            self.cpu_1,
            self.cpu_2,
        ]

        # --------------------------------------------------------
        # Sistemas
        # --------------------------------------------------------

        self.race = RaceManager(self.cars)

        self.powerups = PowerUpManager()

        self.reset()

    # ================================================================
    # CONFIGURACIÓN DE AUTOS
    # ================================================================

    def _validate_selected_colors(self):
        if self.player_1_color not in CAR_COLORS:
            raise ValueError(f"Color inválido para J1: {self.player_1_color}")

        if self.player_2_color not in CAR_COLORS:
            raise ValueError(f"Color inválido para J2: {self.player_2_color}")

        if self.player_1_color == self.player_2_color:
            raise ValueError("Jugador 1 y Jugador 2 deben usar autos distintos.")

    def _create_car(
        self,
        name,
        color,
        player_id,
    ):
        car = Car(
            name=name,
            image=self.car_images[color],
            player_id=player_id,
        )

        # Guardamos el color en el auto sin necesitar
        # modificar el constructor de Car.
        car.color = color

        return car

    # ================================================================
    # RESET
    # ================================================================

    def reset(self):
        self.race.reset()
        self.powerups.reset()
        self.race.start()

    # ================================================================
    # ASSETS
    # ================================================================

    def _load_car_images(self):
        base_path = os.path.join(
            "assets",
            "imagenes",
        )

        images = {}

        for color, data in CAR_COLORS.items():
            path = os.path.join(
                base_path,
                data["file"],
            )

            image = pygame.image.load(path).convert_alpha()

            # Tamaño base grande.
            # Después se achica/agranda según profundidad.
            image = pygame.transform.smoothscale(
                image,
                (180, 150),
            )

            images[color] = image

        return images

    # ================================================================
    # FUENTES
    # ================================================================

    def _font(
        self,
        size,
    ):
        if size not in self.font_cache:
            self.font_cache[size] = pygame.font.Font(
                None,
                size,
            )

        return self.font_cache[size]

    # ================================================================
    # INPUT
    # ================================================================

    def _get_player_controls(self):
        keys = pygame.key.get_pressed()

        # J1
        #
        # A = izquierda
        # D = derecha
        #
        # El avance es automático.
        player_1_controls = {
            "accelerate": True,
            "brake": False,
            "left": keys[pygame.K_a],
            "right": keys[pygame.K_d],
        }

        # J2
        #
        # ← = izquierda
        # → = derecha
        #
        # ↑ y ↓ no hacen nada.
        player_2_controls = {
            "accelerate": True,
            "brake": False,
            "left": keys[pygame.K_LEFT],
            "right": keys[pygame.K_RIGHT],
        }

        return (
            player_1_controls,
            player_2_controls,
        )

    # ================================================================
    # UPDATE
    # ================================================================

    def update(
        self,
        dt,
    ):
        if self.race.finished:
            return

        (
            player_1_controls,
            player_2_controls,
        ) = self._get_player_controls()

        # --------------------------------------------------------
        # Jugadores
        # --------------------------------------------------------

        self.player_1.update(
            dt,
            player_1_controls,
        )

        self.player_2.update(
            dt,
            player_2_controls,
        )

        # --------------------------------------------------------
        # CPU
        # --------------------------------------------------------

        self.cpu_1.update(dt)
        self.cpu_2.update(dt)

        # --------------------------------------------------------
        # Power-ups
        # --------------------------------------------------------

        self.powerups.update(self.cars)

        # --------------------------------------------------------
        # Carrera
        # --------------------------------------------------------

        self.race.update(dt)

    # ================================================================
    # CÁMARA
    # ================================================================

    def _get_camera_distance(self):
        average_distance = (self.player_1.distance + self.player_2.distance) / 2

        return max(
            0.0,
            average_distance - self.camera_offset,
        )

    # ================================================================
    # PERSPECTIVA
    # ================================================================

    def _distance_to_depth(
        self,
        world_distance,
        camera_distance,
    ):
        relative_distance = world_distance - camera_distance

        depth = 1.0 - relative_distance / self.visible_distance

        return max(
            0.0,
            min(
                depth,
                1.15,
            ),
        )

    def _depth_to_y(
        self,
        depth,
    ):
        depth = max(
            0.0,
            min(
                depth,
                1.15,
            ),
        )

        # Curva tipo pseudo-Mode 7.
        curved = depth**1.65

        return self.horizon_y + curved * (self.road_bottom_y - self.horizon_y)

    def _road_width_at_depth(
        self,
        depth,
    ):
        depth = max(
            0.0,
            min(
                depth,
                1.0,
            ),
        )

        curved = depth**1.25

        return (
            self.road_top_width
            + (self.road_bottom_width - self.road_top_width) * curved
        )

    def _lane_to_screen_x(
        self,
        lane_position,
        depth,
    ):
        road_width = self._road_width_at_depth(depth)

        usable_half_width = (road_width / 2) * 0.76

        normalized = lane_position / LANE_LIMIT

        return WIDTH / 2 + normalized * usable_half_width

    def _object_scale(
        self,
        depth,
    ):
        return max(
            0.25,
            min(
                0.25 + depth * 0.93,
                1.18,
            ),
        )

    # ================================================================
    # DRAW
    # ================================================================

    def draw(self):
        camera_distance = self._get_camera_distance()

        self._draw_background()

        self._draw_road(camera_distance)

        self._draw_finish_line(camera_distance)

        self._draw_powerups(camera_distance)

        self._draw_cars(camera_distance)

        self._draw_player_hud()

        self._draw_retro_overlay()

    # ================================================================
    # FONDO
    # ================================================================

    def _draw_background(self):
        # Cielo oscuro retro.
        self.screen.fill((28, 21, 48))

        # Banda de atardecer.
        pygame.draw.rect(
            self.screen,
            (112, 38, 100),
            (
                0,
                self.horizon_y - 60,
                WIDTH,
                60,
            ),
        )

        pygame.draw.rect(
            self.screen,
            (207, 70, 102),
            (
                0,
                self.horizon_y - 28,
                WIDTH,
                28,
            ),
        )

        # Sol.
        pygame.draw.circle(
            self.screen,
            (255, 187, 75),
            (
                WIDTH // 2,
                self.horizon_y - 26,
            ),
            48,
        )

        # Algunas líneas oscuras sobre el sol,
        # bien estética synthwave barata y gloriosa.
        for y in range(
            self.horizon_y - 25,
            self.horizon_y + 15,
            10,
        ):
            pygame.draw.rect(
                self.screen,
                (207, 70, 102),
                (
                    WIDTH // 2 - 50,
                    y,
                    100,
                    4,
                ),
            )

        # Terreno.
        pygame.draw.rect(
            self.screen,
            (39, 112, 67),
            (
                0,
                self.horizon_y,
                WIDTH,
                HEIGHT - self.horizon_y,
            ),
        )

    # ================================================================
    # PISTA
    # ================================================================

    def _draw_road(
        self,
        camera_distance,
    ):
        top_left = WIDTH / 2 - self.road_top_width / 2

        top_right = WIDTH / 2 + self.road_top_width / 2

        bottom_left = WIDTH / 2 - self.road_bottom_width / 2

        bottom_right = WIDTH / 2 + self.road_bottom_width / 2

        road_polygon = [
            (
                top_left,
                self.horizon_y,
            ),
            (
                top_right,
                self.horizon_y,
            ),
            (
                bottom_right,
                self.road_bottom_y,
            ),
            (
                bottom_left,
                self.road_bottom_y,
            ),
        ]

        # Asfalto.
        pygame.draw.polygon(
            self.screen,
            (48, 49, 60),
            road_polygon,
        )

        # Banquinas / bordes.
        pygame.draw.line(
            self.screen,
            (255, 60, 165),
            (
                top_left,
                self.horizon_y,
            ),
            (
                bottom_left,
                self.road_bottom_y,
            ),
            8,
        )

        pygame.draw.line(
            self.screen,
            (255, 60, 165),
            (
                top_right,
                self.horizon_y,
            ),
            (
                bottom_right,
                self.road_bottom_y,
            ),
            8,
        )

        # Segunda línea cian al lado del borde.
        pygame.draw.line(
            self.screen,
            (40, 220, 230),
            (
                top_left + 7,
                self.horizon_y,
            ),
            (
                bottom_left + 18,
                self.road_bottom_y,
            ),
            3,
        )

        pygame.draw.line(
            self.screen,
            (40, 220, 230),
            (
                top_right - 7,
                self.horizon_y,
            ),
            (
                bottom_right - 18,
                self.road_bottom_y,
            ),
            3,
        )

        self._draw_lane_markers(camera_distance)

        self._draw_roadside_posts(camera_distance)

    # ================================================================
    # MARCAS DE CARRIL
    # ================================================================

    def _draw_lane_markers(
        self,
        camera_distance,
    ):
        spacing = 260
        marker_length = 105

        offset = camera_distance % spacing

        start = camera_distance - offset

        for i in range(13):
            distance = start + i * spacing

            end_distance = distance + marker_length

            depth_start = self._distance_to_depth(
                distance,
                camera_distance,
            )

            depth_end = self._distance_to_depth(
                end_distance,
                camera_distance,
            )

            if depth_start <= 0 and depth_end <= 0:
                continue

            y1 = self._depth_to_y(depth_start)

            y2 = self._depth_to_y(depth_end)

            for lane_position in (
                -0.14,
                0.14,
            ):
                x1 = self._lane_to_screen_x(
                    lane_position,
                    depth_start,
                )

                x2 = self._lane_to_screen_x(
                    lane_position,
                    depth_end,
                )

                width = max(
                    1,
                    int(2 + depth_start * 5),
                )

                pygame.draw.line(
                    self.screen,
                    (235, 232, 212),
                    (
                        int(x1),
                        int(y1),
                    ),
                    (
                        int(x2),
                        int(y2),
                    ),
                    width,
                )

    # ================================================================
    # POSTES
    # ================================================================

    def _draw_roadside_posts(
        self,
        camera_distance,
    ):
        spacing = 330

        offset = camera_distance % spacing

        start = camera_distance - offset

        for i in range(11):
            distance = start + i * spacing

            depth = self._distance_to_depth(
                distance,
                camera_distance,
            )

            if depth <= 0:
                continue

            y = self._depth_to_y(depth)

            road_width = self._road_width_at_depth(depth)

            size = max(
                2,
                int(4 + depth * 14),
            )

            for side in (
                -1,
                1,
            ):
                x = WIDTH / 2 + side * (road_width / 2 + 22 + depth * 28)

                pygame.draw.rect(
                    self.screen,
                    (35, 225, 230),
                    (
                        int(x - size / 2),
                        int(y - size * 2),
                        size,
                        size * 3,
                    ),
                )

                pygame.draw.rect(
                    self.screen,
                    (255, 70, 170),
                    (
                        int(x - size / 2),
                        int(y - size * 2),
                        size,
                        max(
                            2,
                            size // 2,
                        ),
                    ),
                )

    # ================================================================
    # META
    # ================================================================

    def _draw_finish_line(
        self,
        camera_distance,
    ):
        depth = self._distance_to_depth(
            RACE_DISTANCE,
            camera_distance,
        )

        if depth <= 0:
            return

        y = self._depth_to_y(depth)

        if y < self.horizon_y or y > HEIGHT:
            return

        road_width = self._road_width_at_depth(depth)

        left = WIDTH / 2 - road_width / 2

        tile_size = max(
            4,
            int(8 + depth * 18),
        )

        columns = max(
            1,
            int(road_width / tile_size),
        )

        for column in range(columns):
            if column % 2 == 0:
                color = (
                    245,
                    245,
                    245,
                )
            else:
                color = (
                    25,
                    25,
                    30,
                )

            pygame.draw.rect(
                self.screen,
                color,
                (
                    int(left + column * tile_size),
                    int(y),
                    tile_size + 1,
                    tile_size,
                ),
            )

    # ================================================================
    # AUTOS
    # ================================================================

    def _draw_cars(
        self,
        camera_distance,
    ):
        draw_data = []

        for car in self.cars:
            depth = self._distance_to_depth(
                car.distance,
                camera_distance,
            )

            if depth <= 0:
                continue

            y = self._depth_to_y(depth)

            x = self._lane_to_screen_x(
                car.lane_position,
                depth,
            )

            draw_data.append(
                (
                    depth,
                    car,
                    x,
                    y,
                )
            )

        # Primero dibujamos los más lejanos.
        draw_data.sort(key=lambda item: item[0])

        for (
            depth,
            car,
            x,
            y,
        ) in draw_data:

            scale = self._object_scale(depth)

            width = max(
                1,
                int(car.image.get_width() * scale),
            )

            height = max(
                1,
                int(car.image.get_height() * scale),
            )

            image = pygame.transform.scale(
                car.image,
                (
                    width,
                    height,
                ),
            )

            # Sombra.
            shadow_width = int(width * 0.74)

            pygame.draw.ellipse(
                self.screen,
                (20, 18, 27),
                (
                    int(x - shadow_width / 2),
                    int(y + height * 0.28),
                    shadow_width,
                    max(
                        5,
                        int(height * 0.14),
                    ),
                ),
            )

            rect = image.get_rect(
                center=(
                    int(x),
                    int(y),
                )
            )

            self.screen.blit(
                image,
                rect,
            )

            # Etiqueta J1/J2.
            if car.is_player:
                self._draw_car_player_tag(
                    car,
                    x,
                    y,
                    height,
                    depth,
                )

    def _draw_car_player_tag(
        self,
        car,
        x,
        y,
        height,
        depth,
    ):
        if depth < 0.30:
            return

        rgb = CAR_COLORS[car.color]["rgb"]

        text = "J1" if car.player_id == 1 else "J2"

        font = self._font(
            max(
                16,
                int(22 * depth),
            )
        )

        surface = font.render(
            text,
            True,
            (255, 255, 255),
        )

        padding = 4

        background = pygame.Rect(
            0,
            0,
            surface.get_width() + padding * 2,
            surface.get_height() + 2,
        )

        background.center = (
            int(x),
            int(y - height * 0.58),
        )

        pygame.draw.rect(
            self.screen,
            (17, 17, 25),
            background,
        )

        pygame.draw.rect(
            self.screen,
            rgb,
            background,
            2,
        )

        text_rect = surface.get_rect(center=background.center)

        self.screen.blit(
            surface,
            text_rect,
        )

    # ================================================================
    # POWER-UPS
    # ================================================================

    def _draw_powerups(
        self,
        camera_distance,
    ):
        for powerup in self.powerups.get_active_powerups():
            depth = self._distance_to_depth(
                powerup.distance,
                camera_distance,
            )

            if depth <= 0:
                continue

            y = self._depth_to_y(depth)

            x = self._lane_to_screen_x(
                powerup.lane_position,
                depth,
            )

            if powerup.kind == "boost":
                self._draw_turbo_pad(
                    x,
                    y,
                    depth,
                )

            elif powerup.kind == "slow":
                self._draw_pothole(
                    x,
                    y,
                    depth,
                )

    # ================================================================
    # TURBO
    # ================================================================

    def _draw_turbo_pad(
        self,
        x,
        y,
        depth,
    ):
        scale = 0.35 + depth * 0.85

        width = max(
            28,
            int(125 * scale),
        )

        height = max(
            12,
            int(46 * scale),
        )

        points = [
            (
                x - width / 2,
                y,
            ),
            (
                x + width / 2,
                y,
            ),
            (
                x + width * 0.38,
                y + height,
            ),
            (
                x - width * 0.38,
                y + height,
            ),
        ]

        # Marco magenta.
        pygame.draw.polygon(
            self.screen,
            (255, 55, 170),
            points,
        )

        inset = max(
            2,
            int(5 * scale),
        )

        inner_points = [
            (
                x - width / 2 + inset,
                y + inset,
            ),
            (
                x + width / 2 - inset,
                y + inset,
            ),
            (
                x + width * 0.38 - inset,
                y + height - inset,
            ),
            (
                x - width * 0.38 + inset,
                y + height - inset,
            ),
        ]

        # Interior cian.
        pygame.draw.polygon(
            self.screen,
            (28, 220, 225),
            inner_points,
        )

        # Flechas.
        arrow_size = max(
            3,
            int(12 * scale),
        )

        for offset in (
            -0.23,
            0.0,
            0.23,
        ):
            cx = x + width * offset

            arrow = [
                (
                    cx,
                    y + height * 0.15,
                ),
                (
                    cx + arrow_size,
                    y + height * 0.53,
                ),
                (
                    cx + arrow_size / 2,
                    y + height * 0.53,
                ),
                (
                    cx + arrow_size / 2,
                    y + height * 0.83,
                ),
                (
                    cx - arrow_size / 2,
                    y + height * 0.83,
                ),
                (
                    cx - arrow_size / 2,
                    y + height * 0.53,
                ),
                (
                    cx - arrow_size,
                    y + height * 0.53,
                ),
            ]

            pygame.draw.polygon(
                self.screen,
                (255, 239, 70),
                arrow,
            )

        # Texto TURBO cuando ya está relativamente cerca.
        if depth > 0.48:
            font_size = max(
                12,
                int(18 * depth),
            )

            font = self._font(font_size)

            text = font.render(
                "TURBO",
                True,
                (255, 255, 255),
            )

            rect = text.get_rect(
                center=(
                    int(x),
                    int(y + height * 0.50),
                )
            )

            self.screen.blit(
                text,
                rect,
            )

    # ================================================================
    # BACHE
    # ================================================================

    def _draw_pothole(
        self,
        x,
        y,
        depth,
    ):
        scale = 0.35 + depth * 0.85

        width = max(
            18,
            int(76 * scale),
        )

        height = max(
            8,
            int(34 * scale),
        )

        points = []

        count = 12

        for i in range(count):
            angle = i / count * math.tau

            variation = 0.76 if i % 2 == 0 else 1.0

            px = x + math.cos(angle) * width / 2 * variation

            py = y + math.sin(angle) * height / 2 * variation

            points.append(
                (
                    px,
                    py,
                )
            )

        # Asfalto roto.
        pygame.draw.polygon(
            self.screen,
            (81, 57, 48),
            points,
        )

        # Pozo.
        pygame.draw.ellipse(
            self.screen,
            (18, 17, 23),
            (
                int(x - width * 0.35),
                int(y - height * 0.25),
                int(width * 0.70),
                int(height * 0.52),
            ),
        )

        # Borde iluminado.
        pygame.draw.arc(
            self.screen,
            (151, 105, 74),
            (
                int(x - width * 0.30),
                int(y - height * 0.20),
                int(width * 0.60),
                int(height * 0.40),
            ),
            math.pi,
            math.tau,
            max(
                1,
                int(depth * 3),
            ),
        )

    # ================================================================
    # HUD JUGADORES
    # ================================================================

    def _draw_player_hud(self):
        self._draw_player_panel(
            self.player_1,
            x=24,
            align="left",
        )

        self._draw_player_panel(
            self.player_2,
            x=WIDTH - 24,
            align="right",
        )

    def _draw_player_panel(
        self,
        car,
        x,
        align,
    ):
        panel_width = 290
        panel_height = 128

        if align == "left":
            panel_x = x
        else:
            panel_x = x - panel_width

        panel_y = 20

        panel_rect = pygame.Rect(
            panel_x,
            panel_y,
            panel_width,
            panel_height,
        )

        # Fondo.
        pygame.draw.rect(
            self.screen,
            (14, 14, 23),
            panel_rect,
        )

        # Línea del color del auto.
        rgb = CAR_COLORS[car.color]["rgb"]

        pygame.draw.rect(
            self.screen,
            rgb,
            panel_rect,
            4,
        )

        # Decoración retro.
        pygame.draw.rect(
            self.screen,
            rgb,
            (
                panel_x + 8,
                panel_y + 8,
                8,
                panel_height - 16,
            ),
        )

        player_text = f"JUGADOR {car.player_id}"

        color_text = car.color.upper()

        title_font = self._font(30)

        small_font = self._font(23)

        effect_font = self._font(38)

        title_surface = title_font.render(
            player_text,
            True,
            (245, 245, 245),
        )

        color_surface = small_font.render(
            color_text,
            True,
            rgb,
        )

        self.screen.blit(
            title_surface,
            (
                panel_x + 27,
                panel_y + 12,
            ),
        )

        self.screen.blit(
            color_surface,
            (
                panel_x + 28,
                panel_y + 43,
            ),
        )

        # --------------------------------------------------------
        # Efecto activo
        # --------------------------------------------------------

        if car.active_effect == "boost":
            effect_text = "TURBO!!"

            effect_color = (
                50,
                240,
                235,
            )

        elif car.active_effect == "slow":
            effect_text = "FRENADO!!"

            effect_color = (
                255,
                85,
                70,
            )

        else:
            effect_text = "ESPERANDO..."

            effect_color = (
                150,
                150,
                160,
            )

        effect_surface = effect_font.render(
            effect_text,
            True,
            effect_color,
        )

        self.screen.blit(
            effect_surface,
            (
                panel_x + 28,
                panel_y + 68,
            ),
        )

        if car.active_effect is not None:
            timer_text = f"{max(car.effect_timer, 0):.1f} s"

            timer_surface = small_font.render(
                timer_text,
                True,
                (255, 255, 255),
            )

            timer_x = panel_x + panel_width - timer_surface.get_width() - 16

            self.screen.blit(
                timer_surface,
                (
                    timer_x,
                    panel_y + 94,
                ),
            )

            # Barra de tiempo visual.
            if car.active_effect == "boost":
                max_duration = 1.8
            else:
                max_duration = 1.8

            timer_ratio = max(
                0.0,
                min(
                    car.effect_timer / max_duration,
                    1.0,
                ),
            )

            bar_x = panel_x + 28

            bar_y = panel_y + 111

            bar_width = 180
            bar_height = 7

            pygame.draw.rect(
                self.screen,
                (52, 52, 62),
                (
                    bar_x,
                    bar_y,
                    bar_width,
                    bar_height,
                ),
            )

            pygame.draw.rect(
                self.screen,
                effect_color,
                (
                    bar_x,
                    bar_y,
                    int(bar_width * timer_ratio),
                    bar_height,
                ),
            )

    # ================================================================
    # EFECTO RETRO
    # ================================================================

    def _draw_retro_overlay(self):
        """
        Scanlines muy suaves para darle textura CRT/retro.

        Después podemos hacerlo bastante más lindo en screens.py.
        """

        overlay = pygame.Surface(
            (
                WIDTH,
                HEIGHT,
            ),
            pygame.SRCALPHA,
        )

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
                    22,
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

        self.screen.blit(
            overlay,
            (
                0,
                0,
            ),
        )
