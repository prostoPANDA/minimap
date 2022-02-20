import sys
import os
import json
from PyQt5.QtWidgets import QWidget, QApplication, QPushButton, QLabel, QLineEdit
from PyQt5.QtCore import Qt, QPointF
from PyQt5.QtGui import QPixmap, QPainter, QColor
import requests


class Map(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def text_clicked(self):
        self.image.setFocus()

    def initUI(self):
        self.setGeometry(300, 300, 600, 450)
        self.setWindowTitle('Mini-map')

        self.image = QLabel(self)
        self.image.resize(600, 450)
        self.image.lower()

        self.textbox = QLineEdit(self)
        self.textbox.move(10, 10)
        self.textbox.resize(280, 30)
        self.textbox.setFocusPolicy(Qt.ClickFocus)
        self.textbox.returnPressed.connect(self.text_clicked)

        self.find_button = QPushButton('Искать', self)
        self.find_button.move(300, 9)
        self.find_button.clicked.connect(self.on_click_find)
        self.find_button.resize(80, 32)

        self.reset_button = QPushButton('Сброс поискового результата', self)
        self.reset_button.move(390, 9)
        self.reset_button.clicked.connect(self.on_click_reset)
        self.reset_button.resize(200, 32)

        self.postcode = ''
        self.postcode_flag = False
        self.postcode_button = QPushButton('Индекс', self)
        self.postcode_button.move(300, 45)
        self.postcode_button.clicked.connect(self.postcode_find)
        self.postcode_button.resize(80, 32)

        self.adress_lable = QLabel(self)
        self.adress_lable.setText("")
        self.adress_lable.resize(500, 10)
        self.adress_lable.move(10, 430)


        self.ZOOM_DELTA = 0.001
        self.WASD_DELTA_CONST = 0.714
        self.WASD_DELTA = 0

        self.url = 'https://static-maps.yandex.ru/1.x/'
        self.params = {'ll': '136.944448;28.819334',
                       'spn': '0.010.01',
                       'l': 'sat',
                       'z': '1'}
        self.pt = ''
        self.ll = [37.530887, 55.703118]
        self.spn = [0.002, 0.002]
        self.l = 'map'
        self.z = 1
        self.map_img = self.get_map()
        self.show()

    def postcode_find(self):
        if self.postcode:
            if not self.postcode_flag:
                self.postcode_flag = self.adress_lable.text()
                self.adress_lable.setText(self.postcode_flag + ' Почтовый индекс: ' + self.postcode)
            else:
                self.adress_lable.setText(self.postcode_flag)
                self.postcode_flag = False

    def on_click_find(self):
        toponym_to_find = self.textbox.text()
        geocoder_api_server = "http://geocode-maps.yandex.ru/1.x/"
        geocoder_params = {
            "apikey": "40d1649f-0493-4b70-98ba-98533de7710b",
            "geocode": toponym_to_find,
            "format": "json"}
        response = None
        try:
            response = requests.get(geocoder_api_server, params=geocoder_params)
        except Exception as err:
            return
        if not response:
            return
        json_response = response.json()
        toponym = json_response["response"]["GeoObjectCollection"][
            "featureMember"][0]["GeoObject"]
        try:
            self.postcode = toponym["metaDataProperty"]["GeocoderMetaData"]["Address"]['postal_code']
        except Exception as err:
            self.postcode = ''
        self.postcode_flag = False
        toponym_coodrinates = toponym["Point"]["pos"]
        toponym_longitude, toponym_lattitude = toponym_coodrinates.split(" ")
        self.ll = [float(toponym_longitude), float(toponym_lattitude)]
        self.pt = f"{toponym_longitude},{toponym_lattitude},round"
        self.map_img = self.get_map()

        toponym = json_response["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]
        toponym_address = toponym["metaDataProperty"]["GeocoderMetaData"]["text"]
        self.adress_lable.setText(toponym_address)
        print(toponym_address)
        self.clearFocus()
        print(self.spn)

    def on_click_reset(self):
        self.textbox.setText("")
        self.adress_lable.setText("")
        self.pt = ''
        self.map_img = self.get_map()
        self.clearFocus()

    def keyPressEvent(self, event):
        key = event.key()
        if key == Qt.Key_Escape:
            sys.exit()
        if key == Qt.Key_M and self.l != 'map':
            self.l = 'map'
        elif key == Qt.Key_C and self.l != 'sat':
            self.l = 'sat'
        elif key == Qt.Key_Z and self.l != 'skl':
            self.l = 'skl'

        if key == Qt.Key_PageUp:
            self.spn[0] += self.ZOOM_DELTA
            self.spn[1] += self.ZOOM_DELTA
        elif key == Qt.Key_PageDown:
            self.spn[0] -= self.ZOOM_DELTA
            self.spn[1] -= self.ZOOM_DELTA

        if key == Qt.Key_Equal:
            self.spn[0] += self.ZOOM_DELTA * 10
            self.spn[1] += self.ZOOM_DELTA * 10
        elif key == Qt.Key_Minus:
            self.spn[0] -= self.ZOOM_DELTA * 10
            self.spn[1] -= self.ZOOM_DELTA * 10
        self.spn[0] = max(self.spn[0], 0.001)
        self.spn[1] = max(self.spn[1], 0.001)

        self.WASD_DELTA = self.WASD_DELTA_CONST * self.spn[0]

        if key == Qt.Key_W or key == Qt.Key_Up:
            self.ll[1] += self.WASD_DELTA * 0.9
        if key == Qt.Key_S or key == Qt.Key_Down:
            self.ll[1] -= self.WASD_DELTA * 0.9
        if key == Qt.Key_A or key == Qt.Key_Left:
            self.ll[0] -= self.WASD_DELTA
        if key == Qt.Key_D or key == Qt.Key_Right:
            self.ll[0] += self.WASD_DELTA

        self.map_img = self.get_map()
        print(self.spn)

    def get_map(self):
        res = requests.get(self.get_url())
        map_file = "map.png"
        with open(map_file, "wb") as file:
            file.write(res.content)
        return self.image.setPixmap(QPixmap(map_file))

    def get_url(self):
        return f'{self.url}?ll={self.ll[0]},{self.ll[1]}&spn={self.spn[0]},{self.spn[1]}&l={self.l}&z={self.z}&pt={self.pt}'


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Map()
    ex.show()
    sys.exit(app.exec())
