from PIL import Image, ImageDraw, ImageFont
import matplotlib.pyplot as plt
import numpy as np
import datetime


DAY_MAPPING = {
    0: "Po",
    1: "Út",
    2: "St",
    3: "Čt",
    4: "Pá",
    5: "So",
    6: "Ne"
}


class CalendarPage():
    def __init__(
            self, 
            h: int = 480, 
            w: int = 800,
            header_h: int = 64,
            num_hours: int = 10,
            day_start_hour: int = 8,
            num_days: int = 5,
            time_axis_w: int = 80,
            left_buffer: int = 8,
            right_buffer: int = 128
        ):
        
        self.h = h
        self.w = w
        self.header_h = header_h
        self.num_hours = num_hours
        self.day_start_hour = day_start_hour
        self.num_days = num_days
        self.time_axis_w = time_axis_w
        self.left_buffer = left_buffer
        self.right_buffer = right_buffer
        
        self.day_w = (self.w - self.time_axis_w - self.right_buffer) // self.num_days
        
        # compute vertical pixels per minute
        self.time_h = (self.h - self.header_h) // self.num_hours
        day_start = datetime.time(self.day_start_hour, 0, 0)
        day_end = datetime.time(self.day_start_hour + self.num_hours, 0, 0)
        total_day_minutes = datetime.timedelta(
            hours=day_end.hour - day_start.hour,
            minutes=day_end.minute - day_start.minute
        ).total_seconds() / 60
        self.px_per_min = (self.num_hours * self.time_h) / total_day_minutes 
        
        # init PIL canvas
        self.canvas = Image.new("1", (w, h), color=1)
        self.draw = ImageDraw.Draw(self.canvas)
        
        self.render_header()
        self.render_time_axis()
        self.render_cursor()

    def render_header(self):
        font = ImageFont.truetype("resources/verdana.ttf", 16)
        self.draw.text(
                (self.time_axis_w + 20, 8), 
                f"Dnes", 
                fill=0, 
                font=font
            )
        today = datetime.datetime.now().strftime('%d. %m.')
        font = ImageFont.truetype("resources/verdana.ttf", 10)
        self.draw.text(
                (self.time_axis_w + 26, 30), 
                f"{today}", 
                fill=0, 
                font=font
            )
        for i in range(1, self.num_days):
            date = datetime.datetime.now() + datetime.timedelta(days=i)
            font = ImageFont.truetype("resources/verdana.ttf", 16)
            self.draw.text(
                    (self.time_axis_w + i * self.day_w + 32, 8), 
                    f"{DAY_MAPPING[date.weekday()]}", 
                    fill=0, 
                    font=font
                )
            day = date.strftime('%d. %m.')
            font = ImageFont.truetype("resources/verdana.ttf", 10)
            self.draw.text(
                    (self.time_axis_w + i * self.day_w + 26, 30), 
                    f"{day}", 
                    fill=0, 
                    font=font
                )

    def render_time_axis(self):
        font_size = 10
        font = ImageFont.truetype("resources/verdana.ttf", font_size)
        for i in range(self.num_hours):
            self.draw.text(
                (self.left_buffer, self.header_h + i * self.time_h), 
                f"{self.day_start_hour + i}:00", 
                fill=0, 
                font=font
            )
            self.draw.line(
                [(self.left_buffer, self.header_h + i * self.time_h + 1), (self.w-128, self.header_h + i * self.time_h + 1)], 
                fill=0
            )
            
    def render_cursor(self):
        day_start = datetime.time(self.day_start_hour, 0, 0)
        current_minutes_from_day_start = datetime.timedelta(
            hours=datetime.datetime.now().hour - day_start.hour,
            minutes=datetime.datetime.now().minute - day_start.minute,
        ).total_seconds() / 60 
        rx0 = self.time_axis_w - 30
        rx1 = self.time_axis_w - 5
        
        ry0 = self.header_h + self.px_per_min * current_minutes_from_day_start - 7
        ry1 = self.header_h + self.px_per_min * current_minutes_from_day_start + 7
        self.draw.pieslice(
            [(rx0, ry0+1), (rx1, ry1-1)],
            start=150,
            end=210,
            fill=0
        )

    def render_event(self, event, day: int):
        if event.start is None or event.end is None:
            return
        
        day_start = datetime.time(self.day_start_hour, 0, 0)
        
        event_start_minutes_from_day_start = datetime.timedelta(
            hours=event.start.hour - day_start.hour,
            minutes=event.start.minute - day_start.minute,
        ).total_seconds() / 60
        
        event_end_minutes_from_day_start = datetime.timedelta(
            hours=event.end.hour - day_start.hour,
            minutes=event.end.minute - day_start.minute
        ).total_seconds() / 60
        
        rx0 = self.time_axis_w + day * self.day_w
        rx1 = self.time_axis_w + (day + 1) * self.day_w
        
        ry0 = self.header_h + self.px_per_min * event_start_minutes_from_day_start
        ry1 = self.header_h + self.px_per_min * event_end_minutes_from_day_start
        self.draw.rectangle(
            [(rx0+1, ry0+1), (rx1-1, ry1-1)],
            fill=0
        )
        font_size = 9
        font = ImageFont.truetype("resources/verdana.ttf", font_size)
        self.draw.text(
            (rx0+2, ry0+1),
            event.name[:18],
            fill=1,
            font=font
        )
        
    def render_busy_status(self, busy_status: bool):
        status_str = "NEMOŽE" if busy_status else "MOŽE"
        x_offset = 0 if busy_status else 20
        font_size = 16
        font = ImageFont.truetype("resources/verdana.ttf", font_size)
        self.draw.text(
            (self.w - self.right_buffer + 32, self.h // 2 - 20),
            "Táta teď",
            fill=0,
            font=font
        )
        font_size = 24
        font = ImageFont.truetype("resources/verdana.ttf", font_size)
        self.draw.text(
            (self.w - self.right_buffer + 12 + x_offset, self.h // 2),
            status_str,
            fill=0,
            font=font
        )

    def show(self):
        plt.imshow(self.canvas)
        plt.show()


    def get_image(self):
        return self.canvas

if  __name__ == "__main__":
    page = CalendarPage(480, 800)
    page.show()
    