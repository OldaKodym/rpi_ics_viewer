import datetime
import time
# import epaper

from ics_parser import ICSParser
from renderer import CalendarPage

if __name__ == "__main__":
    with open("./ics_url.txt", "r") as handle:
        url = handle.read()
    
    cal_parser = ICSParser(url)    

    # epd = epaper.epaper('epd7in5').EPD()
    # epd.init()
    # epd.Clear()
    
    while True:
        cal_parser.update_calendar()
        page = CalendarPage(num_days=7)
        
        for i in range(page.num_days):    
            events = cal_parser.get_days_events(datetime.date.today() + datetime.timedelta(days=i))
            for event in events:
                page.render_event(event, day=i)
        
        page.render_busy_status(cal_parser.get_busy_status())
        
        # epd.display(epd.getbuffer(page.get_image()))
        page.show()
        
        time.sleep(15 * 60)  # sleep 5 minutes
