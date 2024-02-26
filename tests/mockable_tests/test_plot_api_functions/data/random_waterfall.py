import random

random_waterfall_data = [
    {
        "x": f"day {i}",
        "Income": random.randint(0, 100),
        "Expenses": random.randint(0, 100),
    }
    for i in range(500)
]
