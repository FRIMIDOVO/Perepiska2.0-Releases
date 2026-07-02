from PyQt5.QtWidgets import QWidget, QLabel, QHBoxLayout
from PyQt5.QtCore import Qt, QPropertyAnimation, QTimer, QEasingCurve, QPoint
from PyQt5.QtGui import QFont


class Toast(QWidget):
    """
    Красивое внутреннее уведомление для PyQt5.
    Появляется сверху по центру родительского виджета и плавно съезжает вниз.
    """

    def __init__(self, text, notification_type="info", parent=None, duration=2500):
        # Обязательно передаем parent, так как тост живет ВНУТРИ него
        super().__init__(parent)
        if not parent:
            raise ValueError("Для внутреннего Toast обязательно нужно указать parent виджет!")

        self.duration = duration
        self.notification_type = notification_type

        # 1. Настройки виджета (он теперь не отдельное окно, а часть интерфейса)
        self.setAttribute(Qt.WA_TranslucentBackground)

        # Чтобы клики проходили сквозь пустые области тоста к родителю
        self.setAttribute(Qt.WA_TransparentForMouseEvents, False)

        # 2. Создание интерфейса (Иконка + Текст)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 10, 16, 10)
        layout.setSpacing(10)

        # Иконка
        self.icon_label = QLabel(self._get_icon())
        self.icon_label.setFont(QFont("Segoe UI Black", 11))
        self.icon_label.setStyleSheet("background: transparent; color: black;")

        # Текст
        self.text_label = QLabel(text)
        self.text_label.setFont(QFont("Segoe UI", 10, QFont.Weight.Medium))
        self.text_label.setStyleSheet("background: transparent; color: black;")

        layout.addWidget(self.icon_label)
        layout.addWidget(self.text_label)

        # 3. Стильный CSS-дизайн
        self.setStyleSheet(self._get_style())
        self.adjustSize()

        # 4. Рассчитываем координаты (Сверху по центру родителя)
        self.parent_widget = parent

        # Целевая позиция (куда приедет): сверху по центру, отступив 15px вниз
        self.target_x = (self.parent_widget.width() - self.width()) // 2
        self.target_y = 15

        # Стартовая позиция (откуда выезжает): спрятан выше верхней границы родителя
        self.start_x = self.target_x
        self.start_y = -self.height()

        # Помещаем тост в начальную скрытую точку
        self.move(self.start_x, self.start_y)

        # 5. Запуск анимации движения и прозрачности
        self._slide_in()

    def _get_icon(self):
        icons = {"info": "ℹ️", "success": "✅", "warning": "⚠️", "error": "❌"}
        return icons.get(self.notification_type, "ℹ️")

    def _get_style(self):
        colors = {
            "info": "rgba(45, 52, 54, 240)",  # Глубокий темный
            "success": "rgba(46, 204, 113, 240)",  # Приятный зеленый
            "warning": "rgba(241, 196, 15, 240)",  # Насыщенный желтый
            "error": "rgba(231, 76, 60, 240)"  # Сочный красный
        }
        bg_color = colors.get(self.notification_type, colors["info"])
        text_color = "#2d3436" if self.notification_type == "warning" else "#FFFFFF"

        return f"""
            QWidget {{
                background-color: {bg_color};
                border: 1px solid rgba(255, 255, 255, 0.15);
                border-radius: 12px;
            }}
            QLabel {{
                color: {text_color};
            }}
        """

    def _slide_in(self):
        """Анимация выезда сверху вниз"""
        self.show()
        self.raise_()  # Выводим на передний план внутри родителя

        # Анимируем позицию (pos)
        self.anim = QPropertyAnimation(self, b"pos")
        self.anim.setDuration(400)
        self.anim.setStartValue(QPoint(self.start_x, self.start_y))
        self.anim.setEndValue(QPoint(self.target_x, self.target_y))
        # Эффект OutBack дает красивый легкий «отскок» в конце движения
        self.anim.setEasingCurve(QEasingCurve.OutBack)

        self.anim.finished.connect(self._start_hide_timer)
        self.anim.start()

    def _start_hide_timer(self):
        """Ждем заданное время"""
        QTimer.singleShot(self.duration, self._slide_out)

    def _slide_out(self):
        """Анимация отъезда обратно наверх"""
        self.anim = QPropertyAnimation(self, b"pos")
        self.anim.setDuration(350)
        self.anim.setStartValue(QPoint(self.target_x, self.target_y))
        self.anim.setEndValue(QPoint(self.start_x, self.start_y))
        self.anim.setEasingCurve(QEasingCurve.InCubic)

        # После того как улетел — удаляем из памяти
        self.anim.finished.connect(self.close)
        self.anim.finished.connect(self.deleteLater)
        self.anim.start()
