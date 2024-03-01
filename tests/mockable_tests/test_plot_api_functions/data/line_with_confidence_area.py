import requests

# Download the data
res = requests.get(
    url="https://echarts.apache.org/examples/data/asset/data/confidence-band.json"
)

# Convert it to json
confidence_data = res.json()

for dat in confidence_data:
    dat["value"] = dat["value"] * 100
    dat["l"] = dat["l"] * 100
    dat["u"] = dat["u"] * 100
