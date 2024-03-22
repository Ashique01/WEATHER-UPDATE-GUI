import sys
import threading
import requests
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLineEdit, QPushButton, QMessageBox, QLabel, QScrollArea
from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot, QThread, QSize,Qt
from PyQt5.QtGui import QPixmap, QIcon

class WeatherWorker(QObject):
    weather_received = pyqtSignal(str, str, float, str)

    def fetch_weather_data(self, location):
        try:
            # Fetch weather data from OpenWeatherMap API
            api_key = "43fbc1b7c4b6d106036ac3f49215d4b8"
            url = f'http://api.openweathermap.org/data/2.5/weather?q={location}&appid={api_key}&units=metric'
            response = requests.get(url)
            data = response.json()
            if response.status_code != 200:
                error_message = data.get('message', 'Unknown error')
                self.weather_received.emit('', f'Error fetching weather data: {error_message}', 0, '')
            else:
                weather_desc = data['weather'][0]['description'].capitalize()
                temperature = data['main']['temp']
                icon_id = data['weather'][0]['icon']
                icon_url = f'http://openweathermap.org/img/w/{icon_id}.png'
                self.weather_received.emit(location, weather_desc, temperature, icon_url)
        except Exception as e:
            self.weather_received.emit('', f'Error fetching weather data: {str(e)}', 0, '')

class WeatherApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Weather Kakku')
        self.setGeometry(100, 100, 400, 400)

        self.layout = QVBoxLayout()

        self.location_input = QLineEdit()
        self.location_input.setPlaceholderText("Enter Location")
        self.location_input.setStyleSheet("QLineEdit { border: 2px solid #ccc; border-radius: 5px; padding: 8px; font-size: 20px; }")
        self.layout.addWidget(self.location_input)

        self.submit_button = QPushButton(QIcon('submit.png'), 'Get Weather')
        self.submit_button.setIconSize(QSize(16, 16))
        self.submit_button.setStyleSheet("QPushButton { background-color: #4CAF50; color: white; border: none; "
                                          "border-radius: 5px; padding: 10px;}"
                                          "QPushButton:hover { background-color: #45a049; }")
        self.submit_button.clicked.connect(self.get_weather)
        self.layout.addWidget(self.submit_button)

        self.clear_all_button = QPushButton(QIcon('clear_all.png'), 'Clear All')
        self.clear_all_button.setIconSize(QSize(16, 16))
        self.clear_all_button.setStyleSheet("QPushButton { background-color: #2196F3; color: white; border: none; "
                                             "border-radius: 5px; padding: 10px; }"
                                             "QPushButton:hover { background-color: #1976D2; }")
        self.clear_all_button.clicked.connect(self.clear_all)
        self.layout.addWidget(self.clear_all_button)

        self.terminate_button = QPushButton(QIcon('exit.png'), 'Exit')
        self.terminate_button.setIconSize(QSize(16, 16))
        self.terminate_button.setStyleSheet("QPushButton { background-color: #f44336; color: white; border: none; "
                                             "border-radius: 5px; padding: 10px; }"
                                             "QPushButton:hover { background-color: #d32f2f; }")
        self.terminate_button.clicked.connect(self.close)
        self.layout.addWidget(self.terminate_button)

        self.result_scroll_area = QScrollArea()
        self.result_scroll_area.setWidgetResizable(True)
        self.result_layout = QVBoxLayout()
        self.result_widget = QWidget()
        self.result_widget.setLayout(self.result_layout)
        self.result_scroll_area.setWidget(self.result_widget)
        self.layout.addWidget(self.result_scroll_area)

        self.worker_thread = QThread()
        self.worker = WeatherWorker()
        self.worker.moveToThread(self.worker_thread)
        self.worker_thread.start()

        self.worker.weather_received.connect(self.show_weather)

        self.setLayout(self.layout)

    def get_weather(self):
        location = self.location_input.text()
        if not location:
            QMessageBox.warning(self, 'Warning', 'Please enter a location')
            return

        self.submit_button.setEnabled(False)

        # Run networking function in another thread
        threading.Thread(target=self.worker.fetch_weather_data, args=(location,)).start()

    @pyqtSlot(str, str, float, str)
    def show_weather(self, location, weather_desc, temperature, icon_url):
        if location:
            weather_text = f"<span style='font-size: 14pt; color: #333;'><b>Weather in {location}:</b></span><br>"
            weather_text += f"<span style='font-size: 12pt; color: #666;'>{weather_desc}, <b>Temperature:</b> {temperature}°C</span>"
            weather_label = QLabel(weather_text)
            self.result_layout.addWidget(weather_label, alignment=Qt.AlignCenter)
            
            icon_label = QLabel()
            pixmap = QPixmap()
            pixmap.loadFromData(requests.get(icon_url).content)
            pixmap = pixmap.scaledToWidth(100)
            icon_label.setPixmap(pixmap)
            self.result_layout.addWidget(icon_label, alignment=Qt.AlignCenter)
        else:
            QMessageBox.warning(self, 'Error', weather_desc)
        self.submit_button.setEnabled(True)

    def clear_all(self):
        self.location_input.clear()
        for i in reversed(range(self.result_layout.count())):
            widget = self.result_layout.itemAt(i).widget()
            if widget is not None:
                widget.deleteLater()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = WeatherApp()
    window.show()
    sys.exit(app.exec_())
