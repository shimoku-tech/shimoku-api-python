Install with:

`pip install shimoku-api-python`

Start with:

```
from os import getenv
import shimoku_api_python.client as Shimoku

access_token = getenv('SHIMOKU_TOKEN')  # env var with your token
universe_id: str = getenv('UNIVERSE_ID')  # your universe UUID

shimoku = Shimoku.Client(    
    config={'access_token': access_token},
    universe_id=universe_id,
)
```

See the [docs](https://docs.shimoku.com/)

Reach us at contact@shimoku.com or at shimoku.com
