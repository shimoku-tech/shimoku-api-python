from typing import Union, List
from pydantic import BaseModel
import strawberry


@strawberry.type
class UpdateBusinessInput(BaseModel):
    id: Union[str, None] = None
    name: Union[str, None] = None
    type: Union[str, None] = None
    createdAt: Union[str, None] = None
    etlMachineLastProcessed: Union[str, None] = None
    integrationId: Union[str, None] = None
    defaultstr: Union[str, None] = None
    businessUniverseId: Union[str, None] = None
    theme: Union[str, None] = None


@strawberry.type
class CreateAppInput(BaseModel):
    name: str
    normalizedName: str
    id: Union[str, None] = None
    createdAt: Union[str, None] = None
    order: Union[int, None] = None
    hidePath: Union[bool, None] = None
    showBreadcrumb: Union[bool, None] = None
    showHistoryNavigation: Union[bool, None] = None
    hideTitle: Union[bool, None] = None
    isDisabled: Union[bool, None] = None
    appBusinessId: Union[str, None] = None
    universeId: Union[str, None] = None


@strawberry.type
class UpdateAppInput(BaseModel):
    id: Union[str, None] = None
    name: Union[str, None] = None
    normalizedName: Union[str, None] = None
    createdAt: Union[str, None] = None
    order: Union[int, None] = None
    hidePath: Union[bool, None] = None
    showBreadcrumb: Union[bool, None] = None
    showHistoryNavigation: Union[bool, None] = None
    hideTitle: Union[bool, None] = None
    isDisabled: Union[bool, None] = None
    appBusinessId: Union[str, None] = None
    universeId: Union[str, None] = None
    paymentType: Union[str, None] = None
    trialDays: Union[int, None] = None
    appSubscriptionInUseId: Union[str, None] = None
    accountId: Union[str, None] = None
    integrationId: Union[str, None] = None
    churnedDate: Union[str, None] = None
    appTypeId: Union[str, None] = None


@strawberry.type
class DeleteAppInput(BaseModel):
    id: Union[str, None] = None


@strawberry.type
class PublicPermissionInput(BaseModel):
    isPublic: bool
    permission: str
    token: str


@strawberry.type
class CreateDashboardInput(BaseModel):
    name: str
    id: Union[str, None] = None
    createdAt: Union[str, None] = None
    businessId: Union[str, None] = None
    publicPermission: Union[PublicPermissionInput, None] = None
    order: Union[int, None] = None
    isDisabled: Union[bool, None] = None


@strawberry.type
class UpdateDashboardInput(BaseModel):
    id: Union[str, None] = None
    createdAt: Union[str, None] = None
    businessId: Union[str, None] = None
    publicPermission: Union[PublicPermissionInput, None] = None
    name: Union[str, None] = None
    order: Union[int, None] = None
    isDisabled: Union[bool, None] = None
    universeId: Union[str, None] = None


@strawberry.type
class DeleteDashboardInput(BaseModel):
    id: Union[str, None] = None


@strawberry.type
class CreateAppDashboardInput(BaseModel):
    id: Union[str, None] = None
    createdAt: Union[str, None] = None
    dashboardId: Union[str, None] = None
    appId: Union[str, None] = None


@strawberry.type
class UpdateAppDashboardInput(BaseModel):
    id: Union[str, None] = None
    createdAt: Union[str, None] = None
    dashboardId: Union[str, None] = None
    appId: Union[str, None] = None


@strawberry.type
class DeleteAppDashboardInput(BaseModel):
    id: Union[str, None] = None


@strawberry.type
class CreateActivityWebHookInput(BaseModel):
    url: str
    method: str
    id: Union[str, None] = None
    headers: Union[str, None] = None
    activityId: Union[str, None] = None


@strawberry.type
class UpdateActivityWebHookInput(BaseModel):
    id: Union[str, None] = None
    url: Union[str, None] = None
    method: Union[str, None] = None
    headers: Union[str, None] = None
    activityId: Union[str, None] = None


@strawberry.type
class DeleteActivityWebHookInput(BaseModel):
    id: Union[str, None] = None


@strawberry.type
class CreateActivityInput(BaseModel):
    name: str
    id: Union[str, None] = None
    createdAt: Union[str, None] = None
    appId: Union[str, None] = None
    settings: Union[str, None] = None
    universeId: Union[str, None] = None


@strawberry.type
class UpdateActivityInput(BaseModel):
    id: Union[str, None] = None
    createdAt: Union[str, None] = None
    appId: Union[str, None] = None
    name: Union[str, None] = None
    settings: Union[str, None] = None
    activityWebHookId: Union[str, None] = None
    universeId: Union[str, None] = None


@strawberry.type
class DeleteActivityInput(BaseModel):
    id: Union[str, None] = None


@strawberry.type
class CreateRunInput(BaseModel):
    id: Union[str, None] = None
    createdAt: Union[str, None] = None
    activityId: Union[str, None] = None
    settings: Union[str, None] = None
    isWebhookCalled: Union[bool, None] = None


@strawberry.type
class UpdateRunInput(BaseModel):
    id: Union[str, None] = None
    createdAt: Union[str, None] = None
    activityId: Union[str, None] = None
    settings: Union[str, None] = None
    isWebhookCalled: Union[bool, None] = None


@strawberry.type
class DeleteRunInput(BaseModel):
    id: Union[str, None] = None


@strawberry.type
class CreateLogInput(BaseModel):
    id: Union[str, None] = None
    message: Union[str, None] = None
    runId: Union[str, None] = None
    dateTime: Union[str, None] = None
    tags: Union[str, None] = None
    severity: Union[str, None] = None


@strawberry.type
class UpdateLogInput(BaseModel):
    id: Union[str, None] = None
    message: Union[str, None] = None
    runId: Union[str, None] = None
    dateTime: Union[str, None] = None
    tags: Union[str, None] = None
    severity: Union[str, None] = None


@strawberry.type
class DeleteLogInput(BaseModel):
    id: Union[str, None] = None


@strawberry.type
class CreateReportInput(BaseModel):
    order: int
    id: Union[str, None] = None
    appId: Union[str, None] = None
    createdAt: Union[str, None] = None
    grid: Union[str, None] = None
    sizeRows: Union[int, None] = None
    sizeColumns: Union[int, None] = None
    sizePadding: Union[str, None] = None
    isDisabled: Union[bool, None] = None
    reportType: Union[str, None] = None
    path: Union[str, None] = None
    pathOrder: Union[int, None] = None
    dataFields: Union[str, None] = None
    title: Union[str, None] = None
    description: Union[str, None] = None
    chartData: Union[str, None] = None
    chartDataItem: Union[str, None] = None
    chartDataAux: Union[str, None] = None
    smartFilters: Union[str, None] = None
    subscribe: Union[bool, None] = None
    properties: Union[str, None] = None
    bentobox: Union[str, None] = None
    hidePath: Union[bool, None] = None
    showBreadcrumb: Union[bool, None] = None
    showHistoryNavigation: Union[bool, None] = None
    universeId: Union[str, None] = None

@strawberry.type
class UpdateReportInput(BaseModel):
    id: Union[str, None] = None
    appId: Union[str, None] = None
    createdAt: Union[str, None] = None
    order: Union[int, None] = None
    grid: Union[str, None] = None
    sizeRows: Union[int, None] = None
    sizeColumns: Union[int, None] = None
    sizePadding: Union[str, None] = None
    isDisabled: Union[bool, None] = None
    reportType: Union[str, None] = None
    path: Union[str, None] = None
    pathOrder: Union[int, None] = None
    dataFields: Union[str, None] = None
    title: Union[str, None] = None
    description: Union[str, None] = None
    chartData: Union[str, None] = None
    chartDataItem: Union[str, None] = None
    chartDataAux: Union[str, None] = None
    smartFilters: Union[str, None] = None
    subscribe: Union[bool, None] = None
    properties: Union[str, None] = None
    bentobox: Union[str, None] = None
    hidePath: Union[bool, None] = None
    showBreadcrumb: Union[bool, None] = None
    showHistoryNavigation: Union[bool, None] = None
    universeId: Union[str, None] = None


@strawberry.type
class DeleteReportInput(BaseModel):
    id: Union[str, None] = None


@strawberry.type
class CreateReportDataSetInput(BaseModel):
    id: Union[str, None] = None
    dataSetId: Union[str, None] = None
    reportId: Union[str, None] = None
    properties: Union[str, None] = None

@strawberry.type
class UpdateReportDataSetInput(BaseModel):
    id: Union[str, None] = None
    dataSetId: Union[str, None] = None
    reportId: Union[str, None] = None
    properties: Union[str, None] = None


@strawberry.type
class DeleteReportDataSetInput(BaseModel):
    id: Union[str, None] = None


@strawberry.type
class CreateDataSetInput(BaseModel):
    id: Union[str, None] = None
    name: Union[str, None] = None
    dataSetAppId: Union[str, None] = None
    universeId: Union[str, None] = None
    columns: Union[str, None] = None


@strawberry.type
class UpdateDataSetInput(BaseModel):
    id: Union[str, None] = None
    name: Union[str, None] = None
    columns: Union[str, None] = None
    dataSetAppId: Union[str, None] = None
    universeId: Union[str, None] = None


@strawberry.type
class DeleteDataSetInput(BaseModel):
    id: Union[str, None] = None


@strawberry.type
class CreateDataInput(BaseModel):
    id: Union[str, None] = None
    createdAt: Union[str, None] = None
    dataSetId: Union[str, None] = None
    description: Union[str, None] = None
    stringField1: Union[str, None] = None
    stringField2: Union[str, None] = None
    stringField3: Union[str, None] = None
    stringField4: Union[str, None] = None
    stringField5: Union[str, None] = None
    stringField6: Union[str, None] = None
    stringField7: Union[str, None] = None
    stringField8: Union[str, None] = None
    orderField1: Union[float, None] = None
    intField1: Union[float, None] = None
    intField2: Union[float, None] = None
    intField3: Union[float, None] = None
    intField4: Union[float, None] = None
    intField5: Union[float, None] = None
    intField6: Union[float, None] = None
    intField7: Union[float, None] = None
    intField8: Union[float, None] = None
    dateField1: Union[str, None] = None
    dateField2: Union[str, None] = None
    dateField3: Union[str, None] = None
    dateField4: Union[str, None] = None
    dateField5: Union[str, None] = None
    customField1: Union[str, None] = None
    universeId: Union[str, None] = None


@strawberry.type
class BatchCreateDataInput(BaseModel):
    data: List[CreateDataInput]


@strawberry.type
class UpdateDataInput(BaseModel):
    id: Union[str, None] = None
    createdAt: Union[str, None] = None
    dataSetId: Union[str, None] = None
    description: Union[str, None] = None
    stringField1: Union[str, None] = None
    stringField2: Union[str, None] = None
    stringField3: Union[str, None] = None
    stringField4: Union[str, None] = None
    stringField5: Union[str, None] = None
    stringField6: Union[str, None] = None
    stringField7: Union[str, None] = None
    stringField8: Union[str, None] = None
    orderField1: Union[float, None] = None
    intField1: Union[float, None] = None
    intField2: Union[float, None] = None
    intField3: Union[float, None] = None
    intField4: Union[float, None] = None
    intField5: Union[float, None] = None
    intField6: Union[float, None] = None
    intField7: Union[float, None] = None
    intField8: Union[float, None] = None
    dateField1: Union[str, None] = None
    dateField2: Union[str, None] = None
    dateField3: Union[str, None] = None
    dateField4: Union[str, None] = None
    dateField5: Union[str, None] = None
    customField1: Union[str, None] = None
    universeId: Union[str, None] = None


@strawberry.type
class DeleteDataInput(BaseModel):
    id: Union[str, None] = None


@strawberry.type
class CreateReportEntryInput(BaseModel):
    id: Union[str, None] = None
    createdAt: Union[str, None] = None
    reportId: Union[str, None] = None
    description: Union[str, None] = None
    stringField1: Union[str, None] = None
    stringField2: Union[str, None] = None
    stringField3: Union[str, None] = None
    stringField4: Union[str, None] = None
    intField1: Union[float, None] = None
    intField2: Union[float, None] = None
    intField3: Union[float, None] = None
    intField4: Union[float, None] = None
    data: Union[str, None] = None
    universeId: Union[str, None] = None


@strawberry.type
class UpdateReportEntryInput(BaseModel):
    id: Union[str, None] = None
    createdAt: Union[str, None] = None
    reportId: Union[str, None] = None
    description: Union[str, None] = None
    stringField1: Union[str, None] = None
    stringField2: Union[str, None] = None
    stringField3: Union[str, None] = None
    stringField4: Union[str, None] = None
    intField1: Union[float, None] = None
    intField2: Union[float, None] = None
    intField3: Union[float, None] = None
    intField4: Union[float, None] = None
    data: Union[str, None] = None
    universeId: Union[str, None] = None


@strawberry.type
class DeleteReportEntryInput(BaseModel):
    id: Union[str, None] = None


@strawberry.type
class CreateFileInput(BaseModel):
    id: Union[str, None] = None
    appId: Union[str, None] = None
    fileName: Union[str, None] = None
    name: Union[str, None] = None
    universeId: Union[str, None] = None
    contentType: Union[str, None] = None


@strawberry.type
class UpdateFileInput(BaseModel):
    id: Union[str, None] = None
    appId: Union[str, None] = None
    fileName: Union[str, None] = None
    name: Union[str, None] = None
    universeId: Union[str, None] = None
    contentType: Union[str, None] = None


@strawberry.type
class DeleteFileInput(BaseModel):
    id: Union[str, None] = None
    