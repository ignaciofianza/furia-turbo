from config import RACE_DISTANCE


class RaceManager:
    def __init__(self, cars):
        self.cars = cars

        # Estado general de carrera
        self.race_time = 0.0
        self.started = False
        self.finished = False

        # Ganador oficial: siempre J1 o J2
        self.winner = None

        # Indica si ya cruzó el primer jugador
        self.first_player_finished = False

        # Orden real de llegada de los cuatro autos
        self.finish_order = []

        # Después de que gana J1/J2 dejamos unos segundos
        # para que terminen los demás
        self.post_finish_timer = 0.0
        self.post_finish_duration = 5.0

        # Guardamos el dt del último frame
        # para calcular mejor el tiempo exacto de llegada
        self.last_dt = 0.0

    def reset(self):
        self.race_time = 0.0
        self.started = False
        self.finished = False

        self.winner = None
        self.first_player_finished = False

        self.finish_order = []

        self.post_finish_timer = 0.0
        self.last_dt = 0.0

        for car in self.cars:
            car.reset()

    def start(self):
        self.race_time = 0.0
        self.started = True
        self.finished = False

        self.winner = None
        self.first_player_finished = False

        self.finish_order = []

        self.post_finish_timer = 0.0
        self.last_dt = 0.0

    def update(self, dt):
        if not self.started:
            return

        if self.finished:
            return

        self.last_dt = dt
        self.race_time += dt

        # Antes de que gane J1/J2,
        # ninguna CPU puede cruzar la meta.
        self._hold_ai_before_finish()

        # Comprobamos quién cruzó este frame.
        self._check_finishers()

        # Cuando ya llegó el primer jugador,
        # dejamos unos segundos para completar resultados.
        if self.first_player_finished:
            self.post_finish_timer += dt

            all_finished = all(car.finished for car in self.cars)

            if all_finished or self.post_finish_timer >= self.post_finish_duration:
                self.finished = True

    def _hold_ai_before_finish(self):
        """
        Impide que una CPU sea el primer auto en cruzar la meta.

        Puede llegar hasta prácticamente la línea,
        pero queda esperando ahí hasta que termine J1 o J2.
        """

        if self.first_player_finished:
            return

        # Dejamos a la IA apenas antes de la meta.
        ai_limit = RACE_DISTANCE - 5.0

        for car in self.cars:
            if not car.is_ai:
                continue

            if car.finished:
                continue

            if car.distance >= ai_limit:
                car.distance = ai_limit

                # También evitamos que la distancia anterior
                # haga parecer que cruzó la meta.
                car.previous_distance = min(
                    car.previous_distance,
                    ai_limit,
                )

                # Bajamos un poco la velocidad para que no esté
                # intentando atravesar la meta a 300 km/h cada frame.
                car.speed = min(car.speed, 120.0)

    def _check_finishers(self):
        crossed_cars = []

        for car in self.cars:
            if car.finished:
                continue

            if car.crossed_finish_line():
                crossed_cars.append(car)

        if not crossed_cars:
            return

        # Si varios cruzaron durante el mismo frame,
        # calculamos quién cruzó primero realmente.
        crossed_cars.sort(key=self._finish_cross_factor)

        for car in crossed_cars:
            # Seguridad extra:
            # una IA jamás puede ser primera.
            if car.is_ai and not self.first_player_finished:
                continue

            cross_factor = self._finish_cross_factor(car)

            car.finished = True

            # Tiempo estimado exacto de cruce dentro del frame.
            car.finish_time = self.race_time - (1.0 - cross_factor) * self.last_dt

            car.finish_position = len(self.finish_order) + 1

            self.finish_order.append(car)

            # El primer jugador que cruza es el ganador oficial.
            if car.is_player and not self.first_player_finished:
                self.winner = car
                self.first_player_finished = True
                self.post_finish_timer = 0.0

    def _finish_cross_factor(self, car):
        """
        Devuelve en qué parte del frame cruzó la meta.

        0.0 = al principio del frame
        1.0 = al final del frame
        """

        frame_distance = car.distance - car.previous_distance

        if frame_distance <= 0:
            return 1.0

        remaining_distance = RACE_DISTANCE - car.previous_distance

        factor = remaining_distance / frame_distance

        return max(0.0, min(factor, 1.0))

    def get_positions(self):
        """
        Devuelve los 4 autos ordenados.

        Los que ya terminaron:
        por orden de llegada.

        Los que siguen:
        por distancia recorrida.
        """

        finished_cars = [car for car in self.cars if car.finished]

        racing_cars = [car for car in self.cars if not car.finished]

        finished_cars.sort(key=lambda car: car.finish_position)

        racing_cars.sort(
            key=lambda car: car.distance,
            reverse=True,
        )

        return finished_cars + racing_cars

    def get_progress(self, car):
        """
        Progreso entre 0.0 y 1.0.
        """

        return max(
            0.0,
            min(
                car.distance / RACE_DISTANCE,
                1.0,
            ),
        )

    def get_results(self):
        """
        Devuelve resultados finales.

        Autos que terminaron:
        conservan su posición y tiempo.

        Autos que no terminaron cuando se corta la carrera:
        quedan después en orden de distancia.
        """

        return self.get_positions()
