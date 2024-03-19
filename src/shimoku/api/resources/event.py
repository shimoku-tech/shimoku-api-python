from typing import Optional, Union, TYPE_CHECKING

from shimoku.api.base_resource import Resource

if TYPE_CHECKING:
    from shimoku.api.resources.business import Business
    from shimoku.api.resources.app import App
    from shimoku.api.resources.dashboard import Dashboard

import logging

logger = logging.getLogger(__name__)


class Event(Resource):
    """Event resource class"""

    _module_logger = logger
    resource_type = "event"
    plural = "events"

    def __init__(self,
        parent: "Business",
        uuid: Optional[str] = None,
    ):
        params = dict(
            type="NO_EVENT",
            resourceId=None,
            content={},
            authResourceType="BUSINESS_ADMIN",
            mainAuthResourceId=parent["id"],
        )

        super().__init__(
            parent=parent, uuid=uuid, params=params, params_to_serialize=["content"]
        )

    def set_auth_resource(self, auth_resource: Union["App", "Dashboard"]):
        self["authResourceType"] = auth_resource.resource_type.upper()
        self["mainAuthResourceId"] = auth_resource["id"]
