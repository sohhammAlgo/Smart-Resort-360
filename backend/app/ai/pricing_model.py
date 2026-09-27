"""Agent 3 — Dynamic Pricing. Rule-driven mapping from forecast demand to a
recommended price multiplier — low demand lowers price, high demand raises it."""

BASE_ROOM_PRICE = 150.0


def recommend_price(
    occupancy_forecast: float, base_price: float = BASE_ROOM_PRICE
) -> dict:
    if occupancy_forecast < 0.4 * 10:  # low
        multiplier = 0.9
    elif occupancy_forecast < 0.75 * 10:  # medium
        multiplier = 1.0
    else:  # high
        multiplier = 1.25
    return {
        "base_price": base_price,
        "multiplier": multiplier,
        "recommended_price": round(base_price * multiplier, 2),
    }
