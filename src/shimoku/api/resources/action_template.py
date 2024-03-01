from typing import Optional, TYPE_CHECKING, TypedDict

from shimoku.api.base_resource import Resource

if TYPE_CHECKING:
    from shimoku.api.resources.universe import Universe

import logging
from shimoku.execution_logger import log_error

logger = logging.getLogger(__name__)


class ActionTemplate(Resource):
    _module_logger = logger
    resource_type = "actionTemplate"
    alias_field = "name"
    plural = "actionTemplates"

    class ActionTemplateParams(TypedDict):
        name: Optional[str]
        description: Optional[str]
        allowedUniverseIds: Optional[list[str]]
        public: bool

    def __init__(
        self,
        parent: "Universe",
        uuid: Optional[str] = None,
        alias: Optional[str] = None,
        db_resource: Optional[dict] = None,
    ):
        params = ActionTemplate.ActionTemplateParams(
            name=alias,
            description=None,
            allowedUniverseIds=None,
            public=False,
        )

        super().__init__(
            parent=parent,
            uuid=uuid,
            db_resource=db_resource,
            # children=,
            check_params_before_creation=["name"],
            params=params,
        )
