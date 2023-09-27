from __future__ import annotations

import fnmatch
import re
import dateutil.parser
from typing import Optional, List, Union, Type, Callable
import graphene
from dataclasses import field
from functools import partial


class AccountExposedList(graphene.ObjectType):
    total = graphene.Int()
    nextToken = graphene.String()
    items = graphene.List(lambda: AccountExposed)


class ReportExposedList(graphene.ObjectType):
    total = graphene.Int()
    nextToken = graphene.String()
    items = graphene.List(lambda: ReportExposed)


class FileExposedList(graphene.ObjectType):
    total = graphene.Int()
    nextToken = graphene.String()
    items = graphene.List(lambda: FileExposed)


class ActivityExposedList(graphene.ObjectType):
    total = graphene.Int()
    nextToken = graphene.String()
    items = graphene.List(lambda: ActivityExposed)


class DataSetExposedList(graphene.ObjectType):
    total = graphene.Int()
    nextToken = graphene.String()
    items = graphene.List(lambda: DataSetExposed)


class RolePermissionExposedList(graphene.ObjectType):
    items = graphene.List(lambda: RolePermissionExposed)


class AppDashboardExposedList(graphene.ObjectType):
    items = graphene.List(lambda: AppDashboardExposed)


class AppTypeExposed(graphene.ObjectType):
    id = graphene.String()
    key = graphene.String()
    name = graphene.String()
    appTypeUniverseId = graphene.String()
    normalizedName = graphene.String()


class AppExposed(graphene.ObjectType):
    id = graphene.String()
    name = graphene.String()
    trialDays = graphene.Int()
    isDisabled = graphene.Boolean()
    appBusinessId = graphene.String()
    createdAt = graphene.String()
    churnedDate = graphene.String()
    reports = graphene.Field(lambda: ReportExposedList)
    hideTitle = graphene.Boolean()
    paymentType = graphene.String()
    order = graphene.Int()
    normalizedName = graphene.String()
    files = graphene.Field(lambda: FileExposedList)
    hidePath = graphene.Boolean()
    showBreadcrumb = graphene.Boolean()
    showHistoryNavigation = graphene.Boolean()
    activities = graphene.Field(lambda: ActivityExposedList)
    dataSets = graphene.Field(lambda: DataSetExposedList)
    rolePermissions = graphene.Field(lambda: RolePermissionExposedList)
    appDashboards = graphene.Field(lambda: AppDashboardExposedList)
    universeId = graphene.String()
    type = graphene.Field(lambda: AppTypeExposed)


class DashboardExposedList(graphene.ObjectType):
    total = graphene.Int()
    nextToken = graphene.String()
    items = graphene.List(lambda: DashboardExposed)


class BusinessExposed(graphene.ObjectType):
    id = graphene.String()
    name = graphene.String()
    type = graphene.String()
    createdAt = graphene.String()
    etlMachineLastProcessed = graphene.String()
    integrationId = graphene.String()
    defaultAppPaymentType = graphene.String()
    defaultstr = graphene.String()
    theme = graphene.String()
    roles = graphene.List(lambda: RolePermissionExposed)
    rolePermissions = graphene.Field(lambda: RolePermissionExposedList)
    businessUniverseId = graphene.String()
    dashboards = graphene.Field(lambda: DashboardExposedList)
    apps = graphene.Field(lambda: AppExposedList)
    modules = graphene.Field(lambda: ModuleExposedList)
    universe = graphene.Field(lambda: UniverseFilteredExposed)


class ModuleExposed(graphene.ObjectType):
    enabled = graphene.Boolean()
    id = graphene.String()
    type = graphene.String()


class ModuleExposedList(graphene.ObjectType):
    items = graphene.List(lambda: ModuleExposed)


class AccountExposed(graphene.ObjectType):
    id = graphene.String()
    createdAt = graphene.String()
    startupAppId = graphene.String()
    userType = graphene.String()
    notificationsLastRead = graphene.String()
    startupApp = graphene.Field(lambda: AppExposed)
    business = graphene.Field(BusinessExposed)
    shopifyToken = graphene.String()
    roles = graphene.List(graphene.String)


class ReportDataSetExposedList(graphene.ObjectType):
    items = graphene.List(lambda: ReportDataSetExposed)


class ReportExposed(graphene.ObjectType):
    id = graphene.String()
    appId = graphene.String()
    app = graphene.Field(lambda: AppExposed)
    createdAt = graphene.String()
    order = graphene.Int()
    grid = graphene.String()
    sizeRows = graphene.Int()
    sizeColumns = graphene.Int()
    sizePadding = graphene.String()
    isDisabled = graphene.Boolean()
    reportType = graphene.String()
    path = graphene.String()
    pathOrder = graphene.Int()
    dataFields = graphene.String()
    title = graphene.String()
    description = graphene.String()
    chartData = graphene.String()
    chartDataItem = graphene.String()
    chartDataAux = graphene.String()
    smartFilters = graphene.String()
    subscribe = graphene.Boolean()
    reportDataSets = graphene.Field(lambda: ReportDataSetExposedList)
    properties = graphene.String()
    bentobox = graphene.String()
    hidePath = graphene.Boolean()
    showBreadcrumb = graphene.Boolean()
    showHistoryNavigation = graphene.Boolean()
    universeId = graphene.String()

    @staticmethod
    def list_resolver_extra(
            publicPermissions: DashboardPublicPermissionInputExposed = None,
            **kwargs
    ):
        items = kwargs.get('items')
        return items


class DataExposedList(graphene.ObjectType):
    total = graphene.Int()
    nextToken = graphene.String()
    items = graphene.List(lambda: DataExposed)


class DataSetExposed(graphene.ObjectType):
    id = graphene.String()
    data = graphene.Field(lambda: DataExposedList)
    reportDataSetId = graphene.String()
    reportDataSets = graphene.Field(lambda: ReportDataSetExposedList)
    dataSetAppId = graphene.String()
    app = graphene.Field(lambda: AppExposed)
    universeId = graphene.String()
    name = graphene.String()
    columns = graphene.String()


class ReportDataSetExposed(graphene.ObjectType):
    id = graphene.String()
    dataSetId = graphene.String()
    dataSet = graphene.Field(lambda: DataSetExposed)
    reportId = graphene.String()
    report = graphene.Field(lambda: ReportExposed)
    properties = graphene.String()


class DashboardPublicPermissionInputExposed(graphene.InputObjectType):
    resourceId = graphene.String()
    token = graphene.String()


class SearchableDataSortableFields(graphene.Enum):
    id = "id"
    createdAt = "createdAt"
    dataSetId = "dataSetId"
    description = "description"
    stringField1 = "stringField1"
    stringField2 = "stringField2"
    stringField3 = "stringField3"
    stringField4 = "stringField4"
    stringField5 = "stringField5"
    stringField6 = "stringField6"
    stringField7 = "stringField7"
    stringField8 = "stringField8"
    stringField9 = "stringField9"
    stringField10 = "stringField10"
    stringField11 = "stringField11"
    stringField12 = "stringField12"
    stringField13 = "stringField13"
    stringField14 = "stringField14"
    stringField15 = "stringField15"
    stringField16 = "stringField16"
    stringField17 = "stringField17"
    stringField18 = "stringField18"
    stringField19 = "stringField19"
    stringField20 = "stringField20"
    stringField21 = "stringField21"
    stringField22 = "stringField22"
    stringField23 = "stringField23"
    stringField24 = "stringField24"
    stringField25 = "stringField25"
    stringField26 = "stringField26"
    stringField27 = "stringField27"
    stringField28 = "stringField28"
    stringField29 = "stringField29"
    stringField30 = "stringField30"
    stringField31 = "stringField31"
    stringField32 = "stringField32"
    stringField33 = "stringField33"
    stringField34 = "stringField34"
    stringField35 = "stringField35"
    stringField36 = "stringField36"
    stringField37 = "stringField37"
    stringField38 = "stringField38"
    stringField39 = "stringField39"
    stringField40 = "stringField40"
    stringField41 = "stringField41"
    stringField42 = "stringField42"
    stringField43 = "stringField43"
    stringField44 = "stringField44"
    stringField45 = "stringField45"
    stringField46 = "stringField46"
    stringField47 = "stringField47"
    stringField48 = "stringField48"
    stringField49 = "stringField49"
    stringField50 = "stringField50"
    intField1 = "intField1"
    intField2 = "intField2"
    intField3 = "intField3"
    intField4 = "intField4"
    intField5 = "intField5"
    intField6 = "intField6"
    intField7 = "intField7"
    intField8 = "intField8"
    intField9 = "intField9"
    intField10 = "intField10"
    intField11 = "intField11"
    intField12 = "intField12"
    intField13 = "intField13"
    intField14 = "intField14"
    intField15 = "intField15"
    intField16 = "intField16"
    intField17 = "intField17"
    intField18 = "intField18"
    intField19 = "intField19"
    intField20 = "intField20"
    intField21 = "intField21"
    intField22 = "intField22"
    intField23 = "intField23"
    intField24 = "intField24"
    intField25 = "intField25"
    intField26 = "intField26"
    intField27 = "intField27"
    intField28 = "intField28"
    intField29 = "intField29"
    intField30 = "intField30"
    intField31 = "intField31"
    intField32 = "intField32"
    intField33 = "intField33"
    intField34 = "intField34"
    intField35 = "intField35"
    intField36 = "intField36"
    intField37 = "intField37"
    intField38 = "intField38"
    intField39 = "intField39"
    intField40 = "intField40"
    intField41 = "intField41"
    intField42 = "intField42"
    intField43 = "intField43"
    intField44 = "intField44"
    intField45 = "intField45"
    intField46 = "intField46"
    intField47 = "intField47"
    intField48 = "intField48"
    intField49 = "intField49"
    intField50 = "intField50"
    dateField1 = "dateField1"
    dateField2 = "dateField2"
    dateField3 = "dateField3"
    dateField4 = "dateField4"
    dateField5 = "dateField5"
    dateField6 = "dateField6"
    dateField7 = "dateField7"
    dateField8 = "dateField8"
    customField1 = "customField1"
    orderField1 = "orderField1"


class SearchableSortDirection(graphene.Enum):
    asc = "asc"
    desc = "desc"


class SearchableDataSortInput(graphene.InputObjectType):
    field = graphene.Field(lambda: SearchableDataSortableFields)
    direction = graphene.Field(lambda: SearchableSortDirection)


class SearchableIDFilterInput(graphene.InputObjectType):
    ne = graphene.String()
    gt = graphene.String()
    lt = graphene.String()
    gte = graphene.String()
    lte = graphene.String()
    eq = graphene.String()
    match = graphene.String()
    matchPhrase = graphene.String()
    matchPhrasePrefix = graphene.String()
    multiMatch = graphene.String()
    exists = graphene.Boolean()
    wildcard = graphene.String()
    regexp = graphene.String()
    range = graphene.List(graphene.String)


class StringOrStringList(graphene.Scalar):
    """
    Custom Scalar to handle both String and List of Strings
    """

    @staticmethod
    def serialize(value):
        return value

    @staticmethod
    def parse_value(value):
        if not isinstance(value, list):
            return [value]  # Convert single string to a list
        return value

    @staticmethod
    def parse_literal(ast):
        # Handle parsing GraphQL literals
        if isinstance(ast, graphene.StringValue):
            return [ast.value]
        elif isinstance(ast, graphene.ListValue):
            return [elem.value for elem in ast.values if isinstance(elem, graphene.StringValue)]


class SearchableStringFilterInput(graphene.InputObjectType):
    ne = graphene.Field(StringOrStringList)
    gt = graphene.Field(StringOrStringList)
    lt = graphene.Field(StringOrStringList)
    gte = graphene.Field(StringOrStringList)
    lte = graphene.Field(StringOrStringList)
    eq = graphene.Field(StringOrStringList)
    match = graphene.Field(StringOrStringList)
    matchPhrase = graphene.Field(StringOrStringList)
    matchPhrasePrefix = graphene.Field(StringOrStringList)
    multiMatch = graphene.Field(StringOrStringList)
    exists = graphene.Boolean()
    wildcard = graphene.Field(StringOrStringList)
    regexp = graphene.Field(StringOrStringList)
    range = graphene.Field(StringOrStringList)


class FloatOrString(graphene.Scalar):
    """
    Custom Scalar type to handle both Float and String types
    """

    @staticmethod
    def serialize(value):
        return value

    @staticmethod
    def parse_value(value):
        try:
            return float(value)
        except ValueError:
            return str(value)

    @staticmethod
    def parse_literal(ast):
        if isinstance(ast, (graphene.FloatValue, graphene.StringValue)):
            return ast.value


class SearchableFloatFilterInput(graphene.InputObjectType):
    # Front end sends strings
    ne = graphene.Field(FloatOrString)
    gt = graphene.Field(FloatOrString)
    lt = graphene.Field(FloatOrString)
    gte = graphene.Field(FloatOrString)
    lte = graphene.Field(FloatOrString)
    eq = graphene.Field(FloatOrString)
    range = graphene.List(FloatOrString)


class SearchableStringFilterInputOrList(graphene.InputObjectType):
    items = graphene.List(SearchableStringFilterInput)

    @staticmethod
    def parse_value(value):
        if not isinstance(value, list):
            return [value]
        return value


class SearchableDataFilterInput(graphene.InputObjectType):
    id = graphene.Field(lambda: SearchableIDFilterInput)
    createdAt = graphene.Field(lambda: SearchableStringFilterInput)
    dataSetId = graphene.Field(lambda: SearchableIDFilterInput)
    description = graphene.Field(lambda: SearchableStringFilterInput)
    stringField1 = graphene.Field(lambda: SearchableStringFilterInput)
    stringField2 = graphene.Field(lambda: SearchableStringFilterInput)
    stringField3 = graphene.Field(lambda: SearchableStringFilterInput)
    stringField4 = graphene.Field(lambda: SearchableStringFilterInput)
    stringField5 = graphene.Field(lambda: SearchableStringFilterInput)
    stringField6 = graphene.Field(lambda: SearchableStringFilterInput)
    stringField7 = graphene.Field(lambda: SearchableStringFilterInput)
    stringField8 = graphene.Field(lambda: SearchableStringFilterInput)
    stringField9 = graphene.Field(lambda: SearchableStringFilterInput)
    stringField10 = graphene.Field(lambda: SearchableStringFilterInput)
    stringField11 = graphene.Field(lambda: SearchableStringFilterInput)
    stringField12 = graphene.Field(lambda: SearchableStringFilterInput)
    stringField13 = graphene.Field(lambda: SearchableStringFilterInput)
    stringField14 = graphene.Field(lambda: SearchableStringFilterInput)
    stringField15 = graphene.Field(lambda: SearchableStringFilterInput)
    stringField16 = graphene.Field(lambda: SearchableStringFilterInput)
    stringField17 = graphene.Field(lambda: SearchableStringFilterInput)
    stringField18 = graphene.Field(lambda: SearchableStringFilterInput)
    stringField19 = graphene.Field(lambda: SearchableStringFilterInput)
    stringField20 = graphene.Field(lambda: SearchableStringFilterInput)
    stringField21 = graphene.Field(lambda: SearchableStringFilterInput)
    stringField22 = graphene.Field(lambda: SearchableStringFilterInput)
    stringField23 = graphene.Field(lambda: SearchableStringFilterInput)
    stringField24 = graphene.Field(lambda: SearchableStringFilterInput)
    stringField25 = graphene.Field(lambda: SearchableStringFilterInput)
    stringField26 = graphene.Field(lambda: SearchableStringFilterInput)
    stringField27 = graphene.Field(lambda: SearchableStringFilterInput)
    stringField28 = graphene.Field(lambda: SearchableStringFilterInput)
    stringField29 = graphene.Field(lambda: SearchableStringFilterInput)
    stringField30 = graphene.Field(lambda: SearchableStringFilterInput)
    stringField31 = graphene.Field(lambda: SearchableStringFilterInput)
    stringField32 = graphene.Field(lambda: SearchableStringFilterInput)
    stringField33 = graphene.Field(lambda: SearchableStringFilterInput)
    stringField34 = graphene.Field(lambda: SearchableStringFilterInput)
    stringField35 = graphene.Field(lambda: SearchableStringFilterInput)
    stringField36 = graphene.Field(lambda: SearchableStringFilterInput)
    stringField37 = graphene.Field(lambda: SearchableStringFilterInput)
    stringField38 = graphene.Field(lambda: SearchableStringFilterInput)
    stringField39 = graphene.Field(lambda: SearchableStringFilterInput)
    stringField40 = graphene.Field(lambda: SearchableStringFilterInput)
    stringField41 = graphene.Field(lambda: SearchableStringFilterInput)
    stringField42 = graphene.Field(lambda: SearchableStringFilterInput)
    stringField43 = graphene.Field(lambda: SearchableStringFilterInput)
    stringField44 = graphene.Field(lambda: SearchableStringFilterInput)
    stringField45 = graphene.Field(lambda: SearchableStringFilterInput)
    stringField46 = graphene.Field(lambda: SearchableStringFilterInput)
    stringField47 = graphene.Field(lambda: SearchableStringFilterInput)
    stringField48 = graphene.Field(lambda: SearchableStringFilterInput)
    stringField49 = graphene.Field(lambda: SearchableStringFilterInput)
    stringField50 = graphene.Field(lambda: SearchableStringFilterInput)
    intField1 = graphene.Field(lambda: SearchableFloatFilterInput)
    intField2 = graphene.Field(lambda: SearchableFloatFilterInput)
    intField3 = graphene.Field(lambda: SearchableFloatFilterInput)
    intField4 = graphene.Field(lambda: SearchableFloatFilterInput)
    intField5 = graphene.Field(lambda: SearchableFloatFilterInput)
    intField6 = graphene.Field(lambda: SearchableFloatFilterInput)
    intField7 = graphene.Field(lambda: SearchableFloatFilterInput)
    intField8 = graphene.Field(lambda: SearchableFloatFilterInput)
    intField9 = graphene.Field(lambda: SearchableFloatFilterInput)
    intField10 = graphene.Field(lambda: SearchableFloatFilterInput)
    intField11 = graphene.Field(lambda: SearchableFloatFilterInput)
    intField12 = graphene.Field(lambda: SearchableFloatFilterInput)
    intField13 = graphene.Field(lambda: SearchableFloatFilterInput)
    intField14 = graphene.Field(lambda: SearchableFloatFilterInput)
    intField15 = graphene.Field(lambda: SearchableFloatFilterInput)
    intField16 = graphene.Field(lambda: SearchableFloatFilterInput)
    intField17 = graphene.Field(lambda: SearchableFloatFilterInput)
    intField18 = graphene.Field(lambda: SearchableFloatFilterInput)
    intField19 = graphene.Field(lambda: SearchableFloatFilterInput)
    intField20 = graphene.Field(lambda: SearchableFloatFilterInput)
    intField21 = graphene.Field(lambda: SearchableFloatFilterInput)
    intField22 = graphene.Field(lambda: SearchableFloatFilterInput)
    intField23 = graphene.Field(lambda: SearchableFloatFilterInput)
    intField24 = graphene.Field(lambda: SearchableFloatFilterInput)
    intField25 = graphene.Field(lambda: SearchableFloatFilterInput)
    intField26 = graphene.Field(lambda: SearchableFloatFilterInput)
    intField27 = graphene.Field(lambda: SearchableFloatFilterInput)
    intField28 = graphene.Field(lambda: SearchableFloatFilterInput)
    intField29 = graphene.Field(lambda: SearchableFloatFilterInput)
    intField30 = graphene.Field(lambda: SearchableFloatFilterInput)
    intField31 = graphene.Field(lambda: SearchableFloatFilterInput)
    intField32 = graphene.Field(lambda: SearchableFloatFilterInput)
    intField33 = graphene.Field(lambda: SearchableFloatFilterInput)
    intField34 = graphene.Field(lambda: SearchableFloatFilterInput)
    intField35 = graphene.Field(lambda: SearchableFloatFilterInput)
    intField36 = graphene.Field(lambda: SearchableFloatFilterInput)
    intField37 = graphene.Field(lambda: SearchableFloatFilterInput)
    intField38 = graphene.Field(lambda: SearchableFloatFilterInput)
    intField39 = graphene.Field(lambda: SearchableFloatFilterInput)
    intField40 = graphene.Field(lambda: SearchableFloatFilterInput)
    intField41 = graphene.Field(lambda: SearchableFloatFilterInput)
    intField42 = graphene.Field(lambda: SearchableFloatFilterInput)
    intField43 = graphene.Field(lambda: SearchableFloatFilterInput)
    intField44 = graphene.Field(lambda: SearchableFloatFilterInput)
    intField45 = graphene.Field(lambda: SearchableFloatFilterInput)
    intField46 = graphene.Field(lambda: SearchableFloatFilterInput)
    intField47 = graphene.Field(lambda: SearchableFloatFilterInput)
    intField48 = graphene.Field(lambda: SearchableFloatFilterInput)
    intField49 = graphene.Field(lambda: SearchableFloatFilterInput)
    intField50 = graphene.Field(lambda: SearchableFloatFilterInput)
    dateField1 = graphene.Field(lambda: SearchableStringFilterInput)
    dateField2 = graphene.Field(lambda: SearchableStringFilterInput)
    dateField3 = graphene.Field(lambda: SearchableStringFilterInput)
    dateField4 = graphene.Field(lambda: SearchableStringFilterInput)
    dateField5 = graphene.Field(lambda: SearchableStringFilterInput)
    dateField6 = graphene.Field(lambda: SearchableStringFilterInput)
    dateField7 = graphene.Field(lambda: SearchableStringFilterInput)
    dateField8 = graphene.Field(lambda: SearchableStringFilterInput)
    customField1 = graphene.Field(lambda: SearchableStringFilterInput)
    orderField1 = graphene.Field(lambda: SearchableFloatFilterInput)

    @classmethod
    def add_fields(cls) -> Type[SearchableDataFilterInput]:
        """ This is necessary because of the way the filter is defined in the API, these keywords are reserved
        in python so we have to add them programmatically.
        """
        add_fields = [
            ('and', graphene.List(SearchableDataFilterInput)),
            ('or', graphene.List(SearchableDataFilterInput)),
            ('not', graphene.Field(SearchableDataFilterInput))
        ]
        for field_name, field_type in add_fields:
            setattr(cls, field_name, field_type)
            if isinstance(field_type, graphene.List):
                cls._meta.fields[field_name] = graphene.InputField(field_type)
            else:
                cls._meta.fields[field_name] = field_type

        return cls


class DataExposed(graphene.ObjectType):
    id = graphene.String()
    createdAt = graphene.String()
    dataSetId = graphene.String()
    dataSet = graphene.Field(lambda: DataSetExposed)
    description = graphene.String()
    stringField1 = graphene.String()
    stringField2 = graphene.String()
    stringField3 = graphene.String()
    stringField4 = graphene.String()
    stringField5 = graphene.String()
    stringField6 = graphene.String()
    stringField7 = graphene.String()
    stringField8 = graphene.String()
    stringField9 = graphene.String()
    stringField10 = graphene.String()
    stringField11 = graphene.String()
    stringField12 = graphene.String()
    stringField13 = graphene.String()
    stringField14 = graphene.String()
    stringField15 = graphene.String()
    stringField16 = graphene.String()
    stringField17 = graphene.String()
    stringField18 = graphene.String()
    stringField19 = graphene.String()
    stringField20 = graphene.String()
    stringField21 = graphene.String()
    stringField22 = graphene.String()
    stringField23 = graphene.String()
    stringField24 = graphene.String()
    stringField25 = graphene.String()
    stringField26 = graphene.String()
    stringField27 = graphene.String()
    stringField28 = graphene.String()
    stringField29 = graphene.String()
    stringField30 = graphene.String()
    stringField31 = graphene.String()
    stringField32 = graphene.String()
    stringField33 = graphene.String()
    stringField34 = graphene.String()
    stringField35 = graphene.String()
    stringField36 = graphene.String()
    stringField37 = graphene.String()
    stringField38 = graphene.String()
    stringField39 = graphene.String()
    stringField40 = graphene.String()
    stringField41 = graphene.String()
    stringField42 = graphene.String()
    stringField43 = graphene.String()
    stringField44 = graphene.String()
    stringField45 = graphene.String()
    stringField46 = graphene.String()
    stringField47 = graphene.String()
    stringField48 = graphene.String()
    stringField49 = graphene.String()
    stringField50 = graphene.String()
    intField1 = graphene.Float()
    intField2 = graphene.Float()
    intField3 = graphene.Float()
    intField4 = graphene.Float()
    intField5 = graphene.Float()
    intField6 = graphene.Float()
    intField7 = graphene.Float()
    intField8 = graphene.Float()
    intField9 = graphene.Float()
    intField10 = graphene.Float()
    intField11 = graphene.Float()
    intField12 = graphene.Float()
    intField13 = graphene.Float()
    intField14 = graphene.Float()
    intField15 = graphene.Float()
    intField16 = graphene.Float()
    intField17 = graphene.Float()
    intField18 = graphene.Float()
    intField19 = graphene.Float()
    intField20 = graphene.Float()
    intField21 = graphene.Float()
    intField22 = graphene.Float()
    intField23 = graphene.Float()
    intField24 = graphene.Float()
    intField25 = graphene.Float()
    intField26 = graphene.Float()
    intField27 = graphene.Float()
    intField28 = graphene.Float()
    intField29 = graphene.Float()
    intField30 = graphene.Float()
    intField31 = graphene.Float()
    intField32 = graphene.Float()
    intField33 = graphene.Float()
    intField34 = graphene.Float()
    intField35 = graphene.Float()
    intField36 = graphene.Float()
    intField37 = graphene.Float()
    intField38 = graphene.Float()
    intField39 = graphene.Float()
    intField40 = graphene.Float()
    intField41 = graphene.Float()
    intField42 = graphene.Float()
    intField43 = graphene.Float()
    intField44 = graphene.Float()
    intField45 = graphene.Float()
    intField46 = graphene.Float()
    intField47 = graphene.Float()
    intField48 = graphene.Float()
    intField49 = graphene.Float()
    intField50 = graphene.Float()
    dateField1 = graphene.String()
    dateField2 = graphene.String()
    dateField3 = graphene.String()
    dateField4 = graphene.String()
    dateField5 = graphene.String()
    dateField6 = graphene.String()
    dateField7 = graphene.String()
    dateField8 = graphene.String()
    customField1 = graphene.String()
    orderField1 = graphene.Float()
    universeId = graphene.String()

    @staticmethod
    def filter_func_template(field_value, filter_value, type_converter, comparator):
        if isinstance(filter_value, list):
            return any([comparator(type_converter(field_value), type_converter(value)) for value in filter_value])
        else:
            return comparator(type_converter(field_value), type_converter(filter_value))

    @staticmethod
    def filter_field(
            items: list, field: str,
            filterFieldInput: Union[SearchableIDFilterInput, SearchableStringFilterInput, SearchableFloatFilterInput]
    ) -> list:
        type_converter: Callable = lambda x: x
        if 'dateField' in field:
            # Set the values lower than an hour to 0
            type_converter: Callable = lambda x: dateutil.parser.parse(x).replace(
                minute=0, second=0, microsecond=0, tzinfo=dateutil.tz.tzutc()
            )
        elif 'intField' in field or 'orderField' in field:
            type_converter: Callable = lambda x: float(x)

        filters: List[Callable] = []
        func = DataExposed.filter_func_template
        if filterFieldInput.ne is not None:
            filters.append(partial(func, filter_value=filterFieldInput.ne,
                                   type_converter=type_converter, comparator=lambda x, y: x != y))
        if filterFieldInput.gt is not None:
            filters.append(partial(func, filter_value=filterFieldInput.gt,
                                   type_converter=type_converter, comparator=lambda x, y: x > y))
        if filterFieldInput.lt is not None:
            filters.append(partial(func, filter_value=filterFieldInput.lt,
                                   type_converter=type_converter, comparator=lambda x, y: x < y))
        if filterFieldInput.gte is not None:
            filters.append(partial(func, filter_value=filterFieldInput.gte,
                                   type_converter=type_converter, comparator=lambda x, y: x >= y))
        if filterFieldInput.lte is not None:
            filters.append(partial(func, filter_value=filterFieldInput.lte,
                                   type_converter=type_converter, comparator=lambda x, y: x <= y))
        if filterFieldInput.eq is not None:
            filters.append(partial(func, filter_value=filterFieldInput.eq,
                                   type_converter=type_converter, comparator=lambda x, y: x == y))
        if isinstance(filterFieldInput, (SearchableIDFilterInput, SearchableStringFilterInput)):
            if filterFieldInput.match is not None:
                filters.append(partial(func, filter_value=filterFieldInput.match,
                                       type_converter=type_converter, comparator=lambda x, y: x == y))
            if filterFieldInput.matchPhrase is not None:
                filters.append(partial(func, filter_value=filterFieldInput.matchPhrase,
                                       type_converter=type_converter, comparator=lambda x, y: x in y))
            if filterFieldInput.matchPhrasePrefix is not None:
                filters.append(partial(func, filter_value=filterFieldInput.matchPhrasePrefix,
                                       type_converter=type_converter, comparator=lambda x, y: x.startswith(y)))
            if filterFieldInput.multiMatch is not None:
                filters.append(partial(func, filter_value=filterFieldInput.multiMatch,
                                       type_converter=type_converter, comparator=lambda x, y: x in y))
            if filterFieldInput.exists:
                filters.append(lambda x: x is not None)
            if filterFieldInput.wildcard:
                filters.append(partial(func, filter_value=filterFieldInput.wildcard,
                                       type_converter=type_converter, comparator=lambda x, y: fnmatch.fnmatch(x, y)))
            if filterFieldInput.regexp:
                filters.append(partial(func, filter_value=filterFieldInput.regexp,
                                       type_converter=type_converter, comparator=lambda x, y: re.match(y, x)))
        return [item for item in items if all([filter_func(getattr(item, field)) for filter_func in filters])]

    @staticmethod
    def filter(input_items, filterInput: SearchableDataFilterInput) -> list:
        not_results = []
        or_results = []
        results = [item for item in input_items]
        filtered = False
        for key, value in filterInput.__dict__.items():
            if value is not None:
                if key == 'and':
                    if len(value) == 0:
                        results = []
                    for _filter in value:
                        results = DataExposed.filter(results, _filter)
                    filtered = True
                elif key == 'or':
                    for _filter in value:
                        or_results.extend(DataExposed.filter(input_items, _filter))
                elif key == 'not':
                    not_results.append(DataExposed.filter(results, value))
                    filtered = True
                else:
                    results = DataExposed.filter_field(results, key, value)
                    filtered = True

        if not filtered:
            results = []
        elif not_results:
            results = [item for item in results if item not in not_results[0]]

        for or_result in or_results:
            if or_result not in results:
                results.append(or_result)

        return results

    @staticmethod
    def list_resolver_extra(
            publicPermissions: DashboardPublicPermissionInputExposed = None,
            sort: SearchableDataSortInput = None,
            filter: SearchableDataFilterInput = None,
            **kwargs
    ):
        items = kwargs.get('items')
        if sort is not None and sort.field is not None and sort.direction is not None:
            sort_direction = sort.direction.value
            sort_field = sort.field.value
            items = sorted(items, key=lambda x: getattr(x, sort_field), reverse=sort_direction == 'desc')
        if filter is not None:
            items = DataExposed.filter(items, filter)
        return items


class FileExposed(graphene.ObjectType):
    id = graphene.String()
    appId = graphene.String()
    app = graphene.Field(AppExposed)
    fileName = graphene.String()
    name = graphene.String()
    createdAt = graphene.String()
    updatedAt = graphene.String()
    universeId = graphene.String()
    contentType = graphene.String()


class RunExposedList(graphene.ObjectType):
    items = graphene.List(lambda: RunExposed)


class ActivityExposed(graphene.ObjectType):
    id = graphene.String()
    createdAt = graphene.String()
    appId = graphene.String()
    app = graphene.Field(lambda: AppExposed)
    runs = graphene.Field(lambda: RunExposedList)
    name = graphene.String()
    settings = graphene.String()
    universeId = graphene.String()
    activityWebHook = graphene.Field(lambda: ActivityWebHookExposed)


class LogExposedList(graphene.ObjectType):
    items = graphene.List(lambda: LogExposed)


class RunExposed(graphene.ObjectType):
    id = graphene.String()
    createdAt = graphene.String()
    activityId = graphene.String()
    activity = graphene.Field(lambda: ActivityExposed)
    settings = graphene.String()
    logs = graphene.Field(lambda: LogExposedList)
    isWebhookCalled = graphene.Boolean()


class LogExposed(graphene.ObjectType):
    id = graphene.String()
    message = graphene.String()
    runId = graphene.String()
    run = graphene.Field(lambda: RunExposed)
    dateTime = graphene.String()
    tags = graphene.String()
    severity = graphene.String()


class RolePermissionExposed(graphene.ObjectType):
    role = graphene.String()
    permission = graphene.String()
    resource = graphene.String()
    target = graphene.String()


class PublicPermission(graphene.ObjectType):
    isPublic = graphene.Boolean()
    permission = graphene.String()
    token = graphene.String()


class DashboardExposed(graphene.ObjectType):
    id = graphene.String()
    createdAt = graphene.String()
    appDashboards = graphene.Field(AppDashboardExposedList)
    businessId = graphene.String()
    rolePermissions = graphene.Field(lambda: RolePermissionExposedList)
    publicPermission = graphene.Field(lambda: PublicPermission)
    name = graphene.String()
    order = graphene.Int()
    isDisabled = graphene.Boolean()


class AppDashboardExposed(graphene.ObjectType):
    id = graphene.String()
    createdAt = graphene.String()
    dashboard = graphene.Field(DashboardExposed)
    app = graphene.Field(AppExposed)
    appId = graphene.String()


class UniverseModuleExposed(graphene.ObjectType):
    id = graphene.String()
    type = graphene.String()
    enabled = graphene.Boolean()


class BusinessAppTypeExposed(graphene.ObjectType):
    id = graphene.String()
    businessId = graphene.String()
    appTypeId = graphene.String()
    business = graphene.Field(lambda: BusinessExposed)


class BusinessExposedList(graphene.ObjectType):
    total = graphene.Int()
    nextToken = graphene.String()
    items = graphene.List(lambda: BusinessExposed)


class UniverseExposed(graphene.ObjectType):
    id = graphene.String()
    name = graphene.String()
    business = graphene.Field(lambda: BusinessExposedList)
    theme = graphene.String()
    activeUniversePlanId = graphene.String()
    activeUniversePlan = graphene.Field(lambda: ActiveUniversePlan)
    modules = graphene.Field(lambda: ModuleExposedList)


class UniverseFilteredExposed(graphene.ObjectType):
    id = graphene.String()
    name = graphene.String()
    business = graphene.Field(lambda: BusinessExposedList)
    theme = graphene.String()
    activeUniversePlanId = graphene.String()
    activeUniversePlan = graphene.Field(lambda: ActiveUniversePlan)
    modules = graphene.Field(lambda: ModuleExposedList)


class ActiveUniversePlan(graphene.ObjectType):
    id = graphene.String()
    planType = graphene.Field(lambda: PlanType)


class PlanType(graphene.ObjectType):
    id = graphene.String()
    limits = graphene.String()
    price = graphene.Int()
    type = graphene.String()


class AppExposedList(graphene.ObjectType):
    total = graphene.Int()
    nextToken = graphene.String()
    items = graphene.List(lambda: AppExposed)


class ActivityWebHookExposed(graphene.ObjectType):
    id = graphene.String()
    url = graphene.String()
    method = graphene.String()
    headers = graphene.String()
    activityId = graphene.String()
    createdAt = graphene.String()
    updatedAt = graphene.String()
    activity = graphene.Field(lambda: ActivityExposed)
