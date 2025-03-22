""" Import necessary modules for the program to work """
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QGraphicsDropShadowEffect, QSpacerItem, QSizePolicy
)
from PyQt5.QtGui import QColor, QFont, QFontDatabase, QPixmap
from PyQt5.QtCore import Qt, QPropertyAnimation, QEasingCurve
import os
import sys


""" Create a class for the buttons in the UI """
class AnimatedButton(QPushButton):

    """ Initialization """
    def __init__(self, text, color, hover_color=None, is_brave=False):
        super().__init__(text)
        self.default_color = color
        self.hover_color = hover_color if hover_color else color
        self.is_brave = is_brave
        self.default_text_color = QColor(0, 0, 0)
        self.hover_text_color = QColor(255, 255, 255) if is_brave else self.default_text_color
        text_color = QColor(255, 255, 255) if self.is_brave else self.default_text_color
        self.setStyleSheet(f"background-color: {self.default_color.name()}; color: {text_color.name()}; border: none;")
        self.setFont(QFont("Chakra Petch", 14, QFont.Bold))
        self.setFixedSize(240, 40)
        self.shadow_effect = QGraphicsDropShadowEffect()
        self.shadow_effect.setBlurRadius(80)
        self.shadow_effect.setColor(self.default_color.darker(200))
        self.shadow_effect.setOffset(0, 0)
        self.setGraphicsEffect(self.shadow_effect)
        self.animation = QPropertyAnimation(self.shadow_effect, b"blurRadius")
        self.animation.setDuration(800)
        self.animation.setEasingCurve(QEasingCurve.InOutQuad)

    """ Hover effect """
    def enterEvent(self, event):
        self.animation.stop()
        self.animation.setStartValue(self.shadow_effect.blurRadius())
        self.animation.setEndValue(200)
        self.animation.start()
        text_color = self.hover_text_color.name() if self.is_brave else self.default_text_color.name()
        self.setStyleSheet(f"background-color: {self.hover_color.name()}; color: {text_color}; border: none;")
        super().enterEvent(event)

    """ Unhover effect """
    def leaveEvent(self, event):
        self.animation.stop()
        self.animation.setStartValue(self.shadow_effect.blurRadius())
        self.animation.setEndValue(80)
        self.animation.start()
        text_color = QColor(255, 255, 255) if self.is_brave else self.default_text_color
        self.setStyleSheet(f"background-color: {self.default_color.name()}; color: {text_color.name()}; border: none;")
        super().leaveEvent(event)


""" Create a class for the browser selection UI """
class BrowserSelectScreen(QWidget):

    """ Initialization """
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Browser Selector")
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.showFullScreen()
        self.setStyleSheet("background-color: black;")
        self.load_chakra_petch_font()
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)
        layout.setContentsMargins(0, 0, 0, 0)
        title_layout = QVBoxLayout()
        title_label = QLabel("Welcome. Select a web browser")
        title_label.setStyleSheet("color: white; font-weight: bold;")
        title_label.setFont(QFont("Chakra Petch", 24, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        title_layout.addWidget(title_label)
        title_layout.setStretch(0, 1)
        layout.addLayout(title_layout)
        image_label = QLabel(self)
        image_path = self.get_resource_path("browser_selection.png")
        pixmap = QPixmap(image_path)
        scaled_pixmap = pixmap.scaledToWidth(int(1920 * 0.6), Qt.SmoothTransformation)
        image_label.setPixmap(scaled_pixmap)
        image_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(image_label)
        browsers = {
            "Chrome": QColor(255, 255, 255),
            "Edge": QColor(255, 255, 255),
            "Brave": QColor(34, 139, 34),
            "Firefox": QColor(255, 255, 255),
            "Librewolf": QColor(255, 255, 255),
        }
        self.selected_browser = None
        button_layout = QHBoxLayout()
        button_layout.setSpacing(20)
        button_layout.setAlignment(Qt.AlignCenter)
        button_columns = []
        for browser, color in browsers.items():
            column_layout = QVBoxLayout()
            column_layout.setAlignment(Qt.AlignTop)
            button = AnimatedButton(browser, color, is_brave=(browser == "Brave"))
            button.clicked.connect(lambda _, b=browser: self.select_browser(b))
            column_layout.addWidget(button)
            if browser == "Brave":
                label = QLabel("Recommended Browser")
                label.setStyleSheet("color: rgb(34, 139, 34); font-weight: bold; background: transparent;")
                label.setAlignment(Qt.AlignCenter)
                label.setFixedWidth(button.width())
                label.setFont(QFont("Chakra Petch", 15, QFont.Bold))
                column_layout.addWidget(label)
                spacer = QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Expanding)
                column_layout.addItem(spacer)
            button_columns.append(column_layout)
        for column in button_columns:
            button_layout.addLayout(column)
        layout.addLayout(button_layout)
        self.setLayout(layout)

    """ Load the Chakra Petch font, which is used for the UI """
    def load_chakra_petch_font(self):
        font_path = self.get_resource_path("ChakraPetch-Regular.ttf")
        font_id = QFontDatabase.addApplicationFont(font_path)
        if font_id == -1:
            print("Failed to load font.")
        else:
            print("Font loaded successfully.")

    """ Get the correct resource path, whether running as a script or an EXE """
    def get_resource_path(self, relative_path):
        if getattr(sys, 'frozen', False):
            base_path = sys._MEIPASS
        else:
            base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        return os.path.join(base_path, relative_path)

    """ Return value of the selected browser """
    def select_browser(self, browser_name):
        self.selected_browser = browser_name
        print(f"Selected browser: {self.selected_browser}")
        self.close()
        return self.selected_browser

if __name__ == "__main__":
    app = QApplication(sys.argv)
    browser_select_screen = BrowserSelectScreen()
    browser_select_screen.show()
    sys.exit(app.exec_())