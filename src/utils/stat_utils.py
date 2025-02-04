import math


def calculate_dew_point(temperature: float, humidity: float) -> float:
    vpd = calculate_vapour_pressure_deficit(temperature, humidity)
    return 240.7 * vpd / (7.6- vpd)


def calculate_vapour_pressure_deficit(temperature: float, humidity: float) -> float:
    return math.log10(
        humidity
        / 100
        * (6.1078 * math.pow(10, (7.6 * temperature) / (240.7 + temperature)))
        / 6.1078
    )
