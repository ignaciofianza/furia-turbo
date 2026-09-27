import os
import random

import pygame

from config import (
    RACE_DISTANCE,
    BOOST_MULTIPLIER,
    BOOST_DURATION,
    SLOW_MULTIPLIER,
    SLOW_DURATION,
)


class PowerUp:
    def __init__(
        self,
        kind,
        distance,
        lane_position,
    ):
        self.kind = kind
        self.distance = distance
        self.lane_position = lane_position

        self.active = True

    def apply_to(self, car):
        if not self.active:
            return False

        # Las CPU nunca pueden agarrar power-ups.
        if car.is_ai:
            return False

        if self.kind == "boost":
            car.apply_effect(
                effect="boost",
                multiplier=BOOST_MULTIPLIER,
                duration=BOOST_DURATION,
            )

        elif self.kind == "slow":
            car.apply_effect(
                effect="slow",
                multiplier=SLOW_MULTIPLIER,
                duration=SLOW_DURATION,
            )

        else:
            return False

        self.active = False

        return True


class PowerUpManager:
    def __init__(self):
        self.powerups = []

        # ---------------------------------------------------------
        # SONIDOS
        # ---------------------------------------------------------

        self.boost_sound = self._load_sound("boost.wav")

        self.brake_sound = self._load_sound("brake.wav")

        # Volumen de efectos.
        if self.boost_sound:
            self.boost_sound.set_volume(0.75)

        if self.brake_sound:
            self.brake_sound.set_volume(0.75)

    # =============================================================
    # AUDIO
    # =============================================================

    def _load_sound(
        self,
        filename,
    ):
        path = os.path.join(
            "assets",
            "audio",
            filename,
        )

        if not os.path.exists(path):
            print(f"[Audio] No se encontró: {path}")

            return None

        try:
            return pygame.mixer.Sound(path)

        except pygame.error as error:
            print(f"[Audio] Error cargando {filename}: {error}")

            return None

    def _play_powerup_sound(
        self,
        kind,
    ):
        if kind == "boost":
            if self.boost_sound:
                self.boost_sound.play()

        elif kind == "slow":
            if self.brake_sound:
                self.brake_sound.play()

    # =============================================================
    # RESET
    # =============================================================

    def reset(self):
        self.powerups = self._generate_powerups()

    # =============================================================
    # GENERACIÓN
    # =============================================================

    def _generate_powerups(self):
        powerups = []

        # Dejamos el comienzo tranquilo.
        current_distance = 700

        # No ponemos power-ups justo en la meta.
        end_distance = RACE_DISTANCE - 700

        while current_distance < end_distance:
            kind = random.choice(
                [
                    "boost",
                    "slow",
                ]
            )

            lane_position = random.uniform(
                -0.35,
                0.35,
            )

            powerups.append(
                PowerUp(
                    kind=kind,
                    distance=current_distance,
                    lane_position=lane_position,
                )
            )

            current_distance += random.randint(
                450,
                700,
            )

        return powerups

    # =============================================================
    # UPDATE
    # =============================================================

    def update(
        self,
        cars,
    ):
        for powerup in self.powerups:
            if not powerup.active:
                continue

            for car in cars:
                # CPU ignora completamente
                # los power-ups.
                if car.is_ai:
                    continue

                if not self._car_touched_powerup(
                    car,
                    powerup,
                ):
                    continue

                applied = powerup.apply_to(car)

                if applied:
                    self._play_powerup_sound(powerup.kind)

                # El power-up ya fue consumido,
                # no seguimos buscando otro auto.
                break

    # =============================================================
    # COLISIÓN
    # =============================================================

    def _car_touched_powerup(
        self,
        car,
        powerup,
    ):
        """
        Comprueba si el auto pasó por la distancia
        del power-up durante este frame y si estaba
        lateralmente encima de él.
        """

        crossed_distance = car.previous_distance < powerup.distance <= car.distance

        if not crossed_distance:
            return False

        frame_distance = car.distance - car.previous_distance

        if frame_distance <= 0:
            return False

        # Punto exacto del frame en el que
        # el auto cruzó el power-up.
        factor = (powerup.distance - car.previous_distance) / frame_distance

        lane_at_crossing = (
            car.previous_lane_position
            + (car.lane_position - car.previous_lane_position) * factor
        )

        # Un poco generoso porque es un juego
        # arcade para gurises.
        collision_range = 0.12

        return abs(lane_at_crossing - powerup.lane_position) <= collision_range

    # =============================================================
    # DRAW SUPPORT
    # =============================================================

    def get_active_powerups(self):
        return [powerup for powerup in self.powerups if powerup.active]
