from typing import Optional, Dict, TYPE_CHECKING

from shimoku.api.base_resource import Resource

if TYPE_CHECKING:
    from shimoku.api.resources.universe import Universe

import logging

logger = logging.getLogger(__name__)


class ActivityTemplate(Resource):
    _module_logger = logger
    resource_type = "activityTemplate"
    alias_field = ("name", "version")
    plural = "activityTemplates"

    def __init__(
        self,
        parent: "Universe",
        uuid: Optional[str] = None,
        alias: Optional[str] = None,
        db_resource: Optional[Dict] = None,
    ):
        params = dict(
            name=alias if alias else "",
            version="",
            description="",
            availableModeCost={},
            inputSettings={},
            minRunInterval=0,
            enabled=False,
            provider="",
            tags=[],
        )

        super().__init__(
            parent=parent,
            uuid=uuid,
            db_resource=db_resource,
            params_to_serialize=["availableModeCost", "inputSettings"],
            params=params,
        )
