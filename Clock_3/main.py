import sys
from PyQt6.QtWidgets import QApplication, QWidget, QHBoxLayout, QVBoxLayout, QMainWindow
from PyQt6.QtGui import QPainter, QPen, QColor, QFont, QFontDatabase
from PyQt6.QtCore import Qt, QTimer, QTime
import csv
from datetime import datetime, timedelta


CATEGORY_COLORS = {
    "Work": "#FFD700",  # Gold
    "Leisure": "#1E90FF",  # DodgerBlue
    "Exercise": "#32CD32",  # LimeGreen
    "Sleep": "#8A2BE2",  # BlueViolet
    "Other": "#FFA07A"  # LightSalmon
}

events = []  # To store event data

def load_events_from_csv():
    global events
    events.clear()  # Clear existing events
    now = datetime.datetime.now()

    # Only consider current day if after 6:00
    if now.hour < 6:
        adjusted_date = now - datetime.timedelta(days=1)
    else:
        adjusted_date = now

    day_of_week = adjusted_date.weekday()
    days = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
    day_name = days[day_of_week]

    filename = f"{day_name}_schedule.csv"
    with open(filename, 'r') as file:
        reader = csv.reader(file)
        next(reader)  # Skip header row
        for row in reader:
            # Assuming the CSV format is: name,start_time,end_time,category
            event = {
                "name": row[0],
                "start_time": datetime.strptime(row[1], "%H:%M").time(),
                "end_time": datetime.strptime(row[2], "%H:%M").time(),
                "category": row[3]
            }
            events.append(event)


class DarkModeRotating24hClock(QWidget):
    def __init__(self):
        super().__init__()
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update)
        self.timer.start(1000)  # Update every second
        self.setMinimumSize(720, 720)  # Set a minimum size for visibility

    def drawDot(self, painter, x, y, size=5):
        """Draw a single dot."""
        painter.drawEllipse(x, y, size, size)

    def drawNumber(self, painter, num, topLeftX, topLeftY):
        """Draw a number using dots. This is a simplified example."""
        # Mapping of number to dot positions for a 3x5 grid. This needs to be fully defined.
        numberMap = {
            '0': [(0,0), (0,1), (0,2), (0,3), (0,4), (1,0), (1,4), (2,0), (2,1), (2,2), (2,3), (2,4)],
            '1': [(1,1), (2,0), (2,1), (2,2), (2,3), (2,4)],
            '2': [(0,0), (1,0), (2,0), (2,1), (1,2), (0,3), (0,4), (1,4), (2,4)],
            '3': [(0,0), (1,0), (2,0), (2,1), (1,2), (2,3), (0,4), (1,4), (2,4), (2,2)],
            '4': [(0,0), (0,1), (0,2), (1,2), (2,0), (2,1), (2,2), (2,3), (2,4)],
            '5': [(0,0), (1,0), (2,0), (0,1), (0,2), (1,2), (2,2), (2,3), (0,4), (1,4), (2,4)],
            '6': [(0,0), (0,1), (0,2), (0,3), (0,4), (1,0), (1,2), (1,4), (2,0), (2,2), (2,3), (2,4)],
            '7': [(0,0), (1,0), (1,2), (2,0), (2,1), (2,2), (2,3), (2,4)],
            '8': [(0,0), (0,1), (0,2), (0,3), (0,4), (1,0), (1,2), (1,4), (2,1), (2,2), (2,3), (2,0), (2,4)],
            '9': [(0,0), (0,1), (0,2), (0,4), (1,0), (1,2), (1,4), (2,0), (2,1), (2,2), (2,3), (2,4)]
        }

        for digit, positions in numberMap.items():
            if num == int(digit):
                for pos in positions:
                    self.drawDot(painter, topLeftX + pos[0]*3, topLeftY + pos[1]*3, 2)  # Adjusted for size and spacing


    def paintEvent(self, event):
        rect = min(self.width(), self.height())

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Center and scale the painter
        painter.translate(self.width() / 2, self.height() / 2)
        painter.scale(rect / 250, rect / 250)  # Adjust scale based on new geometry

        # Get current time
        currentTime = QTime.currentTime()
        hour = currentTime.hour()
        minute = currentTime.minute()
        totalSeconds = currentTime.hour() * 3600 + currentTime.minute() * 60 + currentTime.second()

        # Calculate angle, considering 24h format (86400 seconds in a day)
        angle = 360.0 * totalSeconds / 86400

        # Rotate the clock face
        painter.rotate(-angle)

        # Set font for numbers with size 4
        font = QFont("Arial", 4)
        painter.setFont(font)

        # Draw events
        day_start = time(6, 0)  # Day starts at 6:00 AM
        for event in events:
            start_delta = datetime.combine(datetime.today(), event["start_time"]) - datetime.combine(datetime.today(), day_start)
            end_delta = datetime.combine(datetime.today(), event["end_time"]) - datetime.combine(datetime.today(), day_start)
            start_angle = (start_delta.total_seconds() / 86400) * 360
            span_angle = ((end_delta.total_seconds() - start_delta.total_seconds()) / 86400) * 360

            # Check if event is in the past
            now = datetime.now().time()
            color = CATEGORY_COLORS.get(event["category"], "#FF0000")  # Default to red if category not found
            if event["end_time"] < now:
                color = QColor(color).darker(150).name()  # Grey out past events

            painter.setBrush(QColor(color))
            painter.drawPie(-100, -100, 200, 200, int(start_angle * 16), int(span_angle * 16))


        # Draw 24-hour clock face
        for i in range(24):
           # Hour lines in blue
           painter.setPen(QPen(QColor("#007bff"), 0.5, Qt.PenStyle.SolidLine))
           painter.drawLine(0, -98, 0, -88)
           # Draw hour labels in blue aligned with the hour lines
           painter.setPen(QColor("#007bff"))  # Set text color to blue

           # Calculate text alignment offset
           text = str(i)
           hour_srt_rect = painter.fontMetrics().boundingRect(text)
           # Align text horizontally with hour lines and position it outside
           painter.drawText(round(-hour_srt_rect.width() / 2), round( -98 + hour_srt_rect.height() - 10), text)  # Adjusted for alignment

           painter.rotate(15.0)  # 360 degrees / 24 segments

        # Draw minute ticks for every 5 minutes in black
        painter.setPen(QPen(Qt.GlobalColor.black, 0.25, Qt.PenStyle.SolidLine))
        for i in range(24 * 12):  # 12 five-minute segments per hour
            if i % 12 != 0:  # Skip hours, already drawn
                painter.drawLine(0, -98, 0, -92)
            painter.rotate(1.25)  # 360 degrees / (24 hours * 12 segments)

        # Reset rotation for drawing the fixed time indicator
        painter.resetTransform()
        painter.translate(self.width() / 2, self.height() / 2)
        painter.scale(rect / 250, rect / 250)

        # Draw current time indicator (static red line)
        painter.setPen(QPen(Qt.GlobalColor.red, 0.5, Qt.PenStyle.SolidLine))
        painter.drawLine(0, -5, 0, -98)  # Static line indicating current time

        # Display the digital clock at the center
        # Calculate starting positions
        baseX = -25  # Adjust as necessary for positioning
        baseY = 0   # This positions the digital clock in the center

        # Draw hour digits
        self.drawNumber(painter, hour // 10, baseX, baseY)
        self.drawNumber(painter, hour % 10, baseX + 12, baseY)  # Shift for next digit

        # Draw colon (smaller dots)
        self.drawDot(painter, baseX + 25, baseY+3, 1)  # Top dot of the colon
        self.drawDot(painter, baseX + 25, baseY+10, 1)  # Bottom dot of the colon

        # Draw minute digits
        self.drawNumber(painter, minute // 10, baseX + 29, baseY)
        self.drawNumber(painter, minute % 10, baseX + 42, baseY)  # Shift for next digit


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Left-Aligned 24-Hour Rotating Analog Clock - Dark Mode")
        self.setGeometry(330, 150, 1280, 720)  # Adjust size as needed

        self.initUI()

    def initUI(self):
        self.setStyleSheet("background-color: #333;")  # Dark background
        self.setAutoFillBackground(True)
        self.centralWidget = QWidget(self)  # Create a central widget
        self.setCentralWidget(self.centralWidget)

        self.layout = QHBoxLayout()  # Use a QHBoxLayout for horizontal alignment

        # Initialize the DarkModeRotating24hClock widget
        self.clock = DarkModeRotating24hClock()

        # Add the clock to the layout with left alignment
        self.layout.addWidget(self.clock, alignment=Qt.AlignmentFlag.AlignLeft)

        # Set the layout to the central widget
        self.centralWidget.setLayout(self.layout)


# Include the DarkModeRotating24hClock class definition here

def main():
    app = QApplication(sys.argv)
    mainWindow = MainWindow()
    mainWindow.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
