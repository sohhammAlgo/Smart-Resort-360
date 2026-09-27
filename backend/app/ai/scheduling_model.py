"""Agent 5 — Staff Scheduling recommendation from occupancy forecast -> workload."""


def recommend_staffing(occupancy_forecast_pct: float, base_staff: int = 10) -> dict:
    if occupancy_forecast_pct >= 90:
        workload = "HIGH"
        recommended_staff = int(base_staff * 1.5)
    elif occupancy_forecast_pct >= 60:
        workload = "MEDIUM"
        recommended_staff = base_staff
    else:
        workload = "LOW"
        recommended_staff = max(4, int(base_staff * 0.7))
    return {"workload": workload, "recommended_staff": recommended_staff}
