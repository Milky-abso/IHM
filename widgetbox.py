from PyQt5.QtCore import Qt, QTimer, QPropertyAnimation, QParallelAnimationGroup, QRect, QSize, QEvent, QPoint, QTime, QMimeData, QEasingCurve
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QSlider, QVBoxLayout, QHBoxLayout, QLabel, \
    QFrame, QGridLayout, QMessageBox, QButtonGroup, QTabWidget, \
    QDialog, QTableWidgetItem, QLCDNumber, QScrollArea, QSizePolicy, QGraphicsOpacityEffect, QCheckBox, QLineEdit, QStyleOptionSlider
from PyQt5.QtGui import QIcon, QPixmap, QFont, QPainter, QPen, QDrag, QCursor, QMovie, QColor
import os
from ihm import rasp_config

if rasp_config:
    import pigpio

"""===============================================================================================================BOUTONS==============|"""


# Bouton +/- des seuils
class IncreaseButton(QPushButton):
    def __init__(self, text, connection):
        super().__init__()
        self.fontbtnincrease = QFont('Serif', 10, 1)
        self.setText(text)
        self.increasebutton_stylesheet = """
                IncreaseButton {
                    border: 1px solid;
                    min-width: 50px;
                    max-width: 50px;
                    min-height: 40px;
                    max-height: 40px;
                    border-radius: 5px;
                    background-color: #D3D0CB;
                    color: black;
                }
                IncreaseButton:checked 
                {
                    background-color: rgba(18, 190, 34, 120);
                }
                IncreaseButton:pressed { background-color: green }
        """
        self.setStyleSheet(self.increasebutton_stylesheet)
        self.setFont(self.fontbtnincrease)
        self.clicked.connect(connection)


# Bouton valider des seuils
class ValidateButton(QPushButton):
    def __init__(self, text, connection):
        super().__init__()
        self.fontbtnvalidate = QFont('Serif', 10, 1)
        self.setText(text)
        self.validatebutton_stylesheet = """
                ValidateButton {
                    border: 1px solid;
                    min-width: 100px;
                    max-width: 100px;
                    min-height: 40px;
                    max-height: 40px;
                    border-radius: 5px;
                    background-color: #D3D0CB;
                    color: black;
                }
                ValidateButton:checked 
                {
                    background-color: rgba(18, 190, 34, 120);
                }
                ValidateButton:pressed { background-color: green }
        """
        self.setStyleSheet(self.validatebutton_stylesheet)
        self.setFont(self.fontbtnvalidate)
        self.clicked.connect(connection)


# les boutons memoires a 3 états du focus et de l'iris
class MemoryFocusButton(QPushButton):
    def __init__(self, parent=None, *__args):
        super().__init__(*__args)
        self.fontbtnmemo = QFont('Serif', 10)
        self.setProperty('color', '0')
        self.membutton_stylesheet = """
                        MemoryFocusButton[color = "0"]{
                            border: 1px solid;
                            min-width: 65px;
                            max-width: 65px;
                            min-height: 40px;
                            max-height: 40px;
                            border-radius: 5px;
                            background-color: #D3D0CB;
                            color: black;
                        }
                        MemoryFocusButton[color = "1"]{
                            border: 1px solid;
                            min-width: 65px;
                            max-width: 65px;
                            min-height: 40px;
                            max-height: 40px;
                            border-radius: 5px;
                            background-color: rgba(250,250,0,120);
                        }
                        MemoryFocusButton[color = "2"]{
                            border: 1px solid;
                            min-width: 65px;
                            max-width: 65px;
                            min-height: 40px;
                            max-height: 40px;
                            border-radius: 5px;
                            background-color: rgba(18,190,34,120);
                        }
                        MemoryFocusButton[color = "3"]{
                            border: 1px solid;
                            min-width: 65px;
                            max-width: 65px;
                            min-height: 40px;
                            max-height: 40px;
                            border-radius: 5px;
                            background-color: 120*255/1
                            1;
                        }
                        MemoryFocusButton[color = "4"]{
                            border: 1px solid;
                            min-width: 65px;
                            max-width: 65px;
                            min-height: 40px;
                            max-height: 40px;
                            border-radius: 5px;
                            background-color: rgba(70,200,200,120);
                        }
                        MemoryFocusButton[border = true]{
                            border-color:  rgb(80,80,80);
                            border-style: ridge;
                            border-width: 3px
                        }
                        MemoryFocusButton[border = false]{
                            border-color:  black;
                            border-style: solid;
                            border-width: 1px
                        }
                        """
        self.setStyleSheet(self.membutton_stylesheet)
        self.setFont(self.fontbtnmemo)
        self.setText("Memory")
        self.setMinimumHeight(40)
        self.setMaximumHeight(40)
        self.setMinimumWidth(60)
        self.setMaximumWidth(60)
        self.state = [1, 1, 1, 1, 1]
        self.selected = False
        self.mem_number = 0
        self.value_memorized = [20000] * 5
        self.pushstart = 0
        self.pushend = 0
        self.index_machine = 0
        self.installEventFilter(self)
        self.bool = False
        self.timer_push = QTimer()
        self.timer_push.timeout.connect(self.timer_timeout)

    def in_memory(self, index):
        if self.state[index] == 1:
            self.state[index] = 2

    def timer_timeout(self):
        self.bool = True
        self.timer_push.stop()
        self.state[self.index_machine] = 3
        self.value_memorized[self.index_machine] = 0
        self.setText("memo " + str(self.mem_number))
        self.reset_backgroundcolor()

    def eventFilter(self, source, event):
        if event.type() == QEvent.MouseButtonPress:
            self.bool = False
            self.timer_push.start(2000)

        if event.type() == QEvent.MouseButtonRelease and not self.bool:
            self.timer_push.stop()

        return super(MemoryFocusButton, self).eventFilter(source, event)

    def reset_backgroundcolor(self):
        self.setProperty('color', '0')
        self.setStyleSheet(self.styleSheet())

    def setbackgroundcolor(self):
        self.setProperty('color', str(self.mem_number))
        self.setStyleSheet(self.styleSheet())

    def setStateforMachine(self, index):
        self.index_machine = index
        if self.state[self.index_machine] == 1:
            self.reset_backgroundcolor()
            self.setText("memo " + str(self.mem_number))
            self.setframe(False)
        elif self.state[self.index_machine] == 2:
            self.setbackgroundcolor()
            self.setText("Recall " + str(self.mem_number))
            self.setframe(False)
        else:
            pass

    def setframe(self, bool):
        self.setProperty("border", bool)
        self.setStyle(self.style())
        self.selected = bool


#  Bouton cadreur dans la fenetre settings de l'interface utilisateur
class CadreurButton(QPushButton):
    def __init__(self, parent=None, *__args):
        super().__init__(*__args)

        self.fontbtncadreur = QFont('Serif', 10)
        self.cadreurbutton_stylesheet = """
                CadreurButton {
                    border: 1px solid;
                    min-width: 65px;
                    min-height: 40px;
                    max-height: 40px;
                    border-radius: 5px;
                    background-color: #E6CCC4 ;                  
                }
                CadreurButton:checked 
                {
                    background-color: #C58E85;
                }
                CadreurButton:pressed { background-color: #CFAA9F; }
        """
        self.setStyleSheet(self.cadreurbutton_stylesheet)
        self.setFont(self.fontbtncadreur)
        self.setCheckable(True)
        self.setAcceptDrops(True)
        self.name = self.text()


#  Bouton menu dans la fenetre settings de l'interface utilisateur
class SettingsMenuButton(QPushButton):
    def __init__(self, parent=None, *__args):
        super().__init__(*__args)

        self.fontbtnsetting = QFont('Serif', 10)
        self.settingsbutton_stylesheet = """
                SettingsMenuButton {
                    border: 1px solid;
                    min-width: 65px;
                    min-height: 40px;
                    max-height: 40px;
                    border-radius: 5px;
                    background-color: #444A54;              
                    color: white;    
                }
                SettingsMenuButton:pressed { background-color: #E6CCC4; }
        """
        self.setStyleSheet(self.settingsbutton_stylesheet)
        self.setFont(self.fontbtnsetting)
        self.name = self.text()


class EnableButton(QPushButton):
    def __init__(self, name, connection):
        super().__init__()
        self.fontbtnenable = QFont('Serif', 10, 1)
        self.name = name
        self.enablebutton_stylesheet = """
                EnableButton {
                    border: 1px solid;
                    min-width: 101px;
                    min-height: 80px;
                    border-radius: 5px;
                    background-color: #D3D0CB;
                    color: black;
                }
                EnableButton:checked 
                {
                    background-color: rgba(18, 190, 34, 120);
                }
                EnableButton:pressed { background-color: green }
        """
        self.setStyleSheet(self.enablebutton_stylesheet)
        self.setFont(self.fontbtnenable)
        self.setCheckable(True)
        self.setAcceptDrops(True)
        self.clicked.connect(connection)
        self.rename()

    def rename(self):
        if "Enable" in self.text():
            self.setText("Disable " + self.name)
        else:
            self.setText("Enable " + self.name)


class MotorButton(QPushButton):
    def __init__(self, parent=None, *__args):
        super().__init__(*__args)
        self.fontbtnmotor = QFont('Serif', 10, 1)

        self.motorbutton_stylesheet = """
                MotorButton {
                    border: 1px solid;
                    min-width: 65px;
                    max-width: 65px;
                    min-height: 40px;
                    max-height: 40px;
                    border-radius: 5px;
                    background-color: #D3D0CB;
                    color: black;
                }
                MotorButton:checked 
                {
                    background-color: rgba(18, 190, 34, 120);
                }
                MotorButton:pressed { background-color: green }
        """
        self.setStyleSheet(self.motorbutton_stylesheet)
        self.setFont(self.fontbtnmotor)
        self.setCheckable(True)
        self.name = self.text()


#  Bouton utilisé dans l'interface settings ADMIN
class PosMemoButton(QPushButton):
    def __init__(self, text):
        super().__init__()
        self.fontbtnpush = QFont('Serif', 8)
        self.text_name = text
        self.setText(self.text_name)
        self.state = 0
        self.memory_raz = False
        self.setProperty('color', '0')
        self.PosMemoButton_stylesheet = """
                        PosMemoButton[color = "0"]{
                            border: 1px solid;
                            min-width: 90px;
                            max-width: 90px;
                            min-height: 30px;
                            max-height: 30px;
                            border-radius: 5px;
                            background-color: #D3D0CB;
                            color: black;
                        }
                        PosMemoButton[color = "1"]{
                            border: 1px solid;
                            min-width: 90px;
                            max-width: 90px;
                            min-height: 30px;
                            max-height: 30px;
                            border-radius: 5px;
                            background-color: rgba(18,190,34,120);
                        }                    
                """
        self.setStyleSheet(self.PosMemoButton_stylesheet)
        self.timer_push = QTimer()
        self.timer_push.timeout.connect(self.timer_timeout)
        self.installEventFilter(self)
        self.memorized_pos = (0, 0, 0, 0)

    def eventFilter(self, source, event):
        if event.type() == QEvent.MouseButtonPress:
            self.timer_push.start(2000)

        if event.type() == QEvent.MouseButtonRelease:
            self.timer_push.stop()

        return super(PosMemoButton, self).eventFilter(source, event)

    def setbackgroundcolor(self):
        self.setProperty('color', str(self.state))
        self.setStyleSheet(self.styleSheet())

    def change_state(self):
        if self.state == 0:
            self.state = 1
        self.setbackgroundcolor()

    def timer_timeout(self):
        self.timer_push.stop()
        self.state = 0
        self.setbackgroundcolor()
        self.memory_raz = True


# Boutons du pavé numérique
class ButtonPave(QPushButton):
    def __init__(self, name, connection):
        super().__init__()
        self.setText(name)
        self.setFixedHeight(50)
        self.setFixedWidth(65)
        self.clicked.connect(connection)


# une classe qui construit les boutons checkable des inverseurs
class InvertButton(QPushButton):
    def __init__(self, parent=None, *__args):
        super().__init__(parent, *__args)

        self.fontbtninvert = QFont('Serif', 10)
        self.invertbutton_stylesheet = """
                InvertButton {
                    border: 1px solid;
                    min-width: 65px;
                    max-width: 65px;
                    min-height: 40px;
                    max-height: 40px;
                    border-radius: 5px;
                    background-color: #D3D0CB;
                    color: black;

                }
                InvertButton:checked 
                {
                    background-color: rgba(18, 190, 34, 120);
                }
        """
        self.setStyleSheet(self.invertbutton_stylesheet)
        self.setFont(self.fontbtninvert)
        self.setText("Invert")
        self.setCheckable(True)


# Boutons limite de l'interface limite dans l'espace utilisateur: sert a fixer les limites pan/tilt (droite gauche haut bas) d'une tête
class ButtonLim(QPushButton):
    def __init__(self, name):
        super().__init__()
        self.setText(name)
        self.fontbtnlim = QFont('Serif', 8)
        self.lim_but_stylesheet = """ButtonLim {
                                                border: 2px solid;
                                                min-width: 100px;
                                                max-width: 100px;
                                                min-height: 60px;
                                                max-height: 60px;
                                                border-radius: 5px;
                                                background: rgba(120, 120, 150, 120);
                                            }
                                            ButtonLim:checked 
                                            {
                                                background-color: rgb(0, 255, 0);
                                            }
                                    """
        self.setCheckable(True)
        self.setStyleSheet(self.lim_but_stylesheet)


# une classe qui construit les boutons checkable des machines ( bouton tout en haut de l'interface utilisateur)
class MachineButton(QPushButton):
    def __init__(self, parent=None, *__args):
        super().__init__(*__args)

        self.pushedbutton_stylesheet = """
                MachineButton {
                    border: 2px solid;
                    min-width: 150px;
                    max-width: 150px;
                    min-height: 100px;
                    max-height: 100px;
                    border-radius: 20px;
                    outline: none;
                }
                MachineButton:checked 
                {
                    border: 2px solid;
                    border-radius: 20px;
                    background-color: rgb(170, 197, 214);
                }
                MachineButton:focus {
                    outline: none;
                    border: 2px solid;
                    border-radius: 20px;             
                }
                MachineButton:pressed {
                    outline: none;
                    border: 2px solid;
                    border-radius: 20px;            
                }

        """
        self.setStyleSheet(self.pushedbutton_stylesheet)
        self.setFlat(True)
        self.layout_but = QHBoxLayout()
        resize = self.sizePolicy()
        resize.setRetainSizeWhenHidden(True)
        self.setSizePolicy(resize)
        self.gif_wait_optique = QMovie("Icones/nooptic.gif")
        self.gif_wait_optique_V4 = QMovie("Icones/V4-nooptic.gif")
        self.gif_loading = QMovie("Icones/loading_recherche_test.gif")
        self.gif_loading.frameChanged.connect(self.on_frameChanged_loading)

        self.image_dragdrop = QPixmap("Icones/drop_machine.png")
        self.isdragged = False
        self.num_has_changed = False
        self.font_cam_number = QFont('ARIAL', 15, QFont.Bold)

        self.timer_push = QTimer()
        self.timer_push.timeout.connect(self.change_cam_number)

        self.but_cam_number = QPushButton()
        self.but_cam_number.setFlat(True)
        self.but_cam_number_stylesheet = """
                        QPushButton {
                            border: 0px solid;
                            min-width: 40px;
                            max-width: 40px;
                            min-height: 40px;
                            max-height: 40px;
                            border-radius: 20px;
                            background-color: #CFAA9F ;                  
                        }
                        QPushButton:pressed { background-color: #CFAA9F; }
                """
        self.but_cam_number.setStyleSheet(self.but_cam_number_stylesheet)
        self.but_cam_number.setFont(self.font_cam_number)
        self.layout_but.addWidget(self.but_cam_number)
        self.layout_but.setContentsMargins(80, 50, 0, 0)
        self.setLayout(self.layout_but)
        self.dragStartPosition = self.pos()
        self.but_cam_number.installEventFilter(self)

    def eventFilter(self, source, event):
        if event.type() == QEvent.MouseButtonPress:
            self.timer_push.start(1000)

        if event.type() == QEvent.MouseButtonRelease:
            self.timer_push.stop()

        return self.but_cam_number.eventFilter(source, event)

    def change_cam_number(self):
        self.timer_push.stop()
        pave = PaveNumerique(0)
        number = pave.value
        self.but_cam_number.setText(str(number))
        self.num_has_changed = True

    def mousePressEvent(self, event):
        self.dragStartPosition = event.pos()

    def mouseMoveEvent(self, event):
        if (event.pos() - self.dragStartPosition).manhattanLength() >= QApplication.startDragDistance():
            self.isdragged = True
            self.drag = QDrag(self)
            self.drag.setPixmap(self.image_dragdrop)
            mimeData = QMimeData()
            self.drag.setMimeData(mimeData)
            self.drag.exec(Qt.MoveAction)

    def mouseReleaseEvent(self, event):
        self.click()
        super(MachineButton, self).mouseReleaseEvent(event)

    def on_frameChanged_optic(self):
        self.setIconSize(QSize(200, 200))
        self.setIcon(QIcon(self.gif_wait_optique.currentPixmap()))

    def on_frameChanged_optic_V4(self):
        self.setIconSize(QSize(200, 200))
        self.setIcon(QIcon(self.gif_wait_optique_V4.currentPixmap()))

    def on_frameChanged_loading(self):
        self.setIconSize(QSize(200, 200))
        self.setIcon(QIcon(self.gif_loading.currentPixmap()))

    def unset_gif_loading(self):
        if self.gif_loading.state() == 2:
            self.gif_loading.stop()
        else:
            pass

    def unset_gif_optique(self):
        if self.gif_wait_optique.state() == 2:
            self.gif_wait_optique.stop()
        elif self.gif_wait_optique_V4.state() == 2:
            self.gif_wait_optique_V4.stop()
        else:
            pass

    def set_gif_loading(self):
        if self.gif_loading.state() != 2:
            self.gif_loading.start()
        else:
            pass

    def set_gif_optique(self, vers):
        if vers == "V6":
            if self.gif_wait_optique.state() != 2:  # 2 == Qmovie Running 0== Not running 1 == Paused
                self.gif_wait_optique.start()
                self.gif_wait_optique.frameChanged.connect(self.on_frameChanged_optic)
                self.gif_wait_optique.finished.connect(self.gif_wait_optique.start)
            else:
                pass
        elif vers == "V4":
            if self.gif_wait_optique_V4.state() != 2:  # 2 == Qmovie Running 0== Not running 1 == Paused
                self.gif_wait_optique_V4.start()
                self.gif_wait_optique_V4.frameChanged.connect(self.on_frameChanged_optic_V4)
                self.gif_wait_optique_V4.finished.connect(self.gif_wait_optique_V4.start)
            else:
                pass
        else:
            pass


# Le voyant ON/OFF du zoom assist
class VoyantOnOff(QPushButton):
    def __init__(self, parent=None, *__args):
        super().__init__(*__args)

        self.fontvoyant = QFont('Serif', 8)
        self.VoyantOnOff_stylesheet = """
                VoyantOnOff {
                    border: 0px solid;
                    min-width: 40px;
                    max-width: 40px;
                    min-height: 20px;
                    max-height: 20px;
                    border-radius: 10px;
                    background-color: rgba(200, 0, 0, 120)
                }
                VoyantOnOff:checked 
                {
                    background-color: rgba(18, 190, 34, 120);
                }
        """
        self.setStyleSheet(self.VoyantOnOff_stylesheet)
        self.setFont(self.fontvoyant)
        self.setText("OFF")
        self.setMinimumHeight(40)
        self.setMaximumHeight(40)
        self.setMinimumWidth(60)
        self.setMaximumWidth(60)
        self.setCheckable(True)
        self.setAttribute(Qt.WA_TransparentForMouseEvents)


"""===============================================================================================================KEYBOARD KEYS=========|"""


# Boutons classiques du clavier virtuel
class KeyboardKeys(QPushButton):
    def __init__(self):
        super().__init__()
        self.fontkey = QFont('Serif', 12, 1, QFont.Bold)
        self.setFont(self.fontkey)
        self.keys_stylesheet = """KeyboardKeys {        border: 2px solid;
                                                        min-width: 60px;
                                                        max-width: 60px;
                                                        min-height: 60px;
                                                        max-height: 60px;
                                                        border-radius: 5px;
                                                        background: #444A54;
                                                        color: #E1DDD7;
                                                    }
                                                    KeyboardKeys:pressed
                                                    {
                                                        background-color: #E6CCC4;
                                                    }
                                            """
        self.setStyleSheet(self.keys_stylesheet)


# Bouton barre espace du clavier virtuel
class KeyboardSpace(QPushButton):
    def __init__(self):
        super().__init__()
        self.fontkey = QFont('Serif', 8, QFont.Bold)
        self.setFont(self.fontkey)
        self.space_stylesheet = """KeyboardSpace {
                                                        border: 2px solid;
                                                        min-width: 400px;
                                                        max-width: 400px;
                                                        min-height: 60px;
                                                        max-height: 60px;
                                                        border-radius: 5px;
                                                        background: #444A54;
                                                        color: #E1DDD7;
                                                    }
                                                    KeyboardSpace:pressed
                                                    {
                                                        background-color: #E6CCC4;
                                                    }
                                            """
        self.setStyleSheet(self.space_stylesheet)


# Bouton majuscule du clavier virtuel
class KeyboardCaps(QPushButton):
    def __init__(self):
        super().__init__()
        self.fontkey = QFont('Serif', 10, QFont.Bold)
        self.setFont(self.fontkey)
        self.caps_stylesheet = """KeyboardCaps {
                                                        border: 2px solid;
                                                        min-width: 85px;
                                                        max-width: 85px;
                                                        min-height: 60px;
                                                        max-height: 60px;
                                                        border-radius: 5px;
                                                        background: #444A54;
                                                        color: #E1DDD7;
                                                    }
                                                    KeyboardCaps:pressed
                                                    {
                                                        background-color: #E6CCC4;
                                                    }
                                            """
        self.setStyleSheet(self.caps_stylesheet)


"""===============================================================================================================WIDGET===============|"""


# Clavier virtuel
class KeyboardWidget(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAutoFillBackground(True)
        palette = self.palette()
        palette.setColor(self.backgroundRole(), QColor(100, 100, 100, 200))
        self.setPalette(palette)
        self.capsON = False
        self.parent = parent
        self.validate = False
        self.cancel = False
        self.value = ''
        self.current_button = ''
        self.touches_minuscule = [['', '', '', 'a', 'z', 'e', 'r', 't', 'y', 'u', 'i', 'o', 'p', '<---', ''],
                                  ['', '', '', '', 'q', 's', 'd', 'f', 'g', 'h', 'j', 'k', 'l', 'm', 'Valider', ''],
                                  ['', '', '', '', '', 'w', 'x', 'c', 'v', 'b', 'n', ',', '.', ':', '!', 'maj'],
                                  ['', '', '', 'Espace', 'Annuler']]
        self.touches_majuscule = [['', '', '', 'A', 'Z', 'E', 'R', 'T', 'Y', 'U', 'I', 'O', 'P', '<---' ''],
                                  ['', '', '', '', 'Q', 'S', 'D', 'F', 'G', 'H', 'J', 'K', 'L', 'M', 'Valider', ''],
                                  ['', '', '', '', '', 'W', 'X', 'C', 'V', 'B', 'N', ',', '.', ':', '!', 'MAJ'],
                                  ['', '', '', 'Espace', 'Annuler']]
        self.touches_numeriques = [['7', '8', '9'],
                                   ['4', '5', '6'],
                                   ['1', '2', '3'],
                                   ['0', '.']]
        self.setMinimumHeight(301)
        self.setMinimumWidth(1024)
        self.layout_clavier = QHBoxLayout()
        self.layout_numeric = QGridLayout()
        self.layout_numeric.setContentsMargins(0, 0, 0, 0)
        self.layout_numeric.setHorizontalSpacing(1)
        self.layout_numeric.setVerticalSpacing(1)
        self.layout_numeric.setAlignment(Qt.AlignBottom)
        self.layout_touches = QVBoxLayout()
        self.layout_touches.setContentsMargins(0, 0, 0, 0)
        self.layout_touches.setSpacing(1)
        self.writing_layout = QHBoxLayout()
        self.first_line = QHBoxLayout()
        self.second_line = QHBoxLayout()
        self.third_line = QHBoxLayout()
        self.fourth_line = QHBoxLayout()
        self.list_layout = [self.first_line, self.second_line, self.third_line, self.fourth_line]
        self.label_casetext = QLabel("Entrez votre prénom puis validez : ")
        self.casetext = QLineEdit()
        self.cursor = QCursor(Qt.CursorShape(Qt.ArrowCursor))
        self.casetext.setCursor(self.cursor)
        self.writing_layout.addWidget(self.label_casetext)
        self.writing_layout.addWidget(self.casetext, Qt.AlignVCenter, Qt.AlignVCenter)
        self.compteur = 0

        for lignes in self.touches_numeriques:
            self.compteur = 0
            for touches in lignes:
                self.current_button = KeyboardKeys()
                self.current_button.setText(touches)
                self.current_button.clicked.connect(self.getKeys)
                self.layout_numeric.addWidget(self.current_button, self.touches_numeriques.index(lignes), self.compteur)
                self.compteur += 1

        for layout in self.list_layout:
            layout.setContentsMargins(0, -5, 0, -5)  # (Marge Gauche, Marche Haut, Marche droite, Marge bas)
            layout.setSpacing(1)
            if layout is self.fourth_line:
                layout.setAlignment(Qt.AlignHCenter)
            else:
                layout.setAlignment(Qt.AlignLeading)

        for lignes in self.touches_minuscule:
            for touches in lignes:
                index_ligne = self.touches_minuscule.index(lignes)

                if touches not in ('maj', 'Espace', 'Annuler', '<---', '', 'Valider'):
                    self.current_button = KeyboardKeys()
                    self.current_button.setText(touches)
                    self.current_button.clicked.connect(self.getKeys)
                elif touches == 'Espace':
                    self.current_button = KeyboardSpace()
                    self.current_button.setText(touches)
                    self.current_button.clicked.connect(self.espace)
                elif touches == 'maj':
                    self.current_button = KeyboardCaps()
                    self.current_button.setText(touches)
                    self.current_button.clicked.connect(self.majuscule)
                elif touches == '<---':
                    self.current_button = KeyboardCaps()
                    self.current_button.setText(touches)
                    self.current_button.clicked.connect(self.backspace)

                elif touches == 'Annuler':
                    self.current_button = KeyboardCaps()
                    self.current_button.setText(touches)
                    self.current_button.clicked.connect(self.annuler)

                elif touches == 'Valider':
                    self.current_button = KeyboardCaps()
                    self.current_button.setText(touches)
                    self.current_button.clicked.connect(self.valider)

                elif touches == '':
                    self.current_button = QLabel()
                else:
                    pass
                self.list_layout[index_ligne].addWidget(self.current_button)
        self.layout_touches.addLayout(self.writing_layout)
        self.layout_touches.addLayout(self.first_line)
        self.layout_touches.addLayout(self.second_line)
        self.layout_touches.addLayout(self.third_line)
        self.layout_touches.addLayout(self.fourth_line)
        self.layout_clavier.addLayout(self.layout_touches)
        self.layout_clavier.addLayout(self.layout_numeric)
        self.setLayout(self.layout_clavier)

    def getKeys(self):
        self.casetext.setText(self.casetext.text() + self.sender().text())

    def majuscule(self):
        self.capsON = not self.capsON
        if self.capsON:
            for lignes in self.touches_majuscule:
                index_ligne = self.touches_majuscule.index(lignes)
                for i in range(len(lignes)):
                    self.list_layout[index_ligne].itemAt(i).widget().setText(self.touches_majuscule[index_ligne][i])
        else:
            for lignes in self.touches_minuscule:
                index_ligne = self.touches_minuscule.index(lignes)
                for i in range(len(lignes)):
                    self.list_layout[index_ligne].itemAt(i).widget().setText(self.touches_minuscule[index_ligne][i])

    def backspace(self):
        self.casetext.backspace()

    def annuler(self):
        self.cancel = True
        self.parent.add()

    def espace(self):
        self.casetext.setText(self.casetext.text() + ' ')

    def valider(self):
        self.value = self.casetext.text()
        self.validate = True
        self.parent.add()


# Widget expand collapse mémoires positions remote
class WidgetMemoire(QLabel):
    def __init__(self, connection, connection_slider):
        super(WidgetMemoire, self).__init__()
        self.connection = connection
        self.WidgetMemoire_stylesheet = """
                        WidgetMemoire {
                            border: 1px solid;
                            min-width: 72px;
                            max-width: 72px;
                            min-height: 40px;
                            max-height: 40px;
                            border-radius: 5px;
                            background: #D3D0CB;
                        }
                """
        """self.setMinimumWidth(65)
        self.setMinimumHeight(40)"""
        self.expanded = False
        self.param_expanded = False
        self.current_machine = 0
        self.good_list = ''
        self.animation = QPropertyAnimation(self, b'minimumWidth')
        self.animation.setDuration(600)
        self.anim_param = QPropertyAnimation(self, b'minimumHeight')
        self.anim_param.setDuration(600)
        self.anim_param.finished.connect(self.finish_param)
        self.animation.finished.connect(self.finishedanim)
        self.image_param = QPixmap('Icones/param.png')
        self.param_icon = QIcon(self.image_param)

        self.list_memo1 = [PosMemoButton("memo\nn°1"), PosMemoButton("memo\nn°2"), PosMemoButton("memo\nn°3"), PosMemoButton("memo\nn°4"), PosMemoButton("memo\nn°5")]
        self.list_memo2 = [PosMemoButton("memo\nn°1"), PosMemoButton("memo\nn°2"), PosMemoButton("memo\nn°3"), PosMemoButton("memo\nn°4"), PosMemoButton("memo\nn°5")]
        self.list_memo3 = [PosMemoButton("memo\nn°1"), PosMemoButton("memo\nn°2"), PosMemoButton("memo\nn°3"), PosMemoButton("memo\nn°4"), PosMemoButton("memo\nn°5")]
        self.list_memo4 = [PosMemoButton("memo\nn°1"), PosMemoButton("memo\nn°2"), PosMemoButton("memo\nn°3"), PosMemoButton("memo\nn°4"), PosMemoButton("memo\nn°5")]
        self.list_memo5 = [PosMemoButton("memo\nn°1"), PosMemoButton("memo\nn°2"), PosMemoButton("memo\nn°3"), PosMemoButton("memo\nn°4"), PosMemoButton("memo\nn°5")]

        self.dict_memo = {
            0: self.list_memo1,
            1: self.list_memo2,
            2: self.list_memo3,
            3: self.list_memo4,
            4: self.list_memo5,
        }

        self.setWindowFlag(Qt.WindowStaysOnTopHint)
        self.label_memoire = QLabel(" Memoire\n  Position")

        self.main_layout = QVBoxLayout()
        self.main_layout.setContentsMargins(0, 3, 0, 5)  # (Marge Gauche, Marche Haut, Marche droite, Marge bas)
        self.layout_widget_memoire = QHBoxLayout()
        self.layout_widget_memoire.setContentsMargins(0, 0, 5, 0)
        self.layout_memoire = QHBoxLayout()
        self.layout_param = QGridLayout()

        for button in self.list_memo1:
            self.layout_memoire.addWidget(button, Qt.AlignVCenter, Qt.AlignHCenter)
            button.clicked.connect(self.connection)
            button.hide()
        for button in self.list_memo2:
            self.layout_memoire.addWidget(button, Qt.AlignVCenter, Qt.AlignHCenter)
            button.clicked.connect(self.connection)
            button.hide()
        for button in self.list_memo3:
            self.layout_memoire.addWidget(button, Qt.AlignVCenter, Qt.AlignHCenter)
            button.clicked.connect(self.connection)
            button.hide()
        for button in self.list_memo4:
            self.layout_memoire.addWidget(button, Qt.AlignVCenter, Qt.AlignHCenter)
            button.clicked.connect(self.connection)
            button.hide()
        for button in self.list_memo5:
            self.layout_memoire.addWidget(button, Qt.AlignVCenter, Qt.AlignHCenter)
            button.clicked.connect(self.connection)
            button.hide()

        self.images_vignettes = [[b'', b'', b'', b'', b'']] * 5

        self.vignette_memo_1 = VignetteMemo(self)
        self.vignette_memo_2 = VignetteMemo(self)
        self.vignette_memo_3 = VignetteMemo(self)
        self.vignette_memo_4 = VignetteMemo(self)
        self.vignette_memo_5 = VignetteMemo(self)

        self.label_vignette_1 = QLabel("View n°1")
        self.label_vignette_2 = QLabel("View n°2")
        self.label_vignette_3 = QLabel("View n°3")
        self.label_vignette_4 = QLabel("View n°4")
        self.label_vignette_5 = QLabel("View n°5")

        self.list_vignette = [self.vignette_memo_1, self.vignette_memo_2, self.vignette_memo_3, self.vignette_memo_4, self.vignette_memo_5]
        self.list_label_vignette = [self.label_vignette_1, self.label_vignette_2, self.label_vignette_3, self.label_vignette_4, self.label_vignette_5]

        self.button_settings = QPushButton()
        self.button_settings.setIcon(self.param_icon)
        self.button_settings.setIconSize(QSize(28, 28))
        self.button_settings.setFixedSize(30, 30)
        self.button_settings.clicked.connect(self.opensettings)

        self.label_accel = QLabel("Acceleration")
        self.label_accel.setFont(QFont('Arial', 12))

        self.slider_accel = AccelSlider()
        self.slider_accel.setValue(500)
        self.slider_accel.valueChanged.connect(lambda widget=self.slider_accel: connection_slider(widget))

        self.line_accel = DigitalLine()
        self.line_accel.setText("500")
        self.slider_accel.hide()
        self.line_accel.hide()
        self.label_accel.hide()

        self.layout_widget_memoire.addWidget(self.label_memoire, Qt.AlignLeft, Qt.AlignLeft)
        self.layout_widget_memoire.addLayout(self.layout_memoire)
        self.layout_widget_memoire.addWidget(self.button_settings, Qt.AlignVCenter)

        self.layout_param.setRowStretch(0 | 1 | 2 | 3, 30)
        self.layout_param.addWidget(self.label_vignette_1, 0, 0, Qt.AlignCenter)
        self.layout_param.addWidget(self.label_vignette_2, 0, 1, Qt.AlignCenter)
        self.layout_param.addWidget(self.label_vignette_3, 0, 2, Qt.AlignCenter)
        self.layout_param.addWidget(self.label_vignette_4, 0, 3, Qt.AlignCenter)
        self.layout_param.addWidget(self.label_vignette_5, 0, 4, Qt.AlignCenter)

        self.layout_param.addWidget(self.vignette_memo_1, 1, 0, Qt.AlignCenter)
        self.layout_param.addWidget(self.vignette_memo_2, 1, 1, Qt.AlignCenter)
        self.layout_param.addWidget(self.vignette_memo_3, 1, 2, Qt.AlignCenter)
        self.layout_param.addWidget(self.vignette_memo_4, 1, 3, Qt.AlignCenter)
        self.layout_param.addWidget(self.vignette_memo_5, 1, 4, Qt.AlignCenter)

        self.layout_param.addWidget(self.label_accel, 2, 0)
        self.layout_param.addWidget(self.slider_accel, 2, 1, 1, 3)
        self.layout_param.addWidget(self.line_accel, 2, 4)

        for vignette in self.list_vignette:
            vignette.hide()
            vignette.setEnabled(True)
        for label in self.list_label_vignette:
            label.hide()

        self.button_settings.hide()
        self.position = self.pos()
        self.raise_()
        self.main_layout.addLayout(self.layout_widget_memoire, Qt.AlignTop)
        self.main_layout.addLayout(self.layout_param)
        self.setLayout(self.main_layout)

        self.setStyleSheet(self.WidgetMemoire_stylesheet)

    def mouseReleaseEvent(self, event):
        self.raise_()
        if self.param_expanded:
            if 0 < event.pos().x() < 70 and 0 < event.pos().y() < 40:
                self.expandcollapse()
                self.expand_param()
                self.label_memoire.setText(" Memoire\n  Position")
        else:
            if 0 < event.pos().x() < 70 and 0 < event.pos().y() < 40:
                self.expandcollapse()

    def expandcollapse(self):
        if not self.expanded:
            self.expanded = True
            self.animation.setEasingCurve(QEasingCurve.OutBounce)
            self.animation.setStartValue(72)
            self.animation.setEndValue(605)
            self.animation.start()
            for button in self.good_list:
                button.show()

        else:
            self.animation.setEasingCurve(QEasingCurve.InOutQuad)
            self.animation.setStartValue(605)
            self.animation.setEndValue(72)
            self.animation.start()
            self.button_settings.hide()
            self.expanded = False

    def justcollapse(self):
        if self.expanded:
            self.animation.setEasingCurve(QEasingCurve.InOutQuad)
            self.animation.setStartValue(460)
            self.animation.setEndValue(72)
            self.animation.start()
            self.expanded = False
        if self.param_expanded:
            self.anim_param.setEasingCurve(QEasingCurve.InOutQuad)
            """self.anim_param.setStartValue(QRect(self.pos(), QSize(490, 400)))
            self.anim_param.setEndValue(QRect(self.pos(), QSize(490, 40)))"""
            self.anim_param.setStartValue(250)
            self.anim_param.setEndValue(40)
            self.anim_param.start()
            self.param_expanded = False
            for vignette in self.list_vignette[:len(self.good_list)]:
                vignette.hide()
            for label in self.list_label_vignette[:len(self.good_list)]:
                label.hide()
            self.slider_accel.hide()
            self.line_accel.hide()
            self.label_accel.hide()
            self.label_memoire.setText(" Memoire\n  Position")
        else:
            pass

    def expand_param(self):
        if not self.param_expanded:
            self.anim_param.setEasingCurve(QEasingCurve.OutBounce)
            self.anim_param.setStartValue(40)
            self.anim_param.setEndValue(250)
            self.show()
            self.activateWindow()
            self.raise_()

            self.anim_param.start()
            self.param_expanded = True

        else:
            self.anim_param.setEasingCurve(QEasingCurve.InOutQuad)
            self.anim_param.setStartValue(250)
            self.anim_param.setEndValue(40)
            self.anim_param.start()
            self.param_expanded = False
            for vignette in self.list_vignette[:len(self.good_list)]:
                vignette.hide()
            for label in self.list_label_vignette[:len(self.good_list)]:
                label.hide()
            self.slider_accel.hide()
            self.line_accel.hide()
            self.label_accel.hide()
            self.label_memoire.setText(" Memoire\n  Position")

    def finishedanim(self):
        if self.expanded:
            self.button_settings.show()
        else:
            for button in self.good_list:
                button.hide()
            self.button_settings.hide()

    def finish_param(self):
        if self.param_expanded:
            for vignette in self.list_vignette[:len(self.good_list)]:
                vignette.show()
            for label in self.list_label_vignette[:len(self.good_list)]:
                label.show()
            self.slider_accel.show()
            self.line_accel.show()
            self.label_accel.show()
            self.label_memoire.setText(" CLOSE\n  HERE")
        else:
            pass

    def setgoodlist(self):
        for btn in self.good_list:
            btn.hide()
        self.good_list = self.dict_memo.get(self.current_machine, [] * 10)
        if 6 > len(self.good_list) > 0 and self.expanded:
            for btn in self.good_list:
                btn.show()

    def opensettings(self):
        self.expand_param()

    def setsnapshot(self, image, num_memo):
        pix = QPixmap()
        pix.loadFromData(image, "JPG")
        self.images_vignettes[self.current_machine][num_memo - 1] = image
        self.list_vignette[num_memo - 1].set_image_centre(pix)

    def unsetsnap(self, num_memo):
        self.images_vignettes[self.current_machine][num_memo - 1] = b''
        self.list_vignette[num_memo - 1].unset_image()


# le petit panneau des tips
class WarningPanel(QWidget):
    def __init__(self, parent=None):
        super(WarningPanel, self).__init__(parent)
        self.setFixedHeight(30)
        self.image_warning = QPixmap('Icones/warning.png')
        self.container_icon_warning = QLabel()
        self.container_icon_warning.setPixmap(self.image_warning.scaled(30, 30, Qt.KeepAspectRatio))
        self.container_icon_warning.setContentsMargins(0, 0, 0, 0)
        self.container_icon_warning.resize(30, 30)
        self.container_icon_warning.setEnabled(False)
        # self.setAutoFillBackground(True)
        # Voyant warning erreur
        self.label_tips = QLabel("no problemo")
        self.label_tips.setFixedHeight(30)
        self.clock = DigitalClock()
        self.layout_warningpanel = QGridLayout()
        self.layout_warningpanel.setContentsMargins(0, 0, 0, 0)
        self.layout_warningpanel.addWidget(self.clock, 0, 0)
        self.layout_warningpanel.addWidget(self.container_icon_warning, 0, 1)
        self.layout_warningpanel.addWidget(self.label_tips, 0, 2)
        self.setLayout(self.layout_warningpanel)
        self.text = ''
        self.current_error = ''
        self.error_table = {
            'C1': "Pas de moteur détecté à la colonne",
            'B1': "Pas de moteur détecté au chariot",
            'C2': "erreur 2  colonne non définie",
            'B2': "erreur 2 chariot non définie",
            '4': "erreur 4 non définie"
        }

    def setTips(self, text):

        if text != self.text:
            self.label_tips.setText(text)
            self.text = text
            self.container_icon_warning.setEnabled(True)
        else:
            pass

    def setTempTips(self, text, secondes):
        minitimer = QTimer()
        minitimer.timeout.connect(lambda widget=minitimer: self.setEverythingOk())
        self.label_tips.setText(text)
        self.container_icon_warning.setEnabled(True)
        minitimer.start(secondes * 1000)

    def setEverythingOk(self):
        self.label_tips.setText("no problemo")
        self.text = "no problemo"
        self.container_icon_warning.setEnabled(False)

    def setErrorTips(self, error):
        if self.current_error != error:
            self.setTips(self.error_table.get(error, 'erreur inconnue' + str(error)))
            self.current_error = error
        else:
            pass


# Widget de scrolling : Permet des switcher entre differentes vues des sliders lorsque le furio est connecté
class ScrollWidget(QWidget):
    def __init__(self, layout):
        super().__init__()
        self.openscroll = True
        self.focus_on_sliders = False
        self.getfocusback = False
        self.alreadylaunch_gauche = False
        self.alreadylaunch_droite = False
        self.flag_moving = False

        self.mousepos_from_slider = 0
        self.touch_pixel_range = 40
        self.list_joystick = (2, 3, 5, 6, 8, 9)
        self.list_panbar = (2, 5, 8)
        self.liste_active = self.list_joystick  # par defaut on met le joystick
        self.zoomassistwidth = 57
        self.widgetlist = []
        self.list_animation = []
        self.setContentsMargins(0, 0, 0, 0)
        self.mousepos = 0
        self.diff = 0
        self.currentpage = 0
        self.indicateur_scroll = ScrollIndicator(self)
        self.indicateur_scroll.setWindowFlags(Qt.FramelessWindowHint)
        self.indicateur_scroll.show()
        self.slider_focused = ''
        self.animation_indicateur = QPropertyAnimation(self.indicateur_scroll, b'geometry')
        self.animation_indicateur.setEasingCurve(QEasingCurve.OutBounce)
        self.animation_indicateur.setDuration(600)
        self.animation_indicateur.finished.connect(self.indic_fini)
        self.frame_width = 308
        self.frame_width_x4 = 154
        self.frame_width_x4_posX = self.frame_width_x4 + 1
        self.frame_posX = self.frame_width + 1
        self.frame_height = 390
        self.countedFrame = layout.count()
        for x in range(0, self.countedFrame):
            self.widgetlist.append(layout.itemAt(x).widget())
            self.list_animation.append(QPropertyAnimation(self.widgetlist[x], b'geometry'))
            self.list_animation[x].setEasingCurve(QEasingCurve.OutBack)
            self.list_animation[x].setDuration(400)
            self.list_animation[x].setStartValue(QRect(500, 0, self.frame_width - self.zoomassistwidth, 390))
        self.Openscrolling(False)

        self.setLayout(layout)

    def Openscrolling(self, bool):
        if bool:
            if bool != self.openscroll:
                self.openscroll = True
                self.zoomassistwidth = 0
                self.showpage(2, 1)
            else:
                pass
        else:
            if bool != self.openscroll:
                self.openscroll = False
                self.zoomassistwidth = 57
                self.showpage(2, 1)
            else:
                pass

    def mousePressEvent(self, event):
        self.mousepos = event.pos().x()
        self.focus_on_sliders = False
        self.setFocus()

    def mouseMoveEvent(self, event):
        self.flag_moving = True
        self.diff = self.mousepos - event.pos().x()
        for y in range(0, 4):
            for z in (2, 3, 4):
                if self.widgetlist[y].children()[z] == QApplication.focusWidget():
                    self.focus_on_sliders = True
        if self.getfocusback:
            self.setFocus()
            self.focus_on_sliders = False
            self.diff = self.mousepos_from_slider - event.pos().x()
        """if self.currentpage == 0:
            self.widgetlist[0].move(QPoint(0, 0))
            self.widgetlist[1].move(QPoint(309, 0))
        elif self.currentpage == 1:
            self.widgetlist[2].move(QPoint(0, 0))
            self.widgetlist[3].move(QPoint(309, 0))
        else:
            self.widgetlist[0].move(QPoint(0, 0))
            self.widgetlist[1].move(QPoint(155, 0))
            self.widgetlist[2].move(QPoint(310, 0))
            self.widgetlist[3].move(QPoint(465, 0))"""

        if self.openscroll and not self.focus_on_sliders:
            if self.diff > self.touch_pixel_range and not self.alreadylaunch_gauche:
                self.alreadylaunch_droite = False
                self.animation_indicateur.setStartValue(QRect(650, 0, 100, 390))
                self.animation_indicateur.setEndValue(QRect(570, 0, 100, 390))
                self.indicateur_scroll.change_pixmap("gauche")
                self.indicateur_scroll.raise_()
                self.animation_indicateur.start()
                self.alreadylaunch_gauche = True
            elif self.diff < -1 * self.touch_pixel_range and not self.alreadylaunch_droite:
                self.alreadylaunch_gauche = False
                self.animation_indicateur.setStartValue(QRect(-80, 0, 100, 390))
                self.animation_indicateur.setEndValue(QRect(0, 0, 100, 390))
                self.indicateur_scroll.raise_()
                self.indicateur_scroll.change_pixmap("droite")
                self.animation_indicateur.start()
                self.alreadylaunch_droite = True
            else:
                pass
        else:
            self.indicateur_scroll.move(QPoint(600, 600))

    def mouseReleaseEvent(self, event):
        self.flag_moving = False
        self.alreadylaunch_gauche = False
        self.alreadylaunch_droite = False
        if self.openscroll and not self.focus_on_sliders:
            if self.diff > self.touch_pixel_range:
                self.showpage(self.currentpage, 1)
            elif self.diff < -1 * self.touch_pixel_range:
                self.showpage(self.currentpage, -1)
        else:
            pass
        self.diff = 0
        self.getfocusback = False
        self.indicateur_scroll.move(QPoint(600, 600))

    def showpage(self, page, sens):
        if sens > 0:
            for f in range(0, self.countedFrame):
                self.list_animation[f].setStartValue(QRect(500, 0, self.frame_width, 390))
            if page == 0:
                self.widgetlist[0].hide()  # widgetlist = liste des styledFrame donc le carré contenant a l'index 0:PAN 1:TILT 2:TRACK 3:LIFT
                self.widgetlist[1].hide()

                self.widgetlist[2].children()[1].children()[1].setText("TRACK")
                self.widgetlist[2].setMaximumWidth(308)
                self.widgetlist[3].setMaximumWidth(308)

                self.list_animation[2].start()
                self.list_animation[3].start()
                self.widgetlist[2].show()
                self.widgetlist[3].show()

                self.currentpage += 1
            elif page == 1:
                for x in self.list_joystick:  # on cache chaque widget a l'interieur d'une StyledFrame a l'exception du titre:(PAN TILT etc..) de la colonne vitesse (Slider, val slider etc..) et de l'inversion qui sont fixes
                    self.widgetlist[2].children()[x].hide()
                    self.widgetlist[3].children()[x].hide()
                for y in self.liste_active:
                    self.widgetlist[0].children()[y].hide()
                    self.widgetlist[1].children()[y].hide()

                self.list_animation[0].setEndValue(QRect(0, 0, self.frame_width_x4, 390))
                self.list_animation[1].setEndValue(QRect(self.frame_width_x4_posX, 0, self.frame_width_x4, 390))
                self.list_animation[2].setEndValue(QRect(self.frame_width_x4_posX * 2, 0, self.frame_width_x4, 390))
                self.list_animation[3].setEndValue(QRect(self.frame_width_x4_posX * 3, 0, self.frame_width_x4, 390))

                self.widgetlist[0].setMaximumWidth(154)
                self.widgetlist[1].setMaximumWidth(154)
                self.widgetlist[2].setMaximumWidth(154)
                self.widgetlist[3].setMaximumWidth(154)

                self.list_animation[0].start()
                self.list_animation[1].start()
                self.list_animation[2].start()
                self.list_animation[3].start()

                self.widgetlist[2].children()[1].children()[1].setText("Track")

                self.widgetlist[0].show()
                self.widgetlist[1].show()
                self.widgetlist[2].show()
                self.widgetlist[3].show()
                self.currentpage += 1
            else:
                for x in self.list_joystick:
                    self.widgetlist[2].children()[x].show()
                    self.widgetlist[3].children()[x].show()
                for y in self.liste_active:
                    self.widgetlist[0].children()[y].show()
                    self.widgetlist[1].children()[y].show()

                self.list_animation[0].setEndValue(QRect(0, 0, self.frame_width - self.zoomassistwidth, self.frame_height))
                self.list_animation[1].setEndValue(QRect(self.frame_posX - self.zoomassistwidth, 0, self.frame_width - self.zoomassistwidth, self.frame_height))
                self.list_animation[2].setEndValue(QRect(0, 0, self.frame_width - self.zoomassistwidth, self.frame_height))
                self.list_animation[3].setEndValue(QRect(self.frame_posX - self.zoomassistwidth, 0, self.frame_width - self.zoomassistwidth, self.frame_height))

                self.widgetlist[2].hide()
                self.widgetlist[3].hide()
                self.widgetlist[0].setMaximumWidth(308)
                self.widgetlist[1].setMaximumWidth(308)
                self.list_animation[0].start()
                self.list_animation[1].start()
                self.widgetlist[0].show()
                self.widgetlist[1].show()
                self.currentpage = 0

        elif sens < 0:
            for f in range(0, self.countedFrame):
                self.list_animation[f].setStartValue(QRect(-250, 0, self.frame_width - self.zoomassistwidth, 390))
            if page == 0:
                for x in self.list_joystick:
                    self.widgetlist[2].children()[x].hide()
                    self.widgetlist[3].children()[x].hide()
                for y in self.liste_active:
                    self.widgetlist[0].children()[y].hide()
                    self.widgetlist[1].children()[y].hide()

                self.list_animation[0].setEndValue(QRect(0, 0, self.frame_width_x4, self.frame_height))
                self.list_animation[1].setEndValue(QRect(self.frame_width_x4_posX, 0, self.frame_width_x4, self.frame_height))
                self.list_animation[2].setEndValue(QRect(self.frame_width_x4_posX * 2, 0, self.frame_width_x4, self.frame_height))
                self.list_animation[3].setEndValue(QRect(self.frame_width_x4_posX * 3, 0, self.frame_width_x4, self.frame_height))

                self.widgetlist[2].children()[1].children()[1].setText("Track")

                self.widgetlist[0].show()
                self.widgetlist[1].show()
                self.widgetlist[2].show()
                self.widgetlist[3].show()

                self.widgetlist[0].setMaximumWidth(154)
                self.widgetlist[1].setMaximumWidth(154)
                self.widgetlist[2].setMaximumWidth(154)
                self.widgetlist[3].setMaximumWidth(154)

                self.list_animation[0].start()
                self.list_animation[1].start()
                self.list_animation[2].start()
                self.list_animation[3].start()

                self.currentpage = 2

            elif page == 1:
                self.widgetlist[2].hide()
                self.widgetlist[3].hide()

                self.widgetlist[0].setMaximumWidth(308)
                self.widgetlist[1].setMaximumWidth(308)

                self.list_animation[0].start()
                self.list_animation[1].start()
                self.widgetlist[0].show()
                self.widgetlist[1].show()
                self.currentpage -= 1
            else:
                for x in self.list_joystick:
                    self.widgetlist[2].children()[x].show()
                    self.widgetlist[3].children()[x].show()
                for y in self.liste_active:
                    self.widgetlist[0].children()[y].show()
                    self.widgetlist[1].children()[y].show()

                self.list_animation[0].setEndValue(QRect(0, 0, self.frame_width - self.zoomassistwidth, self.frame_height))
                self.list_animation[1].setEndValue(QRect(self.frame_posX, 0, self.frame_width - self.zoomassistwidth, self.frame_height))
                self.list_animation[2].setEndValue(QRect(0, 0, self.frame_width - self.zoomassistwidth, self.frame_height))
                self.list_animation[3].setEndValue(QRect(self.frame_posX, 0, self.frame_width - self.zoomassistwidth, self.frame_height))

                self.widgetlist[0].hide()
                self.widgetlist[1].hide()

                self.widgetlist[2].children()[1].children()[1].setText("TRACK")

                self.widgetlist[2].setMaximumWidth(308)
                self.widgetlist[3].setMaximumWidth(308)

                self.list_animation[2].start()
                self.list_animation[3].start()
                self.widgetlist[2].show()
                self.widgetlist[3].show()
                self.currentpage -= 1

        else:
            pass

    def set_commande_liste(self, cmd):
        if cmd == 'panbar':
            self.liste_active = self.list_panbar
        else:
            self.liste_active = self.list_joystick
        self.showpage(2, 1)

    def indic_fini(self):
        if not self.flag_moving:
            self.indicateur_scroll.move(QPoint(600, 600))
        else:
            pass


# affiche le numero du boitier au-dessus de l'image
class StatusLabel(QWidget):
    def __init__(self, pixmap):
        super().__init__()
        self.pixmap = pixmap.scaled(80, 80, Qt.KeepAspectRatio)
        self.setFixedSize(self.pixmap.size())
        self.rect = QRect(0, 0, self.pixmap.width(), self.pixmap.height())
        self.text = ""
        self.text1 = ""
        self.text2 = ""
        self.frompoignee = False
        self.color = Qt.white

    def paintEvent(self, event):
        painter = QPainter(self)
        pen = QPen(self.color, 2, Qt.SolidLine)
        painter.setPen(pen)

        painter.drawPixmap(self.rect, self.pixmap)

        if self.frompoignee:
            pen = QPen(Qt.black, 2, Qt.SolidLine)
            painter.setPen(pen)
            painter.drawText(40, 80, self.text1)  # zoom
            painter.drawText(0, 50, self.text2)  # point

        else:
            painter.drawText(25, 50, self.text)

        self.frompoignee = False

    def changepixmap(self, pixmap, text):
        self.text = text
        self.pixmap = pixmap.scaled(80, 80, Qt.KeepAspectRatio)
        self.rect = QRect(0, 0, self.pixmap.width(), self.pixmap.height())
        self.update()

    def changepixmappoignee(self, pixmap, textzoom, textfocus):
        self.text1 = textzoom if self.text1 == "" else self.text1
        self.text2 = textfocus if self.text2 == "" else self.text2

        self.pixmap = pixmap.scaled(80, 80, Qt.KeepAspectRatio)
        self.rect = QRect(0, 0, self.pixmap.width(), self.pixmap.height())
        self.frompoignee = True
        self.update()


# le menu latéral
class SideMenu(QWidget):
    def __init__(self, parent=None):
        global rasp_config
        super(SideMenu, self).__init__(parent)
        self.setStyleSheet("SideMenu {background: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0, stop:0 rgba(60,60,60,180),"
                           "stop:0.91 rgba(60,60,60,180), stop:0.92 transparent);}")
        self.image_lum_off = QPixmap('Icones/lum_off.png').scaled(30, 30, Qt.KeepAspectRatio)
        self.image_lum_on = QPixmap('Icones/lum_on.png').scaled(30, 30, Qt.KeepAspectRatio)
        self.image_superviz = QPixmap('Icones/superviz.png')
        self.superviz_icon = QIcon(self.image_superviz)
        self.image_target = QPixmap('Icones/Targeting.png')
        self.target_icon = QIcon(self.image_target)
        self.image_user = QPixmap('Icones/user.png')
        self.user_icon = QIcon(self.image_user)
        self.menu_isopen = False
        self.flag_close_gesture = False
        self.flag_open_gesture = False
        self.flag_direction_changed = False
        self.flag_animation = False
        self.newMousePos = 0
        self.__mouseBeginPos = 0
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.y_size = 0
        self.main_layout_menu = QHBoxLayout()
        self.main_layout_menu.setSpacing(0)
        self.main_layout_menu.setContentsMargins(5, 5, 0, 5)
        self.menu_layout = QVBoxLayout()
        self.menu_layout.setContentsMargins(1, 1, 1, 1)
        self.grab_layout = QVBoxLayout()
        self.grab_layout.setSpacing(0)
        self.grab_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout_menu.addLayout(self.menu_layout)
        self.main_layout_menu.addLayout(self.grab_layout)
        self.layout_cmd_os = QHBoxLayout()
        self.layout_lumi = QHBoxLayout()
        self.layout_btn = QHBoxLayout()
        self.graber = GraberSideMenu()
        self.graber.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.image_poweroff = QPixmap('Icones/poweroff.png')
        self.poweroff_icon = QIcon(self.image_poweroff)

        self.image_reboot = QPixmap('Icones/reboot.png')
        self.reboot_icon = QIcon(self.image_reboot)

        self.btn_poweroff = QPushButton()
        self.btn_poweroff.setIcon(self.poweroff_icon)
        self.btn_poweroff.setIconSize(QSize(80, 80))
        self.btn_poweroff.setFlat(True)
        self.btn_poweroff.clicked.connect(self.poweroff)

        self.btn_reboot = QPushButton()
        self.btn_reboot.setIcon(self.reboot_icon)
        self.btn_reboot.setIconSize(QSize(80, 80))
        self.btn_reboot.setFlat(True)
        self.btn_reboot.clicked.connect(self.reboot)

        self.btn_switch = QPushButton("Targetting")
        self.btn_switch.setIcon(self.target_icon)
        self.btn_switch.setIconSize(QSize(40, 40))
        self.btn_switch.setFlat(True)

        self.btn_superviz = QPushButton("Superviz")
        self.btn_superviz.setIcon(self.superviz_icon)
        self.btn_superviz.setIconSize(QSize(40, 40))
        self.btn_superviz.setFlat(True)

        self.luminosity_slider = BacklightSlider()
        self.luminosity_slider.valueChanged.connect(
            lambda widget=self.luminosity_slider: self.slider_lum_changed(widget))
        if rasp_config:
            self.pwm = pigpio.pi()
            self.pwm.set_mode(18, pigpio.OUTPUT)
            self.pwm.hardware_PWM(18, 1000, 500000)

        self.lum_off = QLabel()
        self.lum_on = QLabel()
        self.lum_off.setPixmap(self.image_lum_off)
        self.lum_on.setPixmap(self.image_lum_on)

        self.menu_layout.addLayout(self.layout_btn, Qt.AlignJustify)
        self.menu_layout.addLayout(self.layout_lumi, Qt.AlignJustify)

        self.menu_layout.addLayout(self.layout_cmd_os, Qt.AlignJustify)

        self.layout_lumi.addWidget(self.lum_off, Qt.AlignJustify, Qt.AlignJustify)
        self.layout_lumi.addWidget(self.luminosity_slider, Qt.AlignJustify, Qt.AlignJustify)
        self.layout_lumi.addWidget(self.lum_on, Qt.AlignJustify, Qt.AlignJustify)

        # self.layout_btn.addWidget(self.btn_switch, Qt.AlignJustify, Qt.AlignJustify)
        self.layout_btn.addWidget(self.btn_superviz, Qt.AlignJustify, Qt.AlignJustify)

        self.layout_cmd_os.addWidget(self.btn_poweroff, Qt.AlignJustify, Qt.AlignJustify)
        self.layout_cmd_os.addWidget(self.btn_reboot, Qt.AlignJustify, Qt.AlignJustify)
        self.grab_layout.addWidget(self.graber, Qt.AlignRight, Qt.AlignRight)
        self.setLayout(self.main_layout_menu)
        self.setAutoFillBackground(False)
        self.anim = QPropertyAnimation(self, b"geometry")
        self.anim.finished.connect(self.setAnimFlag)
        self.diff = 0
        self.sign = lambda x: (x > 0) - (x < 0)
        self.correct_val = lambda y: (y >= 0) and 0 or (y <= -300) and -300 or (-300 < y < 0) and y
        self.old_pos = 0
        self.initPos = -300

    def mousePressEvent(self, event):
        self.__mouseBeginPos = event.globalX()
        self.initPos = self.pos().x()

    def mouseMoveEvent(self, event):
        self.newMousePos = event.globalX()
        if self.old_pos > self.newMousePos and self.flag_direction_changed:
            self.__mouseBeginPos = self.old_pos
            self.flag_direction_changed = False
        self.diff = self.newMousePos - self.__mouseBeginPos
        if self.sign(self.diff) > 0 and not self.flag_animation:
            if self.flag_close_gesture:
                self.flag_direction_changed = True
                self.initPos = self.pos().x()
                self.setGeometry(QRect(self.initPos + self.diff, 0, self.size().width(), self.size().height())) if -300 <= self.correct_val(self.pos().x()) < 0 else self.setGeometry(
                    QRect(0, 0, self.size().width(), self.size().height()))
            else:
                self.setGeometry(QRect(self.initPos + self.diff, 0, self.size().width(), self.size().height())) if -300 <= self.correct_val(self.pos().x()) < 0 else self.setGeometry(
                    QRect(0, 0, self.size().width(), self.size().height()))  # self.setGeometry(QRect(self.correct_val(self.diff), 0, self.size().width(), self.size().height()))
            self.flag_close_gesture = False
            self.flag_open_gesture = True

        elif self.sign(self.diff) < 0 and not self.flag_animation:
            if self.flag_open_gesture:
                self.flag_direction_changed = True
                self.initPos = self.pos().x()
                self.setGeometry(QRect(self.initPos + self.diff, 0, self.size().width(), self.size().height())) if -300 < self.correct_val(self.pos().x()) <= 0 else self.setGeometry(
                    QRect(-300, 0, self.correct_val(self.diff), self.size().height()))
            else:
                self.setGeometry(QRect(self.initPos + self.diff, 0, self.size().width(), self.size().height())) if -300 < self.correct_val(self.pos().x()) <= 0 else self.setGeometry(
                    QRect(-300, 0, self.size().width(), self.size().height()))
                self.raise_()
            self.flag_close_gesture = True
            self.flag_open_gesture = False
        else:
            pass

        self.old_pos = self.newMousePos

    def mouseReleaseEvent(self, event):
        if self.flag_open_gesture and not self.flag_animation:
            self.doanimation(self.correct_val(self.pos().x()))
        elif self.flag_close_gesture and not self.flag_animation:
            self.undoanimation(self.correct_val(self.pos().x()))
        self.old_pos = 0
        self.flag_close_gesture = False
        self.flag_open_gesture = False

    def undoanimation(self, x):
        self.anim.setDuration(150)
        self.anim.setStartValue(QRect(x, 0, self.size().width(), self.y_size))
        self.anim.setEndValue(QRect(-300, 0, self.size().width(), self.y_size))
        self.flag_animation = True
        self.anim.start()

    def doanimation(self, x):
        self.set_y_size(self.size().height())
        self.show()
        self.raise_()
        self.anim.setDuration(150)
        self.anim.setStartValue(QRect(x, 0, self.size().width(), self.y_size))
        self.anim.setEndValue(QRect(0, 0, self.size().width(), self.y_size))
        self.flag_animation = True
        self.anim.start()

    def setAnimFlag(self):
        self.flag_animation = False
        self.show()
        self.raise_()

    def set_y_size(self, y):
        self.y_size = y

    def slider_lum_changed(self, val_slider):
        if rasp_config:
            self.pwm.hardware_PWM(12, 10000, val_slider * 1000)
        else:
            print("val slider", val_slider)

    def poweroff(self):
        msg = QMessageBox()
        msg.setWindowFlags(Qt.X11BypassWindowManagerHint | Qt.CustomizeWindowHint | Qt.WindowStaysOnTopHint)
        msg.setText("Vous êtes sûr de vouloir eteindre ? ")
        msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        ret = msg.exec_()

        if ret == QMessageBox.Yes:
            print("poweroff")
            os.system('poweroff')
        else:
            print(" not poweroff")

    def reboot(self):
        msg = QMessageBox()
        msg.setWindowFlags(Qt.X11BypassWindowManagerHint | Qt.CustomizeWindowHint | Qt.WindowStaysOnTopHint)
        msg.setText("Vous êtes sûr de vouloir redemarrer ? ")
        msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        ret = msg.exec_()

        if ret == QMessageBox.Yes:
            print("reboot")
            os.system('reboot')
        else:
            print(" not reboot")


"""===============================================================================================================DIVERS===============|"""


# inutilisé pour le moment
class StyledScrollArea(QScrollArea):
    def __init__(self, parent=None, *__args):
        super().__init__(*__args)
        self.scrollarea_stylesheet = """
                        StyledScrollArea {

                                background: transparent ;
                                }"""
        self.setStyleSheet(self.scrollarea_stylesheet)
        # self.setWidgetResizable(True)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.diff = 0
        self.olddiff = 0

    def mousePressEvent(self, event):
        self.mousepos = event.pos().x()

    def mouseMoveEvent(self, event):
        self.diff = self.mousepos - event.pos().x()

        if self.diff > 0:
            self.horizontalScrollBar().setValue(self.horizontalScrollBar().value() + self.diff)
        elif self.diff < 0:
            self.horizontalScrollBar().setValue(self.horizontalScrollBar().value() + self.diff)
        else:
            pass
        self.mousepos = event.pos().x()


# Bouton On/Off pour activer desactiver le x2 du focus
class RadioSwitch(QCheckBox):
    def __init__(self, parent=None, *__args):
        super().__init__(parent, *__args)
        self.setStyleSheet("""QCheckBox::indicator::unchecked {
                              image: url(Icones/switchoff_petit.png);
                            }
                            QCheckBox::indicator::checked {
                              image: url(Icones/switchon-petit.png);
                            }""")
        self.setContentsMargins(0, 0, 0, 0)
        self.label = QLabel("X2", self)
        self.label.move(20, 8)


# l'encadrement de mes widgets containers
class StyledFrame(QFrame):
    def __init__(self, parent=None, *__args):
        super().__init__(*__args)
        self.setFrameShape(QFrame.StyledPanel)
        self.setFrameShadow(QFrame.Plain)
        self.setContentsMargins(-50, -50, -50, -50)
        self.setLineWidth(2)
        self.setMinimumWidth(150)
        # self.setMaximumWidth(250)
        self.setMinimumHeight(390)
        # self.setMaximumHeight(400)
        self.setProperty('color', '0')
        self.setStyleSheet("""StyledFrame[color = "0"]{
                            border: 1px solid rgb(0,0,0);
                            background: rgba(255, 255, 240, 255);}"""
                           """StyledFrame[color = "1"]{
                            border: 2px solid rgb(0,0,0);
                            background: rgb(170, 197, 214);}""")
        self.installEventFilter(self)

    def set_bg(self, nb):
        self.setProperty('color', str(nb))
        self.setStyleSheet(self.styleSheet())


# zone de drop pour les boutons machines
class DropMyButton(QLabel):
    def __init__(self):
        super(DropMyButton, self).__init__()
        self.setAcceptDrops(True)
        self.connection = ""
        self.setFixedWidth(40)
        self.image_drop = QPixmap('Icones/separator.png')

    def dragEnterEvent(self, event):
        event.acceptProposedAction()
        self.setPixmap(self.image_drop.scaled(50, 100, Qt.IgnoreAspectRatio, Qt.SmoothTransformation))

    def dragLeaveEvent(self, event):
        self.setPixmap(QPixmap())

    def dropEvent(self, event):
        self.connection()
        self.setPixmap(QPixmap())
        # self.setText(event.mimeData().text())


"""===============================================================================================================SLIDER===============|"""


# une classe qui construit un slider personalisé utilisé pour la vitesse courbe et ratio
class StyledSlider(QSlider):
    def __init__(self, parent=None, *__args):
        super().__init__(*__args)

        self.slider_stylesheet = """
                StyledSlider {
                        min-width: 50px;
                        max-width: 50px;
                        min-height: 200px;
                        max-height: 200px;  
                    }

                StyledSlider::groove:vertical {
                    border: 3px ;
                    border-color: rgb(0,0,0);
                    border-style: solid;
                    border-radius: 5px;
                    width: 3px;
                    margin: 0 12px;
                    }

                StyledSlider::sub-page
                    {
                        background: rgb(209, 223, 255);
                        border: 1px ;
                        border-color: rgb(0,0,0);
                        border-style: solid;
                        border-radius: 5px;
                    }

                StyledSlider::add-page 
                    {
                        background: rgb(113, 149, 232);
                        border: 1px ;
                        border-color: rgb(0,0,0);
                        border-style: solid;
                        border-radius: 5px;

                    }

                StyledSlider::handle:vertical {
                    background: rgb(90, 90, 90);
                    border-style:None;
                    height: 35px; 
                    width: 50px;
                    margin: 1px -25px;
                    border-radius: 5px;
                    }

                            """
        self.setOrientation(Qt.Vertical)
        self.flag_stop_move = False
        self.setFocusPolicy(Qt.StrongFocus)
        self.setTickPosition(self.TicksBothSides)
        self.setRange(0, 100)
        self.setPageStep(1)
        self.setTickInterval(50)
        self.setSingleStep(1)
        self.setStyleSheet(self.slider_stylesheet)
        self.mousepos = 0
        self.diff = 0
        self.installEventFilter(self)
        self.range_out_slider = 40
        self.initStyleOption(QStyleOptionSlider())

    def eventFilter(self, source, event):
        if event.type() == QEvent.MouseButtonPress:
            self.diff = 0
            self.mousepos = event.pos().x()
            self.flag_stop_move = False
            self.blockSignals(False)

        if event.type() == QEvent.MouseMove:
            if not self.flag_stop_move:
                self.diff = self.mousepos - event.pos().x()
                if self.diff > self.range_out_slider or self.diff < -self.range_out_slider:
                    self.flag_stop_move = True
            if self.flag_stop_move:
                self.parent().parent().getfocusback = True
                self.parent().parent().mousepos_from_slider = self.mousepos
                self.parent().parent().mouseMoveEvent(event)
                return True

        if event.type() == QEvent.Timer:
            if self.flag_stop_move:
                return True

        if event.type() == QEvent.MouseButtonRelease:
            self.parent().parent().mouseReleaseEvent(event)

        return super(QSlider, self).eventFilter(source, event)


class AccelSlider(QSlider):
    def __init__(self, parent=None, *__args):
        super().__init__(*__args)
        self.accelslider_stylesheet = """
                AccelSlider {
                        min-width: 280px;
                        max-width: 280px;
                        min-height: 50px;
                        max-height: 50px;  
                    }

                AccelSlider::groove:horizontal {
                    border: 3px ;
                    border-color: rgb(0,0,0);
                    border-style: solid;
                    border-radius: 5px;
                    height: 3px;
                    margin: 4 0px;
                    }

                AccelSlider::sub-page
                    {
                        background: rgb(209, 223, 255);
                        border: 1px ;
                        border-color: rgb(0,0,0);
                        border-style: solid;
                        border-radius: 5px;
                    }

                AccelSlider::add-page 
                    {
                        background: rgb(113, 149, 232);
                        border: 1px ;
                        border-color: rgb(0,0,0);
                        border-style: solid;
                        border-radius: 5px;

                    }

                AccelSlider::handle:horizontal {
                    background: rgb(90, 90, 90);
                    border-style:None;
                    height: 40px; 
                    width: 40px;
                    margin: -20px 1px;
                    border-radius: 20px;
                    }

                            """

        self.setOrientation(Qt.Horizontal)
        self.setFocusPolicy(Qt.StrongFocus)
        self.setTickPosition(self.TicksBothSides)
        self.setRange(0, 1000)
        self.setPageStep(1)
        self.setTickInterval(50)
        self.setSingleStep(1)
        self.setStyleSheet(self.accelslider_stylesheet)


# le bouton bistable pour switcher de l'iris au focus et vice versa
class SwitchDiaphButton(QSlider):
    def __init__(self, parent=None, *__args):
        super().__init__(*__args)
        self.layoutdiaph = QHBoxLayout()
        self.switch_diaph_stylesheet = """
                SwitchDiaphButton {
                        min-width: 150px;
                        max-width: 150px;
                        min-height: 50px;
                        max-height: 50px;  
                    }

                SwitchDiaphButton::groove:horizontal {
                    border: 1px ;
                    border-color: rgb(0,0,0);
                    border-style: solid;
                    border-radius: 5px;
                    height: 28px;
                    margin: 0 12px;
                    }

                SwitchDiaphButton::sub-page
                    {
                        background: rgb(160, 160, 160);
                        border: 1px ;
                        border-color: rgb(0,0,0);
                        border-style: solid;
                        border-radius: 5px;
                    }

                SwitchDiaphButton::add-page 
                    {
                        background: rgb(170, 197, 214);
                        border: 1px ;
                        border-color: rgb(0,0,0);
                        border-style: solid;
                        border-radius: 5px;

                    }

                SwitchDiaphButton::handle:horizontal {
                    background: rgb(90, 90, 90);
                    border: 0px;
                    height: 50px; 
                    width: 35px;
                    margin: -25px -5px;
                    border-radius: 5px;
                    }
                            """
        self.setOrientation(Qt.Horizontal)
        self.setFocusPolicy(Qt.StrongFocus)
        self.setRange(1, 2)
        self.setSingleStep(1)

        self.label_diaph = QLabel("            Iris")
        self.label_focus = QLabel("Focus")
        self.label_diaph.setFont(QFont("Serif", 15))
        self.label_focus.setFont(QFont("Serif", 15))
        self.layoutdiaph.addWidget(self.label_focus, Qt.AlignLeft)
        self.layoutdiaph.addWidget(self.label_diaph, Qt.AlignRight)

        self.label_focus.hide()
        self.setStyleSheet(self.switch_diaph_stylesheet)
        self.setLayout(self.layoutdiaph)


# une classe qui construit un slider personalisé pour le backlight
class BacklightSlider(QSlider):
    def __init__(self, parent=None, *__args):
        super().__init__(*__args)
        self.layoutbacklightslider = QHBoxLayout()
        self.slider_backlight_stylesheet = """
                BacklightSlider {
                        min-width: 200px;
                        max-width: 200px;
                        min-height: 50px;
                        max-height: 50px;  
                    }

                BacklightSlider::groove:horizontal {
                    border: 0px solid #262626;
                    height: 5px;
                    margin: 10 0px;
                    }
                BacklightSlider::sub-page
                    {
                        background: rgb(160, 160, 160);
                        height: 5px;
                        margin: 10 0px;
                    }

                BacklightSlider::add-page 
                    {
                        background: rgb(170, 197, 214);
                        height: 5px;
                        margin: 10 0px;
                    }

                BacklightSlider::handle:horizontal {
                    background: rgb(35, 41, 58);
                    border: 0px;
                    height: 40px; 
                    width: 54px;
                    margin: -20px 0px;
                    border-radius: 20px
                    }
                            """
        self.setOrientation(Qt.Horizontal)
        self.setFocusPolicy(Qt.StrongFocus)
        self.setTickPosition(self.TicksBothSides)
        self.setRange(10, 1000)
        self.setTickInterval(1)
        self.setSingleStep(1)
        self.setValue(500)
        self.setStyleSheet(self.slider_backlight_stylesheet)
        self.setLayout(self.layoutbacklightslider)


"""===============================================================================================================LCDNUMBER===========|"""


# affiche la valeur des sliders en numero lcd
class DigitalLine(QLCDNumber):
    def __init__(self, parent=None):
        super(DigitalLine, self).__init__(parent)
        self.setContentsMargins(0, 0, 0, 0)
        self.setSegmentStyle(QLCDNumber.Flat)
        self.setMinimumHeight(25)
        self.setFixedWidth(60)
        self.setDigitCount(4)
        self.text = "0"

    def setText(self, text):
        self.text = text
        self.display(self.text)
        self.update()

    def getText(self):
        return self.text


# Anciennement l'heure, remplacé par le temps qui passe depuis l'allumage de l'appli ( #pasdepiledansleraspberry)
class DigitalClock(QLCDNumber):
    def __init__(self, parent=None):
        super(DigitalClock, self).__init__(parent)
        self.setFrameStyle(QFrame.NoFrame)
        self.setSegmentStyle(QLCDNumber.Flat)
        self.setDigitCount(10)
        self.time = QTime(0, 0, 0)
        self.text = ""
        timer = QTimer(self)
        timer.timeout.connect(self.showTime)
        timer.start(1000)
        self.showTime()
        self.resize(200, 100)

    def showTime(self):
        self.time = self.time.addSecs(1)
        self.text = self.time.toString('hh:mm:ss')
        if (self.time.second() % 2) == 0:
            self.text = self.text[:2] + ' ' + self.text[3:5] + ' ' + self.text[6:]
        self.display(self.text)


"""
    def mousePressEvent(self, event):
        self.dragStartPosition = event.pos()

    def mouseMoveEvent(self, event):
        if (event.pos() - self.dragStartPosition).manhattanLength() < QApplication.startDragDistance():
            drag = QDrag(self)
            mimeData = QMimeData()
            mimeData.setText(self.text)
            drag.setMimeData(mimeData)

            drag.exec(Qt.CopyAction | Qt.MoveAction)"""

"""===============================================================================================================LABELS===============|"""


# les 3 petits points du menu latéral pour l'attraper
class GraberSideMenu(QLabel):
    def __init__(self, parent=None):
        super(GraberSideMenu, self).__init__(parent)
        self.setStyleSheet("GraberSideMenu {background: transparent;}")
        self.setAttribute(Qt.WA_StyledBackground, True)
        # self.layout.setSpacing(0)
        self.setContentsMargins(0, 0, 0, 0)
        self.image_settings = QPixmap('Icones/menu3.png')
        self.setPixmap(self.image_settings)
        self.resize(24, 44)
        self.setAutoFillBackground(True)


# une classe qui peint le petit widget du focus
class IndicatorFocus(QLabel):
    def __init__(self, parent=None, *__args):
        super().__init__(*__args)
        self.ypos = 130
        self.ypos_mem = [[0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]]
        self.ypos_mem_iris = [0] * 4
        self.valuefocus = "0"
        self.memory_status = [[False, False, False, False], [False, False, False, False], [False, False, False, False], [False, False, False, False], [False, False, False, False]]
        self.memory_status_iris = [False, False, False, False]
        self.color = [Qt.yellow, Qt.green, Qt.red, Qt.darkCyan]
        self.memorypushed = 0
        self.cur_val = round(16383 / 2)
        self.val_focus = self.cur_val
        self.val_iris = self.cur_val
        self.flag_iris = False
        self.current_machine_index = 0
        self.button_precision = RadioSwitch(self)
        self.button_precision.setFixedSize(53, 30)
        self.button_precision.move(QPoint(0, 135))
        self.stop_text = lambda x: (x <= 32.6) and 32.6 or (x >= 279) and 279 or (279 > x > 32.6) and x
        self.disable = False

    def paintEvent(self, event):
        painter = QPainter(self)
        for memory in range(0, 4):
            if self.memory_status[self.current_machine_index][memory] and not self.flag_iris:
                pen = QPen(self.color[memory], 2, Qt.SolidLine)
                painter.setPen(pen)
                painter.drawLine(70, self.ypos_mem[self.current_machine_index][memory] + 20, 130, self.ypos_mem[self.current_machine_index][memory] + 20)
            elif self.memory_status_iris[memory] and self.flag_iris:
                pen = QPen(self.color[memory], 2, Qt.SolidLine)
                painter.setPen(pen)
                painter.drawLine(70, self.ypos_mem_iris[memory] + 20, 130, self.ypos_mem_iris[memory] + 20)

        pen = QPen(Qt.black, 2, Qt.SolidLine)
        painter.setPen(pen)
        painter.drawRect(70, 20, 60, 260)
        painter.drawLine(65, self.ypos + 20, 75, self.ypos + 20)
        painter.drawLine(125, self.ypos + 20, 135, self.ypos + 20)

        painter.setFont(QFont("Serif", 15))
        if self.flag_iris:
            painter.drawText(30, 280, "Close")
            painter.drawText(30, 25, "Open")
        else:
            painter.drawText(50, 285, "0")
            painter.setFont(QFont("Arial", 18))
            painter.drawText(48, 28, u"\u221E")
        painter.setFont(QFont("Arial", 11))

        painter.drawText(self.getTextPos(), self.stop_text(self.ypos + 25), str(round(100 * int(self.valuefocus) / 16383, 2))) if self.valuefocus != u"\u221E" else painter.drawText(self.getTextPos(),
                                                                                                                                                                                     self.stop_text(
                                                                                                                                                                                         self.ypos + 25),
                                                                                                                                                                                     self.valuefocus)
        painter.drawLine(55, 150, 65, 150)

        return

    def updateline(self, val, str_val_focus):
        if not self.disable:
            if self.flag_iris:
                self.cur_val = val
                self.ypos = (260 / (-16383)) * (val - 16383)
                self.valuefocus = str_val_focus if val < 16383 else u"\u221E"
                self.update()
            else:
                self.cur_val = val
                self.ypos = (260 / (-16383)) * (val - 16383)
                self.valuefocus = str_val_focus if val < 16383 else u"\u221E"
                self.update()
        else:
            pass

    def saveposfocus(self, mem_nb, index):
        self.current_machine_index = index
        if self.flag_iris:
            self.memorypushed = mem_nb
            self.ypos_mem_iris[mem_nb] = self.ypos
            self.memory_status_iris[mem_nb] = True
            self.update()
        else:
            self.memorypushed = mem_nb
            self.ypos_mem[self.current_machine_index][mem_nb] = self.ypos
            self.memory_status[self.current_machine_index][mem_nb] = True
            self.update()

        return self.cur_val

    def delposfocus(self, mem_nb):
        if self.flag_iris:
            self.memory_status_iris[mem_nb] = False
        else:
            self.memory_status[self.current_machine_index][mem_nb] = False
            self.ypos_mem[self.current_machine_index][mem_nb] = 0
        self.update()

    def updateposmemory(self, index):
        self.current_machine_index = index
        for mem in range(0, 4):
            self.memory_status[self.current_machine_index][mem] = True
        self.update()

    def set_irisfocus_val(self):
        if not self.flag_iris:
            self.val_iris = self.ypos
            self.ypos = self.val_focus
        if self.flag_iris:
            self.val_focus = self.ypos
            self.ypos = self.val_iris
        self.update()

    def getTextPos(self):
        nbdigit = sum(c.isdigit() for c in self.valuefocus)
        position = {
            5: 80,
            4: 84,
            3: 88,
            2: 92,
            1: 96,
            0: 96
        }
        pos = position.get(nbdigit, "err nb inconnu")
        return pos

    def getCurVal(self):
        return self.cur_val

    def disable_focus(self, bool):
        self.disable = bool


# Shema pour les limites de tilt de la tête. Actuellement inutilisé
class TiltLimitShema(QLabel):
    def __init__(self, parent=None, *__args):
        super().__init__(*__args)
        self.rect = QRect(0, 0, 50, 50)
        self.color = Qt.black
        self.lineposx = 0
        self.lineposy = 0

    def paintEvent(self, event):
        painter = QPainter(self)
        pen = QPen(self.color, 1, Qt.SolidLine)
        painter.setPen(pen)

        painter.drawEllipse(self.rect)
        painter.drawRect(0, 50, 50, 50)
        painter.drawLine(25, 25, self.lineposx, self.lineposy)
        return

    def updateline(self):
        baba = 0


# comme son nom l'indique : les vignettes du tracking
class VignetteTrack(QLabel):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setFixedSize(320, 245)
        # self.layout.setSpacing(0)
        self.setMouseTracking(True)
        self.setAutoFillBackground(True)
        self.setEnabled(False)
        self.previous_menu_side = ""
        self.numero = 0
        self.isactive = False
        self.issetted = False
        self.isclicked = False

        self.image_poubelle = QPixmap('Icones/poubelle3.png')
        self.image_snapshot = QPixmap('Icones/addsnapshot.png')

        self.frame_targeton = QFrame(self)
        self.frame_targeton.setProperty("border", "1")
        self.setStyleSheet("VignetteTrack {background: transparent;}")
        self.frame_targeton.setStyleSheet("""QFrame [border = "0"] {
                                            border: 5px solid rgb(255,0,0);
                                            background: rgba(255, 255, 255, 0);
                                            border-radius: 5px;}"""
                                          """QFrame [border = "1"] {
                                          border: 3px solid rgb(0,0,200);
                                          background: rgba(255, 255, 255, 0);
                                          border-radius: 5px;}"""
                                          )
        self.frame_targeton.setFixedSize(320, 245)
        self.frame_targeton.setAttribute(Qt.WA_TransparentForMouseEvents)
        self.mainlayout = QHBoxLayout(self.frame_targeton)

        self.timer_target = QTimer()
        self.timer_target.timeout.connect(self.blink_targeton)

        self.pix = QPixmap()

        self.common_height = 230
        self.var_width_left = 60
        self.var_width_right = 60
        self.var_y_left = 9
        self.var_y_right = 9
        self.var_x_left = 9
        self.var_x_right = 251

        # Del or NEW menu :
        self.leftNewPanel = QLabel()
        self.leftNewPanel.setGeometry(QRect(self.var_x_left, self.var_y_left, self.var_width_left, self.common_height))
        self.leftNewPanel.setStyleSheet("""QLabel { background-color: rgb(0, 255, 0);}""")
        self.leftNewPanel.setPixmap(self.image_snapshot)
        self.leftNewPanel.setAttribute(Qt.WA_TransparentForMouseEvents)
        self.rightDelPanel = QLabel()
        self.rightDelPanel.setGeometry(QRect(self.var_x_right, self.var_y_right, self.var_width_right, self.common_height))
        self.rightDelPanel.setStyleSheet("""QLabel { background-color: rgb(255, 0, 0);} """)
        self.rightDelPanel.setPixmap(self.image_poubelle)
        self.rightDelPanel.setAttribute(Qt.WA_TransparentForMouseEvents)

        self.effect_left = QGraphicsOpacityEffect()
        self.effect_right = QGraphicsOpacityEffect()
        self.leftNewPanel.setGraphicsEffect(self.effect_left)
        self.rightDelPanel.setGraphicsEffect(self.effect_right)

        self.mainlayout.addWidget(self.leftNewPanel, Qt.AlignVCenter, Qt.AlignLeft)
        # self.mainlayout.addWidget(self.frame_targeton, Qt.AlignVCenter, Qt.AlignHCenter)
        self.mainlayout.addWidget(self.rightDelPanel, Qt.AlignVCenter, Qt.AlignRight)
        self.anim_duration = 200
        self.mousepos = 0
        self.newmousepos = 0
        self.valueTimer = 600
        self.timer_vignette = QTimer()
        self.timer_vignette.timeout.connect(self.timer_vignette_timeout)
        self.delOrNewMenu = False
        self.anim_select_running = False
        self.anim_fadein_running = False

        # animation apparition des menus supprimer ou prendre un nouveau snapshot
        self.startval = 0
        self.endval = 0.5

        self.parallelAnimFadeIn = QParallelAnimationGroup()

        self.fadeIn_panel_left = QPropertyAnimation(self.effect_left, b"opacity")
        self.fadeIn_panel_left.setDuration(self.anim_duration)
        self.fadeIn_panel_left.setEasingCurve(QEasingCurve.InCurve)

        self.fadeIn_panel_right = QPropertyAnimation(self.effect_right, b"opacity")
        self.fadeIn_panel_right.setDuration(self.anim_duration)
        self.fadeIn_panel_right.setEasingCurve(QEasingCurve.InCurve)

        self.parallelAnimFadeIn.addAnimation(self.fadeIn_panel_left)
        self.parallelAnimFadeIn.addAnimation(self.fadeIn_panel_right)
        self.parallelAnimFadeIn.finished.connect(self.set_status_fadein)

        # animation blinking target ON
        self.anim_blicking = QPropertyAnimation(self, b"")

        # animation selection un ou l'autre des menus
        self.parallelAnimSelect = QParallelAnimationGroup()
        self.anim_duration = 300  # vitesse de glissement des deux menus delete ou nouveau snapshot

        self.select_panel_left = QPropertyAnimation(self.leftNewPanel, b"geometry")
        self.select_panel_left.setDuration(self.anim_duration)
        self.select_panel_left.setEasingCurve(QEasingCurve.InCurve)

        self.select_panel_right = QPropertyAnimation(self.rightDelPanel, b"geometry")
        self.select_panel_right.setDuration(self.anim_duration)
        self.select_panel_right.setEasingCurve(QEasingCurve.InCurve)

        self.parallelAnimSelect.addAnimation(self.select_panel_left)
        self.parallelAnimSelect.addAnimation(self.select_panel_right)
        self.parallelAnimSelect.finished.connect(self.set_status_select)

        self.leftNewPanel.hide()
        self.rightDelPanel.hide()

        self.setLayout(self.mainlayout)
        self.installEventFilter(self)

    def eventFilter(self, source, event):
        if event.type() == QEvent.MouseButtonPress:
            self.isclicked = True
            self.mousepos = event.pos()
            self.newmousepos = self.mousepos
            if self.issetted:
                self.timer_vignette.start(self.valueTimer)
            else:
                self.delOrNewMenu = False
        if event.type() == QEvent.MouseMove:
            print("mouse move")
            if not self.anim_fadein_running and self.isclicked:
                if self.newmousepos.x() < 69 and self.mousepos.x() - event.pos().x() > 0:
                    self.selectMenu("left")
                elif self.newmousepos.x() > 251 and self.mousepos.x() - event.pos().x() < 0:
                    self.selectMenu("right")
                elif 69 < self.newmousepos.x() < 251:
                    self.selectMenu("middle")
            self.newmousepos = event.pos()
        if event.type() == QEvent.MouseButtonRelease:
            self.isclicked = False
            self.timer_vignette.stop()
            if not self.delOrNewMenu:  # comportement sur monoclic d'une vignette
                self.setEnabled(True)
                if not self.issetted:
                    self.parent.asking_snapshot = True
                self.issetted = True

                if self.isactive:
                    self.isactive = False
                    self.setEnabled(False)
                    self.parent.release_target = True
                    self.parent.previous_target = ""
                else:
                    self.isactive = True
                    self.blink_targeton()
                    self.parent.target_locked = True
                    self.parent.one_and_only()
                    self.parent.last_clicked_vign = self.numero

            elif self.issetted:  # comportement appui long (affichage du menu delete ou new vignette)
                self.delOrNewMenu = False
                self.newmousepos = event.pos()
                self.showMenuDelNew(False)
                if self.newmousepos.x() < 109:  # si on demande une nouvelle vignette (gauche)
                    self.unset_image()
                    self.parent.asking_snapshot = True
                    self.isactive = False
                    self.setEnabled(False)
                    self.parent.release_target = True
                elif self.newmousepos.x() > 211:  # si on supprime la vignette (droite)
                    self.issetted = False
                    self.isactive = False
                    self.parent.release_target = True
                    self.unset_image()
                else:  # Si on se place entre les deux menus (neutre)
                    self.blink_targeton()
            else:
                pass
        return super(VignetteTrack, self).eventFilter(source, event)

    def blink_targeton(self):
        self.frame_targeton.setProperty("border", "0")
        self.setStyleSheet(self.styleSheet())
        if self.frame_targeton.isHidden():
            self.frame_targeton.show()
        else:
            self.frame_targeton.hide()

        if not self.isactive:
            self.frame_targeton.show()
            self.timer_target.stop()
            self.frame_targeton.setProperty("border", "1")
            self.setStyleSheet(self.styleSheet())
        else:
            self.timer_target.start(800)

    def showMenuDelNew(self, open):
        if open:
            self.frame_targeton.show()
            self.frame_targeton.setProperty("border", "1")
            self.setStyleSheet(self.styleSheet())
            self.timer_target.stop()
            self.startval = 0
            self.endval = 0.5
            self.leftNewPanel.show()
            self.rightDelPanel.show()
        else:
            self.startval = 0.5
            self.endval = 0
            # self.parallelAnimFadeIn.finished.connect(self.leftNewPanel.hide and self.rightDelPanel.hide)

        self.fadeIn_panel_left.setStartValue(self.startval)
        self.fadeIn_panel_right.setStartValue(self.startval)
        self.fadeIn_panel_left.setEndValue(self.endval)
        self.fadeIn_panel_right.setEndValue(self.endval)
        self.parallelAnimFadeIn.start()

    def setsnapshot(self, image):
        pix = QPixmap()
        pix.loadFromData(image, "JPG")
        self.set_image_centre(pix)

    def selectMenu(self, side):
        if side == "left":
            self.var_width_left = 240
            self.var_width_right = 60
            self.var_x_right = 251
            self.select_panel_left.setStartValue(QRect(9, 9, 60, self.common_height))
            self.select_panel_right.setStartValue(QRect(251, 9, 60, self.common_height))
        elif side == "right":
            self.var_width_left = 60
            self.var_width_right = 240
            self.var_x_right = 71
            self.select_panel_right.setStartValue(QRect(251, 9, 60, self.common_height))
            self.select_panel_left.setStartValue(QRect(9, 9, 60, self.common_height))
        elif side == "middle":
            if self.previous_menu_side == "right":
                self.select_panel_right.setStartValue(QRect(71, 9, 240, self.common_height))
                self.select_panel_left.setStartValue(QRect(9, 9, 60, self.common_height))
            elif self.previous_menu_side == "left":
                self.select_panel_left.setStartValue(QRect(9, 9, 240, self.common_height))
                self.select_panel_right.setStartValue(QRect(251, 9, 60, self.common_height))
            else:
                self.var_width_left = 60
                self.var_width_right = 60
                self.var_x_right = 251

        self.select_panel_left.setEndValue(QRect(self.var_x_left, self.var_y_left, self.var_width_left, self.common_height))
        self.select_panel_right.setEndValue(QRect(self.var_x_right, self.var_y_right, self.var_width_right, self.common_height))
        self.anim_select_running = False

        if side is not self.previous_menu_side:
            self.anim_select_running = True
            self.parallelAnimSelect.start()
        else:
            pass
        self.previous_menu_side = side

    def set_image_centre(self, image):
        self.pix = image
        self.setPixmap(self.pix.scaled(315, 245, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        self.setAlignment(Qt.AlignCenter)

    def unset_image(self):
        self.pix.swap(QPixmap())
        self.setPixmap(self.pix)

    def set_status_fadein(self):
        self.anim_fadein_running = False

    def set_status_select(self):
        self.anim_select_running = False

    def timer_vignette_timeout(self):
        self.delOrNewMenu = True
        self.timer_vignette.stop()
        self.showMenuDelNew(True)

    def desactiver(self):
        self.isactive = False
        self.setEnabled(False)


class VignetteMemo(QLabel):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setFixedSize(115, 90)
        self.setAutoFillBackground(True)
        self.numero = 0
        self.pix = QPixmap()
        self.mainlayout = QHBoxLayout()
        self.setLayout(self.mainlayout)

    def set_image_centre(self, image):
        self.pix = image
        print("size img :", self.pix.size())
        self.setPixmap(self.pix.scaled(115, 90, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        self.setAlignment(Qt.AlignCenter)

    def unset_image(self):
        self.pix.swap(QPixmap())
        self.setPixmap(self.pix)


# Mapping d'une emission
class MapEmission(QLabel):
    def __init__(self, parent=None, *__args):
        super().__init__(*__args)
        self.width_draw = 700
        self.height_draw = 400
        self.setFixedSize(self.width_draw + 1, self.height_draw + 1)
        self.tablette_width = 100
        self.tablette_height = 50
        self.tablette_ori_x = self.width_draw / 2 - self.tablette_width / 2
        self.tablette_ori_y = self.height_draw / 2
        self.nb_machines_max = 5
        self.longueur_trait_boitier = 100
        self.width_boitier = 60
        self.height_boitier = 40
        self.width_machine = 80
        self.height_machine = 80
        self.ecart_machines = (self.longueur_trait_boitier * 5 + self.tablette_width) / (self.nb_machines_max - 1)

    def paintEvent(self, event):
        painter = QPainter(self)
        pen = QPen(Qt.black, 2, Qt.SolidLine)
        painter.setPen(pen)
        # On dessine la zone de dessin par un cadre
        painter.drawRect(0, 0, self.width_draw, self.height_draw)
        # On dessine la tablette le Maestro donc nous même par ce que c'est invariant elle sera toujours la :
        # position coin superieur(x,y)  + (width, height) = rect(x,y,width,height)
        painter.drawRect(self.tablette_ori_x, self.tablette_ori_y, self.tablette_width, self.tablette_height)

        pen.setStyle(Qt.DashDotDotLine)
        painter.setPen(pen)
        # on dessine la ligne commande tilt pan
        painter.drawLine(self.tablette_ori_x + self.tablette_width, self.tablette_ori_y + self.tablette_height / 2, self.tablette_ori_x + self.tablette_width + self.longueur_trait_boitier,
                         self.tablette_ori_y + self.tablette_height / 2)
        # on dessine la ligne commande zoom point
        painter.drawLine(self.tablette_ori_x, self.tablette_ori_y + self.tablette_height / 2, self.tablette_ori_x - self.longueur_trait_boitier, self.tablette_ori_y + self.tablette_height / 2)
        # on dessine la ligne commande track lift
        painter.drawLine(self.tablette_ori_x + self.tablette_width / 2, self.tablette_ori_y + self.tablette_height, self.tablette_ori_x + self.tablette_width / 2,
                         self.tablette_ori_y + self.tablette_height + self.longueur_trait_boitier)
        pen.setStyle(Qt.SolidLine)
        painter.setPen(pen)
        # maintenant leur carrés respectifs
        # tilt pan
        painter.drawRect(self.tablette_ori_x + self.tablette_width + self.longueur_trait_boitier, self.tablette_ori_y + self.tablette_height / 2 - self.height_boitier / 2, self.width_boitier,
                         self.height_boitier)
        # zoom point
        painter.drawRect(self.tablette_ori_x - self.longueur_trait_boitier, self.tablette_ori_y + self.tablette_height / 2 - self.height_boitier / 2, -self.width_boitier, self.height_boitier)
        # track lift
        painter.drawRect(self.tablette_ori_x + self.tablette_width / 2 - self.width_boitier / 2, self.tablette_ori_y + self.tablette_height + self.longueur_trait_boitier, self.width_boitier,
                         self.height_boitier)

        pen.setStyle(Qt.DashDotDotLine)
        painter.setPen(pen)
        # Lignes machines
        # verticale
        painter.drawLine(self.tablette_ori_x + self.tablette_width / 2, self.tablette_ori_y, self.tablette_ori_x + self.tablette_width / 2, self.tablette_ori_y - self.longueur_trait_boitier / 2)
        # Horizontale
        painter.drawLine(self.tablette_ori_x - self.longueur_trait_boitier * 2.5, self.tablette_ori_y - self.longueur_trait_boitier / 2,
                         self.tablette_ori_x + self.longueur_trait_boitier * 2.5 + self.tablette_width, self.tablette_ori_y - self.longueur_trait_boitier / 2)
        # 5 fois verticale
        for i in range(0, self.nb_machines_max):
            painter.drawLine(self.tablette_ori_x - self.longueur_trait_boitier * 2.5 + i * self.ecart_machines, self.tablette_ori_y - self.longueur_trait_boitier / 2,
                             self.tablette_ori_x - self.longueur_trait_boitier * 2.5 + i * self.ecart_machines, self.tablette_ori_y - self.longueur_trait_boitier)
        # On dessine les carrés machines
        pen.setStyle(Qt.SolidLine)
        painter.setPen(pen)
        for i in range(0, self.nb_machines_max):
            painter.drawRect(self.tablette_ori_x - self.longueur_trait_boitier * 2.5 + i * self.ecart_machines - self.width_machine / 2,
                             self.tablette_ori_y - self.longueur_trait_boitier - self.height_machine, self.width_machine, self.height_machine)


class ScrollIndicator(QLabel):
    def __init__(self, parent=None):
        super(ScrollIndicator, self).__init__(parent)
        self.setFixedSize(QSize(50, 390))
        # self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setStyleSheet("""ScrollIndicator {background:transparent;}""")
        self.image_chevron_left = QPixmap('Icones/chevron_gauche.png').scaled(50, 50, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.image_chevron_right = QPixmap('Icones/chevron_droite.png').scaled(50, 50, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        # self.setAutoFillBackground(True)

    def change_pixmap(self, sens):
        if sens == "droite":
            self.setPixmap(self.image_chevron_right)
        elif sens == "gauche":
            self.setPixmap(self.image_chevron_left)
        else:
            pass


"""===============================================================================================================TABLEAU ET ONGLET===|"""


# les cases tableaux de parametres (subclass un Qtablewidgetitem permet d'aligner le texte au centre) Se retrouve dans l'interface settings ADMIN
class CaseTableau(QTableWidgetItem):
    def __init__(self, text):
        super().__init__()
        self.setTextAlignment(Qt.AlignCenter)
        self.setText(text)
        self.setFlags(Qt.ItemIsEnabled)


# Widget onglet : se retrouve dans les settings utilisateurs
class StyledTabwidget(QTabWidget):
    def __init__(self, parent=None, *__args):
        super().__init__(*__args)
        self.tab_stylesheet = """
                        StyledTabwidget::pane {
                                border-top: 1px solid black;  
                                position: absolute;
                                top: 0.5em;                              
                                background: white ;
                                }
                        StyledTabwidget::tab-bar {                            
                                alignment: center ;
                                }
                        QTabBar::Tab:selected { 
                                border: 1px solid black; 
                                border-radius: 3px;
                                width: 200px;   
                                height: 40px;                      
                                background: #C58E85 ;
                                }
                        QTabBar::Tab:!selected { 
                                border: 1px solid black;
                                border-radius: 3px;                                
                                width: 200px;   
                                height: 40px;                             
                                background: #E6CCC4 ;
                                }
                        QTabBar::tear { 

                                background: red ;
                                }
                            """
        self.setStyleSheet(self.tab_stylesheet)


"""===============================================================================================================DIALOG===============|"""


class SettingsDialog(QWidget):
    def __init__(self, parent):
        super(SettingsDialog, self).__init__(parent)
        self.parent = parent
        self.reponse = ""
        self.reponse_emi = ""
        self.loader = self.parent.datManager
        self.cadreur_selected = ""
        self.emission_selected = ""
        self.widgetback = QWidget(self)
        self.widgetback.setFixedSize(self.parent.size())

        self.widgetback.resize(self.parent.size())
        self.widgetback.setStyleSheet("""QWidget { background: #E1DDD7;
                                                         border: 2px solid;
                                                         border-radius: 10px;}""")
        layout = QVBoxLayout()
        layout.addWidget(self.widgetback)

        self.setFixedSize(self.parent.size())
        self.resize(self.parent.size())
        self.layout_windowsbutton = QHBoxLayout()

        # ----------------------------------------------- main button cadreurs
        self.btn_recall = SettingsMenuButton()
        self.btn_recall.setText("Recall")
        self.btn_recall.setCheckable(False)
        self.btn_recall.setEnabled(False)

        self.btn_save = SettingsMenuButton()
        self.btn_save.setText("Save")
        self.btn_save.setCheckable(False)
        self.btn_save.setEnabled(False)

        self.new_one = SettingsMenuButton()
        self.new_one.setText("Ajouter\nCadreur")
        self.new_one.clicked.connect(self.add)

        self.del_one = SettingsMenuButton()
        self.del_one.setText("Supprimer\nCadreur")
        self.del_one.clicked.connect(self.delete)

        self.btn_cancel = SettingsMenuButton()
        self.btn_cancel.setText("Fermer")
        self.btn_cancel.setCheckable(False)

        self.layout_windowsbutton.addWidget(self.new_one)
        self.layout_windowsbutton.addWidget(self.del_one)
        self.layout_windowsbutton.addWidget(self.btn_save)
        self.layout_windowsbutton.addWidget(self.btn_recall)
        self.layout_windowsbutton.addWidget(self.btn_cancel)

        self.btn_cancel.clicked.connect(self.cancel)
        self.btn_recall.clicked.connect(self.recall)
        self.btn_save.clicked.connect(self.save)

        self.main_config_layout = QVBoxLayout()
        self.keyboard = KeyboardWidget(self)
        self.keyboard.hide()

        self.anim_keyboard = QPropertyAnimation(self.keyboard, b'geometry')
        self.anim_keyboard.setEasingCurve(QEasingCurve.OutCirc)
        self.anim_keyboard.setDuration(1000)
        self.anim_keyboard.setStartValue(QRect(0, 800, self.keyboard.width(), self.keyboard.height()))
        self.anim_keyboard.setEndValue(QRect(0, 305, self.keyboard.width(), self.keyboard.height()))
        # self.main_config_layout.setContentsMargins(0,0,0,0)
        self.cadreur_layout = QGridLayout()
        self.emissions_layout = QHBoxLayout()
        self.font_layout = QGridLayout()

        self.conteneur = StyledTabwidget(self)
        self.onglet_cadreur = QWidget()
        self.onglet_emissions = QWidget()
        self.onglet_font = QWidget()

        self.conteneur.addTab(self.onglet_cadreur, "Cadreurs")
        self.conteneur.addTab(self.onglet_emissions, "Emission")
        self.conteneur.currentChanged.connect(self.switch_table)

        self.onglet_cadreur.layout = self.cadreur_layout
        self.onglet_emissions.layout = self.emissions_layout
        self.onglet_font.layout = self.font_layout

        self.layout_btn_emission = QGridLayout()
        self.layout_btn_emission.setSpacing(5)
        self.mapping = MapEmission()
        self.emissions_layout.setSpacing(0)
        self.emissions_layout.addLayout(self.layout_btn_emission)
        self.emissions_layout.addWidget(self.mapping)
        self.main_config_layout.addLayout(self.layout_windowsbutton, 3)
        self.main_config_layout.addWidget(self.conteneur, 2)
        self.parent.layout().addWidget(self.keyboard)

        self.onglet_cadreur.setLayout(self.onglet_cadreur.layout)
        self.onglet_emissions.setLayout(self.onglet_emissions.layout)
        self.onglet_font.setLayout(self.onglet_font.layout)

        # Onglet cadreurs---------------------------------------------------------
        self.btn_group_cadreurs = QButtonGroup()
        self.list_opv = self.loader.charger("OPV")

        self.index_col = 0
        self.index_ligne = 0
        self.btnparligne = 5

        if self.list_opv:
            for people in self.list_opv:
                button = CadreurButton()
                button.setText(people)
                button.clicked.connect(self.witchcadreur)
                self.btn_group_cadreurs.addButton(button)
                self.cadreur_layout.addWidget(button, self.index_ligne, self.index_col)
                self.index_col = (self.index_col + 1) if self.index_col < self.btnparligne else 0
                self.index_ligne = (self.index_ligne + 1) if self.index_col == 0 else self.index_ligne
        else:
            self.list_opv = []
        # Onglet Emission-------------------------------------------------------------
        self.btn_group_emission = QButtonGroup()
        self.list_emission = self.loader.charger("Emission")

        self.index_col_emi = 0
        self.index_ligne_emi = 0
        self.btnparligne_emi = 1

        if self.list_emission:
            for emission in self.list_emission:
                button = CadreurButton()
                button.setText(emission)
                button.setFixedWidth(50)
                button.clicked.connect(self.witchemission)
                self.btn_group_emission.addButton(button)
                self.layout_btn_emission.addWidget(button, self.index_ligne_emi, self.index_col_emi)
                self.index_col_emi = (self.index_col_emi + 1) if self.index_col_emi < self.btnparligne_emi else 0
                self.index_ligne_emi = (self.index_ligne_emi + 1) if self.index_col_emi == 0 else self.index_ligne_emi
        else:
            self.list_emission = []

        # self.font_layout.addWidget(self.btn_erase)
        """for fonts in QFontDatabase().families(QFontDatabase.Latin):
            if self.previousfont != fonts:
                self.label = QLabel()
                self.label.setStyleSheet("QLabel { color: black;}")
                police = QFont(fonts, 10, 1)
                self.label.setFont(police)
                self.label.setText(fonts)
                self.font_layout.addWidget(self.label, self.index_ligne, self.index_col)
                self.index_col = (self.index_col + 1) if self.index_col < 10 else 0
                self.index_ligne = (self.index_ligne + 1) if self.index_col == 0 else self.index_ligne
            else:
                pass
            self.previousfont += 1
            if self.previousfont > 20:
                break"""

        self.setLayout(self.main_config_layout)
        self.setStyleSheet("SettingsDialog { background: rgba(255,255,255,0);}")
        # self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint | Qt.X11BypassWindowManagerHint | Qt.Tool)
        self.move(0, 0)

    def switch_table(self):
        if self.conteneur.currentIndex() == 0:
            self.new_one.setText("Ajouter\nCadreur")
            self.del_one.setText("Supprimer\nCadreur")
            if self.btn_group_cadreurs.checkedButton():
                self.btn_recall.setText("recall\n" + self.btn_group_cadreurs.checkedButton().text())
                self.btn_save.setText("save\n" + self.btn_group_cadreurs.checkedButton().text())
            else:
                self.btn_recall.setText("recall")
                self.btn_save.setText("save")
                self.btn_recall.setEnabled(False)
                self.btn_save.setEnabled(False)
        elif self.conteneur.currentIndex() == 1:
            self.new_one.setText("Ajouter\nEmission")
            self.del_one.setText("Supprimer\nEmission")
            if self.btn_group_emission.checkedButton():
                self.btn_recall.setText("recall\n" + self.btn_group_emission.checkedButton().text())
                self.btn_save.setText("save\n" + self.btn_group_emission.checkedButton().text())
            else:
                self.btn_recall.setText("recall")
                self.btn_save.setText("save")
                self.btn_recall.setEnabled(False)
                self.btn_save.setEnabled(False)
        else:
            print("autre onglet")

    def witchcadreur(self):
        self.cadreur_selected = self.sender().text()
        self.btn_recall.setText("recall\n" + self.cadreur_selected + " param")
        self.btn_save.setText("save\n" + self.cadreur_selected + " param")
        self.btn_recall.setEnabled(True)
        self.btn_save.setEnabled(True)

    def witchemission(self):
        self.emission_selected = self.sender().text()
        self.btn_recall.setText("recall\n" + self.emission_selected + " param")
        self.btn_save.setText("save\n" + self.emission_selected + " param")
        self.btn_recall.setEnabled(True)
        self.btn_save.setEnabled(True)

    def add(self):
        # self.keyboard.move(0, 800)
        self.anim_keyboard.start()
        self.keyboard.show()
        self.keyboard.raise_()
        self.keyboard.move(0, 305)
        if self.conteneur.currentIndex() == 0:  # Si on est à la PREMIERE page des settings : les cadreurs
            if self.keyboard.validate:
                button = CadreurButton()
                button.setText(self.keyboard.value) if self.keyboard.value != "" else button.setText("unknown")
                button.clicked.connect(self.witchcadreur)
                self.btn_group_cadreurs.addButton(button)
                self.cadreur_layout.addWidget(button, self.index_ligne, self.index_col)
                self.index_col = (self.index_col + 1) if self.index_col < self.btnparligne else 0
                self.index_ligne = (self.index_ligne + 1) if self.index_col == 0 else self.index_ligne
                self.list_opv.append(self.keyboard.value)
                self.loader.enregistrer(self.list_opv, 'OPV')
                self.keyboard.validate = False
                self.keyboard.hide()
            elif self.keyboard.cancel:
                self.keyboard.hide()
                self.keyboard.cancel = False
        elif self.conteneur.currentIndex() == 1:  # Si on est à la DEUXIEME page des settings : les cadreurs
            if self.keyboard.validate:
                button = CadreurButton()
                button.setText(self.keyboard.value) if self.keyboard.value != "" else button.setText("unknown")
                button.clicked.connect(self.witchemission)
                self.btn_group_emission.addButton(button)
                self.layout_btn_emission.addWidget(button, self.index_ligne_emi, self.index_col_emi)
                self.index_col_emi = (self.index_col_emi + 1) if self.index_col_emi < self.btnparligne_emi else 0
                self.index_ligne_emi = (self.index_ligne_emi + 1) if self.index_col_emi == 0 else self.index_ligne_emi
                self.list_emission.append(self.keyboard.value)
                self.loader.enregistrer(self.list_emission, 'Emission')
                self.keyboard.validate = False
                self.keyboard.hide()
            elif self.keyboard.cancel:
                self.keyboard.hide()
                self.keyboard.cancel = False
        else:
            pass

    def delete(self):
        if self.conteneur.currentIndex() == 0:
            if self.cadreur_selected != "":
                for i in range(len(self.list_opv)):
                    if self.cadreur_layout.itemAt(i).widget().text() == self.cadreur_selected:
                        widget_c = self.cadreur_layout.itemAt(i).widget()
                        self.cadreur_layout.removeWidget(widget_c)
                        widget_c.deleteLater()
                        break
                del self.list_opv[self.list_opv.index(self.cadreur_selected)]
                self.loader.enregistrer(self.list_opv, 'OPV')
                self.cadreur_selected = ''
                self.index_col = (self.index_col - 1) if self.index_col != 0 else 0
                self.index_ligne = (self.index_ligne - 1) if self.index_col > self.btnparligne else self.index_ligne
            else:
                print("selectionnez un cadreur a supprimer")
        elif self.conteneur.currentIndex() == 1:
            if self.emission_selected != "":
                for i in range(0, self.layout_btn_emission.count()):
                    if self.layout_btn_emission.itemAt(i).widget().text() == self.emission_selected:
                        widget_e = self.layout_btn_emission.itemAt(i).widget()
                        self.layout_btn_emission.removeWidget(widget_e)
                        widget_e.deleteLater()
                        break
                        # widget_e = None
                del self.list_emission[self.list_emission.index(self.emission_selected)]
                self.loader.enregistrer(self.list_emission, 'Emission')
                self.emission_selected = ''
                self.index_col_emi = (self.index_col_emi - 1) if self.index_col_emi != 0 else 0
                self.index_ligne_emi = (self.index_ligne_emi - 1) if self.index_col_emi > self.btnparligne_emi else self.index_ligne_emi
            else:
                print("selectionnez une emission a supprimer")
        else:
            pass
        self.btn_recall.setText("recall")
        self.btn_save.setText("save")
        self.btn_recall.setEnabled(False)
        self.btn_save.setEnabled(False)

    def cancel(self):
        self.reponse = ('', '')
        self.reponse_emi = ('', '')
        self.close()

    def recall(self):
        if self.conteneur.currentIndex() == 0:
            if self.cadreur_selected != "":
                self.reponse = (self.cadreur_selected, "recall")
                self.close()
            else:
                pass
        elif self.conteneur.currentIndex() == 1:
            if self.emission_selected != "":
                self.reponse_emi = (self.emission_selected, "recall")
                self.close()
            else:
                pass

    def save(self):
        if self.conteneur.currentIndex() == 0:
            if self.cadreur_selected != "":
                self.reponse = (self.cadreur_selected, "save")
                self.close()
            else:
                pass
        if self.conteneur.currentIndex() == 1:
            if self.emission_selected != "":
                self.reponse_emi = (self.emission_selected, "save")
                self.close()
            else:
                pass


# Le pavé numérique : Permet de changer les valeurs dans les settings ADMIN
class PaveNumerique(QDialog):
    def __init__(self, actualvalue):
        super(PaveNumerique, self).__init__()
        self.frame_pave = QFrame(self)
        self.frame_pave.setStyleSheet("""QFrame {
                                          border: 3px solid rgb(0,0,200);
                                          background: rgba(255, 255, 255, 100);
                                          border-radius: 5px;}"""
                                      )
        self.frame_pave.setFixedSize(250, 300)
        self.main_pave_layout = QVBoxLayout(self.frame_pave)
        self.label_layout = QHBoxLayout()
        self.label_layout.setContentsMargins(10, 0, 6, 0)
        self.pave_layout = QGridLayout()
        self.value = 0
        self.setFixedHeight(300)
        self.setFixedWidth(250)
        self.actualvalue = str(actualvalue)
        self.linepave = QLabel(self.actualvalue)
        self.linepave.setFixedHeight(20)
        self.linepave.setFixedWidth(180)
        self.setWindowTitle("Pavé numérique")
        self.setWindowFlags(Qt.X11BypassWindowManagerHint | Qt.CustomizeWindowHint | Qt.WindowStaysOnTopHint)
        self.but_ok = ButtonPave("OK", self.okay)
        self.but_virgule = ButtonPave(".", self.numbers)
        self.but_del = ButtonPave("DEL", self.delete)
        self.but_del.setFixedWidth(65)
        self.but_del.setFixedHeight(50)

        self.label_layout.addWidget(self.linepave)
        self.label_layout.addWidget(self.but_del)

        z = 9
        for y in range(1, 4):
            for i in range(3, 0, -1):
                button = ButtonPave(str(z), self.numbers)
                self.pave_layout.addWidget(button, y, i)
                z -= 1

        self.pave_layout.addWidget(self.but_virgule, 4, 1)
        self.pave_layout.addWidget(ButtonPave("0", self.numbers), 4, 2)
        self.pave_layout.addWidget(self.but_ok, 4, 3)

        self.main_pave_layout.addLayout(self.label_layout, Qt.AlignCenter)
        self.main_pave_layout.addLayout(self.pave_layout)

        self.setLayout(self.main_pave_layout)

        self.exec_()

    def delete(self):
        text = self.linepave.text()
        text = text[:-1]
        self.linepave.setText(text)

    def okay(self):
        if self.linepave.text().isdigit():
            self.value = int(self.linepave.text())
        elif self.linepave.text() == '':
            self.value = 0
        else:
            self.value = float(self.linepave.text())
        self.close()

    def numbers(self):
        text = self.sender().text()
        line = self.linepave.text()
        line += text
        self.linepave.setText(line)


# Fenetre pour fixer les limites
class LimitDialog(QDialog):
    def __init__(self, haut, bas, gauche, droite):
        super(LimitDialog, self).__init__()
        self.widgetbg = QWidget(self)
        self.widgetbg.setFixedSize(350, 300)
        self.widgetbg.setStyleSheet("""QWidget { background: rgba(255,255,240,255);
                                                 border: 2px solid;
                                                 border-radius: 10px;}""")
        layout = QVBoxLayout()
        layout.addWidget(self.widgetbg)
        self.main_limit_layout = QGridLayout()
        self.setFixedHeight(300)
        self.setFixedWidth(350)
        self.but_settop = ButtonLim("HAUT")
        self.but_setbot = ButtonLim("BAS")
        self.but_setleft = ButtonLim("GAUCHE")
        self.but_setright = ButtonLim("DROITE")
        self.but_save = ButtonLim("VALIDER")
        self.but_save.clicked.connect(self.save)
        self.but_cancel = ButtonLim("ANNULER")
        self.but_cancel.clicked.connect(self.cancel)

        self.main_limit_layout.addWidget(self.but_settop, 0, 1)
        self.main_limit_layout.addWidget(self.but_setbot, 2, 1)
        self.main_limit_layout.addWidget(self.but_setleft, 1, 0)
        self.main_limit_layout.addWidget(self.but_setright, 1, 2)
        self.main_limit_layout.addWidget(self.but_save, 2, 0)
        self.main_limit_layout.addWidget(self.but_cancel, 2, 2)
        self.setLayout(self.main_limit_layout)
        self.sendokay = False
        self.sendcancel = False
        self.but_settop.setChecked(haut)
        self.but_setbot.setChecked(bas)
        self.but_setleft.setChecked(gauche)
        self.but_setright.setChecked(droite)
        self.setStyleSheet("LimitDialog { background: rgba(255,255,255,0);}")
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint | Qt.X11BypassWindowManagerHint)
        self.show()

    def cancel(self):
        self.sendcancel = True
        self.close()

    def save(self):
        self.sendokay = True
        self.close()


# Fenetre Pop up pour indiquer que trop de commande ou machines du même type sont connectées
class ErrorDialog(QDialog):
    def __init__(self, origine, cmd):
        super(ErrorDialog, self).__init__()
        self.widgetbg = QWidget(self)
        self.widgetbg.setFixedSize(500, 300)
        self.widgetbg.setStyleSheet("""QWidget { background: rgba(255,255,240,255);
                                                         border: 2px solid;
                                                         border-radius: 10px;}""")
        self.setFixedHeight(300)
        self.setFixedWidth(500)

        self.error_message_cmd = "Vous venez de connecter le " + cmd + "\nUne commande du même type est déjà connectée.\nDéconnectez la commande que vous ne voulez pas utiliser\npuis cliquez sur 'Prêt'"
        self.error_message_machine = ''
        self.flag_choose_machine = False

        layout = QVBoxLayout()
        layout.addWidget(self.widgetbg)
        self.main_error_layout = QVBoxLayout()
        self.window_icon_layout = QHBoxLayout()
        self.button_layout = QHBoxLayout()

        self.but_okay = MotorButton()
        self.but_okay.setText("Prêt")
        self.but_okay.setCheckable(False)
        self.but_okay.clicked.connect(self.okay)

        self.image_icon = QPixmap('Icones/warning.png')
        self.label_icon = QLabel()
        self.label_icon.setPixmap(self.image_icon)

        self.label_title = QLabel('Doublon de commande')
        self.label_title.setFont(QFont('Serif', 20))
        self.label_message = QLabel()
        self.label_message.setFont(QFont('Serif', 12))

        if origine == 'cmd':
            self.label_message.setText(self.error_message_cmd)
        elif origine == 'machine':
            self.label_message.setText(self.error_message_machine)
        else:
            pass
        self.main_error_layout.addLayout(self.window_icon_layout)

        self.window_icon_layout.addWidget(self.label_icon, Qt.AlignLeft, Qt.AlignLeft)
        self.window_icon_layout.addWidget(self.label_title, Qt.AlignLeft, Qt.AlignLeft)
        self.window_icon_layout.addWidget(QLabel(), Qt.AlignRight, Qt.AlignRight)  # spacer
        self.main_error_layout.addWidget(self.label_message)
        self.main_error_layout.addLayout(self.button_layout)
        self.button_layout.addWidget(self.but_okay)

        self.setLayout(self.main_error_layout)
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint | Qt.X11BypassWindowManagerHint)

    def okay(self):
        self.flag_choose_machine = True
        self.close()
