"""
Data structure for events and recurring events
Recurring events are represented as a series of events with a base event and frequency
"""

from datetime import datetime, timedelta
from typing import List, Optional


class Event:
    def __init__(
        self,
        title: str,
        start_date: datetime,
        end_date: datetime,
        description: str = "",
        attendees: Optional[List[str]] = None,
        color: Optional[str] = None,
        series_id: Optional[int] = None,
    ):
        self.event_id = id(self)
        self.title = title
        self.start_date = start_date
        self.end_date = end_date
        self.description = description
        self.attendees = attendees or []
        self.color = color
        self.series_id = series_id

    def __repr__(self):
        return (
            f"Event(title='{self.title}', start_date={self.start_date}, "
            f"end_date={self.end_date}, series_id={self.series_id})"
        )

    def __lt__(self, other):
        return self.start_date < other.start_date


class Series:
    def __init__(self, base_event: Event, frequency: timedelta):
        self.series_id = id(self)
        self.base_event = base_event
        self.frequency = frequency

    def generate_events(self, duration_days: int) -> List[Event]:
        """Generate events for the series."""
        events = []
        current_date = self.base_event.start_date

        while current_date <= self.base_event.start_date + timedelta(
            days=duration_days
        ):
            new_event = Event(
                title=self.base_event.title,
                start_date=current_date,
                end_date=current_date
                + (self.base_event.end_date - self.base_event.start_date),
                description=self.base_event.description,
                attendees=self.base_event.attendees,
                color=self.base_event.color,
                series_id=self.base_event.series_id,
            )
            events.append(new_event)

            current_date += self.frequency

        return events


class Calendar:
    def __init__(self, days_in_future: int):
        self.events: List[Event] = []
        self.days_in_future = days_in_future

    def add_event(self, event: Event):
        """Insert event into the list and maintain sorted order."""
        # Find the position to insert the new event
        index = 0
        while index < len(self.events) and self.events[index] < event:
            index += 1
        self.events.insert(index, event)

    def add_series(self, series: Series):
        """Add a series of events to the calendar."""
        for event in series.generate_events(duration_days=self.days_in_future):
            self.add_event(event)

    def __repr__(self):
        return f"Calendar(events={self.events})"


if __name__ == "__main__":
    calendar = Calendar(14)

    base_event = Event(
        title="Weekly Team Meeting",
        start_date=datetime(2024, 9, 5, 9, 0),
        end_date=datetime(2024, 9, 5, 10, 0),
        description="A weekly team sync meeting",
        attendees=["alice@example.com", "bob@example.com"],
    )

    series = Series(base_event=base_event, frequency=timedelta(weeks=1))

    additional_event = Event(
        title="One-Time Workshop",
        start_date=datetime(2024, 9, 7, 14, 0),
        end_date=datetime(2024, 9, 7, 16, 0),
        description="A one-time workshop on new tech",
        attendees=["carol@example.com"],
        color="blue",
    )

    calendar.add_event(additional_event)
    calendar.add_series(series)

    print(calendar)
