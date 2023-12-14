import asyncio
import graphene
import queue
import uuid
from pydantic import BaseModel
import warnings
warnings.filterwarnings("ignore", module="pydantic")
import strawberry
warnings.filterwarnings("default", module="pydantic")
from fastapi import FastAPI


class EventType(graphene.Enum):
    NO_EVENT = "NO_EVENT"
    EVENT = "EVENT"
    REPORT_UPDATED = "REPORT_UPDATED"
    REPORT_CREATED = "REPORT_CREATED"
    REPORT_DELETED = "REPORT_DELETED"
    APP_UPDATED = "APP_UPDATED"
    APP_CREATED = "APP_CREATED"
    APP_DELETED = "APP_DELETED"
    DASHBOARD_UPDATED = "DASHBOARD_UPDATED"
    DASHBOARD_CREATED = "DASHBOARD_CREATED"
    DASHBOARD_DELETED = "DASHBOARD_DELETED"
    BUSINESS_CONTENTS_UPDATED = "BUSINESS_CONTENTS_UPDATED"


class Event(graphene.ObjectType):
    id = graphene.String()
    type = graphene.Field(EventType)
    resourceId = graphene.String()
    content = graphene.String()
    universeId = graphene.String()


events_queue: queue.Queue = queue.Queue()
new_event_available: asyncio.Event = asyncio.Event()


class Subscription(graphene.ObjectType):
    onEventCreated = graphene.Field(Event)

    async def subscribe_onEventCreated(root, info):
        global new_event_available
        new_event_available = asyncio.Event()
        while True:
            await new_event_available.wait()  # Wait until a new event is signaled
            while not events_queue.empty():  # Process all events in the queue
                yield events_queue.get()
            new_event_available.clear()  # Reset the event


@strawberry.type
class CreateEventInput(BaseModel):
    type: str
    resourceId: str
    content: str


def define_event_method(fast_api_app: FastAPI):
    @fast_api_app.post("/external/v1/universe/{parent1Id}/business/{parent0Id}/event")
    async def create(parent1Id: str, parent0Id: str, params: CreateEventInput):
        event = Event(
            id=str(uuid.uuid4()),
            type=params.type,
            resourceId=params.resourceId,
            content=params.content,
            universeId=parent1Id
        )
        events_queue.put(event)
        new_event_available.set()  # Signal that a new event is available
        return event

