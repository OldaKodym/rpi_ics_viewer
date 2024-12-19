import requests
import datetime
from collections import namedtuple

import icalendar
import recurring_ical_events


Event = namedtuple("Event", "name date start end")


class ICSParser():
    def __init__(self, url: str):
        
        self.url = url
        self.calendar = None
        self.events = []
        self.update_calendar()
        
    def update_calendar(self):
        ics = requests.get(self.url, allow_redirects=True)
        self.calendar = icalendar.Calendar.from_ical(ics.content)
        
        start_date = (2000, 1, 1)
        end_date =   (2100,  1, 1)

        events = [e for e in self.calendar.walk('VEVENT')]
        events += [e for e in recurring_ical_events.of(self.calendar).between(start_date, end_date) if e not in events]

        self.events = []
        for event in events:
            start_date = event.get("DTSTART").dt
            name = event.get("SUMMARY")
            
            if "canceled" in name.lower() or "zrušeno" in name.lower():
                continue
            
            if "date" in dir(event.get("DTSTART").dt):  # event is not all-day
                date = event.get("DTSTART").dt.date()
                start_time = event.get("DTSTART").dt.time()
                end_time = event.get("DTEND").dt.time()
            else:
                date = event.get("DTSTART").dt
                start_time = None
                end_time = None

            self.events.append(Event(name, date, start_time, end_time))
            
    def get_todays_events(self):
        return [e for e in self.events if e.date == datetime.date.today()]
    
    def get_days_events(self, date: datetime.date):
        return [e for e in self.events if e.date == date]
    
    def get_busy_status(self) -> bool:
        for e in self.events:
            now = datetime.datetime.now()
            if e.start is None or e.end is None:
                continue
            if e.date == now.date() and e.start < now.time() < e.end:
                return True
        return False
