import sys
from PyQt6.QtWidgets import (
    QApplication,
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QMainWindow,
    QPushButton,
    QCheckBox,
    QToolTip,
)
from PyQt6.QtGui import QPainter, QPen, QColor, QFont, QPainterPath, QIcon
from PyQt6.QtCore import Qt, QTimer, QTime, QPointF, QUrl, QRect
from PyQt6.QtMultimedia import QSoundEffect
import csv
from datetime import datetime, timedelta
import numpy as np

APP_STYLE = "Fusion"

# Workarounds: icon on taskbar, dark mode title bar, app style
if sys.platform == "linux" or sys.platform == "linux2":
    a = 1  # Placeholder
elif sys.platform == "darwin":
    a = 1  # Placeholder
elif sys.platform == "win32":
    # Icon in taskbar
    import ctypes

    myappid = "kikofmas.chrono_compass.v0_1_0"
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

    # Dark mode title bar
    sys.argv += ["-platform", "windows:darkmode=2"]

    # App Style
    APP_STYLE = "Windows"


# Global "day start" time
day_start = 6

# Material Design Dark Mode Color Palette
# Used as the app's color palette
MATERIAL_COLORS = {
    "primary": "#BB86FC",
    "secondary": "#03DAC6",
    "background": "#121212",
    "background_variant": "#333",
    "surface": "#121212",
    "error": "#CF6679",
    "on_primary": "#000000",
    "on_secondary": "#000000",
    "on_background": "#FFFFFF",
    "on_surface": "#FFFFFF",
    "on_error": "#000000",
    "primary_variant": "#3700B3",
    "secondary_variant": "#018786",
    "error_variant": "#B00020",
}

PIKACHU_COLORS = {
    "primary": "#F6C90E",
    "secondary": "#b13b06",
    "background": "#303841",
    "background_variant": "#2B2B2B",
    "surface": "#121212",
    "error": "#83142C",
    "on_primary": "#000000",
    "on_secondary": "#219C90",
    "on_background": "#CCCCCC",
    "on_surface": "#CCCCCC",
    "on_error": "#000000",
    "primary_variant": "#219C90",
    "secondary_variant": "#D83F31",
    "error_variant": "#B00020",
}

# Current Palette
APP_PALETTE = PIKACHU_COLORS

CATEGORY_COLORS = {
    "Work": "#BB86FC",
    "Meeting": "#11009E",
    "Exercise": "#03DAC6",
    "Food": "#f60e3b",
    "Duties": "#6527BE",
    "Other": "#77ACF1",
    "Sleep": "#000000",
}

# Global variable with event data. Can be accessed by any widget.
# Reads data from the relevant .csv once at app start-up
events = []

current_event_color = APP_PALETTE["error"]


def load_events_from_csv():
    global events
    events.clear()
    now = datetime.now()

    # Only consider current day if after 6:00
    if now.hour < day_start:
        adjusted_date = now - timedelta(days=1)
    else:
        adjusted_date = now

    day_of_week = adjusted_date.weekday()
    days = [
        "monday",
        "tuesday",
        "wednesday",
        "thursday",
        "friday",
        "saturday",
        "sunday",
    ]
    day_name = days[day_of_week]

    filepath = f"week_schedules/{day_of_week}_{day_name}_schedule.csv"

    with open(filepath, "r") as file:
        reader = csv.reader(file)
        next(reader)  # Skip header row

        for row in reader:
            if not row or not any(row):
                continue

            if len(row) >= 4:
                event = {
                    "name": row[0],
                    "start_time": datetime.strptime(row[1], "%H:%M").time(),
                    "end_time": datetime.strptime(row[2], "%H:%M").time(),
                    "category": row[3],
                }
                events.append(event)
            else:
                print(f"Row skipped due to insufficient columns: {row}")


class DarkModeRotating24hClock(QWidget):
    def __init__(self):
        super().__init__()
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update)
        self.timer.start(1000)
        self.setMouseTracking(True)
        self.setMinimumSize(800, 800)

    def mouseMoveEvent(self, mouseEvent):
        # Calculate mouse position relative to the center
        center = QPointF(self.width() / 2, self.height() / 2)
        mousePos = mouseEvent.position() - center
        mouseAngle = np.degrees(np.arctan2(mousePos.y(), mousePos.x())) % 360
        mouseRadius = np.sqrt(mousePos.x() ** 2 + mousePos.y() ** 2)
        show_tooltip = False

        currentTime = QTime.currentTime()
        totalSeconds = (
            currentTime.hour() * 3600 + currentTime.minute() * 60 + currentTime.second()
        )

        # Calculate angle, considering 24h format (86400 seconds in a day)
        clock_angle = 360.0 * totalSeconds / 86400

        QToolTip.hideText()

        # Determine if the mouse is within the clock's event display area
        if 120 <= mouseRadius <= 300:
            for event in events:
                start_time_seconds = (
                    event["start_time"].hour * 3600 + event["start_time"].minute * 60
                )
                end_time_seconds = (
                    event["end_time"].hour * 3600 + event["end_time"].minute * 60
                )
                start_angle = 360.0 * start_time_seconds / 86400
                end_angle = 360.0 * end_time_seconds / 86400

                # Adjust for full rotation
                if start_angle > end_angle:
                    end_angle += 360

                # Convert angles to match clock drawing if necessary
                start_angle_clock = (start_angle - 90 - clock_angle) % 360
                end_angle_clock = (end_angle - 90 - clock_angle) % 360
                if start_angle_clock > end_angle_clock:
                    if mouseAngle >= start_angle_clock or mouseAngle <= end_angle_clock:
                        show_tooltip = True
                else:
                    if start_angle_clock <= mouseAngle <= end_angle_clock:
                        show_tooltip = True

                if show_tooltip:
                    event_info = f"{event['name']} from {event['start_time'].strftime('%H:%M')} to {event['end_time'].strftime('%H:%M')}"
                    QToolTip.showText(mouseEvent.globalPosition().toPoint(), event_info)
                    break

    def drawDot(self, painter, x, y, size=5):
        painter.drawEllipse(x, y, size, size)

    def drawNumber(self, painter, num, topLeftX, topLeftY):
        # Mapping of number to dot positions for a 3x5 grid.
        numberMap = {
            "0": [
                (0, 0),
                (0, 1),
                (0, 2),
                (0, 3),
                (0, 4),
                (1, 0),
                (1, 4),
                (2, 0),
                (2, 1),
                (2, 2),
                (2, 3),
                (2, 4),
            ],
            "1": [(1, 1), (2, 0), (2, 1), (2, 2), (2, 3), (2, 4)],
            "2": [
                (0, 0),
                (1, 0),
                (2, 0),
                (2, 1),
                (1, 2),
                (0, 3),
                (0, 4),
                (1, 4),
                (2, 4),
            ],
            "3": [
                (0, 0),
                (1, 0),
                (2, 0),
                (2, 1),
                (1, 2),
                (2, 3),
                (0, 4),
                (1, 4),
                (2, 4),
                (2, 2),
            ],
            "4": [
                (0, 0),
                (0, 1),
                (0, 2),
                (1, 2),
                (2, 0),
                (2, 1),
                (2, 2),
                (2, 3),
                (2, 4),
            ],
            "5": [
                (0, 0),
                (1, 0),
                (2, 0),
                (0, 1),
                (0, 2),
                (1, 2),
                (2, 2),
                (2, 3),
                (0, 4),
                (1, 4),
                (2, 4),
            ],
            "6": [
                (0, 0),
                (0, 1),
                (0, 2),
                (0, 3),
                (0, 4),
                (1, 0),
                (1, 2),
                (1, 4),
                (2, 0),
                (2, 2),
                (2, 3),
                (2, 4),
            ],
            "7": [(0, 0), (1, 0), (1, 2), (2, 0), (2, 1), (2, 2), (2, 3), (2, 4)],
            "8": [
                (0, 0),
                (0, 1),
                (0, 2),
                (0, 3),
                (0, 4),
                (1, 0),
                (1, 2),
                (1, 4),
                (2, 1),
                (2, 2),
                (2, 3),
                (2, 0),
                (2, 4),
            ],
            "9": [
                (0, 0),
                (0, 1),
                (0, 2),
                (0, 4),
                (1, 0),
                (1, 2),
                (1, 4),
                (2, 0),
                (2, 1),
                (2, 2),
                (2, 3),
                (2, 4),
            ],
        }

        for digit, positions in numberMap.items():
            if num == int(digit):
                for pos in positions:
                    # Adjusted for size and spacing
                    self.drawDot(
                        painter, topLeftX + pos[0] * 3, topLeftY + pos[1] * 3, 2
                    )

    def paintEvent(self, event):
        rect = min(self.width(), self.height())

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setRenderHint(QPainter.RenderHint.VerticalSubpixelPositioning)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        painter.setRenderHint(QPainter.RenderHint.TextAntialiasing)
        painter.setRenderHint(QPainter.RenderHint.NonCosmeticBrushPatterns)

        # Center and scale the painter
        painter.translate(self.width() / 2, self.height() / 2)
        # Adjust scale based on new geometry
        painter.scale(rect / 250, rect / 250)

        # Get current time
        currentTime = QTime.currentTime()
        hour = currentTime.hour()
        minute = currentTime.minute()
        totalSeconds = (
            currentTime.hour() * 3600 + currentTime.minute() * 60 + currentTime.second()
        )

        # Calculate angle, considering 24h format (86400 seconds in a day)
        angle = 360.0 * totalSeconds / 86400

        # Rotate the clock face
        painter.rotate(-angle)

        font = QFont("Arial", 4)
        painter.setFont(font)

        # Draw events
        for event in events:
            start_time_seconds = (
                event["start_time"].hour * 3600 + event["start_time"].minute * 60
            )
            end_time_seconds = (
                event["end_time"].hour * 3600 + event["end_time"].minute * 60
            )
            if start_time_seconds > end_time_seconds:
                end_time_seconds += 86400

            start_angle = 360.0 * start_time_seconds / 86400 - 90
            span_angle = 360.0 * (end_time_seconds - start_time_seconds) / 86400

            color = CATEGORY_COLORS.get(event["category"], CATEGORY_COLORS["Other"])

            # Check if event is in the past
            now = datetime.now().time()
            if event["end_time"] < now and (
                event["end_time"].hour >= day_start or now.hour < day_start
            ):
                color = QColor(color).darker(250).name()
            alpha = 128  # 0 to 255, where 255 is fully opaque
            transparent_color = QColor(color)
            transparent_color.setAlpha(alpha)

            # Drawing the sector
            path = QPainterPath()
            inner_radius = 40
            outer_radius = 98.5

            # Calculate start and end points for the outer arc
            start_point_outer = QPointF(
                outer_radius * np.cos(np.radians(start_angle)),
                outer_radius * np.sin(np.radians(start_angle)),
            )
            end_point_outer = QPointF(
                outer_radius * np.cos(np.radians(start_angle + span_angle)),
                outer_radius * np.sin(np.radians(start_angle + span_angle)),
            )
            start_point_inner = QPointF(
                inner_radius * np.cos(np.radians(start_angle)),
                inner_radius * np.sin(np.radians(start_angle)),
            )
            end_point_inner = QPointF(
                inner_radius * np.cos(np.radians(start_angle + span_angle)),
                inner_radius * np.sin(np.radians(start_angle + span_angle)),
            )

            # Draw the outer arc
            path.moveTo(start_point_inner)
            path.lineTo(start_point_outer)
            path.arcTo(
                -outer_radius,
                -outer_radius,
                2 * outer_radius,
                2 * outer_radius,
                -start_angle,
                -span_angle,
            )
            path.lineTo(end_point_inner)
            path.arcTo(
                -inner_radius,
                -inner_radius,
                2 * inner_radius,
                2 * inner_radius,
                -start_angle - span_angle,
                +span_angle,
            )
            path.closeSubpath()

            painter.save()  # Save the painter's state
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QColor(transparent_color))
            painter.drawPath(path)
            painter.restore()  # Restore the painter's state after drawing the event

        # Draw 24-hour clock face
        for i in range(24):
            # Hour lines
            if (i < hour and i > day_start) or (
                hour < day_start and (i > day_start or i < hour)
            ):
                painter.setPen(
                    QPen(
                        QColor(APP_PALETTE["on_background"]).darker(250),
                        0.5,
                        Qt.PenStyle.SolidLine,
                    )
                )
            else:
                painter.setPen(
                    QPen(
                        QColor(APP_PALETTE["on_background"]), 0.5, Qt.PenStyle.SolidLine
                    )
                )
            painter.drawLine(0, -98, 0, -88)
            # Draw hour labels
            # Set text color to blue
            if (i < hour and i > day_start) or (
                hour < day_start and (i > day_start or i < hour)
            ):
                painter.setPen(QColor(APP_PALETTE["on_background"]).darker(250))

            else:
                painter.setPen(QColor(APP_PALETTE["on_background"]))

            text = str(i)
            hour_srt_rect = painter.fontMetrics().boundingRect(text)
            painter.drawText(
                round(-hour_srt_rect.width() / 2),
                round(-98 + hour_srt_rect.height() - 10),
                text,
            )

            painter.rotate(15.0)  # 360 degrees / 24 segments

        # Draw minute ticks for every 5 minutes

        for i in range(24 * 12):  # 12 five-minute segments per hour
            if (i < hour * 12 and i > day_start * 12) or (
                hour < day_start and (i > day_start * 12 or i < hour * 12)
            ):
                painter.setPen(
                    QPen(
                        QColor(APP_PALETTE["primary"]).darker(250),
                        0.65,
                        Qt.PenStyle.SolidLine,
                    )
                )
            else:
                painter.setPen(
                    QPen(QColor(APP_PALETTE["primary"]), 0.65, Qt.PenStyle.SolidLine)
                )
            if i % 12 != 0:  # Skip hours, already drawn
                painter.drawLine(0, -98, 0, -92)
            painter.rotate(1.25)  # 360 degrees / (24 hours * 12 segments)

        # Reset rotation for drawing the fixed time indicator
        painter.resetTransform()
        painter.translate(self.width() / 2, self.height() / 2)
        painter.scale(rect / 250, rect / 250)

        # Draw current time indicator (static vertical line)
        painter.setPen(QPen(QColor(APP_PALETTE["secondary"]), 1, Qt.PenStyle.SolidLine))
        painter.drawLine(0, -5, 0, -100)  # Static line indicating current time

        # Display the digital clock at the center
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor(APP_PALETTE["secondary"]))
        painter.drawEllipse(-38, -38, 76, 76)

        # Calculate starting positions for digits
        baseX = -25
        if (hour // 10) == 1:
            baseX = -27
        baseY = -7

        painter.setPen(QColor(APP_PALETTE["on_primary"]))
        painter.setBrush(QColor(APP_PALETTE["on_primary"]))

        # Draw hour digits
        self.drawNumber(painter, hour // 10, baseX, baseY)
        self.drawNumber(painter, hour % 10, baseX + 12, baseY)  # Shift for next digit

        # Draw colon
        self.drawDot(painter, baseX + 25, baseY + 3, 1)  # Top dot of the colon
        # Bottom dot of the colon
        self.drawDot(painter, baseX + 25, baseY + 10, 1)

        # Draw minute digits
        self.drawNumber(painter, minute // 10, baseX + 29, baseY)
        self.drawNumber(painter, minute % 10, baseX + 42, baseY)  # Shift for next digit


class CustomEventWidget(QWidget):
    def __init__(self, event, event_info, is_current_event, parent=None):
        super().__init__(parent)
        self.event = event
        self.event_info = event_info
        self.is_current_event = is_current_event
        self.setFixedSize(350, 30)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setRenderHint(QPainter.RenderHint.VerticalSubpixelPositioning)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        painter.setRenderHint(QPainter.RenderHint.TextAntialiasing)
        painter.setRenderHint(QPainter.RenderHint.NonCosmeticBrushPatterns)

        # Draw the background rectangle with rounded corners
        rect = self.rect()
        backgroundColor = QColor(APP_PALETTE["background"])
        if self.is_current_event:
            backgroundColor = QColor(APP_PALETTE["error"])
        painter.setBrush(QColor(backgroundColor))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(rect, 10, 10)

        # Draw the category color square
        categoryColor = QColor(
            CATEGORY_COLORS.get(self.event["category"], CATEGORY_COLORS["Other"])
        )
        painter.setBrush(categoryColor)
        squareSize = 20
        painter.drawRoundedRect(
            10, round((rect.height() - squareSize) / 2), squareSize, squareSize, 5, 5
        )

        # Draw the first letter of the category
        painter.setPen(QColor(APP_PALETTE["on_primary"]))
        painter.setFont(QFont("Arial", 10))
        categoryLetter = self.event["category"][0].upper()
        painter.drawText(
            QRect(10, round((rect.height() - squareSize) / 2), squareSize, squareSize),
            Qt.AlignmentFlag.AlignCenter,
            categoryLetter,
        )

        # Draw the event info text
        textStart = 10 + squareSize + 10  # Start after the square and some padding
        painter.setPen(QColor(APP_PALETTE["primary"]))
        painter.drawText(
            textStart,
            0,
            rect.width() - textStart,
            rect.height(),
            Qt.AlignmentFlag.AlignVCenter,
            self.event_info,
        )


class EventsListWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout(self)
        self.updateEventsList()
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.updateEventsList)
        self.timer.start(1000)

    def updateEventsList(self):
        global current_event_color

        # Clear existing widgets in the layout
        for i in reversed(range(self.layout.count())):
            layoutItem = self.layout.itemAt(i)
            if layoutItem.widget():
                layoutItem.widget().deleteLater()
            else:
                self.layout.removeItem(layoutItem)

        # Sort events by start time before displaying
        sorted_events = sorted(
            events,
            key=lambda x: (
                (
                    x["start_time"].hour + 24
                    if 0 <= x["start_time"].hour < 6
                    else x["start_time"].hour
                ),
                x["start_time"].minute,
            ),
        )

        # Reset current event color to defualt. If there is an occuring event the for loop bellow changes it again.
        current_event_color = APP_PALETTE["error"]

        now = datetime.now()
        for event in sorted_events:
            is_current_event = False
            event_start = datetime.combine(now.date(), event["start_time"])
            event_end = datetime.combine(now.date(), event["end_time"])
            if (event_start < now < event_end) or (
                event_start < now
                and now > event_end
                and event["end_time"].hour < day_start
                and event_start > event_end
            ):
                is_current_event = True
                current_event_color = CATEGORY_COLORS.get(
                    event["category"], CATEGORY_COLORS["Other"]
                )
                time_to_event = f"{((event_end - now).seconds // 3600):02d}h{(((event_end - now).seconds % 3600) // 60):02d}m left"
            elif now < event_start or (
                now > event_start
                and event["start_time"].hour < day_start
                and now.hour > day_start
            ):
                time_to_event = f"T - {((event_start - now).seconds // 3600):02d}h{(((event_start - now).seconds % 3600) // 60):02d}m"
            else:
                continue  # Skip past events

            event_info = f"{event['start_time'].strftime('%H:%M')} - {event['end_time'].strftime('%H:%M')}  |  {time_to_event}  |  {event['name']}"

            customEventWidget = CustomEventWidget(event, event_info, is_current_event)
            self.layout.addWidget(customEventWidget)
        self.layout.addStretch()  # Add stretch to push all widgets towards the top


class PomodoroTimerWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.workDuration = 25 * 60
        self.breakDuration = 5 * 60
        self.isWorkTime = True
        self.isWaitingClick = False
        self.timeLeft = self.workDuration
        self.timer = QTimer()
        self.timer.timeout.connect(self.updateTimer)

        # Layout for controls
        controlLayout = QHBoxLayout()

        # Start/Stop button
        self.startStopButton = QPushButton("Start", self)
        self.startStopButton.setStyleSheet(
            "QPushButton {background-color: "
            + f'{APP_PALETTE["error"]}'
            + "; color: "
            + f'{APP_PALETTE["on_background"]}'
            + ";}"
        )
        self.startStopButton.setIcon(QIcon("_internal/play.png"))
        self.startStopButton.clicked.connect(self.startStopTimer)
        controlLayout.addWidget(
            self.startStopButton,
            alignment=(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignBottom),
        )

        # Reset button
        self.resetButton = QPushButton("Reset", self)
        self.resetButton.setStyleSheet(
            "QPushButton {background-color: "
            + f'{APP_PALETTE["error"]}'
            + "; color: "
            + f'{APP_PALETTE["on_background"]}'
            + ";}"
        )
        self.resetButton.setIcon(QIcon("_internal/reset.png"))
        self.resetButton.clicked.connect(self.resetTimer)
        controlLayout.addWidget(
            self.resetButton,
            alignment=(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignBottom),
        )

        # Checkbox for auto_start_next
        self.autoStartNext = QCheckBox("Auto Start Next ", self)
        self.autoStartNext.setStyleSheet(
            "QCheckBox::indicator {width: 21px; height: 21px; border: 1px solid; border-color: "
            + f'{APP_PALETTE["on_background"]}'
            + "; } QCheckBox::indicator:checked { background-color: "
            + f'{APP_PALETTE["on_error"]}'
            + "; } QCheckBox {background-color: "
            + f'{APP_PALETTE["error"]}'
            + "; color: "
            + f'{APP_PALETTE["on_background"]}'
            + ";}"
        )
        controlLayout.addWidget(
            self.autoStartNext,
            alignment=(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignBottom),
        )

        # Main layout for the widget
        mainLayout = QVBoxLayout(self)  # Set the layout for the widget
        mainLayout.addLayout(controlLayout)
        # Add a stretch factor to push everything above it upwards
        mainLayout.addStretch(1)

        self.setLayout(mainLayout)

        self.setMinimumSize(350, 350)

        # Add sound effect for Pomodoro timer
        self.effect = QSoundEffect()
        self.effect.setSource(QUrl.fromLocalFile("sound.wav"))

    def startStopTimer(self):
        if self.timer.isActive():
            self.timer.stop()
            self.startStopButton.setIcon(QIcon("_internal/play.png"))
            self.startStopButton.setText("Start")
        else:
            if self.isWaitingClick and self.isWorkTime:
                self.isWaitingClick = False
                self.isWorkTime = False
                self.timeLeft = self.breakDuration
            elif self.isWaitingClick and not self.isWorkTime:
                self.isWaitingClick = False
                self.isWorkTime = True
                self.timeLeft = self.workDuration
            self.updateTimer()
            self.timer.start(1000)
            self.startStopButton.setIcon(QIcon("_internal/pause.png"))
            self.startStopButton.setText("Stop")

    def resetTimer(self):
        self.timer.stop()
        self.isWorkTime = True
        self.timeLeft = self.workDuration
        self.update()
        self.startStopButton.setText("Start")

    def updateTimer(self):
        self.timeLeft -= 1

        if self.timeLeft <= 0:
            self.effect.play()
            if self.isWorkTime and self.autoStartNext.isChecked():
                self.isWorkTime = False
                self.timeLeft = self.breakDuration
                self.timer.start(1000)
            elif not self.isWorkTime and self.autoStartNext.isChecked():
                self.isWorkTime = True
                self.timeLeft = self.workDuration
                self.timer.start(1000)
            else:
                self.isWaitingClick = True
                self.timer.stop()
                self.startStopButton.setText("Start")

        self.update()  # Trigger a repaint

    def paintEvent(self, event):
        global current_event_color

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setRenderHint(QPainter.RenderHint.VerticalSubpixelPositioning)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        painter.setRenderHint(QPainter.RenderHint.TextAntialiasing)
        painter.setRenderHint(QPainter.RenderHint.NonCosmeticBrushPatterns)

        rect = self.rect()
        pieRect = QRect(
            rect.left() + 25, rect.top() + 50, rect.width() - 50, rect.height() - 50
        )
        painter.setPen(Qt.PenStyle.NoPen)
        alpha = 128  # 0 to 255, where 255 is fully opaque
        transparent_color = QColor(current_event_color)
        transparent_color.setAlpha(alpha)
        painter.setBrush(transparent_color)
        totalTime = self.workDuration if self.isWorkTime else self.breakDuration
        spanAngle = 360.0 * self.timeLeft / totalTime
        painter.drawPie(pieRect, 90 * 16, -round(spanAngle * 16))

        # Draw digital timer inside the "pie chart"
        painter.setPen(QColor(APP_PALETTE["on_primary"]))
        painter.setFont(QFont("Arial", 16))
        minutes = self.timeLeft // 60
        seconds = self.timeLeft % 60
        painter.drawText(
            pieRect,
            Qt.AlignmentFlag.AlignCenter,
            f"{minutes:02d}:{seconds:02d}",
        )


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Chrono-Compass")
        self.setWindowIcon(QIcon("_internal/icon.png"))
        self.setGeometry(330, 150, 1280, 720)

        self.initUI()

    def initUI(self):
        self.setStyleSheet(
            "background-color: " + f'{APP_PALETTE["background_variant"]}' + ";"
        )
        self.setAutoFillBackground(True)
        self.centralWidget = QWidget(self)  # Create a central widget
        self.setCentralWidget(self.centralWidget)

        self.layout = QHBoxLayout()

        self.clock = DarkModeRotating24hClock()
        self.layout.addWidget(self.clock, alignment=Qt.AlignmentFlag.AlignLeft)

        verticalContainer = QWidget()
        verticalLayout = QVBoxLayout(verticalContainer)

        self.eventsListWidget = EventsListWidget()
        self.eventsListWidget.setMinimumWidth(300)
        verticalLayout.addWidget(
            self.eventsListWidget,
            alignment=(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop),
        )

        self.pomodoroTimer = PomodoroTimerWidget()
        verticalLayout.addWidget(
            self.pomodoroTimer,
            alignment=Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignLeft,
        )

        self.layout.addWidget(verticalContainer, alignment=Qt.AlignmentFlag.AlignLeft)

        self.centralWidget.setLayout(self.layout)


def main():
    load_events_from_csv()
    app = QApplication(sys.argv)
    app.setStyle(APP_STYLE)
    mainWindow = MainWindow()
    mainWindow.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
