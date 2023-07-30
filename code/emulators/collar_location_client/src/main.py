from enum import Enum
from gps_sensor import GPSSensor
from updates_controller import UpdatesController
import threading
import time
import os
from environment import COLLAR_ID, MODE, SIMULATION_ROUTE_PATH


class Mode(str, Enum):
    SIMULATION = "SIMULATION"
    AUTHENTIC = "AUTHENTIC"


def absolute_path(relative_path: str) -> str:
    return os.path.join(os.path.dirname(__file__), relative_path)


def simulate_gps_location_sensor_updates(gps_sensor: GPSSensor) -> None:
    with open(absolute_path(SIMULATION_ROUTE_PATH), "r") as f:
        while True:
            line = f.readline()
            if not line:
                break
            # line is float,float
            location = tuple([float(val.strip()) for val in line.strip().split(",")])
            if len(location) != 2:
                raise RuntimeError(f"Invalid GPS location line: {line}")
            print(f"[Simulation]: Producing new location: {location}")
            gps_sensor.set_location(location=location)
            time.sleep(1)


if __name__ == "__main__":
    producer = UpdatesController(collar_id=COLLAR_ID)
    gps_sensor = GPSSensor()

    gps_sensor.on_new_location = producer.on_gps_location_update

    if MODE == Mode.AUTHENTIC:
        print("Authentic Mode Start")
        # let the gps sensor handle it natively
        gps_sensor.start()
    elif MODE == Mode.SIMULATION:
        # run simulation
        print("Simulation Mode Start")
        threading.Thread(
            target=simulate_gps_location_sensor_updates, args=(gps_sensor,)
        ).start()
    else:
        raise EnvironmentError(f"Unsupported script mode: {MODE}")