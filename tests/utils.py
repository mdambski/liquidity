from datetime import date, datetime
from json import JSONEncoder

import numpy as np


class JSONSerializer(JSONEncoder):
    """JSON serializer for objects not serializable by default json code."""

    def default(self, obj):
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        if isinstance(obj, (datetime, date)):
            return obj.isoformat()
        return JSONEncoder.default(self, obj)
