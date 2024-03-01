from typing import Dict, Optional, TYPE_CHECKING

import re
from shimoku.api.base_resource import Resource

if TYPE_CHECKING:
    from shimoku.api.resources.app import App

import logging

logger = logging.getLogger(__name__)


class File(Resource):
    """File resource class"""

    _module_logger = logger
    resource_type = "file"
    plural = "files"
    alias_field = "name"
    elastic_supported = True

    def __init__(
        self,
        parent: "App",
        uuid: Optional[str] = None,
        alias: Optional[str] = None,
        db_resource: Optional[Dict] = None,
    ):
        params = dict(
            name=alias,
            fileName=re.sub("[^0-9a-zA-Z]+", "-", alias).lower() if alias else None,
            url="",
            contentType="",
            tags=[],
            metadata={},
        )

        super().__init__(
            parent=parent,
            uuid=uuid,
            db_resource=db_resource,
            params=params,
            check_params_before_creation=["name"],
            params_to_serialize=["metadata"],
        )

    async def delete(self):
        """Delete the report"""
        return await self._base_resource.delete()
