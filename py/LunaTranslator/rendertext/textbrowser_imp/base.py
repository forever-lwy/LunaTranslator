from qtsymbols import *
from myutils.config import globalconfig
import unicodedata
from gui.textbrowser import ColorControl, SpecialColor


class base(QWidget):
    def paintText(self, painter: QPainter):
        raise Exception

    def setShadow(self):
        pass

    def moveoffset(self):
        return self.config.get("width", 0), self.config.get("width", 0)

    def extraWH(self):
        return 2 * self.config.get("width", 0), 2 * self.config.get("width", 0)

    @property
    def config(self):
        return globalconfig["rendertext"]["textbrowser"][self.typename].get("args", {})

    @property
    def basecolor(self):
        return QColor(self._basecolor.get())

    def setColor(self, color: ColorControl):
        if color is None:
            self._basecolor = SpecialColor.DefaultColor
        else:
            self._basecolor = color

    @property
    def stylestates(self):
        return self._basecolor.get()

    def maybestylechanged(self):
        if not self.isVisible():
            return
        if self._stylestates == self.stylestates:
            return
        self.move(self.x(), self.y())
        self.adjustSize()
        self.update()

    def __init__(self, typename, parent):
        super().__init__(parent)
        self._stylestates = None
        self._basecolor = SpecialColor.DefaultColor
        self.typename = typename
        self.movedy = 0
        self.movedx = 0
        self._pix = None
        self._m_text = ""

    def adjustSize(self):
        self._pix = None
        font = self.font()
        text = self.text()
        font_m = QFontMetricsF(font)
        w, h = self.extraWH()
        self.resize(
            int(font_m.size(0, text).width() + w),
            int(font_m.height() + h),
        )
        self.setShadow()
        self._stylestates = self.stylestates

    def move(self, x: int, y: int):
        self.movedx = 0
        self.movedy = 0
        dx, dy = self.moveoffset()
        text = self.text()
        al = False
        for _ in text:
            d = unicodedata.bidirectional(_)
            if d == "AL" or d == "R":
                al = True
                break
            if d == "L":
                break
        if al:
            self.movedx -= self.width()
            self.movedx += dx
        else:
            self.movedx -= dx
        self.movedy -= dy
        super().move(QPoint(int(x + self.movedx), int(y + self.movedy)))

    def y(self):
        y = super().y()
        return y - self.movedy

    def x(self):
        x = super().x()
        return x - self.movedx

    def pos(self) -> QPoint:
        return QPointF(self.x(), self.y()).toPoint()

    def clearShadow(self):
        self.setGraphicsEffect(None)

    def text(self):
        return self._m_text

    def setText(self, text):
        self._m_text = text

    def paintEvent(self, event):
        if not self._pix:
            rate = self.devicePixelRatioF()
            self._pix = QPixmap(self.size() * rate)
            self._pix.setDevicePixelRatio(rate)
            self._pix.fill(Qt.GlobalColor.transparent)
            painter = QPainter(self._pix)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            self.paintText(painter)
        painter = QPainter(self)
        painter.drawPixmap(0, 0, self._pix)
