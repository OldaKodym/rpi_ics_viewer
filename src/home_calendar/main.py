import datetime
import time
import epaper

from ics_parser import ICSParser
from renderer import CalendarPage

if __name__ == "__main__":
    with open("./ics_url.txt", "r") as handle:
        url = handle.read()
    
    cal_parser = ICSParser(url)    

    epd = epaper.epaper('epd7in5_V2').EPD()
    print('init')
    epd.init()
    print('clearl')
    epd.Clear()
    
    while True:
        try:
            print('pulling cal...')
            cal_parser.update_calendar()
            print('rendering..')
            page = CalendarPage(num_days=7)
        
            for i in range(page.num_days):    
                events = cal_parser.get_days_events(datetime.date.today() + datetime.timedelta(days=i))
                for event in events:
                    page.render_event(event, day=i)
        
            page.render_busy_status(cal_parser.get_busy_status())
        
            print('displaying')
            epd.init_fast()
            epd.display(epd.getbuffer(page.get_image()))
        # page.show()
        
            print('done, sleeping for 10 min')
            epd.sleep()
        
        except Exception as e:
            print("failed refreshing due to exception:")
            print(e)

        time.sleep(10 * 60)  # sleep 10 minutes
