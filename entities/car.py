import random

from config import (
    PLAYER_MAX_SPEED,
    PLAYER_ACCELERATION,
    PLAYER_BRAKE,
    PLAYER_FRICTION,
    LANE_SPEED,
    LANE_LIMIT,
    AI_MIN_SPEED,
    AI_MAX_SPEED,
    RACE_DISTANCE,
)


class Car:
    def __init__(self, name, image, player_id=None):
        self.name = name
        self.image = image

        # player_id:
        # 1    -> Jugador 1
        # 2    -> Jugador 2
        # None -> IA
        self.player_id = player_id

        self.reset()

    @property
    def is_player(self):
        return self.player_id is not None

    @property
    def is_ai(self):
        return self.player_id is None

    def reset(self):
        # Carrera
        self.distance = 0.0
        self.previous_distance = 0.0

        # Posición lateral normalizada
        self.lane_position = random.uniform(-0.2, 0.2)
        self.previous_lane_position = self.lane_position

        # Movimiento
        self.speed = 0.0

        # IA
        self.ai_target_speed = random.uniform(
            AI_MIN_SPEED,
            AI_MAX_SPEED,
        )

        # Meta
        self.finished = False
        self.finish_time = None
        self.finish_position = None

        # Power-ups / efectos
        self.speed_multiplier = 1.0
        self.effect_timer = 0.0
        self.active_effect = None

    def update(self, dt, controls=None):
        if self.finished:
            return

        self.previous_distance = self.distance
        self.previous_lane_position = self.lane_position

        if self.is_player:
            self.update_player(dt, controls)
        else:
            self.update_ai(dt)

        self.update_effect(dt)

        effective_speed = self.speed * self.speed_multiplier
        self.distance += effective_speed * dt

        self.distance = min(self.distance, RACE_DISTANCE + 500)

    def update_player(self, dt, controls):
        if controls is None:
            return

        accelerate = controls.get("accelerate", False)
        brake = controls.get("brake", False)
        left = controls.get("left", False)
        right = controls.get("right", False)

        if accelerate:
            self.speed += PLAYER_ACCELERATION * dt
        else:
            self.speed -= PLAYER_FRICTION * dt

        if brake:
            self.speed -= PLAYER_BRAKE * dt

        self.speed = max(
            0.0,
            min(self.speed, PLAYER_MAX_SPEED),
        )

        if left:
            self.lane_position -= LANE_SPEED * dt

        if right:
            self.lane_position += LANE_SPEED * dt

        self.lane_position = max(
            -LANE_LIMIT,
            min(self.lane_position, LANE_LIMIT),
        )

    def update_ai(self, dt):
        acceleration = 80.0

        if self.speed < self.ai_target_speed:
            self.speed += acceleration * dt

        elif self.speed > self.ai_target_speed:
            self.speed -= acceleration * dt

        # Cambios suaves de velocidad para que no parezcan trenes.
        if random.random() < 0.003:
            self.ai_target_speed = random.uniform(
                AI_MIN_SPEED,
                AI_MAX_SPEED,
            )

        # Movimiento lateral ocasional.
        if random.random() < 0.004:
            self.lane_position += random.uniform(
                -0.12,
                0.12,
            )

        self.lane_position = max(
            -LANE_LIMIT,
            min(self.lane_position, LANE_LIMIT),
        )

    def apply_effect(self, effect, multiplier, duration):
        self.active_effect = effect
        self.speed_multiplier = multiplier
        self.effect_timer = duration

    def clear_effect(self):
        self.active_effect = None
        self.speed_multiplier = 1.0
        self.effect_timer = 0.0

    def update_effect(self, dt):
        if self.effect_timer <= 0:
            return

        self.effect_timer -= dt

        if self.effect_timer <= 0:
            self.clear_effect()

    def crossed_finish_line(self):
        if self.finished:
            return False
        return self.previous_distance < RACE_DISTANCE and self.distance >= RACE_DISTANCE
