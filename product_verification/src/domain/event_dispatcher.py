from abc import ABC, abstractmethod
from typing import List
from src.domain import DomainEvent


class EventDispatcher(ABC):
    @abstractmethod
    async def dispatch(self, event: DomainEvent) -> None:
        pass

    @abstractmethod
    async def dispatch_all(self, events: List[DomainEvent]) -> None:
        pass


class InMemoryEventDispatcher(EventDispatcher):
    def __init__(self):
        self._events: List[DomainEvent] = []

    async def dispatch(self, event: DomainEvent) -> None:
        self._events.append(event)
        print(f"[EVENT DISPATCHED] {event.__class__.__name__}: {event.__dict__}")

    async def dispatch_all(self, events: List[DomainEvent]) -> None:
        for event in events:
            await self.dispatch(event)

    def get_dispatched_events(self) -> List[DomainEvent]:
        return self._events.copy()

    def clear(self) -> None:
        self._events.clear()
