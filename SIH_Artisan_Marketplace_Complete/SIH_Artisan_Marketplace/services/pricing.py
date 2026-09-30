def calculate_price(cost, hours, complexity, labour_rate=150, margin=0.25):
    cost = max(float(cost), 0)
    hours = max(float(hours), 0)
    complexity = max(1, min(int(complexity), 5))

    complexity_multiplier = {
        1: 0.90,
        2: 1.00,
        3: 1.10,
        4: 1.25,
        5: 1.45
    }[complexity]

    base = cost + hours * labour_rate
    adjusted = base * complexity_multiplier
    suggested = adjusted / max(1 - margin, 0.05)

    return {
        "base_cost": base,
        "complexity_multiplier": complexity_multiplier,
        "margin": margin,
        "suggested_price": round(suggested),
        "min_price": round(adjusted * 1.05),
        "max_price": round(suggested * 1.35)
    }
