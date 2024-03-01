import requests
import pandas as pd

res = requests.get(
    url="https://echarts.apache.org/examples/data/asset/data/aqi-beijing.json"
)

# Convert it to json
data = res.json()[-100:]

# Remap data
segmented_line_data = pd.DataFrame(
    [
        {
            "date": data[i][0],
            "y": data[i][1],
            "y_displaced": data[(i + 10) % len(data)][1],
            "y_multiplied": data[i][1] * 2,
        }
        for i in range(len(data))
    ]
)
