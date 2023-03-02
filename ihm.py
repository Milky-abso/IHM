import appmap

from PyQt5.QtCore import Qt, QCoreApplication, QTimer, QRect, QPoint, pyqtSignal, pyqtSlot, QObject, QSize
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QHBoxLayout, QLabel, \
    QFrame, QGridLayout, QMessageBox, QFormLayout, QButtonGroup, QStackedWidget, QMainWindow, QTabWidget, \
    QTableWidget, QSizePolicy
from PyQt5.QtGui import QIcon, QPixmap, QFont, QCursor
from Maestro import thread_ID_number

import widgetbox as wb
import sys
import time
import Maestro
import os
import pickle
import logging
import psutil
import ctypes
import sys

libc = ctypes.cdll.LoadLibrary('libc.so.6')
rasp_config = False  # True = config raspberry, False = config ordinateur)

if rasp_config:
    os.chdir('/home/pi/Tablette_V6')
    os.system("ethtool --set-eee eth0 eee off")

"""CLASSES UTILITAIRES====================================================================================================================== UTILS"""


# je charge les images/logos ici (incomplet)
class Pictures:
    def __init__(self):
        self.image_V4 = QPixmap('Icones/V4.png').scaled(110, 115, Qt.KeepAspectRatio)
        self.image_V5 = QPixmap('Icones/V5.png').scaled(100, 80, Qt.KeepAspectRatio)
        self.image_V6 = QPixmap('Icones/v6_cam.png')
        self.image_joystick = QPixmap('Icones/joy_tr_tete.png')
        self.image_joystick_cross = QPixmap('Icones/joy_tr_cross.png')
        self.image_panbar = QPixmap('Icones/panbar.png')
        self.image_zoompoint = QPixmap('Icones/cmd_ZP.png')
        self.image_zoompoint_cross = QPixmap('Icones/cmd_ZP_cross.png')
        self.image_lifttrack = QPixmap('Icones/tracklift.png')
        self.image_lifttrack_cross = QPixmap('Icones/tracklift_cross.png')
        self.image_Furio_FX = QPixmap('Icones/furioFX.png')
        self.image_Furio_MO = QPixmap('Icones/furioMO.png')

        self.image_poigneezoom_only = QPixmap('Icones/Pzoom_only.png')
        self.image_poigneepoint_only = QPixmap('Icones/Ppoint_only.png')
        self.image_poignees = QPixmap('Icones/poignees.png')
        self.image_ether_off = QPixmap('Icones/ethernet_off.png')

        self.image_status_butee_none = QPixmap('Icones/butees_furio_none.png')
        self.image_status_butee_left = QPixmap('Icones/butees_furio_left.png')
        self.image_status_butee_right = QPixmap('Icones/butees_furio_right.png')
        self.image_status_butee_top = QPixmap('Icones/butees_furio_top.png')
        self.image_status_butee_bottom = QPixmap('Icones/butees_furio_bottom.png')
        self.image_status_butee_top_left = QPixmap('Icones/butees_furio_top_left.png')
        self.image_status_butee_top_right = QPixmap('Icones/butees_furio_top_right.png')
        self.image_status_butee_bottom_left = QPixmap('Icones/butees_furio_bottom_left.png')
        self.image_status_butee_bottom_right = QPixmap('Icones/butees_furio_bottom_right.png')

        self.V4_icon = QIcon(self.image_V4)
        self.V5_icon = QIcon(self.image_V5)
        self.V6_icon = QIcon(self.image_V6)

        self.FurioFX_icon = QIcon(self.image_Furio_FX)
        self.FurioMO_icon = QIcon(self.image_Furio_MO)

        self.eth_off_icon = QIcon(self.image_ether_off)

        self.pixmap = QPixmap()
        self.number = ''
        self.rect = ''

    def add_number(self, num, vers):
        if vers == 'V6':
            self.pixmap = self.image_V6.copy()
        if vers == 'eth':
            self.pixmap = self.image_ether_off.copy()
        self.number = num
        self.rect = QRect(0, 0, self.pixmap.width(), self.pixmap.height())

        return QIcon(self.pixmap)


# charge et enregistre, les parametres du logiciel dans un fichier
class DataManager:
    def __init__(self):
        self.dictionnary = pickle.load(open('dictionnaire.p', 'rb'))

    def enregistrer(self, var, name):
        self.dictionnary[name] = var
        pickle.dump(self.dictionnary, open('dictionnaire.p', 'wb'))

    def charger(self, name):
        self.dictionnary = pickle.load(open('dictionnaire.p', 'rb'))
        return self.dictionnary.get(name, False)

    def exploreData(self, name):
        print("dictionnary: \n" + name, self.dictionnary[name])

    def supprimer(self, name):
        print("dictionnaire", self.dictionnary)
        self.dictionnary.pop(name)


""" CLASSE FENETRES et objet QT ========================================================================================================== FENETRES"""


# la fenetre principale qui contient les trois autres
class SwitcherWindows(QMainWindow):
    def __init__(self, parent=None):
        super(SwitcherWindows, self).__init__(parent)
        self.setStyleSheet("""SwitcherWindows {
                           background-color:qlineargradient(spread:reflect, x1:0, y1:0, x2:0.5, y2:0.5, stop:0 rgba(255,255,240,255), stop:1 rgba(255,255,240,255)
                            )};""")
        self.witch_menu = True
        self.switch_superviz = True
        self.gosuper = False
        self.gotargeting = False
        self.newPos = QPoint(0, 0)
        self.central_widget = QStackedWidget()
        self.central_widget.showFullScreen()
        self.setCentralWidget(self.central_widget)
        self.start_screen = MainWindow(self)
        self.second_screen = SettingWindow(self)
        self.targeting_screen = TrackingWindows(self)

        self.central_widget.addWidget(self.start_screen)
        self.central_widget.addWidget(self.targeting_screen)
        self.central_widget.addWidget(self.second_screen)

        self.monitor_hz = ""
        self.central_widget.setCurrentWidget(self.start_screen)
        self.menu = wb.SideMenu()
        self.central_widget.addWidget(self.menu)
        self.menu.btn_switch.clicked.connect(self.set_second)
        self.menu.btn_superviz.clicked.connect(self.set_superviz)
        self.menu.raise_()
        self.setAutoFillBackground(False)
        self.menu.show()

    def set_second(self):
        if self.witch_menu:
            self.central_widget.setCurrentWidget(self.targeting_screen)
            self.gotargeting = True
            self.witch_menu = False
            self.menu.btn_switch.setText("user space")
            self.menu.btn_switch.setIcon(self.menu.user_icon)
            self.switch_superviz = True
            self.menu.btn_superviz.setText("superviz")
            self.menu.btn_superviz.setIcon(self.menu.superviz_icon)
        else:
            self.gotargeting = False
            self.central_widget.setCurrentWidget(self.start_screen)
            self.witch_menu = True
            self.menu.btn_switch.setText("Targeting")
            self.menu.btn_switch.setIcon(self.menu.target_icon)
            self.switch_superviz = True
            self.menu.btn_superviz.setText("superviz")
            self.menu.btn_superviz.setIcon(self.menu.superviz_icon)
        self.menu.hide()
        self.menu.show()
        self.menu.raise_()
        self.menu.menu_isopen = False
        self.menu.setGeometry(QRect(-300, 0, 314 + 12, self.menu.y_size))
        self.menu.animationlaunched = False

    def set_superviz(self):
        # self.menu.undoanimation(0)
        if self.switch_superviz:
            self.central_widget.setCurrentWidget(self.second_screen)
            self.gosuper = True
            self.switch_superviz = False
            self.gotargeting = False
            self.menu.btn_superviz.setText("user space")
            self.menu.btn_superviz.setIcon(self.menu.user_icon)
            self.menu.btn_switch.setText("Targeting")
            self.menu.btn_switch.setIcon(self.menu.target_icon)

        else:
            self.central_widget.setCurrentWidget(self.start_screen)
            self.switch_superviz = True
            self.witch_menu = True
            self.gosuper = False
            self.gotargeting = False
            self.menu.btn_switch.setText("Tracking")
            self.menu.btn_switch.setIcon(self.menu.target_icon)
            self.menu.btn_superviz.setText("superviz")
            self.menu.btn_superviz.setIcon(self.menu.superviz_icon)

        self.menu.hide()
        self.menu.show()
        self.menu.raise_()
        self.menu.menu_isopen = False
        self.menu.setGeometry(QRect(-300, 0, 314 + 12, self.menu.y_size))
        self.menu.animationlaunched = False


# la fenetre de tracking
class TrackingWindows(QWidget):
    def __init__(self, parent):
        super(TrackingWindows, self).__init__(parent)
        self.parent = parent
        self.main_traking_layout = QVBoxLayout()

        self.title_vignette_layout = QHBoxLayout()
        self.label_title_track = QLabel(" Targeting")
        self.label_title_track.setFont(QFont('Arial', 30, 100))

        self.image_user = QPixmap('Icones/user.png')
        self.user_icon = QIcon(self.image_user)

        self.btn_back_userspace = wb.QPushButton()
        self.btn_back_userspace.setText("Back to\nUser Space")
        self.btn_back_userspace.setCheckable(False)
        self.btn_back_userspace.setStyleSheet("""
                        QPushButton {
                            border: 1px solid;
                            min-width: 200px;
                            max-width: 200px;
                            min-height: 40px;
                            max-height: 40px;
                            border-radius: 5px;
                            background-color: #D3D0CB;
                            color: black;
                        }
                        QPushButton:pressed { background-color: green }""")
        self.btn_back_userspace.setIcon(self.user_icon)
        self.btn_back_userspace.setIconSize(QSize(40, 40))
        self.btn_back_userspace.setFlat(True)
        self.btn_back_userspace.clicked.connect(self.back_userspace)

        self.title_vignette_layout.addWidget(self.label_title_track, Qt.AlignCenter)
        self.title_vignette_layout.addWidget(self.btn_back_userspace, Qt.AlignLeft)

        self.layout_vignette = QGridLayout()
        self.main_traking_layout.setContentsMargins(0, 0, 0, 50)  # _ , _, _ , bottom
        self.layout_vignette.setSpacing(20)

        self.listvignette = []
        self.previous_target = ""
        self.child = None
        self.asking_snapshot = False
        self.target_locked = False
        self.release_target = False
        self.last_clicked_vign = 12
        u = 0
        y = 0
        for idx, vignette in enumerate(list(range(7))):
            vign = wb.VignetteTrack(self)
            self.layout_vignette.addWidget(vign, y, u, 1, 1)
            self.listvignette.append(vign)
            vign.numero = idx
            if u == 2:
                u = 0
                y = 1
            else:
                u += 1

        self.main_traking_layout.addLayout(self.title_vignette_layout, Qt.AlignCenter)
        self.main_traking_layout.addLayout(self.layout_vignette, Qt.AlignJustify)

        self.setLayout(self.main_traking_layout)

    def get_vignette_number(self):
        return self.last_clicked_vign

    def one_and_only(self):
        temp_list = []
        for vign in self.listvignette:
            if vign.isactive:
                temp_list.append(vign)

        if len(temp_list) > 1:
            for vign in temp_list:
                if vign.numero == self.last_clicked_vign:
                    vign.desactiver()
        else:
            pass

    def setsnapshot(self, img):
        self.listvignette[self.last_clicked_vign].setsnapshot(img)

    def back_userspace(self):
        self.parent.set_second()


# la fenetre de supervision
class SettingWindow(QWidget):
    def __init__(self, parent=None):
        super(SettingWindow, self).__init__(parent)

        self.pictures = Pictures()
        self.list_seuil = [False, False, False, False, False, False, False, False]
        self.ask_refresh = False
        self.reset = False
        self.iris_onoff = False
        self.iris_on = False
        self.iris_off = False
        self.flag_value_changed = False
        self.flag_deceleration = False
        self.flag_set_domaine = False
        self.flag_resetdomaine = False
        self.flag_change_machine = False
        self.enablemotors = ""
        self.index = ''
        self.vers_furio = [''] * 5

        self.val_domaine = 0
        self.main_layout = QVBoxLayout()
        self.btn_machine_list = []
        self.machines_list = []
        self.old_index = 0
        self.machine_selected = ''
        self.machine_selected_changes = False
        self.old_machine_selected = ''
        self.ref_optique = [""] * 5
        self.old_len_machines = 0
        self.machine_layouts = [QVBoxLayout(), QVBoxLayout(),
                                QVBoxLayout(), QVBoxLayout(),
                                QVBoxLayout()]
        self.vers_tete = [""] * 5

        self.label_seuil_list = [QLabel("Seuil  joystick Pan/Tilt"), QLabel("Seuil joystick Zoom"), QLabel("Seuil pédales Track Left"), QLabel("Seuil pédales Track right"),
                                 QLabel("Seuil pédales Lift Up"), QLabel("Seuil pédales Lift Down"), QLabel("Seuil joystick Z"), QLabel("Seuil poignee Zoom")]
        self.label_data_seuil_list = [QLabel("no data"), QLabel("no data"), QLabel("no data"), QLabel("no data"), QLabel("no data"), QLabel("no data"), QLabel("no data"), QLabel("no data")]
        self.label_edit_seuil_list = [QLabel("0"), QLabel("0"), QLabel("0"), QLabel("0"), QLabel("0"), QLabel("0"), QLabel("0"), QLabel("0")]
        self.label_status_seuil_list = [QLabel(" Aucun boitier connecté"), QLabel(" Aucun boitier connecté"), QLabel(" Aucun boitier connecté"), QLabel(" Aucun boitier connecté"),
                                        QLabel(" Aucun boitier connecté"), QLabel(" Aucun boitier connecté"), QLabel(" Aucun boitier connecté"),
                                        QLabel(" Aucun boitier connecté")]

        self.backgrd_unco = """QLabel{background-color: #E6CCC4;}"""
        self.backgrd_co = """QLabel{background-color: rgba(18, 190, 34, 120);}"""
        self.main_setting_layout = QVBoxLayout()
        self.interface_setting_layout = QVBoxLayout()
        self.interface_setting_layout.setSpacing(50)
        self.interface_setting_layout.setContentsMargins(0, 0, 0, 0)
        self.machines_setting_layout = QVBoxLayout()
        self.onglets = QTabWidget()
        self.onglet_boitiers = QWidget()
        self.onglet_machines = QWidget()
        self.onglet_interface = QWidget()
        self.onglets.addTab(self.onglet_boitiers, "Boitiers")
        self.onglets.addTab(self.onglet_machines, "Machines")
        self.onglets.addTab(self.onglet_interface, "Interface")

        self.onglet_boitiers.layout = self.main_setting_layout
        self.onglet_machines.layout = self.machines_setting_layout
        self.onglet_interface.layout = self.interface_setting_layout

        self.main_layout.addWidget(self.onglets, Qt.AlignJustify)
        self.onglet_boitiers.setLayout(self.onglet_boitiers.layout)
        self.onglet_machines.setLayout(self.onglet_machines.layout)
        self.onglet_interface.setLayout(self.onglet_interface.layout)
        self.onglet_interface.layout.setSpacing(0)

        # premier onglet :---------------------------------------------------------------------------------------------- 1er Onglet
        self.layout_data = QFormLayout()
        self.calibration_layout = QGridLayout()
        self.calibration_layout.setSpacing(10)
        self.calibration_layout.setContentsMargins(0, 0, 0, 0)
        self.calibration_layout.setHorizontalSpacing(1)

        self.label_edit_ip = QLabel("Domaine :")
        self.label_edit_ip.setFixedHeight(50)

        self.btn_edit_ip = wb.ValidateButton("domaine", self.editdomaine)
        # self.btn_edit_ip.setText("200.200")

        dom = str(os.popen("""ifconfig | grep "inet " | cut -c 14-26""").read()).split(".")[0]
        self.btn_edit_ip.setText(dom + "." + dom)

        self.btn_reset_ip = wb.ValidateButton("Reset domaine", self.resetdomaine)

        self.main_setting_layout.addLayout(self.calibration_layout, Qt.AlignJustify)
        self.main_setting_layout.addLayout(self.layout_data, Qt.AlignCenter)

        for j in range(len(self.label_seuil_list)):
            self.calibration_layout.addWidget(self.label_seuil_list[j], j, 0)
            self.calibration_layout.addWidget(self.label_data_seuil_list[j], j, 1)
            self.calibration_layout.addWidget(self.label_edit_seuil_list[j], j, 2)
            self.calibration_layout.addWidget(wb.IncreaseButton("+", self.change_seuil), j, 3)
            self.calibration_layout.addWidget(wb.IncreaseButton("-", self.change_seuil), j, 4)
            self.calibration_layout.addWidget(wb.ValidateButton("Valider", self.validateSeuil), j, 5)
            self.calibration_layout.addWidget(self.label_status_seuil_list[j], j, 6)

            self.label_seuil_list[j].setStyleSheet(self.backgrd_unco)
            self.label_data_seuil_list[j].setStyleSheet(self.backgrd_unco)
            self.label_edit_seuil_list[j].setStyleSheet(self.backgrd_unco)
            self.label_status_seuil_list[j].setStyleSheet(self.backgrd_unco)

        self.calibration_layout.addWidget(self.label_edit_ip, len(self.label_seuil_list), 0)
        self.calibration_layout.addWidget(self.btn_edit_ip, len(self.label_seuil_list), 1)
        self.calibration_layout.addWidget(self.btn_reset_ip, len(self.label_seuil_list), 2)

        # deuxieme onglet (tete) :------------------------------------------------------------------------------------- 2eme Onglet
        self.precision_affichage_vitesse_recue = 6
        self.head_layout = QHBoxLayout()
        self.machines_params = QHBoxLayout()
        self.motor_manager = QGridLayout()

        self.machine_btn_group = QButtonGroup()
        self.machine_btn1 = wb.MachineButton()

        self.machine_btn2 = wb.MachineButton()

        self.machine_btn3 = wb.MachineButton()

        self.machine_btn4 = wb.MachineButton()

        self.machine_btn5 = wb.MachineButton()

        self.btn_machine_list.extend((self.machine_btn1, self.machine_btn2,
                                      self.machine_btn3, self.machine_btn4, self.machine_btn5))

        ctr = 0
        for button in self.btn_machine_list:
            button.clicked.connect(self.whichmachineselected)
            self.machine_layouts[ctr].addWidget(button, Qt.AlignCenter, Qt.AlignCenter)
            self.machine_btn_group.addButton(button)
            button.setCheckable(True)
            button.hide()
            self.head_layout.addLayout(self.machine_layouts[ctr])
            ctr += 1

        self.tableau_tete = QTableWidget()
        self.tableau_tete.setFixedHeight(500)
        self.tableau_tete.setRowCount(6)
        self.tableau_tete.setColumnCount(5)
        self.tableau_tete.setItem(0, 0, wb.CaseTableau("Moteurs"))
        self.tableau_tete.setItem(0, 1, wb.CaseTableau("Vitesse"))
        self.tableau_tete.setItem(0, 2, wb.CaseTableau("Vitesse recue"))
        self.tableau_tete.setItem(0, 3, wb.CaseTableau("Intensité"))
        self.tableau_tete.setItem(0, 4, wb.CaseTableau("Status"))

        self.tableau_tete.setItem(1, 0, wb.CaseTableau("PAN"))
        self.tableau_tete.setItem(2, 0, wb.CaseTableau("TILT"))
        self.tableau_tete.setItem(3, 0, wb.CaseTableau("TRACK"))
        self.tableau_tete.setItem(4, 0, wb.CaseTableau("LIFT"))
        self.tableau_tete.setItem(5, 0, wb.CaseTableau("ZOOM"))

        for i in range(1, 6):
            for j in range(1, 5):
                self.tableau_tete.setItem(i, j, wb.CaseTableau("no data"))

        self.tableau_tete.verticalHeader().hide()
        self.tableau_tete.horizontalHeader().hide()

        self.label_motor_manager = QLabel("Motor Manager")
        self.label_motor_manager.setFont(QFont('Serif', 15))
        self.btn_enable_all = wb.EnableButton("ALL", self.enableDisableAction)
        self.btn_enable_all.setFixedSize(210, 80)
        self.btn_enable_pan = wb.EnableButton("PAN", self.enableDisableAction)
        self.btn_enable_tilt = wb.EnableButton("TILT", self.enableDisableAction)
        self.btn_enable_track = wb.EnableButton("TRACK", self.enableDisableAction)
        self.btn_enable_lift = wb.EnableButton("LIFT", self.enableDisableAction)

        self.btn_reset = wb.EnableButton("RESET\nconnected devices", self.reset_machine)
        self.btn_reset.setText("RESET\nConnected\nDevices")
        self.btn_reset.setCheckable(False)

        self.btn_iris_onoff = wb.EnableButton("Iris OFF", self.iris_switch)
        self.btn_iris_onoff.setText("Iris OFF")

        self.motor_manager.setSpacing(3)

        self.motor_manager.addWidget(self.btn_reset, 0, 0)
        self.motor_manager.addWidget(self.btn_iris_onoff, 0, 1)

        self.motor_manager.addWidget(self.label_motor_manager, 1, 0, 1, 4, Qt.AlignBottom)
        self.motor_manager.addWidget(self.btn_enable_all, 2, 0, 1, 4)
        self.motor_manager.addWidget(self.btn_enable_pan, 3, 0)
        self.motor_manager.addWidget(self.btn_enable_tilt, 4, 0)
        self.motor_manager.addWidget(self.btn_enable_track, 3, 1)
        self.motor_manager.addWidget(self.btn_enable_lift, 4, 1)

        self.machines_params.addWidget(self.tableau_tete)
        self.machines_params.addLayout(self.motor_manager)
        self.machines_setting_layout.addLayout(self.head_layout)
        self.machines_setting_layout.addLayout(self.machines_params)

        # troisieme onglet (interface):-------------------------------------------------------------------------------- 3eme Onglet

        """###########################################################################################################TABLEAU Joystick"""
        self.tableau = QTableWidget()
        self.tableau.setMinimumHeight(210)
        self.tableau.setRowCount(7)
        self.tableau.setColumnCount(9)

        self.tableau.setItem(0, 0, wb.CaseTableau("Paramètres\nJoystick"))
        self.tableau.setItem(0, 1, wb.CaseTableau("Vitesse"))
        self.tableau.setItem(0, 3, wb.CaseTableau("Ratio"))
        self.tableau.setItem(0, 5, wb.CaseTableau("Courbe"))
        self.tableau.setItem(0, 7, wb.CaseTableau("Acceleration Memoire"))
        self.tableau.setItem(1, 1, wb.CaseTableau("Min"))
        self.tableau.setItem(1, 2, wb.CaseTableau("Max"))
        self.tableau.setItem(1, 3, wb.CaseTableau("Min"))
        self.tableau.setItem(1, 4, wb.CaseTableau("Max"))
        self.tableau.setItem(1, 5, wb.CaseTableau("Min"))
        self.tableau.setItem(1, 6, wb.CaseTableau("Max"))
        self.tableau.setItem(1, 7, wb.CaseTableau("Min"))
        self.tableau.setItem(1, 8, wb.CaseTableau("Max"))

        self.tableau.setItem(2, 0, wb.CaseTableau("Tête V4"))
        self.tableau.setItem(3, 0, wb.CaseTableau("Tête V6"))
        self.tableau.setItem(4, 0, wb.CaseTableau("Zoom Fuji/Canon"))
        self.tableau.setItem(5, 0, wb.CaseTableau("Tête V5"))
        self.tableau.setItem(6, 0, wb.CaseTableau("Tête Furio"))

        self.tableau.setSpan(0, 1, 1, 2)
        self.tableau.setSpan(0, 3, 1, 2)
        self.tableau.setSpan(0, 5, 1, 2)
        self.tableau.setSpan(0, 7, 1, 2)
        self.tableau.setSpan(0, 0, 2, 1)

        self.tableau.setColumnWidth(0, 200)
        self.tableau.setRowHeight(1, 10)
        self.tableau.verticalHeader().hide()
        self.tableau.horizontalHeader().hide()
        self.tableau.itemClicked.connect(lambda case=self.tableau.itemClicked: self.clickedItem(case))

        """############################################################################################################ TABLEAU PANBAR"""
        self.tableau_panbar = QTableWidget()
        self.tableau_panbar.setMinimumHeight(210)
        self.tableau_panbar.setRowCount(7)
        self.tableau_panbar.setColumnCount(7)

        self.tableau_panbar.setItem(0, 0, wb.CaseTableau("Paramètres\nPanbar"))
        self.tableau_panbar.setItem(0, 1, wb.CaseTableau("Vitesse PAN"))
        self.tableau_panbar.setItem(0, 3, wb.CaseTableau("Ratio"))
        self.tableau_panbar.setItem(0, 5, wb.CaseTableau("Vitesse TILT"))
        self.tableau_panbar.setItem(1, 1, wb.CaseTableau("Min"))
        self.tableau_panbar.setItem(1, 2, wb.CaseTableau("Max"))
        self.tableau_panbar.setItem(1, 3, wb.CaseTableau("Min"))
        self.tableau_panbar.setItem(1, 4, wb.CaseTableau("Max"))
        self.tableau_panbar.setItem(1, 5, wb.CaseTableau("Min"))
        self.tableau_panbar.setItem(1, 6, wb.CaseTableau("Max"))

        self.tableau_panbar.setItem(2, 0, wb.CaseTableau("Tête V4"))
        self.tableau_panbar.setItem(3, 0, wb.CaseTableau("Tête V6"))
        self.tableau_panbar.setItem(4, 0, wb.CaseTableau("Zoom Fuji/Canon"))
        self.tableau_panbar.setItem(5, 0, wb.CaseTableau("Tête V5"))
        self.tableau_panbar.setItem(6, 0, wb.CaseTableau("Tête Furio"))

        self.tableau_panbar.setSpan(0, 1, 1, 2)
        self.tableau_panbar.setSpan(0, 3, 1, 2)
        self.tableau_panbar.setSpan(0, 5, 1, 2)
        self.tableau_panbar.setSpan(0, 0, 2, 1)

        self.tableau_panbar.setColumnWidth(0, 200)
        self.tableau_panbar.setRowHeight(1, 10)
        self.tableau_panbar.verticalHeader().hide()
        self.tableau_panbar.horizontalHeader().hide()
        self.tableau_panbar.itemClicked.connect(lambda case=self.tableau_panbar.itemClicked: self.clickeditemPanbar(case))

        """##########################################################################################################  TABLEAU PEDALES"""
        self.tableau_pedales = QTableWidget()
        self.tableau_pedales.setMinimumHeight(150)
        self.tableau_pedales.setRowCount(4)
        self.tableau_pedales.setColumnCount(9)

        self.tableau_pedales.setItem(0, 0, wb.CaseTableau("Paramètres\nPédales"))
        self.tableau_pedales.setItem(0, 1, wb.CaseTableau("Vitesse"))
        self.tableau_pedales.setItem(0, 3, wb.CaseTableau("Ratio"))
        self.tableau_pedales.setItem(0, 5, wb.CaseTableau("Courbe"))
        self.tableau_pedales.setItem(0, 7, wb.CaseTableau("Deceleration butée"))
        self.max_deceleration = 50000
        self.min_deceleration = 5000
        self.tableau_pedales.setItem(1, 1, wb.CaseTableau("Min"))
        self.tableau_pedales.setItem(1, 2, wb.CaseTableau("Max"))
        self.tableau_pedales.setItem(1, 3, wb.CaseTableau("Min"))
        self.tableau_pedales.setItem(1, 4, wb.CaseTableau("Max"))
        self.tableau_pedales.setItem(1, 5, wb.CaseTableau("Min"))
        self.tableau_pedales.setItem(1, 6, wb.CaseTableau("Max"))
        self.tableau_pedales.setItem(1, 7, wb.CaseTableau("Value"))
        self.tableau_pedales.setItem(2, 0, wb.CaseTableau("Track"))
        self.tableau_pedales.setItem(3, 0, wb.CaseTableau("Lift"))

        self.tableau_pedales.setSpan(0, 1, 1, 2)
        self.tableau_pedales.setSpan(0, 3, 1, 2)
        self.tableau_pedales.setSpan(0, 5, 1, 2)
        self.tableau_pedales.setSpan(0, 7, 1, 2)
        self.tableau_pedales.setSpan(1, 7, 1, 2)
        self.tableau_pedales.setSpan(2, 7, 1, 2)
        self.tableau_pedales.setSpan(3, 7, 1, 2)

        self.tableau_pedales.setSpan(0, 0, 2, 1)
        self.tableau_pedales.setColumnWidth(0, 200)
        self.tableau_pedales.setRowHeight(1, 10)
        self.tableau_pedales.verticalHeader().hide()
        self.tableau_pedales.horizontalHeader().hide()
        self.tableau_pedales.itemClicked.connect(lambda case=self.tableau_panbar.itemClicked: self.clickeditemPedales(case))

        # --------------------------------------------------------------------------------------------------------------------- on place les widgets tableau
        self.interface_setting_layout.addWidget(self.tableau, Qt.AlignCenter)
        self.interface_setting_layout.addWidget(self.tableau_panbar, Qt.AlignHCenter)
        self.interface_setting_layout.addWidget(self.tableau_pedales, Qt.AlignBottom)

        self.setLayout(self.main_layout)

        # index 0: teteV4, index 1: teteV6, index 2 18360: zoomfuji/canon,
        # index 3: furiochariot, index 4: furio colonne, index 5 : V5, index 6: Tete furio. Tuple(min, max)
        """
        self.datManager.enregistrer([(0, 10000), (0, 10000), (0, 10000), (0, 160000), (0, 250000), (0, 10000), (0, 10000)], 'vitesses')
        self.datManager.enregistrer([(4.0, 0.3), (4.0, 0.3), (4.0, 0.3), (4.0, 0.3), (4.0, 0.3), (4.0, 0.3), (4.0, 0.3)], 'ratios')
        self.datManager.enregistrer([(0.3, 5), (0.3, 5), (0.3, 5), (0.3, 5), (0.3, 5), (0.3, 5), (0.3, 5)], 'courbes')
        self.datManager.enregistrer([(550, 3000), (0, 10000), (0, 10000), (0, 2000), (0, 3000), (0, 10000), (0, 10000) ], 'vitessespan')
        self.datManager.enregistrer([(4.0, 0.3), (4.0, 0.3), (4.0, 0.3), (4.0, 0.3), (0.3, 1.7), (0.3, 1.7), (0.3, 1.7)], 'ratioscmd')
        self.datManager.enregistrer([(550, 3000), (0, 10000), (0.3, 5), (0.3, 5), (0.3, 5), (0.3, 5), (0.3, 5)], 'vitessestilt')
        self.datManager.enregistrer([(10000, 9000000), (10000, 9000000), (10000, 9000000), (10000, 9000000), (10000, 9000000), (10000, 9000000), (10000, 9000000)],'accelmemoire')
        print("set_param_vitesse ", self.set_param_vitesse)
                print("set_param_ratio ", self.set_param_ratio)
                print("set_param_courbe ", self.set_param_courbe)
                print("set_param_vitesse_pan ", self.set_param_vitesse_pan)
                print("set_param_ratio_cmd ", self.set_param_ratio_cmd)
                print("set_param_vitesse_tilt ", self.set_param_vitesse_tilt)
                print("set_param_accel ", self.set_param_accel)
                print("set_param_accel_furio ", self.set_param_accel_furio)"""

        self.datManager = DataManager()
        self.set_param_vitesse = self.datManager.charger('vitesses')
        self.set_param_ratio = self.datManager.charger('ratios')
        self.set_param_courbe = self.datManager.charger('courbes')
        self.set_param_vitesse_pan = self.datManager.charger('vitessespan')
        self.set_param_ratio_cmd = self.datManager.charger('ratioscmd')
        self.set_param_vitesse_tilt = self.datManager.charger('vitessestilt')
        self.set_param_accel = self.datManager.charger('accelmemoire')
        self.set_param_accel_furio = self.datManager.charger('accelfurio')

        self.set_param()

    def enableDisableAction(self):
        if self.sender() is self.btn_enable_all and self.btn_enable_all.isChecked():
            self.btn_enable_pan.setChecked(True) if not self.btn_enable_pan.isChecked() else 0
            self.btn_enable_tilt.setChecked(True) if not self.btn_enable_tilt.isChecked() else 0
            self.btn_enable_track.setChecked(True) if not self.btn_enable_track.isChecked() else 0
            self.btn_enable_lift.setChecked(True) if not self.btn_enable_lift.isChecked() else 0
        elif self.sender() is self.btn_enable_all and not self.btn_enable_all.isChecked():
            self.btn_enable_pan.setChecked(False) if self.btn_enable_pan.isChecked() else 0
            self.btn_enable_tilt.setChecked(False) if self.btn_enable_tilt.isChecked() else 0
            self.btn_enable_track.setChecked(False) if self.btn_enable_track.isChecked() else 0
            self.btn_enable_lift.setChecked(False) if self.btn_enable_lift.isChecked() else 0
        else:
            pass
        self.enablemotors = self.sender().text()

    def resetdomaine(self):
        self.flag_resetdomaine = True
        print("reset domaine")

    def editdomaine(self):
        pavenumeric = wb.PaveNumerique(self.sender().text().split(".")[0])

        if pavenumeric.value > 255:
            self.val_domaine = 255
        elif pavenumeric.value < 0:
            self.val_domaine = 0
        else:
            self.val_domaine = int(pavenumeric.value)
        self.sender().setText(str(self.val_domaine) + "." + str(self.val_domaine))
        self.flag_set_domaine = True

    def iris_set(self, check):
        self.btn_iris_onoff.setChecked(True)
        self.btn_iris_onoff.setText("Iris ON")

    def iris_switch(self):
        if self.btn_iris_onoff.isChecked():
            self.iris_on = True
            self.btn_iris_onoff.setText("Iris ON")
            self.iris_onoff = True

        elif self.btn_iris_onoff.isChecked() == False:
            self.iris_off = True
            self.btn_iris_onoff.setText("Iris OFF")
            self.iris_onoff = False

    def clickedItem(self, case):
        if case.row() not in [0, 1] and case.column() != 0:
            pavenumeric = wb.PaveNumerique(case.text())
            case.setText(str(pavenumeric.value))
            if case.text().isdigit():
                value = int(case.text())
            else:
                value = float(case.text())

            if case.column() in [1, 2]:
                if case.row() in [2, 3, 4]:
                    machineparam = list(self.set_param_vitesse[case.row() - 2])
                    machineparam[case.column() - 1] = value
                    self.set_param_vitesse[case.row() - 2] = tuple(machineparam)
                else:
                    machineparam = list(self.set_param_vitesse[case.row()])
                    machineparam[case.column() - 1] = value
                    self.set_param_vitesse[case.row()] = tuple(machineparam)
                self.datManager.enregistrer(self.set_param_vitesse, 'vitesses')

            elif case.column() in [3, 4]:
                if case.row() in [2, 3, 4]:

                    machineparam = list(self.set_param_ratio[case.row() - 2])
                    machineparam[case.column() - 3] = value
                    self.set_param_ratio[case.row() - 2] = tuple(machineparam)
                else:
                    machineparam = list(self.set_param_ratio[case.row()])
                    machineparam[case.column() - 3] = value
                    self.set_param_ratio[case.row()] = tuple(machineparam)
                self.datManager.enregistrer(self.set_param_ratio, 'ratios')
            elif case.column() in [5, 6]:
                if case.row() in [2, 3, 4]:
                    machineparam = list(self.set_param_courbe[case.row() - 2])
                    machineparam[case.column() - 5] = value
                    self.set_param_courbe[case.row() - 2] = tuple(machineparam)
                else:
                    machineparam = list(self.set_param_courbe[case.row()])
                    machineparam[case.column() - 5] = value
                    self.set_param_courbe[case.row()] = tuple(machineparam)
                self.datManager.enregistrer(self.set_param_courbe, 'courbes')
            elif case.column() in [7, 8]:
                if case.row() in [2, 3, 4]:
                    machineparam = list(self.set_param_accel[case.row() - 2])
                    self.set_param_accel[case.row() - 2] = tuple(machineparam)
                    self.datManager.enregistrer(self.set_param_accel, 'accelmemoire')
                else:
                    machineparam = list(self.set_param_accel[case.row()])
                    self.set_param_accel[case.row()] = tuple(machineparam)
                    self.datManager.enregistrer(self.set_param_accel, 'accelmemoire')
            else:
                pass
            self.flag_value_changed = True

    def clickeditemPanbar(self, case):
        if case.row() not in [0, 1] and case.column() != 0:
            pavenumeric = wb.PaveNumerique(case.text())
            case.setText(str(pavenumeric.value))
            if case.text().isdigit():
                value = int(case.text())
            else:
                value = float(case.text())

            if case.column() in [1, 2]:
                if case.row() in [2, 3, 4]:
                    machineparam = list(
                        self.set_param_vitesse_pan[case.row() - 2])  # recupere le tuple (min, max) enregistré, pour le paramètre "vitesse PAN" cas teteV4 V6 et zoom et on le passe en liste
                    machineparam[case.column() - 1] = value  # recupère le param min(0) ou max(1) en fonction d'ou on a cliqué (colonne1 -1 = 0) ou (colonne2 -1 = 1) et on lui donne la valeur rentrée
                    self.set_param_vitesse_pan[case.row() - 2] = tuple(machineparam)  # on re passe la liste en tuple
                else:
                    machineparam = list(
                        self.set_param_vitesse_pan[case.row()])  # recupere le tuple (min, max) enregistré, pour le paramètre "vitesse PAN" cas tete V5 et tete Furio et on le passe en liste
                    machineparam[case.column() - 1] = value  # recupère le param min(0) ou max(1) en fonction d'ou on a cliqué (colonne1 -1 = 0) ou (colonne2 -1 = 1) et on lui donne la valeur rentrée
                    self.set_param_vitesse_pan[case.row()] = tuple(machineparam)  # on re passe la liste en tuple

                self.datManager.enregistrer(self.set_param_vitesse_pan, 'vitessespan')  # et on enregistre
            elif case.column() in [3, 4]:
                if case.row() in [2, 3, 4]:
                    machineparam = list(self.set_param_ratio_cmd[case.row() - 2])
                    machineparam[case.column() - 3] = value
                    self.set_param_ratio_cmd[case.row() - 2] = tuple(machineparam)

                else:
                    machineparam = list(self.set_param_ratio_cmd[case.row()])
                    machineparam[case.column() - 3] = value
                    self.set_param_ratio_cmd[case.row()] = tuple(machineparam)

                self.datManager.enregistrer(self.set_param_ratio_cmd, 'ratioscmd')
            elif case.column() in [5, 6]:
                if case.row() in [2, 3, 4]:
                    machineparam = list(self.set_param_vitesse_tilt[case.row() - 2])
                    machineparam[case.column() - 5] = value
                    self.set_param_vitesse_tilt[case.row() - 2] = tuple(machineparam)
                else:
                    machineparam = list(self.set_param_vitesse_tilt[case.row()])
                    machineparam[case.column() - 5] = value
                    self.set_param_vitesse_tilt[case.row()] = tuple(machineparam)

                self.datManager.enregistrer(self.set_param_vitesse_tilt, 'vitessestilt')
            else:
                pass
            self.flag_value_changed = True

    def clickeditemPedales(self, case):
        if case.row() not in [0, 1] and case.column() != 0:
            pavenumeric = wb.PaveNumerique(case.text())
            case.setText(str(pavenumeric.value))
            if case.text().isdigit():
                value = int(case.text())
            else:
                value = float(case.text())

            if case.column() in [1, 2]:
                machineparam = list(self.set_param_vitesse[case.row() + 1])
                machineparam[case.column() - 1] = value
                self.set_param_vitesse[case.row() + 1] = tuple(machineparam)
                self.datManager.enregistrer(self.set_param_vitesse, 'vitesses')
            elif case.column() in [3, 4]:
                machineparam = list(self.set_param_ratio[case.row() + 1])
                machineparam[case.column() - 3] = value
                self.set_param_ratio[case.row() + 1] = tuple(machineparam)
                self.datManager.enregistrer(self.set_param_ratio, 'ratios')
            elif case.column() in [5, 6]:
                machineparam = list(self.set_param_courbe[case.row() + 1])
                machineparam[case.column() - 5] = value
                self.set_param_courbe[case.row() + 1] = tuple(machineparam)
                self.datManager.enregistrer(self.set_param_courbe, 'courbes')
            elif case.column() in [7, 8]:

                if self.min_deceleration <= value <= self.max_deceleration:
                    self.set_param_accel_furio[case.row() + 1] = value
                elif value < self.min_deceleration:
                    self.set_param_accel_furio[case.row() + 1] = self.min_deceleration
                    case.setText(str(self.min_deceleration))
                elif value > self.max_deceleration:
                    self.set_param_accel_furio[case.row() + 1] = self.max_deceleration
                    case.setText(str(self.max_deceleration))
                else:
                    pass
                self.datManager.enregistrer(self.set_param_accel_furio, 'accelfurio')
                self.flag_deceleration = True
            else:
                pass
            self.flag_value_changed = True

    def set_param(self):
        # index 0: teteV4, index 1: teteV6, index 2 18360: zoomfuji/canon,
        # index 3: furiochariot, index 4: furio colonne, index 5 : V5, index 6: Tete furio. Tuple(min, max)
        for indexParam in (0, 1, 2, 5, 6):
            switcherindex = {
                0: 2,
                1: 3,
                2: 4,
                5: 5,
                6: 6,
            }

            indexRow = switcherindex.get(indexParam, "index inconnu")
            minvit, maxvit = self.set_param_vitesse[indexParam]
            minrat, maxrat = self.set_param_ratio[indexParam]
            mincourb, maxcourb = self.set_param_courbe[indexParam]
            minaccel, maxaccel = self.set_param_accel[indexParam]

            minvitpanpb, maxvitpanpb = self.set_param_vitesse_pan[indexParam]
            minratpb, maxratpb = self.set_param_ratio_cmd[indexParam]
            minvittiltpb, maxvittiltpb = self.set_param_vitesse_tilt[indexParam]

            self.tableau.setItem(indexRow, 1, wb.CaseTableau(str(minvit)))
            self.tableau.setItem(indexRow, 2, wb.CaseTableau(str(maxvit)))
            self.tableau.setItem(indexRow, 3, wb.CaseTableau(str(minrat)))
            self.tableau.setItem(indexRow, 4, wb.CaseTableau(str(maxrat)))
            self.tableau.setItem(indexRow, 5, wb.CaseTableau(str(mincourb)))
            self.tableau.setItem(indexRow, 6, wb.CaseTableau(str(maxcourb)))
            self.tableau.setItem(indexRow, 7, wb.CaseTableau(str(minaccel)))
            self.tableau.setItem(indexRow, 8, wb.CaseTableau(str(maxaccel)))

            self.tableau_panbar.setItem(indexRow, 1, wb.CaseTableau(str(minvitpanpb)))
            self.tableau_panbar.setItem(indexRow, 2, wb.CaseTableau(str(maxvitpanpb)))
            self.tableau_panbar.setItem(indexRow, 3, wb.CaseTableau(str(minratpb)))
            self.tableau_panbar.setItem(indexRow, 4, wb.CaseTableau(str(maxratpb)))
            self.tableau_panbar.setItem(indexRow, 5, wb.CaseTableau(str(minvittiltpb)))
            self.tableau_panbar.setItem(indexRow, 6, wb.CaseTableau(str(maxvittiltpb)))

        for indexParam in (3, 4):
            switcherindex = {
                3: 2,
                4: 3,
            }
            indexRow = switcherindex.get(indexParam, "index inconnu")
            minvit, maxvit = self.set_param_vitesse[indexParam]
            minrat, maxrat = self.set_param_ratio[indexParam]
            mincourb, maxcourb = self.set_param_courbe[indexParam]
            accelfurio = self.set_param_accel_furio[indexParam]

            self.tableau_pedales.setItem(indexRow, 1, wb.CaseTableau(str(minvit)))
            self.tableau_pedales.setItem(indexRow, 2, wb.CaseTableau(str(maxvit)))
            self.tableau_pedales.setItem(indexRow, 3, wb.CaseTableau(str(minrat)))
            self.tableau_pedales.setItem(indexRow, 4, wb.CaseTableau(str(maxrat)))
            self.tableau_pedales.setItem(indexRow, 5, wb.CaseTableau(str(mincourb)))
            self.tableau_pedales.setItem(indexRow, 6, wb.CaseTableau(str(maxcourb)))
            self.tableau_pedales.setItem(indexRow, 7, wb.CaseTableau(str(accelfurio)))

    def validateSeuil(self):
        whoissending = self.calibration_layout.getItemPosition(self.calibration_layout.indexOf(self.sender()))
        self.list_seuil[whoissending[0]] = True

    def change_seuil(self):
        whoissending = self.calibration_layout.getItemPosition(self.calibration_layout.indexOf(self.sender()))
        if whoissending[1] == 3:
            newval = int(self.label_edit_seuil_list[whoissending[0]].text()) + 1
        elif whoissending[1] == 4:
            newval = int(self.label_edit_seuil_list[whoissending[0]].text()) - 1 if int(self.label_edit_seuil_list[whoissending[0]].text()) > 0 else 0
        else:
            pass
        self.label_edit_seuil_list[whoissending[0]].setText(str(newval))

    def set_status(self, idx, cmd, num):
        if idx == 2:
            for i in range(2, 6):
                self.label_status_seuil_list[i].setText(" " + cmd + " n°" + num + " connecté !")
                self.label_seuil_list[i].setStyleSheet(self.backgrd_co)
                self.label_data_seuil_list[i].setStyleSheet(self.backgrd_co)
                self.label_edit_seuil_list[i].setStyleSheet(self.backgrd_co)
                self.label_status_seuil_list[i].setStyleSheet(self.backgrd_co)
        else:
            self.label_status_seuil_list[idx].setText(" " + cmd + " n°" + num + " connecté !")
            self.label_seuil_list[idx].setStyleSheet(self.backgrd_co)
            self.label_data_seuil_list[idx].setStyleSheet(self.backgrd_co)
            self.label_edit_seuil_list[idx].setStyleSheet(self.backgrd_co)
            self.label_status_seuil_list[idx].setStyleSheet(self.backgrd_co)

    def unset_status(self, idx):
        if idx == 2:
            for i in range(2, 6):
                self.label_status_seuil_list[i].setText(" Aucun boitier connecté")
                self.label_seuil_list[i].setStyleSheet(self.backgrd_unco)
                self.label_data_seuil_list[i].setStyleSheet(self.backgrd_unco)
                self.label_edit_seuil_list[i].setStyleSheet(self.backgrd_unco)
                self.label_status_seuil_list[i].setStyleSheet(self.backgrd_unco)
        else:
            self.label_status_seuil_list[idx].setText(" Aucun boitier connecté")
            self.label_seuil_list[idx].setStyleSheet(self.backgrd_unco)
            self.label_data_seuil_list[idx].setStyleSheet(self.backgrd_unco)
            self.label_edit_seuil_list[idx].setStyleSheet(self.backgrd_unco)
            self.label_status_seuil_list[idx].setStyleSheet(self.backgrd_unco)

    def reset_machine(self):
        self.reset = True

    # Affichage machines onglet 2 ==================================================================== Affichage machines onglet 2
    def whichmachineselected(self):
        self.index = self.btn_machine_list.index(self.sender())
        try:
            # print("clicked on this machine:", self.machines_list[self.index])
            self.machine_selected = self.machines_list[self.index]
            self.flag_change_machine = True
            identifier = self.machines_list[self.index].split('.')[2]
            if identifier == "2":
                self.btn_enable_track.setEnabled(False)
                self.btn_enable_lift.setEnabled(False)

            if self.index != self.old_index:
                print("index different window settings machines")

            elif self.machine_selected == self.old_machine_selected:  # Si on reclic sur une machine ca deselectionne tout
                self.machine_btn_group.setExclusive(False)
                self.btn_machine_list[self.index].setChecked(False)
                self.machine_btn_group.setExclusive(True)
                self.machine_selected = ''
                self.old_index = ''
                return
            else:
                pass

            self.old_index = self.index
            self.old_machine_selected = self.machine_selected
            self.machine_selected_changes = True
        except IndexError:
            print("index error which")
            pass

    def set_machine_buttons(self):
        if len(self.machines_list) > 0:
            # print("machine list in setting button", self.machines_list)
            for machine in self.machines_list:
                index = self.machines_list.index(machine)
                identifier = machine.split(".")[2]
                num_machine = machine.split(".")[3]
                ip = machine

                switchcase_machine = {
                    '2': 'tete',
                    '3': 'furio',
                }
                name = switchcase_machine.get(identifier, "Machine invalide")
                if name == 'tete':
                    self.btn_machine_list[index].show()
                    if self.vers_tete[index] not in ('None', 'V4lost', 'V5lost', 'V6lost', 'Nonelost', '', "lost"):
                        switchcase_version = {
                            'V4': (self.pictures.V4_icon, self.pictures.image_V4.rect().size()),
                            'V5': (self.pictures.V5_icon, self.pictures.image_V5.rect().size()),
                            'V6': (self.pictures.add_number(str(num_machine), 'V6'), self.pictures.image_V6.rect().size()),
                        }
                        versiontete = switchcase_version.get(self.vers_tete[index], "None")
                        icon, size = versiontete
                        self.btn_machine_list[index].unset_gif_loading()
                        if self.ref_optique[index] not in ("none", "", "V6"):
                            self.btn_machine_list[index].setIcon(icon)
                            self.btn_machine_list[index].setIconSize(size)
                            self.btn_machine_list[index].unset_gif_loading()
                            self.btn_machine_list[index].unset_gif_optique()
                        else:
                            self.btn_machine_list[index].unset_gif_loading()
                            self.btn_machine_list[index].set_gif_optique(self.vers_tete[index])

                    elif 'lost' in str(self.vers_tete[index]):
                        self.btn_machine_list[index].unset_gif_loading()
                        self.btn_machine_list[index].unset_gif_optique()
                        self.btn_machine_list[index].setIcon(QIcon())
                        self.btn_machine_list[index].setIcon(self.pictures.add_number(str(num_machine), 'eth'))

                    else:
                        self.btn_machine_list[index].set_gif_loading()
                        self.btn_machine_list[index].unset_gif_optique()
                    # self.btn_machine_list[ctr].click()

                elif name == 'furio':
                    self.btn_machine_list[index].show()
                    if self.vers_furio[index] not in ('None', 'FXlost', 'MOlost', 'Nonelost', '', 'lost'):
                        switchcase_version_colonne = {
                            'FX': (self.pictures.FurioFX_icon, self.pictures.image_Furio_FX.rect().size()),
                            'MO': (self.pictures.FurioMO_icon, self.pictures.image_Furio_MO.rect().size()),
                        }
                        versioncolonne = switchcase_version_colonne.get(self.vers_furio[index], "None")
                        icon, size = versioncolonne
                        self.btn_machine_list[index].setIcon(icon)
                        self.btn_machine_list[index].setIconSize(size)

                    # self.btn_machine_list[index].setChecked(True)
                else:
                    pass

    def unset_machine_buttons(self, ip):

        identifier = ip.split(".")[2]
        index = self.machines_list.index(ip)
        switchcase_machine = {
            '2': 'tete',
            '3': 'furio',
        }
        name = switchcase_machine.get(identifier, "Machine invalide")
        if name == 'tete':
            self.machine_btn_group.setExclusive(False)
            if self.btn_machine_list[index].isChecked():
                self.btn_machine_list[index].click()
            else:
                self.btn_machine_list[index].setChecked(False)
            self.btn_machine_list[index].setEnabled(False)
            self.machine_btn_group.setExclusive(True)

            # self.btn_machine_list[index].hide() on va plutot mettre une croix
        elif name == 'furio':
            print("furio windows settings unset ")
            # self.btn_machine_list[index].hide()

    @pyqtSlot()
    def set_vitesse(self, tilt, pan, track, lift, zoom):
        self.tableau_tete.item(1, 1).setText(str(pan))
        self.tableau_tete.item(2, 1).setText(str(tilt))
        self.tableau_tete.item(3, 1).setText(str(track))
        self.tableau_tete.item(4, 1).setText(str(lift))
        self.tableau_tete.item(5, 1).setText(str(zoom))

    @pyqtSlot()
    def set_vitesse_recue(self, tilt, pan, track, lift, zoom):
        self.tableau_tete.item(1, 2).setText(str(round(pan, self.precision_affichage_vitesse_recue)))
        self.tableau_tete.item(2, 2).setText(str(round(tilt, self.precision_affichage_vitesse_recue)))
        self.tableau_tete.item(3, 2).setText(str(round(track, self.precision_affichage_vitesse_recue)))
        self.tableau_tete.item(4, 2).setText(str(round(lift, self.precision_affichage_vitesse_recue)))
        self.tableau_tete.item(5, 2).setText(str(round(zoom, self.precision_affichage_vitesse_recue)))


# la fenetre de commande (fenetre principale)
class MainWindow(QWidget):
    clicked = pyqtSignal()

    def __init__(self, parent):
        super(MainWindow, self).__init__(parent)
        self.parent = parent
        logging.basicConfig(level=logging.INFO, format='[%(levelname)s] (QtThread : MainThread) %(message)s', )  # reglage des messages de logging
        self.thread_info = ""
        self.p = psutil.Process(os.getpid())
        self.time_logging = 10000
        self.timer_logging = QTimer(self)
        self.timer_logging.timeout.connect(self.logging)
        self.timer_logging.start(self.time_logging)

        self.pictures = Pictures()
        self.image_joystick = self.pictures.image_joystick
        self.image_joystick_cross = self.pictures.image_joystick_cross
        self.image_panbar = self.pictures.image_panbar
        self.image_zoompoint = self.pictures.image_zoompoint
        self.image_zoompoint_cross = self.pictures.image_zoompoint_cross
        self.image_lifttrack = self.pictures.image_lifttrack
        self.image_lifttrack_cross = self.pictures.image_lifttrack_cross
        self.image_poigneezoom_only = self.pictures.image_poigneezoom_only
        self.image_poigneepoint_only = self.pictures.image_poigneepoint_only
        self.image_poignees = self.pictures.image_poignees

        # general settings :
        self.ratio_pan = 4.0
        self.ratio_tilt = 4.0
        self.ratio_track = 4.0
        self.ratio_lift = 4.0
        self.courbe_pan = 0.3
        self.courbe_tilt = 0.3
        self.courbe_track = 0.3
        self.courbe_lift = 0.3
        self.vitesse_pan = 0
        self.vitesse_tilt = 0
        self.vitesse_zoom = 0
        self.vitesse_track = 0
        self.vitesse_lift = 0
        self.width_cmd = 120
        # index 0: teteV4, index 1: teteV6, index 2 18360: zoomfuji/canon,
        # index 3: furiochariot, index 4: furio colonne, index 5 : V5. Tuple(min, max)

        # Chargement des parametres
        self.datManager = DataManager()

        self.param_vitesse = self.datManager.charger('vitesses')
        self.param_ratio = self.datManager.charger('ratios')
        self.param_courbe = self.datManager.charger('courbes')
        self.param_vitessepan = self.datManager.charger('vitessespan')
        self.param_ratiocmd = self.datManager.charger('ratioscmd')
        self.param_vitessetilt = self.datManager.charger('vitessestilt')
        self.param_accel = self.datManager.charger('accelmemoire')
        min, max = self.param_accel[0]
        self.accel_memoire = int((max - min) / 2 + min)
        self.param_zoomassist = (0, 0.99)
        self.param_point = (0, 16383)  # coté commande)
        self.param_machine = ['', '', '', '', '']

        self.code_erreur_Furio = ["", ""]  # [Chariot, Colonne]

        self.index = 0
        self.old_index = "init"
        self.data_loaded = False
        self.old_machine_selected = ''
        self.machine_focus_position = [8192] * 5  # 8192 = mid range focus
        self.current_drag_button = 0
        self.flag_emi_cadreur = ""
        self.flag_change_machine = False
        self.call_memory_position = False
        self.recall_memory_position = False
        self.call_memory_focus = False
        self.flag_focus = True
        self.flag_raz_focus = False
        self.memory_position_number = 0
        self.current_memory_pos_button = ""
        self.memory_value = 0
        self.quit_app = False
        self.motor_release = False
        self.state_motor_per_machine = [False] * 5
        self.slider_0 = ""
        self.flag_reload_param = False
        self.poignee_deport_conn = [False, False]

        self.zoomassistIsEnable = False
        self.zoomassistFactor = 0
        self.machines_list = []
        self.machine_selected = ""
        self.machine_selected_changes = False
        self.btn_machine_list = []
        self.dropper_machine_list = []
        self.cmd_list = [''] * 5
        # variable tete optique
        self.vers_tete = [""] * 5
        self.vers_furio = [""] * 5
        self.ref_optique = [""] * 5
        # variable limites
        self.limitdial = ""
        self.error_dial = wb.ErrorDialog('cmd', 'none')
        self.flaglimdiag = False
        self.lim_haut = [False] * 5
        self.lim_bas = [False] * 5
        self.lim_gauche = [False] * 5
        self.lim_droite = [False] * 5

        self.save_state_top = [False] * 5
        self.save_state_bot = [False] * 5
        self.save_state_left = [False] * 5
        self.save_state_right = [False] * 5

        # Flags butees Furio
        self.flag_furio = (False, False, False, False)  # [Gauche, Droite, Haut, Bas]

        # flag reset optique
        self.rstopt = False

        self.icons_list = [""] * 5
        self.old_len_machines = 0

        # Le main layout et donc le debut de l'implementation des objets graphiques de l'interface.
        self.main_layout = QVBoxLayout()
        self.main_layout.setContentsMargins(10, 10, 10, 10)

        # Les 3 layouts horizontaux qui contiennent 1:les machines, 2:iris & status, 3:les commandes
        self.cmd_ZP_layout = QHBoxLayout()
        self.cmd_ZP_layout.setContentsMargins(0, 0, 0, 0)
        self.cmd_ZP_layout.setSpacing(1)
        policy = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.cmd_ZP_layout.setSizeConstraint(self.cmd_ZP_layout.SetFixedSize)
        self.cmd_layout = QHBoxLayout()
        self.cmd_layout.setContentsMargins(0, 0, 0, 0)
        self.cmd_layout.setSpacing(1)
        self.status_layout = QHBoxLayout()
        self.head_layout = QGridLayout()
        # Fonts
        self.fontlabel = QFont('msyh', 15, 100)
        self.font_zassist = QFont('msyh', 13, 100)

        # Iris
        self.switch_diaph = wb.SwitchDiaphButton('Diaph', self)
        self.switch_diaph.valueChanged.connect(lambda widget=self.switch_diaph: self.switch_diaphchanged(widget))
        self.switch_diaph.hide()

        # -----------------------------------------------------------------------------------------------Motor release + limits + Optique + Config
        self.btn_release = wb.MotorButton()
        self.btn_release.setText("Motor\nOFF")
        self.btn_release.clicked.connect(self.releasemotor)

        self.btn_limits = wb.MotorButton()
        self.btn_limits.setCheckable(False)
        self.btn_limits.setText("Set\nLimits")
        self.btn_limits.clicked.connect(self.motorlimits)

        self.btn_reset_opt = wb.MotorButton()
        self.btn_reset_opt.setCheckable(False)
        self.btn_reset_opt.setText("Reset\nOptique")
        self.btn_reset_opt.clicked.connect(self.resetoptique)

        self.btn_config = wb.MotorButton()
        self.btn_config.setCheckable(False)
        self.btn_config.setText("Settings")
        self.btn_config.clicked.connect(self.userconfig)
        # self.btn_config.hide()

        self.btn_memoire = wb.WidgetMemoire(self.memoire_position, self.slidervaluechanged)
        self.btn_memoire.setEnabled(False)

        self.btn_target = wb.MotorButton()
        self.btn_target.setCheckable(False)
        self.btn_target.setText("Vignette\nTargeting")
        self.btn_target.clicked.connect(self.go_targeting)

        # self.btn_memoire.hide()
        self.warningpanel = wb.WarningPanel()

        # ZOOM FOCUS STATUS --------------------------------------------------------------------------------STATUS !!!!
        self.container_zp = wb.StatusLabel(self.image_zoompoint_cross)

        # PAN TILT STATUS
        self.container_joy = wb.StatusLabel(self.image_joystick_cross)

        # TRACK LIFT STATUS
        self.container_lifttrack = wb.StatusLabel(self.image_lifttrack_cross)

        #  BUTEE FURIO STATUS
        self.container_butees = wb.StatusLabel(self.pictures.image_status_butee_none)
        self.container_butees.hide()
        #  FURIO LAYOUTS ----------------------------------------------------------------------------------- FURIO LAYOUTS
        #  TRACK LAYOUT  ----------------------------------------------------------------------------------- TRACK LAYOUTS
        self.trackcontainer = wb.StyledFrame()
        self.track_layout = QVBoxLayout(self.trackcontainer)
        self.track_frame = QFrame()
        self.track_frame.setContentsMargins(-50, 0, 8, -50)
        self.track_frame.setFixedHeight(80)
        # self.track_frame.setFixedWidth(150)
        self.title_track_layout = QHBoxLayout(self.track_frame)
        self.title_track_layout.setContentsMargins(0, 0, 0, 0)  # (Marge Gauche, Marche Haut, Marche droite, Marge bas)
        # self.title_track_layout.setSpacing(10)
        self.slider_track_layout = QHBoxLayout()
        self.layerlinetrack = QHBoxLayout()
        self.layerlabeltrack = QHBoxLayout()

        #  LIFT LAYOUT  ------------------------------------------------------------------------------------ LIFT LAYOUTS
        self.liftcontainer = wb.StyledFrame()
        self.lift_layout = QVBoxLayout(self.liftcontainer)
        self.lift_frame = QFrame()
        self.lift_frame.setFixedHeight(80)
        # self.furio_frame.setFixedWidth(180)
        self.title_lift_layout = QHBoxLayout(self.lift_frame)
        self.slider_lift_layout = QHBoxLayout()
        self.layerlinelift = QHBoxLayout()
        self.layerlabellift = QHBoxLayout()

        #  FOCUS LAYOUT ----------------------------------------------------------------------------------- FOCUS LAYOUT
        self.focuscontainer = wb.StyledFrame()
        self.focuscontainer.setFixedWidth(270)
        self.focus_layout = QVBoxLayout(self.focuscontainer)
        self.focus_h_layout = QHBoxLayout()
        self.focus_frame = QFrame()
        self.focus_frame.setMinimumHeight(80)
        self.focus_frame.setMaximumHeight(80)
        self.title_focus_layout = QHBoxLayout(self.focus_frame)
        self.slider_focus_layout = QVBoxLayout()
        self.focus_memory_layout = QVBoxLayout()

        # ZOOM LAYOUT -------------------------------------------------------------------------------------- ZOOM LAYOUT
        self.zoomcontainer = wb.StyledFrame()
        self.zoomcontainer.setFixedWidth(114)
        self.zoom_layout = QVBoxLayout(self.zoomcontainer)
        self.zoom_layout.setContentsMargins(0, 25, 0, 0)  # (gauche, haut, droite ,bas)
        self.zoom_layout.setSpacing(5)
        self.zoom_frame = QFrame()
        self.zoom_frame.setFixedHeight(40)
        # self.zoom_frame.setFixedWidth(180)
        self.title_zoom_layout = QHBoxLayout(self.zoom_frame)
        self.title_zoom_layout.setContentsMargins(0, 0, 0, 0)
        self.slider_zoom_layout = QHBoxLayout()

        # ZOOM ASSIST ------------------------------------------------------------------------------- ZOOM ASSIST LAYOUT
        self.zoom_assist_container = wb.StyledFrame()
        self.zoom_assist_container.setMinimumWidth(114)
        self.zoom_assist_layout = QVBoxLayout(self.zoom_assist_container)
        self.zoom_assist_layout.setContentsMargins(0, 25, 0, 0)  # (gauche, haut, droite ,bas)
        self.zoom_assist_layout.setSpacing(5)
        self.zoom_assist_frame = QFrame()
        self.zoom_assist_frame.setFixedHeight(40)
        # self.zoom_frame.setFixedWidth(180)
        self.title_zoom_assist_layout = QHBoxLayout(self.zoom_assist_frame)
        self.title_zoom_assist_layout.setContentsMargins(0, 0, 0, 0)
        self.slider_zoom_assist_layout = QHBoxLayout()

        # PAN LAYOUT --------------------------------------------------------------------------------------- PAN LAYOUT
        self.pancontainer = wb.StyledFrame()
        # self.pancontainer.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.pan_layout = QVBoxLayout(self.pancontainer)
        self.pan_frame = QFrame()
        self.pan_frame.setFixedHeight(80)
        # self.pancontainer.setFixedWidth(308)
        self.title_pan_layout = QHBoxLayout(self.pan_frame)
        self.slider_pan_layout = QHBoxLayout()
        self.layerlinepan = QHBoxLayout()
        self.layerlabelpan = QHBoxLayout()

        # TILT LAYOUT ------------------------------------------------------------------------------------- TILT LAYOUT
        self.tiltcontainer = wb.StyledFrame()
        # self.tiltcontainer.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.tilt_layout = QVBoxLayout(self.tiltcontainer)
        self.tilt_frame = QFrame()

        self.tilt_frame.setFixedHeight(80)
        # self.tiltcontainer.setFixedWidth(308)
        self.title_tilt_layout = QHBoxLayout(self.tilt_frame)
        self.slider_tilt_layout = QHBoxLayout()
        self.layerlinetilt = QHBoxLayout()
        self.layerlabeltilt = QHBoxLayout()

        # HEAD LAYOUTS ----------------------------------------------------------------------------------MACHINE LAYOUTS
        self.machine_layouts = [QVBoxLayout(), QVBoxLayout(),
                                QVBoxLayout(), QVBoxLayout(),
                                QVBoxLayout()]

        # Main layout remplissage
        self.main_layout.addLayout(self.head_layout, Qt.AlignCenter)
        self.main_layout.addLayout(self.status_layout, Qt.AlignCenter)
        self.main_layout.addLayout(self.cmd_ZP_layout, Qt.AlignTop)

        # self.main_layout.addLayout(self.cmd_layout, Qt.AlignTop)

        # CONTAINER LAYOUT ---------------------------------------------------------------------------- CONTAINER LAYOUT

        self.framed_status = QHBoxLayout()
        self.framed_iris = QHBoxLayout()
        self.framed_warning = QHBoxLayout()

        self.status_layout.addLayout(self.framed_iris, Qt.AlignLeft)
        self.status_layout.addLayout(self.framed_warning, Qt.AlignCenter)
        self.status_layout.addLayout(self.framed_status, Qt.AlignRight)

        self.framed_iris.addWidget(self.switch_diaph, Qt.AlignCenter, Qt.AlignCenter)
        self.framed_iris.addWidget(self.btn_release, Qt.AlignCenter, Qt.AlignCenter)
        self.framed_iris.addWidget(self.btn_limits, Qt.AlignCenter, Qt.AlignCenter)
        self.framed_iris.addWidget(self.btn_reset_opt, Qt.AlignCenter, Qt.AlignCenter)
        self.framed_iris.addWidget(self.btn_config, Qt.AlignCenter, Qt.AlignCenter)
        self.framed_iris.addWidget(self.btn_target, Qt.AlignCenter, Qt.AlignCenter)
        self.framed_iris.addWidget(self.btn_memoire, Qt.AlignCenter, Qt.AlignCenter)

        self.framed_warning.addWidget(self.warningpanel, Qt.AlignCenter, Qt.AlignCenter)

        self.framed_status.addWidget(self.container_butees, Qt.AlignCenter, Qt.AlignCenter)
        self.framed_status.addWidget(self.container_lifttrack, Qt.AlignCenter, Qt.AlignCenter)
        self.framed_status.addWidget(self.container_zp, Qt.AlignCenter, Qt.AlignCenter)
        self.framed_status.addWidget(self.container_joy, Qt.AlignCenter, Qt.AlignCenter)

        self.cmd_layout.addWidget(self.pancontainer)
        self.cmd_layout.addWidget(self.tiltcontainer)
        self.cmd_layout.addWidget(self.trackcontainer)
        self.cmd_layout.addWidget(self.liftcontainer)
        self.trackcontainer.hide()
        self.liftcontainer.hide()

        #  panneau de commande machines --------------------------------------------------------------------- MACHINES
        self.machine_btn_group = QButtonGroup()
        self.machine_btn1 = wb.MachineButton(self)
        self.font_machine_label = QFont('msyh', 6, 100)

        self.machine_btn2 = wb.MachineButton(self)
        self.machine_btn3 = wb.MachineButton(self)
        self.machine_btn4 = wb.MachineButton(self)
        self.machine_btn5 = wb.MachineButton(self)

        self.machine_dropper = wb.DropMyButton()
        self.machine_dropper.connection = lambda widget=self.machine_dropper: self.reorder_machine_button(0)
        self.machine_dropper2 = wb.DropMyButton()
        self.machine_dropper2.connection = lambda widget=self.machine_dropper2: self.reorder_machine_button(1)
        self.machine_dropper3 = wb.DropMyButton()
        self.machine_dropper3.connection = lambda widget=self.machine_dropper3: self.reorder_machine_button(2)
        self.machine_dropper4 = wb.DropMyButton()
        self.machine_dropper4.connection = lambda widget=self.machine_dropper4: self.reorder_machine_button(3)
        self.machine_dropper5 = wb.DropMyButton()
        self.machine_dropper5.connection = lambda widget=self.machine_dropper5: self.reorder_machine_button(4)
        """self.machine_dropper6 = wb.DropMyButton()
        self.machine_dropper6.connection = lambda widget=self.machine_dropper6: self.reorder_machine_button(4)"""

        self.btn_machine_list.extend((self.machine_btn1, self.machine_btn2,
                                      self.machine_btn3, self.machine_btn4, self.machine_btn5))

        self.dropper_machine_list.extend((self.machine_dropper, self.machine_dropper2,
                                          self.machine_dropper3, self.machine_dropper4, self.machine_dropper5))

        ctr = 0
        ctr_pos = 0
        for button in self.btn_machine_list:
            button.clicked.connect(self.whichmachineselected)
            self.machine_layouts[ctr].addWidget(button, Qt.AlignCenter, Qt.AlignCenter)
            self.machine_btn_group.addButton(button)
            button.setCheckable(True)
            button.hide()
            self.head_layout.addWidget(self.dropper_machine_list[ctr], 0, ctr_pos)
            self.head_layout.addLayout(self.machine_layouts[ctr], 0, ctr_pos + 1)
            ctr += 1
            ctr_pos += 2

        # self.head_layout.addWidget(self.dropper_machine_list[5], 0, 10)
        # Panneau de commande FURIO ------------------------------------------------------------------------- cmd FURIO

        self.label_track = QLabel()
        self.label_track.setText("TRACK")
        self.label_track.setAlignment(Qt.AlignLeft)
        self.label_track.setFont(self.fontlabel)

        self.label_lift = QLabel()
        self.label_lift.setText("LIFT")
        self.label_lift.setAlignment(Qt.AlignCenter)
        self.label_lift.setFont(self.fontlabel)

        self.btninverttrack = wb.InvertButton('Invert', self)
        self.btninvertlift = wb.InvertButton('Invert', self)

        self.slider_ratio_track = wb.StyledSlider()
        self.slider_ratio_track.valueChanged.connect(lambda widget=self.slider_ratio_track: self.slidervaluechanged(widget))

        self.slider_ratio_lift = wb.StyledSlider()
        self.slider_ratio_lift.valueChanged.connect(lambda widget=self.slider_ratio_lift: self.slidervaluechanged(widget))

        self.slider_vitesse_track = wb.StyledSlider()
        self.slider_vitesse_track.setRange(0, 1000)
        self.slider_vitesse_track.valueChanged.connect(lambda widget=self.slider_vitesse_track: self.slidervaluechanged(widget))

        self.slider_vitesse_lift = wb.StyledSlider()
        self.slider_vitesse_lift.setRange(0, 1000)
        self.slider_vitesse_lift.valueChanged.connect(lambda widget=self.slider_vitesse_lift: self.slidervaluechanged(widget))

        self.slider_courbe_track = wb.StyledSlider()
        self.slider_courbe_track.valueChanged.connect(lambda widget=self.slider_courbe_track: self.slidervaluechanged(widget))

        self.slider_courbe_lift = wb.StyledSlider()
        self.slider_courbe_lift.valueChanged.connect(lambda widget=self.slider_courbe_lift: self.slidervaluechanged(widget))

        self.linetrack_ratio = wb.DigitalLine()
        self.linetrack_ratio.setText("0")

        self.linelift_ratio = wb.DigitalLine()
        self.linelift_ratio.setText("0")

        self.linetrack_vitesse = wb.DigitalLine()
        self.linetrack_vitesse.setText("0")

        self.linelift_vitesse = wb.DigitalLine()
        self.linelift_vitesse.setText("0")

        self.linetrack_courbe = wb.DigitalLine()
        self.linetrack_courbe.setText("0")

        self.linelift_courbe = wb.DigitalLine()
        self.linelift_courbe.setText("0")

        self.label_ratio_track = QLabel("SMOOTH")
        self.label_ratio_track.setFont(QFont('Arial', 8))
        self.label_ratio_track.setAlignment(Qt.AlignCenter)

        self.label_ratio_lift = QLabel("SMOOTH")
        self.label_ratio_lift.setFont(QFont('Arial', 8))
        self.label_ratio_lift.setAlignment(Qt.AlignCenter)

        self.label_vitesse_track = QLabel("VITESSE")
        self.label_vitesse_track.setFont(QFont('Arial', 8))
        self.label_vitesse_track.setAlignment(Qt.AlignCenter)

        self.label_vitesse_lift = QLabel("VITESSE")
        self.label_vitesse_lift.setFont(QFont('Arial', 8))
        self.label_vitesse_lift.setAlignment(Qt.AlignCenter)

        self.label_courbe_track = QLabel("COURBE")
        self.label_courbe_track.setFont(QFont('Arial', 8))
        self.label_courbe_track.setAlignment(Qt.AlignCenter)

        self.label_courbe_lift = QLabel("COURBE")
        self.label_courbe_lift.setFont(QFont('Arial', 8))
        self.label_courbe_lift.setAlignment(Qt.AlignCenter)

        self.track_layout.addWidget(self.track_frame, Qt.AlignCenter, Qt.AlignTop)
        self.title_track_layout.addWidget(self.label_track, Qt.AlignCenter, Qt.AlignCenter)
        self.title_track_layout.addWidget(self.btninverttrack, Qt.AlignCenter, Qt.AlignCenter)
        self.track_layout.addLayout(self.slider_track_layout)
        self.slider_track_layout.addWidget(self.slider_ratio_track, Qt.AlignCenter, Qt.AlignJustify)
        self.slider_track_layout.addWidget(self.slider_courbe_track, Qt.AlignCenter, Qt.AlignJustify)
        self.slider_track_layout.addWidget(self.slider_vitesse_track, Qt.AlignCenter, Qt.AlignJustify)

        self.track_layout.addLayout(self.layerlinetrack)
        self.layerlinetrack.addWidget(self.linetrack_ratio, Qt.AlignCenter, Qt.AlignTop)
        self.layerlinetrack.addWidget(self.linetrack_courbe, Qt.AlignCenter, Qt.AlignTop)
        self.layerlinetrack.addWidget(self.linetrack_vitesse, Qt.AlignCenter, Qt.AlignTop)

        self.track_layout.addLayout(self.layerlabeltrack)
        self.layerlabeltrack.addWidget(self.label_ratio_track, Qt.AlignCenter, Qt.AlignJustify)
        self.layerlabeltrack.addWidget(self.label_courbe_track, Qt.AlignCenter, Qt.AlignJustify)
        self.layerlabeltrack.addWidget(self.label_vitesse_track, Qt.AlignCenter, Qt.AlignJustify)

        self.lift_layout.addWidget(self.lift_frame, Qt.AlignCenter, Qt.AlignTop)
        self.title_lift_layout.addWidget(self.label_lift, Qt.AlignCenter, Qt.AlignCenter)
        self.title_lift_layout.addWidget(self.btninvertlift, Qt.AlignCenter, Qt.AlignCenter)
        self.lift_layout.addLayout(self.slider_lift_layout)
        self.slider_lift_layout.addWidget(self.slider_ratio_lift, Qt.AlignCenter, Qt.AlignJustify)
        self.slider_lift_layout.addWidget(self.slider_courbe_lift, Qt.AlignCenter, Qt.AlignJustify)
        self.slider_lift_layout.addWidget(self.slider_vitesse_lift, Qt.AlignCenter, Qt.AlignJustify)

        self.lift_layout.addLayout(self.layerlinelift)
        self.layerlinelift.addWidget(self.linelift_ratio, Qt.AlignCenter, Qt.AlignTop)
        self.layerlinelift.addWidget(self.linelift_courbe, Qt.AlignCenter, Qt.AlignTop)
        self.layerlinelift.addWidget(self.linelift_vitesse, Qt.AlignCenter, Qt.AlignTop)

        self.lift_layout.addLayout(self.layerlabellift)
        self.layerlabellift.addWidget(self.label_ratio_lift, Qt.AlignCenter, Qt.AlignJustify)
        self.layerlabellift.addWidget(self.label_courbe_lift, Qt.AlignCenter, Qt.AlignJustify)
        self.layerlabellift.addWidget(self.label_vitesse_lift, Qt.AlignCenter, Qt.AlignJustify)

        # Panneau de commande Focus -------------------------------------------------------------------------cmd FOCUS
        self.label_focus = QLabel()
        self.label_focus.setText("FOCUS")
        self.label_focus.setAlignment(Qt.AlignCenter)
        self.label_focus.setFont(self.fontlabel)
        self.label_focus.setFixedWidth(150)
        self.btninvertfocus = wb.InvertButton('Invert', self)

        self.btn_memory_focus1 = wb.MemoryFocusButton('', self)
        self.btn_memory_focus1.clicked.connect(self.memory_action)
        self.btn_memory_focus1.setText("memo 1")
        self.btn_memory_focus1.mem_number = 1

        self.btn_memory_focus2 = wb.MemoryFocusButton('', self)
        self.btn_memory_focus2.clicked.connect(self.memory_action)
        self.btn_memory_focus2.setText("memo 2")
        self.btn_memory_focus2.mem_number = 2

        self.btn_memory_focus3 = wb.MemoryFocusButton('', self)
        self.btn_memory_focus3.setText("memo 3")
        self.btn_memory_focus3.clicked.connect(self.memory_action)
        self.btn_memory_focus3.mem_number = 3

        self.btn_memory_focus4 = wb.MemoryFocusButton('', self)
        self.btn_memory_focus4.setText("memo 4")
        self.btn_memory_focus4.clicked.connect(self.memory_action)
        self.btn_memory_focus4.mem_number = 4

        self.list_btn_focus = [self.btn_memory_focus1, self.btn_memory_focus2, self.btn_memory_focus3, self.btn_memory_focus4]
        # self.btn_memory_focus4.clicked.connect(self.quitapp)

        self.btn_memory_iris1 = wb.MemoryFocusButton('', self)
        self.btn_memory_iris1.clicked.connect(self.memory_action)
        self.btn_memory_iris1.setText("memo 1")
        self.btn_memory_iris1.mem_number = 1

        self.btn_memory_iris2 = wb.MemoryFocusButton('', self)
        self.btn_memory_iris2.clicked.connect(self.memory_action)
        self.btn_memory_iris2.setText("memo 2")
        self.btn_memory_iris2.mem_number = 2

        self.btn_memory_iris3 = wb.MemoryFocusButton('', self)
        self.btn_memory_iris3.setText("memo 3")
        self.btn_memory_iris3.clicked.connect(self.memory_action)
        self.btn_memory_iris3.mem_number = 3

        self.btn_memory_iris4 = wb.MemoryFocusButton('', self)
        self.btn_memory_iris4.setText("memo 4")
        self.btn_memory_iris4.clicked.connect(self.memory_action)
        self.btn_memory_iris4.mem_number = 4

        self.indicator_focus = wb.IndicatorFocus()
        self.indicator_focus.setFixedWidth(150)
        self.indicator_focus.setFixedHeight(300)

        self.slider_focus_layout.addWidget(self.indicator_focus, Qt.AlignTop, Qt.AlignTop)

        self.focus_layout.addWidget(self.focus_frame, Qt.AlignCenter, Qt.AlignCenter)
        self.title_focus_layout.addWidget(self.label_focus, Qt.AlignCenter, Qt.AlignCenter)
        self.title_focus_layout.addWidget(self.btninvertfocus, Qt.AlignCenter, Qt.AlignCenter)

        self.focus_layout.addLayout(self.focus_h_layout)
        self.focus_h_layout.addLayout(self.slider_focus_layout, Qt.AlignTop)
        self.focus_h_layout.addLayout(self.focus_memory_layout, Qt.AlignCenter)
        self.focus_memory_layout.addWidget(self.btn_memory_focus1, Qt.AlignCenter, Qt.AlignCenter)
        self.focus_memory_layout.addWidget(self.btn_memory_focus2, Qt.AlignCenter, Qt.AlignCenter)
        self.focus_memory_layout.addWidget(self.btn_memory_focus3, Qt.AlignCenter, Qt.AlignCenter)
        self.focus_memory_layout.addWidget(self.btn_memory_focus4, Qt.AlignCenter, Qt.AlignCenter)

        self.focus_memory_layout.addWidget(self.btn_memory_iris1, Qt.AlignCenter, Qt.AlignCenter)
        self.focus_memory_layout.addWidget(self.btn_memory_iris2, Qt.AlignCenter, Qt.AlignCenter)
        self.focus_memory_layout.addWidget(self.btn_memory_iris3, Qt.AlignCenter, Qt.AlignCenter)
        self.focus_memory_layout.addWidget(self.btn_memory_iris4, Qt.AlignCenter, Qt.AlignCenter)

        self.btn_memory_iris1.hide()
        self.btn_memory_iris2.hide()
        self.btn_memory_iris3.hide()
        self.btn_memory_iris4.hide()

        # Panneau de commande Zoom --------------------------------------------------------------------------cmd ZOOM
        self.btninvertzoom = wb.InvertButton('Invert', self)

        self.slider_zoom = wb.StyledSlider()
        self.slider_zoom.valueChanged.connect(lambda widget=self.slider_zoom: self.slidervaluechanged(widget))

        self.label_zoom = QLabel()
        self.label_zoom.setText("ZOOM")
        self.label_zoom.setAlignment(Qt.AlignCenter)
        self.label_zoom.setFont(self.fontlabel)
        self.linezoom = wb.DigitalLine()
        self.linezoom.setText("0")

        self.label_vitesse_zoom = QLabel("VITESSE")
        self.label_vitesse_zoom.setFont(QFont('Arial', 8))
        self.label_vitesse_zoom.setAlignment(Qt.AlignCenter)

        self.title_zoom_layout.addWidget(self.label_zoom, Qt.AlignCenter, Qt.AlignCenter)
        self.zoom_layout.addWidget(self.zoom_frame, Qt.AlignCenter, Qt.AlignCenter)
        self.zoom_layout.addWidget(self.btninvertzoom, Qt.AlignCenter, Qt.AlignCenter)

        # self.zoom_layout.addLayout(self.slider_zoom_layout)
        self.zoom_layout.addWidget(QLabel(), Qt.AlignBottom, Qt.AlignCenter)  # spacer
        self.zoom_layout.addWidget(self.slider_zoom, Qt.AlignBottom, Qt.AlignCenter)
        self.zoom_layout.addWidget(self.linezoom, Qt.AlignBottom, Qt.AlignCenter)
        self.zoom_layout.addWidget(self.label_vitesse_zoom, Qt.AlignCenter, Qt.AlignTop)

        # Panneau de commande Zoom assist ---------------------------------------------------------------cmd ZOOM ASSIST
        self.slider_zoom_assist = wb.StyledSlider()
        self.slider_zoom_assist.valueChanged.connect(lambda widget=self.slider_zoom_assist: self.slidervaluechanged(widget))

        self.voyant_onoff_zoom_assist = wb.VoyantOnOff('OFF')

        self.label_zoom_assist = QLabel()
        self.label_zoom_assist.setText("ZOOM\nASSIST")
        self.label_zoom_assist.setAlignment(Qt.AlignCenter)
        self.label_zoom_assist.setFont(self.font_zassist)
        self.linezoom_assist = wb.DigitalLine()
        self.linezoom_assist.setText("0")

        self.label_vitesse_zoom_assist = QLabel("RATIO")
        self.label_vitesse_zoom_assist.setFont(QFont('Arial', 8))
        self.label_vitesse_zoom_assist.setAlignment(Qt.AlignCenter)

        self.title_zoom_assist_layout.addWidget(self.label_zoom_assist, Qt.AlignCenter, Qt.AlignCenter)
        self.zoom_assist_layout.addWidget(self.zoom_assist_frame, Qt.AlignCenter, Qt.AlignCenter)
        self.zoom_assist_layout.addWidget(self.voyant_onoff_zoom_assist, Qt.AlignTop, Qt.AlignCenter)
        self.spacer_vertical = QLabel()
        self.spacer_vertical.setFixedHeight(35)
        self.zoom_assist_layout.addWidget(self.spacer_vertical, Qt.AlignCenter, Qt.AlignCenter)  # spacer

        self.zoom_assist_layout.addWidget(self.slider_zoom_assist, Qt.AlignBottom, Qt.AlignCenter)
        self.zoom_assist_layout.addWidget(self.linezoom_assist, Qt.AlignBottom, Qt.AlignCenter)
        self.zoom_assist_layout.addWidget(self.label_vitesse_zoom_assist, Qt.AlignCenter, Qt.AlignTop)

        # Panneau de commande PAN------------------------------------------------------------------------------cmd PAN
        self.btninvertpan = wb.InvertButton('Invert', self)

        self.label_pan = QLabel()
        self.label_pan.setText("PAN")
        self.label_pan.setAlignment(Qt.AlignCenter)
        self.label_pan.setFont(self.fontlabel)

        self.pan_layout.addWidget(self.pan_frame, Qt.AlignCenter, Qt.AlignTop)
        self.title_pan_layout.addWidget(self.label_pan, Qt.AlignCenter, Qt.AlignCenter)
        self.title_pan_layout.addWidget(self.btninvertpan, Qt.AlignCenter, Qt.AlignCenter)

        self.pan_layout.addLayout(self.slider_pan_layout, Qt.AlignTop)
        self.slider_ratio_pan = wb.StyledSlider()
        self.slider_ratio_pan.valueChanged.connect(lambda widget=self.slider_ratio_pan: self.slidervaluechanged(widget))

        self.slider_courbe_pan = wb.StyledSlider()
        self.slider_courbe_pan.valueChanged.connect(
            lambda widget=self.slider_courbe_pan: self.slidervaluechanged(widget))

        self.slider_vitesse_pan = wb.StyledSlider()
        self.slider_vitesse_pan.setRange(0, 1000)
        self.slider_vitesse_pan.valueChanged.connect(
            lambda widget=self.slider_vitesse_pan: self.slidervaluechanged(widget))

        self.slider_pan_layout.addWidget(self.slider_ratio_pan, Qt.AlignCenter, Qt.AlignTop)
        self.slider_pan_layout.addWidget(self.slider_courbe_pan, Qt.AlignCenter, Qt.AlignTop)
        self.slider_pan_layout.addWidget(self.slider_vitesse_pan, Qt.AlignCenter, Qt.AlignTop)

        self.pan_layout.addLayout(self.layerlinepan)

        self.linepan_courbe = wb.DigitalLine()
        self.linepan_courbe.setText("0")

        self.linepan_vit = wb.DigitalLine()
        self.linepan_vit.setText("0")

        self.linepan_ratio = wb.DigitalLine()
        self.linepan_ratio.setText("0")

        self.layerlinepan.addWidget(self.linepan_ratio, Qt.AlignCenter, Qt.AlignTop)
        self.layerlinepan.addWidget(self.linepan_courbe, Qt.AlignCenter, Qt.AlignTop)
        self.layerlinepan.addWidget(self.linepan_vit, Qt.AlignCenter, Qt.AlignTop)

        self.pan_layout.addLayout(self.layerlabelpan)

        self.label_courbe_pan = QLabel("COURBE")
        self.label_courbe_pan.setFont(QFont('Arial', 8))
        self.label_courbe_pan.setAlignment(Qt.AlignCenter)

        self.label_ratio_pan = QLabel("SMOOTH")
        self.label_ratio_pan.setFont(QFont('Arial', 8))
        self.label_ratio_pan.setAlignment(Qt.AlignCenter)

        self.label_vitesse_pan = QLabel("VITESSE")
        self.label_vitesse_pan.setFont(QFont('Arial', 8))
        self.label_vitesse_pan.setAlignment(Qt.AlignCenter)

        self.layerlabelpan.addWidget(self.label_ratio_pan, Qt.AlignCenter, Qt.AlignCenter)
        self.layerlabelpan.addWidget(self.label_courbe_pan, Qt.AlignCenter, Qt.AlignCenter)
        self.layerlabelpan.addWidget(self.label_vitesse_pan, Qt.AlignCenter, Qt.AlignCenter)

        # Panneau de commande TILT-------------------------------------------------------------------------cmd  TILT
        self.btninverttilt = wb.InvertButton('Invert', self)

        self.label_tilt = QLabel()
        self.label_tilt.setText("TILT")
        self.label_tilt.setAlignment(Qt.AlignCenter)
        self.label_tilt.setFont(self.fontlabel)

        self.tilt_layout.addWidget(self.tilt_frame, Qt.AlignCenter, Qt.AlignTop)
        self.title_tilt_layout.addWidget(self.label_tilt, Qt.AlignCenter, Qt.AlignCenter)
        self.title_tilt_layout.addWidget(self.btninverttilt, Qt.AlignCenter, Qt.AlignCenter)

        self.tilt_layout.addLayout(self.slider_tilt_layout)
        self.slider_ratio_tilt = wb.StyledSlider()

        self.slider_ratio_tilt.valueChanged.connect(
            lambda widget=self.slider_ratio_tilt: self.slidervaluechanged(widget))

        self.slider_courbe_tilt = wb.StyledSlider()
        self.slider_courbe_tilt.valueChanged.connect(
            lambda widget=self.slider_courbe_tilt: self.slidervaluechanged(widget))

        self.slider_vitesse_tilt = wb.StyledSlider()
        self.slider_vitesse_tilt.setRange(0, 1000)
        self.slider_vitesse_tilt.valueChanged.connect(
            lambda widget=self.slider_vitesse_tilt: self.slidervaluechanged(widget))

        self.slider_tilt_layout.addWidget(self.slider_ratio_tilt, Qt.AlignCenter, Qt.AlignTop)
        self.slider_tilt_layout.addWidget(self.slider_courbe_tilt, Qt.AlignCenter, Qt.AlignTop)
        self.slider_tilt_layout.addWidget(self.slider_vitesse_tilt, Qt.AlignCenter, Qt.AlignTop)

        self.tilt_layout.addLayout(self.layerlinetilt)

        self.linetilt_courbe = wb.DigitalLine()
        self.linetilt_courbe.setText("0")

        self.linetilt_vit = wb.DigitalLine()
        self.linetilt_vit.setText("0")

        self.linetilt_ratio = wb.DigitalLine()
        self.linetilt_ratio.setText("0")

        self.layerlinetilt.addWidget(self.linetilt_ratio, Qt.AlignCenter, Qt.AlignTop)
        self.layerlinetilt.addWidget(self.linetilt_courbe, Qt.AlignCenter, Qt.AlignTop)
        self.layerlinetilt.addWidget(self.linetilt_vit, Qt.AlignCenter, Qt.AlignTop)

        self.tilt_layout.addLayout(self.layerlabeltilt)

        self.label_courbe_tilt = QLabel("COURBE")
        self.label_courbe_tilt.setFont(QFont('Arial', 8))
        self.label_courbe_tilt.setAlignment(Qt.AlignCenter)

        self.label_ratio_tilt = QLabel("SMOOTH")
        self.label_ratio_tilt.setFont(QFont('Arial', 8))
        self.label_ratio_tilt.setAlignment(Qt.AlignCenter)

        self.label_vitesse_tilt = QLabel("VITESSE")
        self.label_vitesse_tilt.setFont(QFont('Arial', 8))
        self.label_vitesse_tilt.setAlignment(Qt.AlignCenter)

        self.layerlabeltilt.addWidget(self.label_ratio_tilt, Qt.AlignCenter, Qt.AlignCenter)
        self.layerlabeltilt.addWidget(self.label_courbe_tilt, Qt.AlignCenter, Qt.AlignCenter)
        self.layerlabeltilt.addWidget(self.label_vitesse_tilt, Qt.AlignCenter, Qt.AlignCenter)

        # on grise les commandes non connectés
        self.tiltcontainer.setEnabled(False)
        self.pancontainer.setEnabled(False)
        self.zoomcontainer.setEnabled(False)
        self.trackcontainer.setEnabled(False)
        self.liftcontainer.setEnabled(False)
        self.zoom_assist_container.setEnabled(False)
        self.focuscontainer.setEnabled(False)
        self.indicator_focus.disable_focus(True)

        self.widgetscroll = wb.ScrollWidget(self.cmd_layout)
        self.widgetscroll.setStyleSheet("""background : transparent """)
        self.widgetscroll.setMinimumWidth(650)
        self.widgetscroll.setFixedHeight(390)
        self.cmd_ZP_layout.addWidget(self.focuscontainer, Qt.AlignLeft, Qt.AlignLeft)
        self.cmd_ZP_layout.addWidget(self.zoomcontainer, Qt.AlignLeft, Qt.AlignLeft)
        self.cmd_ZP_layout.addWidget(self.zoom_assist_container, Qt.AlignLeft, Qt.AlignLeft)
        self.cmd_ZP_layout.addWidget(self.widgetscroll, Qt.AlignLeft, Qt.AlignLeft)
        self.setLayout(self.main_layout)
        self.userdial = ""

    def go_targeting(self):
        if self.machine_selected != "":
            self.parent.set_second()
        else:
            self.warningpanel.setTempTips("Veuillez d'abord\nselectionner une machine", 5)

    def logging(self):
        for threads in self.p.threads():
            if threads[0] == libc.syscall(thread_ID_number):
                self.thread_info = threads
                break
        calc = round(self.p.cpu_percent(0.1) * ((self.thread_info.system_time + self.thread_info.user_time) / sum(self.p.cpu_times())), 1)
        logging.info("CPU Usage:" + str(calc) + "% ") if calc > 15 else None
        # self.timer.stop()

    def update_status_butee(self):
        # [Gauche, Droite, Haut, Bas]
        witch_butee = {
            (False, False, False, False): self.pictures.image_status_butee_none,
            (False, False, True, False): self.pictures.image_status_butee_top,
            (False, False, False, True): self.pictures.image_status_butee_bottom,
            (True, False, False, False): self.pictures.image_status_butee_left,
            (False, True, False, False): self.pictures.image_status_butee_right,
            (True, False, True, False): self.pictures.image_status_butee_top_left,
            (False, True, True, False): self.pictures.image_status_butee_top_right,
            (True, False, False, True): self.pictures.image_status_butee_bottom_left,
            (False, True, False, True): self.pictures.image_status_butee_bottom_right,
        }
        image_toset = witch_butee.get(self.flag_furio, self.pictures.image_status_butee_none)
        self.container_butees.changepixmap(image_toset, "")

    # Comme son nom l'indique...
    def reorder_machine_button(self, place):
        for ctr in range(len(self.btn_machine_list)):
            self.btn_machine_list[ctr].hide()
            if self.btn_machine_list[ctr].isdragged:
                for layout in self.machine_layouts:
                    if layout.itemAt(0).widget() == self.btn_machine_list[ctr]:
                        self.current_drag_button = self.machine_layouts.index(layout)
                self.btn_machine_list[ctr].isdragged = False
            self.head_layout.removeItem(self.machine_layouts[ctr])
            self.head_layout.removeWidget(self.dropper_machine_list[ctr])

        if self.current_drag_button < place:
            self.machine_layouts.insert(place - 1, self.machine_layouts.pop(self.current_drag_button))
        elif self.current_drag_button > place:
            self.machine_layouts.insert(place, self.machine_layouts.pop(self.current_drag_button))
        else:
            pass
        ctr = 0
        ctr_pos = 0
        for button in self.btn_machine_list:
            if self.btn_machine_list.index(button) < len(self.machines_list):
                button.show()
            self.head_layout.addWidget(self.dropper_machine_list[ctr], 0, ctr_pos)
            self.head_layout.addLayout(self.machine_layouts[ctr], 0, ctr_pos + 1)
            ctr += 1
            ctr_pos += 2

    # Callback boutons memoire position
    def memoire_position(self):
        self.current_memory_pos_button = self.sender()
        witchmemo = {
            "1": 1,
            "2": 2,
            "3": 3,
            "4": 4,
            "5": 5,
        }
        self.memory_position_number = witchmemo.get(self.sender().text().split("°")[1], 6)
        if self.current_memory_pos_button.state == 0 and not self.current_memory_pos_button.memory_raz:
            self.call_memory_position = True
            self.current_memory_pos_button.change_state()
            self.current_memory_pos_button.state = 1
        elif self.current_memory_pos_button.state == 1:
            self.recall_memory_position = True
        else:
            self.btn_memoire.unsetsnap(self.memory_position_number)
            self.current_memory_pos_button.memory_raz = False

    # Callback boutons limites
    def motorlimits(self):
        self.limitdial = wb.LimitDialog(self.lim_haut[self.index], self.lim_bas[self.index], self.lim_gauche[self.index], self.lim_droite[self.index])

        self.save_state_top[self.index] = self.lim_haut[self.index]
        self.save_state_bot[self.index] = self.lim_bas[self.index]
        self.save_state_left[self.index] = self.lim_gauche[self.index]
        self.save_state_right[self.index] = self.lim_droite[self.index]

        self.flaglimdiag = True

    # Callback boutons moteur on/off
    def releasemotor(self):
        self.motor_release = True

    # Callback boutons reset de l'optique
    def resetoptique(self):
        self.rstopt = True

    # Callback boutons settings user
    def userconfig(self):
        self.userdial.show()
        action = ""
        if self.userdial.reponse:
            self.flag_emi_cadreur = "c"
            cadreur, action = self.userdial.reponse
        if self.userdial.reponse_emi:
            self.flag_emi_cadreur = "e"
            emission, action = self.userdial.reponse_emi

        if action == 'save':
            if self.flag_emi_cadreur == "e":
                print("save emi, a remplir, qu'est ce qu'on save ??")
            elif self.flag_emi_cadreur == "c":

                self.param_machine[self.index] = [int(self.linepan_ratio.getText()), int(self.linepan_courbe.getText()),
                                                  int(self.linepan_vit.getText()),
                                                  int(self.linetilt_ratio.getText()), int(self.linetilt_courbe.getText()),
                                                  int(self.linetilt_vit.getText()),
                                                  int(self.linetrack_ratio.getText()), int(self.linetrack_courbe.getText()),
                                                  int(self.linetrack_vitesse.getText()),
                                                  int(self.linelift_ratio.getText()), int(self.linelift_courbe.getText()),
                                                  int(self.linelift_vitesse.getText()),
                                                  int(self.linezoom.getText()), self.btninvertpan.isChecked(),
                                                  self.btninverttilt.isChecked(), self.btninvertzoom.isChecked(),
                                                  self.btninvertfocus.isChecked(), self.btninverttrack.isChecked(),
                                                  self.btninvertlift.isChecked(),
                                                  self.btn_memory_focus1.value_memorized[self.index] if self.btn_memory_focus1.state[self.index] != 1 else False,
                                                  self.btn_memory_focus2.value_memorized[self.index] if self.btn_memory_focus2.state[self.index] != 1 else False,
                                                  self.btn_memory_focus3.value_memorized[self.index] if self.btn_memory_focus3.state[self.index] != 1 else False,
                                                  self.btn_memory_focus4.value_memorized[self.index] if self.btn_memory_focus4.state[self.index] != 1 else False]
                """if self.index == "":
                    self.param_machine[self.old_index].append(self.machines_list[self.old_index])"""
                parametres = []
                for machines in range(len(self.machines_list)):
                    if self.machines_list[machines] != '' and self.param_machine[machines] != '':
                        print("machines", machines)
                        temp = self.param_machine[machines]
                        temp.append(self.machines_list[machines])
                        parametres.append(temp)
                    else:
                        pass
                self.datManager.enregistrer(parametres, cadreur)
                print("saving those settings ", parametres)

        elif action == 'recall':
            if self.flag_emi_cadreur == "e":
                print("recall emi")
            elif self.flag_emi_cadreur == 'c':
                param = self.datManager.charger(cadreur)
                if param:
                    for machines in range(len(self.machines_list)):
                        if self.machines_list[machines] != '':
                            for settings in param:
                                print("settings ", settings)
                                if self.machines_list[machines] == settings[23]:
                                    temp_list = []
                                    temp_list.append(settings)
                                    self.param_machine[self.machines_list.index(self.machines_list[machines])] = temp_list.pop()
                                    break
                        else:
                            pass
                    if self.machine_selected == "":
                        self.flag_reload_param = True
                        self.btn_machine_list[0].click()
                        self.paramsetter(0, 5 - self.param_machine.count(""))
                        self.btn_machine_list[0].click()

                    else:
                        self.flag_reload_param = True
                        self.paramsetter(0, 5 - self.param_machine.count(""))
                        self.btn_machine_list[self.machines_list.index(self.machine_selected)].click()
                else:
                    self.warningpanel.setTempTips("Le cadreur : " + cadreur + "\nn'a aucun paramètre enregistré", 5)
            else:
                pass
        else:
            pass

    # Methode des boutons memoire focus
    def memory_action(self):
        if self.sender() in [self.btn_memory_focus1, self.btn_memory_iris1]:
            if self.sender().state[self.index] == 1:
                self.sender().setText("Recall 1")
                self.sender().in_memory(self.index)
                self.sender().value_memorized[self.index] = self.indicator_focus.saveposfocus(0, self.index)
                self.sender().setbackgroundcolor()
                self.sender().setframe(True)

            elif self.sender().state[self.index] == 2:
                self.memory_value = self.sender().value_memorized[self.index]
                self.call_memory_focus = True
                self.indicator_focus.updateline(self.memory_value, str(self.memory_value))
                self.sender().setframe(True)
                self.sender().setText("Recall 1")
            else:
                self.sender().state[self.index] = 1
                self.indicator_focus.delposfocus(0)
                self.sender().setframe(False)

        elif self.sender() in [self.btn_memory_focus2, self.btn_memory_iris2]:
            if self.sender().state[self.index] == 1:
                self.sender().setText("Recall 2")
                self.sender().in_memory(self.index)
                self.sender().value_memorized[self.index] = self.indicator_focus.saveposfocus(1, self.index)
                self.sender().setbackgroundcolor()
                self.sender().setframe(True)
            elif self.sender().state[self.index] == 2:
                self.memory_value = self.sender().value_memorized[self.index]
                self.call_memory_focus = True
                self.indicator_focus.updateline(self.memory_value, str(self.memory_value))
                self.sender().setframe(True)
                self.sender().setText("Recall 2")
            else:
                self.sender().state[self.index] = 1
                self.indicator_focus.delposfocus(1)
                self.sender().setframe(False)

        elif self.sender() in [self.btn_memory_focus3, self.btn_memory_iris3]:
            if self.sender().state[self.index] == 1:
                self.sender().setText("Recall 3")
                self.sender().in_memory(self.index)
                self.sender().value_memorized[self.index] = self.indicator_focus.saveposfocus(2, self.index)
                self.sender().setbackgroundcolor()
                self.sender().setframe(True)
            elif self.sender().state[self.index] == 2:
                self.memory_value = self.sender().value_memorized[self.index]
                self.call_memory_focus = True
                self.indicator_focus.updateline(self.memory_value, str(self.memory_value))
                self.sender().setframe(True)
                self.sender().setText("Recall 3")
            else:
                self.sender().state[self.index] = 1
                self.indicator_focus.delposfocus(2)
                self.sender().setframe(False)

        elif self.sender() in [self.btn_memory_focus4, self.btn_memory_iris4]:
            if self.sender().state[self.index] == 1:
                self.sender().setText("Recall 4")
                self.sender().in_memory(self.index)
                self.sender().value_memorized[self.index] = self.indicator_focus.saveposfocus(3, self.index)
                self.sender().setbackgroundcolor()
                self.sender().setframe(True)
            elif self.sender().state[self.index] == 2:
                self.memory_value = self.sender().value_memorized[self.index]
                self.call_memory_focus = True
                self.indicator_focus.updateline(self.memory_value, str(self.memory_value))
                self.sender().setframe(True)
                self.sender().setText("Recall 4")
            else:
                self.sender().state[self.index] = 1
                self.indicator_focus.delposfocus(3)
                self.sender().setframe(False)
        else:
            pass
        self.machine_focus_position[self.index] = self.indicator_focus.getCurVal()
        for btn in self.list_btn_focus:
            if btn != self.sender():
                btn.setframe(False)

    # Methode gestion affichage en fonction de la machine selectionnee
    def whichmachineselected(self):
        self.index = self.btn_machine_list.index(self.sender())
        try:
            # print("clicked on this machine:", self.machines_list[self.index])
            self.machine_selected = self.machines_list[self.index]
            self.btn_memoire.setEnabled(True)
            self.flag_change_machine = True
            self.btn_memoire.current_machine = self.index
            identifier = self.machines_list[self.index].split('.')[2]

            if self.old_index == "init":
                autosaved_param = self.datManager.charger("autosave")
                if autosaved_param is not False:
                    self.old_index = ''
                    """self.param_machine[self.index] = autosaved_param
                    self.paramsetter(0, 5)"""
            elif self.old_index != '':
                if not self.flag_reload_param:
                    templistparam = [int(self.linepan_ratio.getText()), int(self.linepan_courbe.getText()),
                                     int(self.linepan_vit.getText()),
                                     int(self.linetilt_ratio.getText()), int(self.linetilt_courbe.getText()),
                                     int(self.linetilt_vit.getText()),
                                     int(self.linetrack_ratio.getText()), int(self.linetrack_courbe.getText()),
                                     int(self.linetrack_vitesse.getText()),
                                     int(self.linelift_ratio.getText()), int(self.linelift_courbe.getText()),
                                     int(self.linelift_vitesse.getText()),
                                     int(self.linezoom.getText()), self.btninvertpan.isChecked(),
                                     self.btninverttilt.isChecked(), self.btninvertzoom.isChecked(),
                                     self.btninvertfocus.isChecked(), self.btninverttrack.isChecked(),
                                     self.btninvertlift.isChecked(),
                                     self.btn_memory_focus1.value_memorized[self.old_index] if self.btn_memory_focus1.state[self.old_index] != 1 else False,
                                     self.btn_memory_focus2.value_memorized[self.old_index] if self.btn_memory_focus1.state[self.old_index] != 1 else False,
                                     self.btn_memory_focus3.value_memorized[self.old_index] if self.btn_memory_focus1.state[self.old_index] != 1 else False,
                                     self.btn_memory_focus4.value_memorized[self.old_index] if self.btn_memory_focus1.state[self.old_index] != 1 else False]
                    self.param_machine[self.old_index] = templistparam
                    self.flag_reload_param = False
            else:
                pass

            if identifier == "3":
                self.zoom_assist_container.hide()
                self.widgetscroll.Openscrolling(True)
            else:
                self.zoom_assist_container.show()
                self.widgetscroll.Openscrolling(False)
                pass

            if self.index != self.old_index and self.param_machine[self.index] != '':
                self.paramsetter(self.index, self.index)
                self.indicator_focus.updateline(int(self.machine_focus_position[self.index]), str(self.machine_focus_position[self.index]))
                self.indicator_focus.updateposmemory(self.index)
                for btn in self.list_btn_focus:
                    btn.setStateforMachine(self.index)
                    if btn.value_memorized[self.index] == self.indicator_focus.getCurVal():
                        btn.setframe(True)
                    else:
                        btn.setframe(False)
                self.warningpanel.setEverythingOk()
                self.btn_memoire.setgoodlist()

            elif self.machine_selected == self.old_machine_selected:  # Si on reclic sur une machine ca deselectionne tout
                self.machine_btn_group.setExclusive(False)
                self.btn_machine_list[self.index].setChecked(False)
                self.machine_btn_group.setExclusive(True)
                self.machine_selected = ''
                self.tiltcontainer.setEnabled(False)
                self.pancontainer.setEnabled(False)
                self.zoomcontainer.setEnabled(False)
                self.trackcontainer.setEnabled(False)
                self.liftcontainer.setEnabled(False)
                self.focuscontainer.setEnabled(False)
                self.indicator_focus.disable_focus(True)

                self.btn_release.setChecked(False)
                self.btn_release.setEnabled(False)
                self.btn_release.setText("Motor\nOFF")

                self.zoom_assist_container.setEnabled(False)
                self.old_index = ''
                self.warningpanel.setTips("Aucune machine\nsélectionnée")
                self.btn_memoire.justcollapse()
                self.btn_memoire.setEnabled(False)
                return
            else:
                self.slider_ratio_pan.setValue(0)
                self.slider_courbe_pan.setValue(0)
                self.slider_vitesse_pan.setValue(0)
                self.slider_ratio_tilt.setValue(0)
                self.slider_courbe_tilt.setValue(0)
                self.slider_vitesse_tilt.setValue(0)
                self.slider_zoom.setValue(0)
                self.slider_ratio_track.setValue(0)
                self.slider_vitesse_track.setValue(0)
                self.slider_ratio_lift.setValue(0)
                self.slider_vitesse_lift.setValue(0)

                self.btninvertpan.setChecked(False)
                self.btninverttilt.setChecked(False)
                self.btninvertzoom.setChecked(False)
                self.btninvertfocus.setChecked(False)
                self.btninverttrack.setChecked(False)
                self.btninvertlift.setChecked(False)

                self.machine_focus_position[self.index] = self.indicator_focus.getCurVal()
                self.warningpanel.setEverythingOk()

                self.btn_memory_focus1.setStateforMachine(self.index)
                self.btn_memory_focus2.setStateforMachine(self.index)
                self.btn_memory_focus3.setStateforMachine(self.index)
                self.btn_memory_focus4.setStateforMachine(self.index)
                self.indicator_focus.updateposmemory(self.index)

                self.btn_memoire.setgoodlist()

                self.enablecontainer()

            if self.state_motor_per_machine[self.index]:
                self.btn_release.setEnabled(True)
                self.btn_release.setChecked(True)
                self.btn_release.setText("Motor\nON")
            elif not self.state_motor_per_machine[self.index]:
                self.btn_release.setEnabled(True)
                self.btn_release.setChecked(False)
                self.btn_release.setText("Motor\nOFF")
            else:
                pass

            self.old_index = self.index
            self.old_machine_selected = self.machine_selected
            self.machine_selected_changes = True

        except IndexError as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(e, fname, exc_tb.tb_lineno)
            pass

    # Methode d'affiliation des paramètres chargés
    def paramsetter(self, indexmin, indexmax):
        try:
            if indexmin != indexmax:
                for i in range(indexmin, indexmax):
                    self.slider_ratio_pan.setValue(self.param_machine[i][0])
                    self.slider_courbe_pan.setValue(self.param_machine[i][1])
                    self.slider_vitesse_pan.setValue(self.param_machine[i][2])
                    self.slider_ratio_tilt.setValue(self.param_machine[i][3])
                    self.slider_courbe_tilt.setValue(self.param_machine[i][4])
                    self.slider_vitesse_tilt.setValue(self.param_machine[i][5])
                    self.slider_ratio_track.setValue(self.param_machine[i][6])
                    self.slider_courbe_track.setValue(self.param_machine[i][7])
                    self.slider_vitesse_track.setValue(self.param_machine[i][8])
                    self.slider_ratio_lift.setValue(self.param_machine[i][9])
                    self.slider_courbe_lift.setValue(self.param_machine[i][10])
                    self.slider_vitesse_lift.setValue(self.param_machine[i][11])
                    self.slider_zoom.setValue(self.param_machine[i][12])
                    self.btninvertpan.setChecked(self.param_machine[i][13])
                    self.btninverttilt.setChecked(self.param_machine[i][14])
                    self.btninvertzoom.setChecked(self.param_machine[i][15])
                    self.btninvertfocus.setChecked(self.param_machine[i][16])
                    self.btninverttrack.setChecked(self.param_machine[i][17])
                    self.btninvertlift.setChecked(self.param_machine[i][18])

                    self.btn_memory_focus1.value_memorized[i] = self.param_machine[i][19]
                    self.btn_memory_focus2.value_memorized[i] = self.param_machine[i][20]
                    self.btn_memory_focus3.value_memorized[i] = self.param_machine[i][21]
                    self.btn_memory_focus4.value_memorized[i] = self.param_machine[i][22]

                    self.btn_memory_focus1.in_memory(i) if self.param_machine[i][19] is not False else ''
                    self.btn_memory_focus2.in_memory(i) if self.param_machine[i][20] is not False else ''
                    self.btn_memory_focus3.in_memory(i) if self.param_machine[i][21] is not False else ''
                    self.btn_memory_focus4.in_memory(i) if self.param_machine[i][22] is not False else ''

                    self.btn_memory_focus1.setStateforMachine(i)
                    self.btn_memory_focus2.setStateforMachine(i)
                    self.btn_memory_focus3.setStateforMachine(i)
                    self.btn_memory_focus4.setStateforMachine(i)

                    self.enablecontainer()
            else:
                self.slider_ratio_pan.setValue(self.param_machine[indexmin][0])
                self.slider_courbe_pan.setValue(self.param_machine[indexmin][1])
                self.slider_vitesse_pan.setValue(self.param_machine[indexmin][2])
                self.slider_ratio_tilt.setValue(self.param_machine[indexmin][3])
                self.slider_courbe_tilt.setValue(self.param_machine[indexmin][4])
                self.slider_vitesse_tilt.setValue(self.param_machine[indexmin][5])
                self.slider_ratio_track.setValue(self.param_machine[indexmin][6])
                self.slider_courbe_track.setValue(self.param_machine[indexmin][7])
                self.slider_vitesse_track.setValue(self.param_machine[indexmin][8])
                self.slider_ratio_lift.setValue(self.param_machine[indexmin][9])
                self.slider_courbe_lift.setValue(self.param_machine[indexmin][10])
                self.slider_vitesse_lift.setValue(self.param_machine[indexmin][11])
                self.slider_zoom.setValue(self.param_machine[indexmin][12])
                self.btninvertpan.setChecked(self.param_machine[indexmin][13])
                self.btninverttilt.setChecked(self.param_machine[indexmin][14])
                self.btninvertzoom.setChecked(self.param_machine[indexmin][15])
                self.btninvertfocus.setChecked(self.param_machine[indexmin][16])
                self.btninverttrack.setChecked(self.param_machine[indexmin][17])
                self.btninvertlift.setChecked(self.param_machine[indexmin][18])

                self.btn_memory_focus1.value_memorized[indexmin] = self.param_machine[indexmin][19]
                self.btn_memory_focus2.value_memorized[indexmin] = self.param_machine[indexmin][20]
                self.btn_memory_focus3.value_memorized[indexmin] = self.param_machine[indexmin][21]
                self.btn_memory_focus4.value_memorized[indexmin] = self.param_machine[indexmin][22]

                self.btn_memory_focus1.in_memory(indexmin) if self.param_machine[indexmin][19] is not False else ''
                self.btn_memory_focus2.in_memory(indexmin) if self.param_machine[indexmin][20] is not False else ''
                self.btn_memory_focus3.in_memory(indexmin) if self.param_machine[indexmin][21] is not False else ''
                self.btn_memory_focus4.in_memory(indexmin) if self.param_machine[indexmin][22] is not False else ''

                self.btn_memory_focus1.setStateforMachine(indexmin)
                self.btn_memory_focus2.setStateforMachine(indexmin)
                self.btn_memory_focus3.setStateforMachine(indexmin)
                self.btn_memory_focus4.setStateforMachine(indexmin)

                self.enablecontainer()

        except IndexError as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(e, fname, exc_tb.tb_lineno)

    # Methode d'activation/desactivation des conteneurs de widgets
    def enablecontainer(self):
        if self.machine_selected != '':
            if self.cmd_list[0] != '':
                self.tiltcontainer.setEnabled(True)
                self.pancontainer.setEnabled(True)
            if self.cmd_list[1] != '':
                self.zoomcontainer.setEnabled(True)
                self.focuscontainer.setEnabled(True)
                self.indicator_focus.disable_focus(False)
                self.zoom_assist_container.setEnabled(True)
            if self.cmd_list[2] != '':
                self.trackcontainer.setEnabled(True)
                self.liftcontainer.setEnabled(True)
                self.tiltcontainer.setEnabled(True)
                self.pancontainer.setEnabled(True)
            if self.cmd_list[3] != '':
                self.zoomcontainer.setEnabled(True)
                self.zoom_assist_container.setEnabled(True)
            if self.cmd_list[4] != '':
                self.focuscontainer.setEnabled(True)
                self.indicator_focus.disable_focus(False)

    # Methode de calcul en fonction du slider actionné
    def slidervaluechanged(self, val_slider):
        valstr = str(val_slider)
        try:
            if self.sender() is self.slider_zoom:
                self.linezoom.setText(valstr)
                min_vit, max_vit = self.param_vitesse[2]
                scaling_vitesse = (((max_vit - min_vit) * val_slider) / 100) + min_vit
                self.vitesse_zoom = scaling_vitesse
            elif self.machine_selected != '':
                if self.sender() in (self.slider_vitesse_track, self.slider_courbe_track, self.slider_ratio_track):
                    machine = 'TRACK'
                    commande = '7'

                elif self.sender() in (self.slider_vitesse_lift, self.slider_courbe_lift, self.slider_ratio_lift):
                    machine = 'LIFT'
                    commande = '7'
                else:
                    machine = self.vers_tete[self.machines_list.index(self.machine_selected)]
                    commande = self.cmd_list[0].split('.')[2] if self.cmd_list[0] != '' else '4'
                # index 0: teteV4, index 1: teteV6, index 2 18360: zoomfuji/canon,
                # index 3: furiochariot, index 4: furio colonne, index 5 : tete V5, index 6 : tete Furio Tuple(min, max)
                witchmach = {
                    'V4' or 'V4lost': 0,
                    'V5' or 'V5lost': 5,
                    'V6' or 'V6lost': 1,
                    'F' or 'Flost': 6,
                    'TRACK': 3,
                    'LIFT': 4,
                    'None' or 'Nonelost': 1,
                    'lost': 1,
                }
                index_param = witchmach.get(machine, 'machine inconnue')
                witchcmd = {
                    '11': "poigneepoint",
                    '10': "poigneezoom",
                    '7': "pedale",
                    '6': "panbar",
                    '5': "zoompoint",
                    '4': "joystick"
                }

                index_param_cmd = witchcmd.get(commande, 'commande inconnue')

                witchslider = {
                    self.slider_ratio_pan: ['ratiopan', self.linepan_ratio, 'ratio_pan'],
                    self.slider_courbe_pan: ['courbepan', self.linepan_courbe, 'courbe_pan'],
                    self.slider_vitesse_pan: ['vitessepan', self.linepan_vit, 'vitesse_pan'],
                    self.slider_ratio_tilt: ['ratiotilt', self.linetilt_ratio, 'ratio_tilt'],
                    self.slider_courbe_tilt: ['courbetilt', self.linetilt_courbe, 'courbe_tilt'],
                    self.slider_vitesse_tilt: ['vitessetilt', self.linetilt_vit, 'vitesse_tilt'],
                    self.slider_ratio_track: ['ratiotrack', self.linetrack_ratio, 'ratio_track'],
                    self.slider_courbe_track: ['courbetrack', self.linetrack_courbe, 'courbe_track'],
                    self.slider_vitesse_track: ['vitessetrack', self.linetrack_vitesse, 'vitesse_track'],
                    self.slider_ratio_lift: ['ratiolift', self.linelift_ratio, 'ratio_lift'],
                    self.slider_courbe_lift: ['courbelift', self.linelift_courbe, 'courbe_lift'],
                    self.slider_vitesse_lift: ['vitesselift', self.linelift_vitesse, 'vitesse_lift'],
                    self.slider_zoom_assist: ['zoomassist', self.linezoom_assist, 'zoomassistFactor'],
                    self.btn_memoire.slider_accel: ['accelmemoire', self.btn_memoire.line_accel, 'accel_memoire'],
                }
                component_slider = witchslider.get(self.sender(), 'commande inconnue')
                slidertype = component_slider[0]
                line = component_slider[1]

                whitchsettings = {
                    'ratiopan': self.param_ratio[index_param] if index_param_cmd == "joystick" else self.param_ratiocmd[index_param],
                    'ratiotilt': self.param_ratio[index_param] if index_param_cmd == "joystick" else self.param_ratiocmd[index_param],
                    'ratiotrack': self.param_ratio[index_param] if index_param_cmd == "pedale" else self.param_ratiocmd[index_param],
                    'ratiolift': self.param_ratio[index_param] if index_param_cmd == "pedale" else self.param_ratiocmd[index_param],
                    'courbepan': self.param_courbe[index_param],
                    'courbetilt': self.param_courbe[index_param],
                    'courbetrack': self.param_courbe[index_param],
                    'courbelift': self.param_courbe[index_param],
                    'vitessepan': self.param_vitesse[index_param] if index_param_cmd == "joystick" else self.param_vitessepan[index_param],
                    'vitessetilt': self.param_vitesse[index_param] if index_param_cmd == "joystick" else self.param_vitessetilt[index_param],
                    'vitessetrack': self.param_vitesse[index_param] if index_param_cmd == "pedale" else self.param_vitessepan[index_param],
                    'vitesselift': self.param_vitesse[index_param] if index_param_cmd == "pedale" else self.param_vitessepan[index_param],
                    'zoomassist': self.param_zoomassist,
                    'accelmemoire': self.param_accel[index_param],
                }
                propersettings = whitchsettings.get(slidertype, 'commande inconnue')
                mini, maxi = propersettings
                scaling = ((maxi - mini) * val_slider)
                scaling_vitesse = ((maxi - mini) * val_slider * val_slider * 0.001)
                scaling = scaling_vitesse / 1000 + mini if slidertype in ('vitessepan', 'vitessetilt', 'vitessetrack', 'vitesselift', 'accelmemoire') else round(scaling / 100 + mini, 2)
                line.setText(valstr)

                if slidertype == 'zoomassist':
                    if scaling == 0:
                        self.voyant_onoff_zoom_assist.setChecked(False)
                        self.voyant_onoff_zoom_assist.setText("OFF")
                        self.zoomassistIsEnable = False
                    else:
                        self.voyant_onoff_zoom_assist.setChecked(True)
                        self.voyant_onoff_zoom_assist.setText("ON")
                        self.zoomassistIsEnable = True

                if slidertype in (
                        'vitessepan', 'vitessetilt', 'vitessetrack', 'vitesselift') and val_slider == 0:  # permet de modifier la plage de vitesse entre le 1 et le max du slider en gardant 0 à 0
                    scaling = 0
                    self.slider_0 = slidertype

                setattr(self, witchslider.get(self.sender(), "erreur")[2], scaling)
            else:
                pass

        except IndexError:
            print("index error in slider value changed")
            self.sender().setValue(0)
            pass
        except TypeError:
            print("type error")
            pass

    # Methode d'affichage focus < -- > Iris
    def switch_diaphchanged(self, val_slider):
        if val_slider == 1:
            self.switch_diaph.label_focus.hide()
            self.switch_diaph.label_diaph.show()
            self.label_focus.setText("FOCUS")
            self.focuscontainer.set_bg(0)
            self.indicator_focus.flag_iris = False
            self.btn_memory_iris1.hide()
            self.btn_memory_iris2.hide()
            self.btn_memory_iris3.hide()
            self.btn_memory_iris4.hide()
            self.btn_memory_focus1.show()
            self.btn_memory_focus2.show()
            self.btn_memory_focus3.show()
            self.btn_memory_focus4.show()
            self.flag_focus = True
            self.indicator_focus.updateline(int(self.indicator_focus.val_focus),
                                            str(int(self.indicator_focus.val_focus)))

        if val_slider == 2:
            self.switch_diaph.label_diaph.hide()
            self.switch_diaph.label_focus.show()
            self.label_focus.setText("IRIS")
            self.focuscontainer.set_bg(1)
            self.indicator_focus.flag_iris = True
            self.btn_memory_iris1.show()
            self.btn_memory_iris2.show()
            self.btn_memory_iris3.show()
            self.btn_memory_iris4.show()
            self.btn_memory_focus1.hide()
            self.btn_memory_focus2.hide()
            self.btn_memory_focus3.hide()
            self.btn_memory_focus4.hide()
            self.flag_focus = False
            self.indicator_focus.updateline(int(self.indicator_focus.val_iris),
                                            str(int(self.indicator_focus.val_iris)))

        self.flag_raz_focus = True

    # Methode d'affichage des boutons machine
    def set_machine_buttons(self):
        if len(self.machines_list) > 0:
            # print("machine list in setting button", self.machines_list)
            for machine in self.machines_list:
                index = self.machines_list.index(machine)
                identifier = machine.split(".")[2]
                num_machine = machine.split(".")[3]
                ip = machine

                switchcase_machine = {
                    '2': 'tete',
                    '3': 'furio',
                }
                name = switchcase_machine.get(identifier, "Machine invalide")
                if name == 'tete':
                    self.btn_machine_list[index].show()
                    if self.vers_tete[index] not in ('None', 'V4lost', 'V5lost', 'V6lost', 'Nonelost', '', 'lost'):
                        switchcase_version = {
                            'V4': (self.pictures.V4_icon, self.pictures.image_V4.rect().size()),
                            'V5': (self.pictures.V5_icon, self.pictures.image_V5.rect().size()),
                            'V6': (self.pictures.add_number(str(num_machine), 'V6'), self.pictures.image_V6.rect().size()),
                        }
                        versiontete = switchcase_version.get(self.vers_tete[index], "None")
                        icon, size = versiontete
                        self.icons_list[index] = icon if self.icons_list[index] == "" else self.icons_list[index]
                        self.btn_machine_list[index].unset_gif_loading()
                        self.btn_machine_list[index].but_cam_number.setText(str(num_machine)) if self.btn_machine_list[index].num_has_changed == False else 0
                        if self.ref_optique[index] not in ("none", "", "V6"):
                            self.btn_machine_list[index].setIcon(self.icons_list[index])
                            self.btn_machine_list[index].setIconSize(size)
                            self.btn_machine_list[index].unset_gif_loading()
                            self.btn_machine_list[index].unset_gif_optique()
                        elif self.ref_optique[index] == "V6":
                            print("clément envoit des OV6 not normal")
                        else:
                            self.btn_machine_list[index].unset_gif_loading()
                            self.btn_machine_list[index].set_gif_optique(self.vers_tete[index])

                    elif 'lost' in str(self.vers_tete[index]):
                        self.btn_machine_list[index].unset_gif_loading()
                        self.btn_machine_list[index].unset_gif_optique()
                        self.btn_machine_list[index].setIcon(QIcon())
                        self.btn_machine_list[index].setIcon(self.pictures.add_number(str(num_machine), 'eth'))
                    else:
                        self.btn_machine_list[index].set_gif_loading()
                        self.btn_machine_list[index].unset_gif_optique()
                    # self.btn_machine_list[ctr].click()

                elif name == 'furio':
                    self.btn_machine_list[index].show()
                    if self.vers_furio[index] not in ('None', 'FXlost', 'MOlost', 'Nonelost', '', 'lost', 'error'):
                        switchcase_version_colonne = {
                            'FX': (self.pictures.FurioFX_icon, self.pictures.image_Furio_FX.rect().size()),
                            'MO': (self.pictures.FurioMO_icon, self.pictures.image_Furio_MO.rect().size()),
                        }
                        versioncolonne = switchcase_version_colonne.get(self.vers_furio[index], "None")
                        icon, size = versioncolonne
                        self.icons_list[index] = icon
                        self.btn_machine_list[index].unset_gif_loading()
                        self.btn_machine_list[index].setIcon(self.icons_list[index])
                        self.btn_machine_list[index].setIconSize(size)
                    # self.btn_machine_list[index].setChecked(True)
                    elif 'lost' in str(self.vers_furio[index]):
                        # print("furio lost go to ethernet icon")
                        self.btn_machine_list[index].unset_gif_loading()
                        self.btn_machine_list[index].unset_gif_optique()
                        self.btn_machine_list[index].setIcon(QIcon())
                        self.btn_machine_list[index].setIcon(self.pictures.add_number(str(num_machine), 'eth'))
                    elif 'error' in str(self.vers_furio[index]):
                        print("erreur furio")
                        #  self.warningpanel.setTips("Erreur Furio Chariot:" + self.code_erreur_Furio[0] + "\nColonne: " + self.code_erreur_Furio[1])
                    else:
                        self.btn_machine_list[index].set_gif_loading()
                        self.btn_machine_list[index].unset_gif_optique()
                    # self.old_len_machines = len(self.machines_list)

    # Methode de déaffichage des boutons machines
    def unset_machine_buttons(self, ip):

        identifier = ip.split(".")[2]
        index = self.machines_list.index(ip)
        switchcase_machine = {
            '2': 'tete',
            '3': 'furio',
        }
        name = switchcase_machine.get(identifier, "Machine invalide")
        if name == 'tete':
            self.machine_btn_group.setExclusive(False)
            if self.btn_machine_list[index].isChecked():
                self.btn_machine_list[index].click()
            else:
                self.btn_machine_list[index].setChecked(False)
            self.btn_machine_list[index].setEnabled(False)
            self.machine_btn_group.setExclusive(True)
        elif name == 'furio':
            self.machine_btn_group.setExclusive(False)
            if self.btn_machine_list[index].isChecked():
                self.btn_machine_list[index].click()
            else:
                self.btn_machine_list[index].setChecked(False)
            self.btn_machine_list[index].setEnabled(False)
            self.machine_btn_group.setExclusive(True)

    # Methode d'affichage des boutons commande
    def set_cmd_btn(self):
        for cmd in self.cmd_list:
            if cmd != '':
                identifier = cmd.split(".")[2]
                num_boitier = cmd.split(".")[3]
                ip = cmd

                switchcase_cmd = {
                    '4': 'joystick',
                    '5': 'zoompoint',
                    '6': 'panbar',
                    '7': 'pedales',
                    '10': 'poigneezoom',
                    '11': 'poigneepoint'

                }
                name = switchcase_cmd.get(identifier, "Peripherique invalide")

                if name == 'joystick':
                    self.pancontainer.show()
                    self.tiltcontainer.show()
                    self.container_joy.changepixmap(self.image_joystick, " n°" + num_boitier)
                    self.slider_courbe_pan.show()
                    self.slider_courbe_tilt.show()
                    self.linetilt_courbe.show()
                    self.linepan_courbe.show()
                    self.label_courbe_pan.show()
                    self.label_courbe_tilt.show()
                    self.enablecontainer()
                    self.widgetscroll.set_commande_liste("joystick")

                if name == 'zoompoint':
                    self.focuscontainer.show()
                    self.zoomcontainer.show()
                    self.container_zp.changepixmap(self.image_zoompoint, " n°" + num_boitier)
                    self.enablecontainer()

                if name == 'panbar':
                    self.pancontainer.show()
                    self.tiltcontainer.show()
                    self.slider_courbe_pan.hide()
                    self.slider_courbe_tilt.hide()
                    self.linetilt_courbe.hide()
                    self.linepan_courbe.hide()
                    self.label_courbe_pan.hide()
                    self.label_courbe_tilt.hide()
                    self.container_joy.changepixmap(self.image_panbar, " n°" + num_boitier)
                    self.enablecontainer()
                    self.widgetscroll.set_commande_liste("panbar")

                if name == 'pedales':
                    self.container_lifttrack.changepixmap(self.image_lifttrack, " n° " + num_boitier)
                    self.container_butees.show()
                    self.enablecontainer()

                if name == "poigneezoom":
                    self.zoomcontainer.show()
                    if not self.poignee_deport_conn[0] and not self.poignee_deport_conn[1]:
                        self.container_zp.changepixmappoignee(self.image_poigneezoom_only, " n°" + num_boitier, "")
                    elif not self.poignee_deport_conn[0] and self.poignee_deport_conn[1]:
                        self.container_zp.changepixmappoignee(self.image_poignees, " n°" + num_boitier, "")
                    else:
                        pass
                    self.zoomcontainer.show()
                    self.poignee_deport_conn[0] = True
                    self.enablecontainer()

                if name == "poigneepoint":
                    if not self.poignee_deport_conn[1] and not self.poignee_deport_conn[0]:
                        self.container_zp.changepixmappoignee(self.image_poigneepoint_only, "", "n°" + num_boitier)
                    elif not self.poignee_deport_conn[1] and self.poignee_deport_conn[0]:
                        self.container_zp.changepixmappoignee(self.image_poignees, "", "n°" + num_boitier)
                    else:
                        pass
                    self.focuscontainer.show()
                    self.poignee_deport_conn[1] = True
                    self.enablecontainer()

    # Methode de déaffichage des boutons commande
    def unset_cmd_btn(self, ip):
        identifier = ip.split(".")[2]
        switchcase_cmd = {
            '4': 'joystick',
            '5': 'zoompoint',
            '6': 'panbar',
            '7': 'pedales',
            '10': 'poigneezoom',
            '11': 'poigneepoint'
        }
        name = switchcase_cmd.get(identifier, "Peripherique invalide")

        if name == 'joystick':
            self.container_joy.changepixmap(self.image_joystick_cross, "")
            self.tiltcontainer.setEnabled(False)
            self.pancontainer.setEnabled(False)

        if name == 'zoompoint':
            self.container_zp.changepixmap(self.image_zoompoint_cross, "")
            self.zoomcontainer.setEnabled(False)
            self.focuscontainer.setEnabled(False)

        if name == 'panbar':
            self.container_joy.changepixmap(self.image_joystick_cross, "")
            self.tiltcontainer.setEnabled(False)
            self.pancontainer.setEnabled(False)

        if name == 'pedales':
            self.container_lifttrack.changepixmap(self.image_lifttrack_cross, "")
            self.container_butees.hide()
            self.trackcontainer.setEnabled(False)
            self.liftcontainer.setEnabled(False)

        if name == "poigneezoom":
            if self.poignee_deport_conn[0] and not self.poignee_deport_conn[1]:
                self.container_zp.changepixmap(self.image_zoompoint_cross, "")
            elif self.poignee_deport_conn[0] and self.poignee_deport_conn[1]:
                self.container_zp.changepixmap(self.image_poigneepoint_only, "")
            else:
                pass
            self.poignee_deport_conn[0] = False
            self.zoomcontainer.setEnabled(False)

        if name == "poigneepoint":
            if self.poignee_deport_conn[1] and not self.poignee_deport_conn[0]:
                self.container_zp.changepixmap(self.image_zoompoint_cross, "")
            elif self.poignee_deport_conn[1] and self.poignee_deport_conn[0]:
                self.container_zp.changepixmap(self.image_poigneezoom_only, "")
            else:
                pass
            self.poignee_deport_conn[1] = False
            self.focuscontainer.setEnabled(False)

    # Demande au Maestro de quitter l'appli... (actuellement non connecté puisque le bouton est masqué pour pas que les OPV fassent de la merde)
    def quitapp(self):
        self.quit_app = True

    # Ferme l'appli une fois que les threads sont stoppés par le Maestro.. (Merci captain obvious)
    @staticmethod
    def quit_gui():
        print("thread Maestro killed")
        QCoreApplication.quit()

    # Messagebox nombre machines connectées trop grand
    def error_nb_machines(self, machine):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Critical)
        msg.setFixedSize(200, 200)
        msg.setText("Too many machines")
        msg.setInformativeText("5 machines are already connected to the tab. you need"
                               " to replace one if you want to use this: " + machine)
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec_()

    # Message box nombre commandes connectées trop grand
    def error_nb_cmd_pantilt(self, cmd):
        self.error_dial = wb.ErrorDialog('cmd', cmd)
        self.error_dial.show()

    def error_nb_cmd_zoompoint(self, cmd):
        self.error_dial = wb.ErrorDialog('cmd', cmd)
        self.error_dial.show()


# Un Qobject qui envoie certains signaux pour le Maestro (Evite les conflits de threads parce que QT il est pas content quand un autre thread ramene sa fraise)
class SignalLauncher(QObject):
    machine_button = pyqtSignal()
    machine_button_settings = pyqtSignal()
    cmd_button = pyqtSignal()
    vitesse_setter = pyqtSignal()
    vitesse_recue_setter = pyqtSignal()
    vitesse_panbar_setter = pyqtSignal()
    vitesse_recue_panbar_setter = pyqtSignal()
    stop = pyqtSignal()
    error_cmd = pyqtSignal()
    error_optic_cmd = pyqtSignal()

    def emitsignal(self, signal):
        switchcase_signal = {
            'machine': 'machine_button',
            'machine_setting': 'machine_button_settings',
            'button': 'cmd_button',
            'vitesse_setter': 'vitesse_setter',
            'vitesse_recue_setter': 'vitesse_recue_setter',
            'vitesse_panbar_setter': 'vitesse_panbar_setter',
            'error_cmd': 'error_cmd',
            'error_optic_cmd': 'error_optic_cmd'
        }
        name = switchcase_signal.get(signal, "signal inconnu")
        attr = getattr(self, name, "erreur")

        return attr.emit()


"""DEMARRAGE DU PROGRAMME ============================================================================================================ DEMARRAGE PGM"""


# le launcher, l'ordre des lignes est important, ne pas le changer.
class Launcher:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.recording = appmap.Recording()
        self.recording.start()
        self.app.aboutToQuit.connect(self.showRecording)
        if rasp_config:
            self.app.setOverrideCursor(QCursor(Qt.BlankCursor))  # Fait sauter le curseur pour l'écran tactile
        self.screen = self.app.primaryScreen()
        self.win = SwitcherWindows()  # classe qui permet de passer de la fenetre de commande a la superviz et targetting
        self.win.setFixedSize(1024, 600)
        if not rasp_config:
            self.win.show()
        else:
            self.win.showFullScreen()  # le full screen est ici pour que la fenetre de settings qu'on créé juste a la ligne du dessous prenne la bonne taille...
        self.win.start_screen.userdial = wb.SettingsDialog(self.win.start_screen)
        self.siglauncher = SignalLauncher()
        self.maestro = Maestro.Maestro(self.win.start_screen, self.win, self.screen.depth(), self.siglauncher)  # on construit la classe maestro
        time.sleep(0.2)  # tempo de 0.2 sec car cette ligne s'execute après le lancement des thread UDP et boucle Maestro
        # on regle quelque truc du side menu (cf. widgetbox) parce qu'il est 'on top'
        self.win.menu.set_y_size(self.win.size().height())
        self.win.menu.setGeometry(QRect(-300, 0, 314 + 12, self.win.menu.y_size))
        print("Launching Qt application...")
        sys.exit(self.app.exec())  # lancement de la boucle infinie qui choppe les events de Qt
        
    def showRecording(self):
        self.recording.stop()
        print(appmap.generation.dump(self.recording), file=sys.stderr)

if __name__ == '__main__':
    launch = Launcher()  # Premiere ligne du programme. On construit la classe launcher.
