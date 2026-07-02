from PyQt5.QtCore import QPropertyAnimation
from PyQt5.QtWidgets import QGraphicsOpacityEffect


class Animations:
    def fade_out_label(self, label):
        """Постепенно делает прозрачным надпись в label"""
        self.effect = QGraphicsOpacityEffect(label)
        label.setGraphicsEffect(self.effect)

        self.animation = QPropertyAnimation(self.effect, b"opacity")
        self.animation.setDuration(2000)  # Длительность 2 секунды
        self.animation.setStartValue(1.0)  # Полностью видимый
        self.animation.setEndValue(0.0)  # Полностью прозрачный

        self.effect.setOpacity(1.0)
        self.animation.finished.connect(label.clear)
        self.animation.start()