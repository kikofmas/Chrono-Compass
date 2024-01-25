import customtkinter as ctk
import tkinter as tk
import math
import time

# App Layout
APP_HEIGHT = 800
APP_WIDTH = 800
APP_GEOMETRY = str(APP_WIDTH) + "x" + str(APP_HEIGHT)
CLOCK_HEIGHT = 700
CLOCK_WIDTH = 700


class ClockApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.canvas_height = CLOCK_HEIGHT
        self.canvas_width = CLOCK_WIDTH

        self.title("24-Hour Clock")
        self.geometry(APP_GEOMETRY)

        self.canvas = tk.Canvas(
            self, width=self.canvas_width, height=self.canvas_height, bg=self["bg"], highlightthickness=0)
        self.canvas.pack(pady=20, padx=20)

        # Draw the time indicator line (static)
        self.draw_time_indicator()

        # Initial draw of the clock face
        self.draw_clock_face(0)

        # Update clock every second
        self.update_clock()

    @staticmethod
    def point_on_circle(cx, cy, radius, angle):
        rad = math.radians(angle)
        x = cx + radius * math.cos(rad)
        y = cy + radius * math.sin(rad)
        return x, y

    def update_clock(self):
        # Get current time
        now = time.localtime()
        hours = now.tm_hour + now.tm_min / 60

        # Calculate angle for rotation
        angle = (hours / 24) * 360

        # Rotate the clock face
        self.draw_clock_face(0)

        # Update every second
        self.after(1000, self.update_clock)

    def draw_time_indicator(self):
        self.canvas.create_line(
            self.canvas_width/2, 20, self.canvas_width/2, self.canvas_width/2, fill="red", width=2)

    def draw_clock_face(self, rotation):
        self.canvas.delete("clock_face")  # Clear existing clock face

        center_x, center_y = self.canvas_width/2, self.canvas_height/2
        radius = self.canvas_width/2 - 20

        # Draw clock circle
        self.canvas.create_oval(center_x - radius, center_y - radius,
                                center_x + radius, center_y + radius,
                                outline="white", width=4, tags="clock_face")

        # Draw hour numbers and minute lines
        for hour in range(24):
            angle = (hour / 24) * 360 - rotation - 90
            print(str(hour) + ": " + str(angle))
            x, y = self.point_on_circle(center_x, center_y, radius + 10, angle)
            self.canvas.create_text(x, y, text=str(
                hour), font=("Arial", 8), tags="clock_face", fill="white")

            # Draw minute lines
            for minute in range(1, 12):
                min_angle = angle + (minute / 12) * (360 / 24)
                inner_x, inner_y = self.point_on_circle(
                    center_x, center_y, radius - 10, min_angle)
                outer_x, outer_y = self.point_on_circle(
                    center_x, center_y, radius, min_angle)
                self.canvas.create_line(
                    inner_x, inner_y, outer_x, outer_y, width=1, tags="clock_face", fill="white")

            min_angle = angle + (360 / 24)
            inner_x, inner_y = self.point_on_circle(
                center_x, center_y, radius - 20, min_angle)
            outer_x, outer_y = self.point_on_circle(
                center_x, center_y, radius, min_angle)
            self.canvas.create_line(
                inner_x, inner_y, outer_x, outer_y, width=1, tags="clock_face", fill="green")

        self.draw_time_slice(1, 0, 13, 0, rotation)

    def draw_time_slice(self, hour1, min1, hour2, min2, rotation):
        # Convert time to angle
        start_angle = (hour1 / 24) * 360 + (min1/60) * (360/24) - rotation - 90 - 15 + 180
        end_angle = (hour2 / 24) * 360 + (min2/60) * (360/24) - rotation - 90 - 15 + 180
        print("Start: " + str(start_angle))
        print("End: " + str(end_angle))

        extent_angle = end_angle - start_angle

        center_x, center_y = self.canvas_width/2, self.canvas_height/2
        radius = self.canvas_height/2 - 20
        box_coords = [center_x + radius, center_y +
                      radius, center_x - radius, center_y - radius]

        # Draw the slice
        self.canvas.create_arc(box_coords, start=start_angle,
                               extent=extent_angle, fill="blue", tags="clock_face")


if __name__ == "__main__":
    ctk.set_appearance_mode("System")
    ctk.set_default_color_theme("blue")
    app = ClockApp()
    app.mainloop()
