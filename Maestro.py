import socket
import time
import sys
import threading
from math import exp
import os
import fileinput
# import pyprctl
import logging
import psutil
import ctypes
libc = ctypes.cdll.LoadLibrary('libc.so.6')

thread_ID_number = 186  # 224 raspberry, 186 PC
request_buffer = []
flag_logging_udp = False

"""CLASSE MERE ===========================================================================================================================MAESTRO"""


class Maestro:
    def __init__(self, win, settings, param, siglauncher):
        logging.basicConfig(level=logging.INFO, format='[%(levelname)s] (%(threadName)s) %(message)s', )  # reglage des messages de logging
        self.interval_debug_info = 100  # temps entre chaque debug info des 3 threads (UDP, request handler, mainloop), 100 = 1 seconde

        # Appel de la fenetre graphique principale pour pouvoir acceder à ses variables
        self.mainapp = win
        # Appel de la fenetre graphique superviz pour pouvoir acceder à ses variables
        self.win = settings
        self.settings = self.win.second_screen
        self.targetwin = self.win.targeting_screen
        self.siglauncher = siglauncher
        self.image_targetting = b''
        self.last_image_memoires = b''
        self.depth = param
        # instenciation des objets thread
        self.maestro_thread = ""
        self.request_thread = ""
        # signaux
        self.siglauncher.machine_button.connect(self.mainapp.set_machine_buttons)
        self.siglauncher.machine_button_settings.connect(self.settings.set_machine_buttons)
        self.siglauncher.cmd_button.connect(self.mainapp.set_cmd_btn)
        self.siglauncher.vitesse_setter.connect(lambda: self.settings.set_vitesse(self.tilt_data, self.pan_data, self.track_data, self.lift_data, self.zoom_data))
        self.siglauncher.vitesse_recue_setter.connect(lambda: self.settings.set_vitesse_recue(self.last_tilt_data, self.last_pan_data, self.last_track_data, self.last_lift_data, self.last_zoom_data))
        self.siglauncher.vitesse_recue_panbar_setter.connect(lambda: self.settings.set_vitesse_recue(self.last_panbar_tilt_data, self.last_panbar_pan_data, self.last_track_data, self.last_lift_data, self.last_zoom_data))
        self.siglauncher.vitesse_panbar_setter.connect(lambda: self.settings.set_vitesse(self.panbar_tilt_data, self.panbar_pan_data, self.track_data, self.lift_data, self.zoom_data))
        self.siglauncher.error_cmd.connect(lambda: self.mainapp.error_nb_cmd_pantilt(self.error_msg))
        self.siglauncher.error_optic_cmd.connect(lambda: self.mainapp.error_nb_cmd_zoompoint(self.error_msg_optic))

        # configuration du serveur UDP
        self.port = 65531
        self.message = ""
        self.receiverudp = UdpReceive('', self.port)
        self.senderudp = UdpSending(self.port)
        self.line = []
        self.myip = "200.200.1.9"
        '''self.myip = str(os.popen("""ifconfig eth0 | grep "inet " | cut -c 14-26""").read())
         self.myip = str(os.popen("""ifconfig enp3s0 | grep "inet " | cut -c 14-26""").read())'''

        # variable qui stock la longueur du buffer de reception des données via UDP
        self.old_len_request = len(request_buffer)
        # variable qui stock les ips des tetes
        self.heads_ip = []
        # variable qui stock le dernier message recu en UDP
        self.str_msg = ""
        # variable qui stock la derniere IP recue en UDP
        self.str_ip = ""
        # variable qui stock le dernier numero de machine ou commande recu
        self.current_numero = ""
        # Variable qui stock le dernier identifiant machine/cmd recu
        self.machine_identifier = ""
        # flag de demarrage
        self.send_reset = False
        # flag qui indique qu'on a déjà 5 machines
        self.flag_full_machine = False
        # flag qui indique qu'on a déjà 2 commandes ( Z/P et joystick | Z/P et panbar etc.)
        self.flag_waiting_reponse = False  # permet d'executer qu'une seule fois la fenetre d'alerte disant que plusieur cmd identiques sont connectés
        self.error_msg = ''
        self.error_msg_optic = ''
        self.flag_stop = False
        self.vitesse_x2 = False
        self.debrayage_panbar = False
        self.flag_signal_settings = False
        self.list_cmd_alive = ['False'] * 5
        self.list_machine_alive = ['False'] * 5
        # compteurs temps :
        self.flag_machines = False
        self.flag_cmd = False
        self.ctn_alive = 0
        self.ctn_zass = 0
        self.ctn_responce = 0
        self.ctn_responce_h = 0
        self.ctn_nb_tour = 0
        self.ctn_computing = 0
        self.ctn_panbar = 0
        self.ctn_affichage = 0
        self.ctn_computing_track = 0
        self.ctn_debug = 0
        self.flag_logging_request = False
        self.thread_info_request = ""
        self.thread_info_maestro = ""
        self.p = psutil.Process(os.getpid())
        # checker
        self.checker_cmd = False
        self.checker_tete = False
        # variable ref optique et status bouton iris
        self.ref_optique = [""] * 5
        self.status_iris = False
        # variables quistock les dernieres valeurs calculées des axes
        self.pan_data = 0
        self.panbar_pan_data = 0
        self.tilt_data = 0
        self.panbar_tilt_data = 0
        self.track_data = 0
        self.lift_data = 0
        self.zoom_data = 0
        self.focus_data = 0  # scaling for optique
        self.old_pan_data = 0
        self.old_panbar_pan_data = 0
        self.old_tilt_data = 0
        self.old_panbar_tilt_data = 0
        self.old_track_data = 0
        self.old_lift_data = 0
        self.old_zoom_data = 0
        self.old_focus_data = 0
        self.last_pan_data = 0
        self.last_tilt_data = 0
        self.last_lift_data = 0
        self.last_track_data = 0
        self.last_panbar_pan_data = 0
        self.last_panbar_tilt_data = 0

        self.previousts = 0
        self.delta = 0

        # variable de recuperation des get pan tilt zoom etc
        self.pan_position = ""
        self.tilt_position = ""
        self.memo_zoom = ""
        self.track_position = ""
        self.lift_position = ""

        self.val_zoom = 60000

        # variable panbar
        self.coeff_vitesse_panbar = 0.01
        self.var_codeur = 524287
        self.flag_first_val_tilt = True
        self.flag_first_val_pan = True
        self.list_optique = [''] * 5
        # Flag panbar ou joystick
        self.panbar_set = False
        self.joystick_set = False
        self.pedales_set = False
        self.last_zoom_data = 0
        self.focus = 130  # scaling for GUI
        self.machine_in_calib = ''
        self.pan_data_virgule = 0.0
        self.tilt_data_virgule = 0.0
        # index de la machine en cours
        self.current_index_machine = 0
        self.switch_machine = 0
        # listes de tableaux (en réalité c'est des listes de listes) (1 par machines) servant au filtre de butterworth
        self.list_butterworth_pan = [[0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0],
                                     [0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0]]
        self.list_butterworth_tilt = [[0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0],
                                      [0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0]]
        self.list_butterworth_track = [[0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0],
                                       [0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0]]
        self.list_butterworth_lift = [[0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0],
                                      [0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0]]
        self.list_butterworth_panbar_pan = [[0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0],
                                            [0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0]]
        self.list_butterworth_panbar_tilt = [[0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0],
                                             [0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0]]
        self.list_butterworth_zoom = [[0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0],
                                      [0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0]]

        # valeur fixe courbe et ratio pour le zoom:
        self.ratio_zoom, _max = self.mainapp.param_ratio[2]
        self.courbe_zoom, _max = self.mainapp.param_courbe[2]

        # fonction qui renvois le signe
        self.which_sign = lambda x: (x > 0) - (x < 0)
        # variables pour le serial inutilisées dans le vrai code puisque tout passe par ethernet
        # self.ser = serial.Serial('/dev/ttyUSB0', 38200)
        self.B1 = ''
        self.data = ''
        self.flag = False
        self.set_edit_seuil_once = False
        self.set_edit_seuil_joy_once = False
        self.set_edit_seuil_pedale_once = False
        # on appelle la fonction qui démarre les threads UDP et la boucle du Maestro
        print("launching thread ...")
        self.start_threads()

    # Methode de lancement des threads UDP et boucle Maestro avec Daemon pour tout fermer proprement avec un sys.exit(0)
    def start_threads(self):

        self.maestro_thread = threading.Thread(name='Maestro thread', target=self.maestro_main, args=(1,), daemon=True)
        self.request_thread = threading.Thread(name='Request thread', target=self.request_handler, args=(1,), daemon=True)

        self.maestro_thread.start()
        print("maestro thread started")
        self.request_thread.start()
        print("Request thread started")
        self.receiverudp.run()
        print("UDP receiver thread started")
        time.sleep(0.2)

    """Thread request (interaction avec l'udp) =================================================================================== THREAD REQUEST"""

    def request_handler(self, u):
        while True:
            if self.flag_logging_request:
                for threads in self.p.threads():
                    if threads[0] == libc.syscall(thread_ID_number):  # 224 on rasp
                        self.thread_info_request = threads
                        break
                if self.thread_info_request is not str:
                    calc = round(self.p.cpu_percent(0.1) * ((self.thread_info_request.system_time + self.thread_info_request.user_time) / sum(self.p.cpu_times())), 1)
                    logging.info("CPU Usage:" + str(calc) + "% ") if calc > 10 else None
                self.flag_logging_request = False
            # on check si le buffer de reception a changé de taille, si oui, c'est qu'on a recu qqe chose
            if len(request_buffer) != 0:
                str_msg, str_ip = request_buffer[0]

                if str_msg.startswith(b'IMG'):
                    print("Image recue")
                    if self.win.gotargeting:
                        self.image_targetting = str_msg.strip(b'IMG')
                        self.targetwin.setsnapshot(self.image_targetting)
                        self.image_targetting = b''
                    else:
                        self.last_image_memoires = str_msg.strip(b'IMG')
                        self.mainapp.btn_memoire.setsnapshot(self.last_image_memoires, self.mainapp.memory_position_number)
                        self.last_image_memoires = b''
                elif str_msg.startswith(b'I'):
                    print("received 'Init msg' from", str_ip)
                    self.senderudp.txsend(b"I", str_ip)  # Reponse auto d'initialisation
                    self.request_processing(
                        request_buffer[0])
                else:
                    self.request_processing(
                        request_buffer[0])  # on call le switchcase qui renvoit vers la bonne fonction

                del request_buffer[0]  # on supprime le premier élément ajouté au buffer

            time.sleep(0.001)  # former: 0.000001

    """SWITCHCASE methodes ================================================================================================== SWITCHCASE methodes"""

    # fonction qui gere les messages qui arrivent et les renvois vers la methode convernée (switchcase) => Machines ou commande
    def request_processing(self, request):
        try:
            str_msg, str_ip = request
            self.str_ip = str_ip
            self.str_msg = str_msg.decode("utf-8")
            self.current_numero = str_ip.split(".")[3]
            self.machine_identifier = str_ip.split(".")[2]

            switchcase = {
                '2': 'head',
                '3': 'furio',
                '4': 'joystick',
                '5': 'zoompoint',
                '6': 'panbar',
                '7': 'pedales',
                '10': 'poigneezoom',
                '11': 'poigneepoint'
            }

            method = getattr(self, switchcase.get(self.machine_identifier, "l'adresse IP ne correspond à rien"),
                             lambda: "Invalid request")
            return method()
        except UnicodeDecodeError:
            print("cant decode this message")

    """MACHINES ================================================================================================================== methodes MACHINES"""
    # fonction qui gere les messages qui arrivent des têtes
    def head(self):
        # print("mahugnon envoit", self.str_msg)
        if not self.flag_full_machine:  # si on n'a pas déjà 5 machines
            # si la machine n'est pas déjà enregistrée
            if self.str_ip not in self.mainapp.machines_list and len(self.mainapp.machines_list) <= 4:
                self.mainapp.machines_list.append(self.str_ip)  # on la rajoute
                self.settings.machines_list = self.mainapp.machines_list
                self.senderudp.txsend(b"H", self.str_ip)
                self.senderudp.txsend(bytes("OG", encoding='utf-8'), self.str_ip)
                self.flag_machines = True
            elif self.str_ip in self.mainapp.machines_list:  # si la machine est déjà enregistrée
                if "lost" in str(self.list_machine_alive[self.mainapp.machines_list.index(self.str_ip)]):
                    self.mainapp.warningpanel.setEverythingOk()
                    self.mainapp.btn_machine_list[self.mainapp.machines_list.index(self.str_ip)].setEnabled(True)
                else:
                    pass
        elif self.flag_full_machine and self.str_ip not in self.mainapp.machines_list:  # si on a déjà 5 machines d'enregistrés
            self.mainapp.error_nb_machines(self.str_ip)  # affiche une petite fenetre d'erreur

        if self.str_msg[0] == "A":  # Alive ?
            pass
        if self.str_msg[0] == "H":
            if "V6" in self.str_msg:
                self.mainapp.vers_tete[self.mainapp.machines_list.index(self.str_ip)] = "V6"
                self.settings.vers_tete = self.mainapp.vers_tete
            if "V5" in self.str_msg:
                self.mainapp.vers_tete[self.mainapp.machines_list.index(self.str_ip)] = "V5"
                self.settings.vers_tete = self.mainapp.vers_tete
            if "V4" in self.str_msg:
                self.mainapp.vers_tete[self.mainapp.machines_list.index(self.str_ip)] = "V4"
                self.settings.vers_tete = self.mainapp.vers_tete
            if "none" in self.str_msg:
                self.mainapp.vers_tete[self.mainapp.machines_list.index(self.str_ip)] = "None"
                self.settings.vers_tete = self.mainapp.vers_tete
            self.flag_machines = True
        if self.str_msg[0] == "M":
            status_moteurs = self.str_msg.split("O")[1]
            self.mainapp.state_motor_per_machine[self.mainapp.machines_list.index(self.str_ip)] = bool(int(status_moteurs))

        if self.str_msg[0] == "O":
            if self.str_msg[1] == "C":
                self.ref_optique[self.mainapp.machines_list.index(self.str_ip)] = self.str_msg.split("C")[1]
                self.mainapp.ref_optique = self.ref_optique
                self.settings.ref_optique = self.mainapp.ref_optique
                self.list_optique[self.mainapp.machines_list.index(self.str_ip)] = 'C'
            elif self.str_msg[1] == "F":
                self.ref_optique[self.mainapp.machines_list.index(self.str_ip)] = self.str_msg.split("F")[1]
                self.mainapp.ref_optique = self.ref_optique
                self.settings.ref_optique = self.mainapp.ref_optique
                self.list_optique[self.mainapp.machines_list.index(self.str_ip)] = 'F'
            else:
                self.ref_optique[self.mainapp.machines_list.index(self.str_ip)] = self.str_msg.split("O")[1]
                self.mainapp.ref_optique = self.ref_optique
                self.settings.ref_optique = self.mainapp.ref_optique
            self.flag_machines = True

        if "PGP" in self.str_msg:
            self.pan_position = int(self.str_msg.split("GP")[1])
        if "TGP" in self.str_msg:
            self.tilt_position = int(self.str_msg.split("P")[1])
        if "ZGP" in self.str_msg:
            self.val_zoom = int(self.str_msg.split("P")[1])
            self.memo_zoom = self.val_zoom
        else:
            pass

        try:
            self.list_machine_alive[self.mainapp.machines_list.index(self.str_ip)] = True
        except ValueError:
            print("not in list, too many machines")

    # fonction qui gere les messages qui arrivent des furios
    def furio(self):
        if not self.flag_full_machine:  # si on a pas déjà 5 machines
            # si la machine est n'est pas déjà enregistrée
            if self.str_ip not in self.mainapp.machines_list and len(self.mainapp.machines_list) <= 4:
                self.mainapp.machines_list.append(self.str_ip)  # on la rajoute
                self.settings.machines_list = self.mainapp.machines_list
                self.senderudp.txsend(b"H", self.str_ip)
                self.senderudp.txsend(b"CGT", self.str_ip)
                self.senderudp.txsend(bytes("OG", encoding='utf-8'), self.str_ip)
                self.flag_machines = True

            elif self.str_ip in self.mainapp.machines_list:  # si la machine est déjà enregistrée
                if "lost" in str(self.list_machine_alive[self.mainapp.machines_list.index(self.str_ip)]):
                    self.mainapp.warningpanel.setEverythingOk()
                    self.mainapp.btn_machine_list[self.mainapp.machines_list.index(self.str_ip)].setEnabled(True)
                    """self.senderudp.txsend(b"R", self.str_ip)
                    print("erreur d'affichage corrigée en envoyant un RESET au Furio, Si cette ligne s'affiche c'est que le furio n'a renvoyé qu'un ALIVE et aucun status de colonne FX MO None")"""
                else:
                    pass
        elif self.flag_full_machine and self.str_ip not in self.mainapp.machines_list:  # si on a déjà 5 machines d'enregistrés
            self.mainapp.error_nb_machines(self.str_ip)  # affiche une petite fenetre d'erreur

        if self.str_msg[0] == "A":  # Alive ?
            pass
        if self.str_msg[0] == "H":
            if "V6" in self.str_msg:
                self.mainapp.vers_tete[self.mainapp.machines_list.index(self.str_ip)] = "V6"
                self.settings.vers_tete = self.mainapp.vers_tete
            if "V5" in self.str_msg:
                self.mainapp.vers_tete[self.mainapp.machines_list.index(self.str_ip)] = "V5"
                self.settings.vers_tete = self.mainapp.vers_tete
            if "V4" in self.str_msg:
                self.mainapp.vers_tete[self.mainapp.machines_list.index(self.str_ip)] = "V4"
                self.settings.vers_tete = self.mainapp.vers_tete
            if "F" in self.str_msg:
                self.mainapp.vers_tete[self.mainapp.machines_list.index(self.str_ip)] = "F"
                self.settings.vers_tete = self.mainapp.vers_tete

            if "none" in self.str_msg:
                self.mainapp.vers_tete[self.mainapp.machines_list.index(self.str_ip)] = "None"
                self.settings.vers_tete = self.mainapp.vers_tete
            self.flag_machines = True

        if self.str_msg[0] == "C":
            if "FX" in self.str_msg:
                self.mainapp.vers_furio[self.mainapp.machines_list.index(self.str_ip)] = "FX"
            if "MO" in self.str_msg:
                self.mainapp.vers_furio[self.mainapp.machines_list.index(self.str_ip)] = "MO"
            if "none" in self.str_msg:
                self.mainapp.vers_furio[self.mainapp.machines_list.index(self.str_ip)] = "None"
            if "E" in self.str_msg:
                self.mainapp.code_erreur_Furio[0] = self.str_msg.split("E")[1]
                self.mainapp.vers_furio[self.mainapp.machines_list.index(self.str_ip)] = "error"
                self.mainapp.warningpanel.setErrorTips(self.str_msg[0] + self.str_msg.split("E")[1])
            if "Ccol" in self.str_msg:
                print("y'a pas de chariot mais y'a une colonne; héhé... Qu'est ce que je fais de cet info moi ?")
            if "GP" in self.str_msg:
                self.lift_position = int(self.str_msg.split("GP")[1])
            self.flag_machines = True

        if self.str_msg[0] == "B":
            if "E" in self.str_msg:
                self.mainapp.code_erreur_Furio[1] = self.str_msg.split("E")[1]
                self.mainapp.warningpanel.setErrorTips(self.str_msg[0] + self.str_msg.split("E")[1])
            if "GP" in self.str_msg:
                self.track_position = int(self.str_msg.split("GP")[1])

        if self.str_msg[0] == "O":
            if "C" in self.str_msg:
                self.ref_optique[self.mainapp.machines_list.index(self.str_ip)] = self.str_msg.split("C")[1]
                self.mainapp.ref_optique = self.ref_optique
                self.settings.ref_optique = self.mainapp.ref_optique
                self.list_optique[self.mainapp.machines_list.index(self.str_ip)] = 'C'
            elif "F" in self.str_msg:
                self.ref_optique[self.mainapp.machines_list.index(self.str_ip)] = self.str_msg.split("F")[1]
                self.mainapp.ref_optique = self.ref_optique
                self.settings.ref_optique = self.mainapp.ref_optique
                self.list_optique[self.mainapp.machines_list.index(self.str_ip)] = 'F'
            else:
                self.ref_optique[self.mainapp.machines_list.index(self.str_ip)] = self.str_msg.split("O")[1]
                self.mainapp.ref_optique = self.ref_optique
                self.settings.ref_optique = self.mainapp.ref_optique
            self.flag_machines = True

        if self.str_msg[0] == "F":  # status des fins de course
            status = self.str_msg.split("F")[1]
            list_status = (bool(int(status[0])), bool(int(status[1])), bool(int(status[2])), bool(int(status[3])))
            self.mainapp.flag_furio = list_status
            self.mainapp.update_status_butee()

        if self.str_msg[0] == "M":
            status_moteurs = self.str_msg.split("O")[1]
            self.mainapp.state_motor_per_machine[self.mainapp.machines_list.index(self.str_ip)] = bool(int(status_moteurs))
            print("moteur status :", status_moteurs)
        if "PGP" in self.str_msg:
            self.pan_position = int(self.str_msg.split("GP")[1])
        if "TGP" in self.str_msg:
            self.tilt_position = int(self.str_msg.split("P")[1])
        if "ZGP" in self.str_msg:
            self.val_zoom = int(self.str_msg.split("P")[1])
            self.memo_zoom = self.val_zoom
        else:
            pass
        try:
            self.list_machine_alive[self.mainapp.machines_list.index(self.str_ip)] = True
        except ValueError:
            print("not in list, too many machines")

    """COMMANDES ===================================================================================================================== methode COMMANDES"""

    # fonction qui gere les messages qui arrivent d'un joystick
    def joystick(self):
        if self.mainapp.cmd_list[0] == '':
            self.mainapp.cmd_list[0] = self.str_ip
            self.settings.set_status(0, "Boitier", self.str_ip.split(".")[3])
            self.senderudp.txsend(bytes("SG", encoding='utf-8'), self.str_ip)
            self.list_cmd_alive[0] = True
            self.flag_cmd = True
            if self.panbar_set is False:
                self.joystick_set = True

        elif self.str_ip == self.mainapp.cmd_list[0]:
            pass
        elif not self.flag_waiting_reponse:
            self.error_msg = 'joystick n°' + self.str_ip.split('.')[3]
            self.siglauncher.error_cmd.emit()
            self.flag_waiting_reponse = True

        if self.str_msg[0] == "C":
            self.settings.launch_windows_calibration()
        if self.str_msg[0] == "S":
            self.settings.label_data_seuil_list[0].setText(self.str_msg.split("S")[1])
            if not self.set_edit_seuil_joy_once:
                self.settings.label_edit_seuil_list[0].setText(self.str_msg.split("S")[1])
                self.set_edit_seuil_joy_once = True

        if self.str_msg[0] == "P":  # si le message commence par P c'est une commande donc on la traite
            if "T" in self.str_msg:
                self.last_pan_data = float(
                    self.str_msg.split('T')[0][1:])  # on decoupe le message pour recupérer la valeur du pan
                self.last_tilt_data = float(self.str_msg.split('T')[1])
            else:
                self.last_pan_data = float(self.str_msg.split('P')[1])

        elif self.str_msg[0] == "T":  # si le message commence par T ya que le tilt
            self.last_tilt_data = float(self.str_msg.split('T')[1])
        else:
            pass

        try:
            self.list_cmd_alive[0] = True

        except ValueError:
            print("not in list, too many cmd")

    # fonction qui gere les messages qui arrivent d'un panBar
    def panbar(self):
        if self.mainapp.cmd_list[0] == '':
            self.mainapp.cmd_list[0] = self.str_ip
            self.settings.set_status(0, "PanBar", self.str_ip.split(".")[3])
            self.list_cmd_alive[0] = True
            self.flag_cmd = True
            self.flag_first_val_tilt = True
            self.flag_first_val_pan = True
            if self.joystick_set is False:
                self.panbar_set = True

        elif self.str_ip == self.mainapp.cmd_list[0]:
            pass
        elif not self.flag_waiting_reponse:
            self.error_msg = 'panbar n°' + self.str_ip.split('.')[3]
            self.siglauncher.error_cmd.emit()
            self.flag_waiting_reponse = True

        if self.str_msg[0] == 'D':
            if "1" in self.str_msg:
                self.vitesse_x2 = True
            elif "0" in self.str_msg:
                self.vitesse_x2 = False
            else:
                pass

        if self.str_msg[0] == "P":  # si le message commence par P c'est une commande donc on la traite
            if "T" in self.str_msg:
                self.last_panbar_pan_data = float(self.str_msg.split('T')[0][1:]) if not self.debrayage_panbar else float(0)  # on decoupe le message pour recupérer la valeur du pan
                self.last_panbar_tilt_data = float(self.str_msg.split('T')[1]) if not self.debrayage_panbar else float(0)
            else:
                self.last_panbar_pan_data = float(self.str_msg.split('P')[1]) if not self.debrayage_panbar else float(0)

        elif self.str_msg[0] == "T":  # si le message commence par T ya que le tilt
            self.last_panbar_tilt_data = float(self.str_msg.split('T')[1]) if not self.debrayage_panbar else float(0)
        else:
            pass

        try:
            self.list_cmd_alive[0] = True

        except ValueError:
            print("not in list, too many cmd")

    # fonction qui gere les messages qui arrivent d'un boitier Z/P
    def zoompoint(self):
        if self.mainapp.cmd_list[1] == '' and self.mainapp.cmd_list[3] == '' and self.mainapp.cmd_list[4] == '':
            self.mainapp.cmd_list[1] = self.str_ip
            self.settings.set_status(1, "Boitier", self.str_ip.split(".")[3])
            self.settings.set_status(6, "Boitier", self.str_ip.split(".")[3])
            self.senderudp.txsend(bytes("SG", encoding='utf-8'), self.str_ip)
            self.list_cmd_alive[1] = True
            self.flag_cmd = True

        elif self.str_ip == self.mainapp.cmd_list[1]:
            pass

        elif not self.flag_waiting_reponse:
            self.error_msg_optic = 'ZoomPoint n°' + self.str_ip.split('.')[3]
            self.siglauncher.error_optic_cmd.emit()
            self.flag_waiting_reponse = True

        if self.str_msg[0] == "M":
            self.switch_machine = int(self.str_msg.split("M")[1])
        if self.str_msg[0] == "C":
            self.settings.launch_windows_calibration()

        if self.str_msg[0] == "S":
            self.settings.label_data_seuil_list[1].setText(self.str_msg.split("Z")[1].split("M")[0])
            self.settings.label_data_seuil_list[6].setText(self.str_msg.split("M")[1])
            if not self.set_edit_seuil_once:
                self.settings.label_edit_seuil_list[1].setText(self.str_msg.split("Z")[1].split("M")[0])
                self.settings.label_edit_seuil_list[6].setText(self.str_msg.split("M")[1])
                self.set_edit_seuil_once = True

        if self.str_msg[0] == "Z":  # si le message commence par Z c'est une commande donc on la traite
            self.last_zoom_data = float(self.str_msg.split('Z')[1])

        if self.str_msg[0] == "F":  # si le message commence par F ya que point
            focuscmd = float(self.str_msg.split('F')[1])
            self.computing_data_focus(focuscmd)
        else:
            pass
        self.list_cmd_alive[1] = True

    # fonction qui gere les messages qui arrivent d'une poignée Zoom
    def poigneezoom(self):
        if self.mainapp.cmd_list[1] == '' and self.mainapp.cmd_list[3] == '':
            self.mainapp.cmd_list[3] = self.str_ip
            """ self.settings.set_status(1, "Boitier", self.str_ip.split(".")[3])
            self.settings.set_status(6, "Boitier", self.str_ip.split(".")[3])"""
            self.settings.set_status(7, "Poignée", self.str_ip.split(".")[3])
            self.senderudp.txsend(bytes("SG", encoding='utf-8'), self.str_ip)
            self.list_cmd_alive[3] = True
            self.flag_cmd = True

        elif self.str_ip == self.mainapp.cmd_list[3]:
            pass

        elif not self.flag_waiting_reponse:
            self.error_msg_optic = 'Poignee de zoom n°' + self.str_ip.split('.')[3]
            self.siglauncher.error_optic_cmd.emit()
            self.flag_waiting_reponse = True

        if self.str_msg[0] == "S":
            self.settings.label_data_seuil_list[7].setText(self.str_msg.split("S")[1])
            if not self.set_edit_seuil_joy_once:
                self.settings.label_edit_seuil_list[0].setText(self.str_msg.split("S")[1])
                self.set_edit_seuil_joy_once = True
        if self.str_msg[0] == "M":
            self.switch_machine = int(self.str_msg.split("M")[1])
        if self.str_msg[0] == "D":
            if "1" in self.str_msg:
                self.debrayage_panbar = True
            elif "0" in self.str_msg:
                self.debrayage_panbar = False
            else:
                pass
        if self.str_msg[0] == "C":
            self.settings.launch_windows_calibration()
        if self.str_msg[0] == "A":  # Alive ?
            pass

        """if self.str_msg[0] == "S":
            self.settings.label_data_seuil_list[1].setText(self.str_msg.split("Z")[1].split("M")[0])
            self.settings.label_data_seuil_list[6].setText(self.str_msg.split("M")[1])
            if not self.set_edit_seuil_once:
                self.settings.label_edit_seuil_list[1].setText(self.str_msg.split("Z")[1].split("M")[0])
                self.settings.label_edit_seuil_list[6].setText(self.str_msg.split("M")[1])
                self.set_edit_seuil_once = True"""

        if self.str_msg[0] == "Z":  # si le message commence par Z c'est une commande donc on la traite
            self.last_zoom_data = float(self.str_msg.split('Z')[1])

        self.list_cmd_alive[3] = True

    # fonction qui gere les messages qui arrivent d'une poignée Point
    def poigneepoint(self):
        if self.mainapp.cmd_list[1] == '' and self.mainapp.cmd_list[4] == '':
            self.mainapp.cmd_list[4] = self.str_ip
            """ self.settings.set_status(1, "Boitier", self.str_ip.split(".")[3])
            self.settings.set_status(6, "Boitier", self.str_ip.split(".")[3])"""
            self.list_cmd_alive[4] = True
            self.flag_cmd = True

        elif self.str_ip == self.mainapp.cmd_list[4]:
            pass

        elif not self.flag_waiting_reponse:
            self.error_msg_optic = 'Poignee de point n°' + self.str_ip.split('.')[3]
            self.siglauncher.error_optic_cmd.emit()
            self.flag_waiting_reponse = True

        """if self.str_msg[0] == "S":
            self.settings.label_data_seuil_list[1].setText(self.str_msg.split("Z")[1].split("M")[0])
            self.settings.label_data_seuil_list[6].setText(self.str_msg.split("M")[1])
            if not self.set_edit_seuil_once:
                self.settings.label_edit_seuil_list[1].setText(self.str_msg.split("Z")[1].split("M")[0])
                self.settings.label_edit_seuil_list[6].setText(self.str_msg.split("M")[1])
                self.set_edit_seuil_once = True"""

        if self.str_msg[0] == "F":
            focuscmd = float(self.str_msg.split('F')[1])
            self.computing_data_focus(focuscmd)

        if self.str_msg[0] == "A":  # Alive ?
            pass
        else:
            pass
        self.list_cmd_alive[4] = True

    # fonction qui gere les messages qui arrivent des pedales
    def pedales(self):
        if self.mainapp.cmd_list[2] == '':
            self.mainapp.cmd_list[2] = self.str_ip
            self.settings.set_status(2, "Boitier", self.str_ip.split(".")[3])
            self.senderudp.txsend(bytes("SG", encoding='utf-8'), self.str_ip)
            self.list_cmd_alive[0] = True
            self.flag_cmd = True
            self.pedales_set = True

        elif self.str_ip == self.mainapp.cmd_list[2]:
            pass
        elif not self.flag_waiting_reponse:
            self.error_msg = 'pedale n°' + self.str_ip.split('.')[3]
            self.siglauncher.error_cmd.emit()
            self.flag_waiting_reponse = True

        if self.str_msg[0] == "S":
            self.settings.label_data_seuil_list[4].setText(self.str_msg.split('U')[1].split("D")[0])
            self.settings.label_data_seuil_list[5].setText(self.str_msg.split('D')[1].split("L")[0])
            self.settings.label_data_seuil_list[2].setText(self.str_msg.split('L')[1].split("R")[0])
            self.settings.label_data_seuil_list[3].setText(self.str_msg.split("R")[1])
            if not self.set_edit_seuil_pedale_once:
                self.settings.label_edit_seuil_list[4].setText(self.str_msg.split('U')[1].split("D")[0])
                self.settings.label_edit_seuil_list[5].setText(self.str_msg.split('D')[1].split("L")[0])
                self.settings.label_edit_seuil_list[2].setText(self.str_msg.split('L')[1].split("R")[0])
                self.settings.label_edit_seuil_list[3].setText(self.str_msg.split("R")[1])
                self.set_edit_seuil_pedale_once = True

        if self.str_msg[0] == "C":  # si le message commence par C c'est une commande lift ou lift + track
            if "R" in self.str_msg:
                self.last_lift_data = float(
                    self.str_msg.split('R')[0][1:])  # on decoupe le message pour recupérer la valeur de track
                self.last_track_data = float(self.str_msg.split('R')[1])
            else:
                self.last_lift_data = float(self.str_msg.split('C')[1])

        elif self.str_msg[0] == "R":  # si le message commence par R ya que le chariot
            self.last_track_data = float(self.str_msg.split('R')[1])
        else:
            pass

        try:
            self.list_cmd_alive[2] = True

        except ValueError:
            print("not in list, too many cmd")

    """METHODES DE CALCULS ================================================================================================== METHODES DE CALCULS"""

    # Scale de la valeur de zoom en fonction du type d'optique
    def get_valzoom(self):
        try:
            if self.list_optique[self.mainapp.machines_list.index(self.mainapp.machine_selected)] == 'F':
                val_zoom_percent = self.val_zoom / 65535
            elif self.list_optique[self.mainapp.machines_list.index(self.mainapp.machine_selected)] == 'C':
                val_zoom_percent = self.val_zoom / 60000
            else:
                val_zoom_percent = 0

            return val_zoom_percent

        except ValueError:
            print("zoom assist cant work without machine")
            return 0
        except TypeError:
            print("val zoom not received yet")

    # Methode de calcul : Filtre de butterworth
    @staticmethod
    def filtre_freg(in_val, f, x):  # faire tourner à vide 10x a peu près ?

        """"x[0] = in_val
        t1 = f * f
        t5 = x[1]
        t10 = 0.1570796327e12 * f
        t11 = 0.4934802202e10 * t1
        t17 = x[4]

        temp1 = 0.1250000000e13 + t11 + t10
        temp2 = 0.4934802202e10 * t1 * x[2]
        temp3 = 0.9869604404e10 * t1 * t5
        temp4 = 0.4934802202e10 * t1 * in_val
        temp5 = (-t10 + 0.1250000000e13 + t11) * x[5]
        temp6 = (-0.2500000000e13 + (0.9869604405e10 * t1)) * t17
        x[0] = temp2

        x[3] = (temp2 + temp3 + temp4 - temp5 - temp6) / temp1
        ret_val = x[3]
        x[2] = t5
        x[1] = in_val
        x[5] = t17
        x[4] = ret_val"""

        t1 = f * f
        t5 = x[1]
        t10 = 0.1570796327e12 * f
        t11 = 0.4934802202e10 * t1
        t17 = x[4]
        x[3] = (0.4934802202e10 * t1 * x[2] + 0.9869604404e10 * t1 * t5 + 0.4934802202e10 * t1 * in_val - (
                -t10 + 0.1250000000e13 + t11) * x[5] - (-0.2500000000e13 + 0.9869604405e10 * t1) * t17) / (
                       0.1250000000e13 + t11 + t10)

        ret_val = x[3]
        x[2] = t5
        x[1] = in_val
        x[5] = t17
        x[4] = ret_val

        return ret_val

    # Methode de calcul exponentiel
    @staticmethod
    def expo_cmd(joy, vit, expo):
        if joy < 0:
            ret_vit_joy = ((exp(-expo * joy) - 1) / (exp(expo) - 1)) * (-vit)
        else:
            ret_vit_joy = ((exp(expo * joy) - 1) / (exp(expo) - 1)) * vit
        return ret_vit_joy

    # Methode qui centralise tout les calculs des données joystick pan et qui applique l'inversion
    def computing_data_pan(self, pan_data):
        pan_data = self.filtre_freg(pan_data, self.mainapp.ratio_pan, self.list_butterworth_pan[self.current_index_machine])
        pan_data = self.expo_cmd(pan_data, self.mainapp.vitesse_pan, self.mainapp.courbe_pan)

        if self.mainapp.btninvertpan.isChecked():
            pan_data = (-1) * pan_data
        else:
            pass

        if self.mainapp.zoomassistIsEnable:
            val_zoom = self.get_valzoom()
            factor = pan_data * self.mainapp.zoomassistFactor
            pan_data = pan_data - factor * val_zoom

        self.pan_data = round(pan_data)
        if self.old_pan_data != self.pan_data:
            tosend = "PV" + str(self.pan_data)
            self.senderudp.txsend(bytes(tosend, encoding='utf-8'), self.mainapp.machine_selected)
        self.old_pan_data = round(self.pan_data)

    # Methode qui centralise tout les calculs des données joystick tilt et qui applique l'inversion
    def computing_data_tilt(self, tilt_data):
        tilt_data = self.filtre_freg(tilt_data, self.mainapp.ratio_tilt, self.list_butterworth_tilt[self.current_index_machine])
        tilt_data = self.expo_cmd(tilt_data, self.mainapp.vitesse_tilt, self.mainapp.courbe_tilt)

        if self.mainapp.btninverttilt.isChecked():
            tilt_data = (-1) * tilt_data
        else:
            pass

        if self.mainapp.zoomassistIsEnable:
            val_zoom = self.get_valzoom()
            factor = tilt_data * self.mainapp.zoomassistFactor
            tilt_data = tilt_data - factor * val_zoom

        self.tilt_data = round(tilt_data)
        if self.old_tilt_data != self.tilt_data:
            tosend = "TV" + str(self.tilt_data)
            self.senderudp.txsend(bytes(tosend, encoding='utf-8'), self.mainapp.machine_selected)
        self.old_tilt_data = round(self.tilt_data)

    # Idem panbar pan
    def computing_data_panbar_pan(self, panbar_pan_data):
        pan_data = self.filtre_freg(panbar_pan_data, self.mainapp.ratio_pan, self.list_butterworth_panbar_pan[self.current_index_machine])
        pan_data = self.expo_cmd(pan_data, self.mainapp.vitesse_pan, self.mainapp.courbe_pan)

        if self.mainapp.btninvertpan.isChecked():
            pan_data = (-1) * pan_data
        else:
            pass

        if self.vitesse_x2:
            pan_data *= 2

        if self.mainapp.zoomassistIsEnable:
            val_zoom = self.get_valzoom()
            factor = pan_data * self.mainapp.zoomassistFactor
            pan_data = pan_data - factor * val_zoom

        self.panbar_pan_data = round(pan_data)
        if self.panbar_pan_data != self.old_panbar_pan_data:
            tosend = "PV" + str(self.panbar_pan_data)
            self.senderudp.txsend(bytes(tosend, encoding='utf-8'), self.mainapp.machine_selected)
            self.old_panbar_pan_data = round(pan_data)

    # Idem panbar tilt
    def computing_data_panbar_tilt(self, panbar_tilt_data):
        tilt_data = self.filtre_freg(panbar_tilt_data, self.mainapp.ratio_tilt, self.list_butterworth_panbar_tilt[self.current_index_machine])
        tilt_data = self.expo_cmd(tilt_data, self.mainapp.vitesse_tilt, self.mainapp.courbe_tilt)

        if self.mainapp.btninverttilt.isChecked():
            tilt_data = (-1) * tilt_data
        else:
            pass

        if self.mainapp.zoomassistIsEnable:
            val_zoom = self.get_valzoom()
            factor = tilt_data * self.mainapp.zoomassistFactor
            tilt_data = tilt_data - factor * val_zoom

        self.panbar_tilt_data = int(tilt_data)
        if self.panbar_tilt_data != self.old_panbar_tilt_data:
            tosend = "TV" + str(self.panbar_tilt_data)
            self.senderudp.txsend(bytes(tosend, encoding='utf-8'), self.mainapp.machine_selected)
            self.old_panbar_tilt_data = round(tilt_data)

    # Idem track
    def computing_data_track(self, track_data):
        track_data = self.filtre_freg(track_data, self.mainapp.ratio_track, self.list_butterworth_track[self.current_index_machine])
        track_data = self.expo_cmd(track_data, self.mainapp.vitesse_track, self.mainapp.courbe_track)
        if self.mainapp.btninverttrack.isChecked():
            track_data = (-1) * track_data
        else:
            pass

        self.track_data = round(track_data)
        if self.old_track_data != self.track_data:
            tosend = "BV" + str(self.track_data)
            self.senderudp.txsend(bytes(tosend, encoding='utf-8'), self.mainapp.machine_selected)
        self.old_track_data = round(self.track_data)

    # Idem Lift data
    def computing_data_lift(self, lift_data):
        lift_data = self.filtre_freg(lift_data, self.mainapp.ratio_lift, self.list_butterworth_lift[self.current_index_machine])
        lift_data = self.expo_cmd(lift_data, self.mainapp.vitesse_lift, self.mainapp.courbe_lift)
        if self.mainapp.btninvertlift.isChecked():
            lift_data = (-1) * lift_data
        else:
            pass

        self.lift_data = round(lift_data)
        if self.old_lift_data != self.lift_data:
            tosend = "CV" + str(self.lift_data)
            self.senderudp.txsend(bytes(tosend, encoding='utf-8'), self.mainapp.machine_selected)
        self.old_lift_data = round(self.lift_data)

    # Idem pour le zoom
    def computing_data_joyzoom(self, zoom_data):
        zoom_data = self.filtre_freg(zoom_data, self.ratio_zoom, self.list_butterworth_zoom[self.current_index_machine])
        zoom_data = self.expo_cmd(zoom_data, self.mainapp.vitesse_zoom, self.courbe_zoom)
        if self.mainapp.btninvertzoom.isChecked():
            zoom_data = (-1) * zoom_data
        else:
            pass

        self.zoom_data = round(zoom_data)
        if self.old_zoom_data != self.zoom_data:
            tosend = "ZV" + str(self.zoom_data)
            self.senderudp.txsend(bytes(tosend, encoding='utf-8'), self.mainapp.machine_selected)
        self.old_zoom_data = self.zoom_data

    # Idem pour point
    def computing_data_focus(self, focus_data):
        self.focus = self.mainapp.machine_focus_position[self.mainapp.machines_list.index(self.mainapp.machine_selected)] if self.mainapp.machine_selected != '' else self.focus

        if self.mainapp.indicator_focus.button_precision.isChecked():
            focus_data /= 10

        if self.mainapp.btninvertfocus.isChecked():
            focus_data = (-1) * focus_data

        if self.mainapp.flag_raz_focus:
            if self.mainapp.flag_focus:
                self.mainapp.indicator_focus.val_iris = self.focus
                self.focus = self.mainapp.indicator_focus.val_focus

            if not self.mainapp.flag_focus:
                self.mainapp.indicator_focus.val_focus = self.focus
                self.focus = self.mainapp.indicator_focus.val_iris
            self.mainapp.flag_raz_focus = False

        self.focus += focus_data

        if self.focus > 16383:
            self.focus = 16383
        if self.focus < 0:
            self.focus = 0

        self.mainapp.indicator_focus.updateline(int(self.focus), str(int(self.focus)))

        if self.mainapp.machine_selected != "":
            self.mainapp.machine_focus_position[self.mainapp.machines_list.index(self.mainapp.machine_selected)] = int(self.focus)

        self.focus_data = round(self.focus * 60000 / 16383)

        if self.old_focus_data != self.focus_data:
            if self.mainapp.indicator_focus.flag_iris:
                tosend = "DP" + str(self.focus_data)
            else:
                tosend = "FP" + str(self.focus_data)
            self.senderudp.txsend(bytes(tosend, encoding='utf-8'), self.mainapp.machine_selected)
        self.old_focus_data = self.focus_data

    """BOUCLE PRINCIPALE MAESTRO ====================================================================================== BOUCLE PRINCIPALE MAESTRO"""

    # boucle Maestro (interaction avec la fenetre Qt)
    def maestro_main(self, u):
        global flag_logging_udp
        # on initialise le timer
        hdeb = time.time()
        # self.mainapp.warningpanel.label_tips.setText(str(self.depth))
        self.senderudp.txsend(b'R', '200.200.255.255')
        self.thread_number = libc.syscall(thread_ID_number)
        while True:
            # Compteur par 10ms
            hfin = time.time()
            if hfin - hdeb >= 0.01:
                self.ctn_alive += 1
                self.ctn_zass += 1
                self.ctn_computing += 1
                self.ctn_affichage += 1
                self.ctn_computing_track += 1
                self.ctn_debug += 1
                if self.checker_cmd:
                    self.ctn_responce += 1
                if self.checker_tete:
                    self.ctn_responce_h += 1
                hdeb = time.time()

            # Envoit aux fonction de calcul des vitesses et position======================================================= COMPUTING
            if self.ctn_computing >= 2:
                if self.joystick_set:
                    self.computing_data_pan(self.last_pan_data)
                    self.computing_data_tilt(self.last_tilt_data)
                elif self.panbar_set:
                    self.computing_data_panbar_pan(self.last_panbar_pan_data)
                    self.computing_data_panbar_tilt(self.last_panbar_tilt_data)
                if self.pedales_set:
                    self.computing_data_track(self.last_track_data)
                    self.computing_data_lift(self.last_lift_data)
                self.computing_data_joyzoom(self.last_zoom_data)
                self.ctn_computing = 0

            if self.ctn_computing_track >= 1:
                if self.pedales_set:
                    self.computing_data_track(self.last_track_data)
                else:
                    pass
                self.ctn_computing_track = 0

            if self.ctn_debug >= 100:
                flag_logging_udp = True
                self.flag_logging_request = True
                for threads in self.p.threads():
                    if threads[0] == self.thread_number:  # 224 on rasp
                        self.thread_info_maestro = threads
                        break
                if self.thread_info_maestro is not str:
                    calc = round(self.p.cpu_percent(0.1) * ((self.thread_info_maestro.system_time + self.thread_info_maestro.user_time) / sum(self.p.cpu_times())), 1)
                    logging.info("CPU Usage:" + str(calc) + "% ") if calc > 10 else None

                self.ctn_debug = 0

            # Destructeur de materiels déconnectés ======================================================================== Deconnecteur
            if self.ctn_responce >= 50:
                for cmd in self.mainapp.cmd_list:
                    if cmd != '':
                        idx = self.mainapp.cmd_list.index(cmd)
                        if not self.list_cmd_alive[idx]:
                            self.mainapp.unset_cmd_btn(self.mainapp.cmd_list[idx])
                            self.settings.unset_status(idx)
                            if self.mainapp.cmd_list[idx].split(".")[2] == '6':
                                self.panbar_set = False
                                self.senderudp.txsend(bytes('PV0', encoding='utf-8'), self.mainapp.machine_selected)
                                self.senderudp.txsend(bytes('TV0', encoding='utf-8'), self.mainapp.machine_selected)
                                self.senderudp.txsend(bytes('ZV0', encoding='utf-8'), self.mainapp.machine_selected)
                                self.list_butterworth_panbar_pan = [[0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0],
                                                                    [0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0]]
                                self.list_butterworth_panbar_tilt = [[0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0],
                                                                     [0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0]]
                            elif self.mainapp.cmd_list[idx].split(".")[2] == '4':
                                self.senderudp.txsend(bytes('PV0', encoding='utf-8'), self.mainapp.machine_selected)
                                self.senderudp.txsend(bytes('TV0', encoding='utf-8'), self.mainapp.machine_selected)
                                self.senderudp.txsend(bytes('ZV0', encoding='utf-8'), self.mainapp.machine_selected)
                                self.joystick_set = False
                                self.list_butterworth_pan = [[0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0],
                                                             [0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0]]
                                self.list_butterworth_tilt = [[0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0],
                                                              [0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0]]
                            elif self.mainapp.cmd_list[idx].split(".")[2] == '7':
                                self.senderudp.txsend(bytes('R0', encoding='utf-8'), self.mainapp.machine_selected)
                                self.senderudp.txsend(bytes('C0', encoding='utf-8'), self.mainapp.machine_selected)
                                self.list_butterworth_track = [[0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0],
                                                               [0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0]]
                                self.list_butterworth_lift = [[0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0],
                                                              [0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0]]
                            self.mainapp.cmd_list[idx] = ''
                            self.list_cmd_alive[idx] = 'false'
                            print("la commande répond pas, elle dégage")
                        else:
                            pass

                self.checker_cmd = False
                self.ctn_responce = 0

            if self.ctn_responce_h >= 50:
                for machine in self.mainapp.machines_list:
                    idx = self.mainapp.machines_list.index(machine)
                    if self.list_machine_alive[idx] == False:
                        self.mainapp.unset_machine_buttons(self.mainapp.machines_list[idx])
                        self.settings.unset_machine_buttons(self.settings.machines_list[idx])
                        self.list_machine_alive[idx] = "lost"
                        self.mainapp.vers_tete[idx] += 'lost' if "lost" not in self.mainapp.vers_tete[idx] else ''
                        self.settings.vers_tete[idx] += 'lost' if "lost" not in self.settings.vers_tete[idx] else ''
                        self.mainapp.vers_furio[idx] += 'lost' if "lost" not in self.mainapp.vers_furio[idx] else ''
                        if self.mainapp.machines_list[idx] == self.mainapp.machine_selected:
                            self.mainapp.machine_selected = ''
                            self.settings.machine_selected = ''
                        else:
                            pass
                        self.settings.machines_list = self.mainapp.machines_list
                        self.flag_full_machine = False
                        self.list_butterworth_pan[idx] = [0, 0, 0, 0, 0, 0]
                        self.list_butterworth_tilt[idx] = [0, 0, 0, 0, 0, 0]
                        self.list_butterworth_panbar_pan[idx] = [0, 0, 0, 0, 0, 0]
                        self.list_butterworth_panbar_tilt[idx] = [0, 0, 0, 0, 0, 0]
                        self.list_butterworth_track[idx] = [0, 0, 0, 0, 0, 0]
                        self.list_butterworth_lift[idx] = [0, 0, 0, 0, 0, 0]
                        if self.mainapp.btn_release.isChecked():
                            self.mainapp.btn_release.click()
                        print("Ca répond pas, ca dégage")

                    elif "lost" in str(self.list_machine_alive[idx]):
                        self.mainapp.warningpanel.setTips("Le boitier tête n°" + machine.split(".")[3] + " est déconnecté\nTentative de reconnexion...")
                        self.flag_machines = True
                        self.senderudp.txsend(b'R', machine)
                    else:
                        pass
                    self.checker_tete = False
                    self.ctn_responce_h = 0

            # On regarde si tout les equipements sont toujours connectés ================================================== Check Deconnexion
            if self.ctn_alive >= 100:
                print("ctn alive at 100")
                """request_buffer.append((b"CMO", "200.200.3.1"))
                request_buffer.append((b"A", "200.200.3.1"))
                request_buffer.append((b"F0101", "200.200.3.1"))"""

                for machine in self.mainapp.machines_list:
                    if self.list_machine_alive[self.mainapp.machines_list.index(machine)]:
                        self.list_machine_alive[self.mainapp.machines_list.index(machine)] = False
                        print("sending Alive")
                        self.senderudp.txsend(b'A', machine)
                    else:
                        print("sending Alive")
                        self.senderudp.txsend(b'A', machine)
                        self.checker_tete = True

                for cmd in self.mainapp.cmd_list:
                    if cmd != '':
                        if self.list_cmd_alive[self.mainapp.cmd_list.index(cmd)]:
                            self.list_cmd_alive[self.mainapp.cmd_list.index(cmd)] = False
                            print("sending Alive")
                            self.senderudp.txsend(b'A', cmd)
                        else:
                            print("sending Alive")
                            self.senderudp.txsend(b'A', cmd)
                            self.checker_cmd = True
                self.ctn_alive = 0

            #  Action Supervision  ========================================================================================== Action Supervision
            if not self.win.gosuper:
                self.flag_stop = False
                self.flag_signal_settings = False

            if self.win.gosuper:
                if self.ctn_affichage >= 20:
                    if self.panbar_set:
                        self.siglauncher.vitesse_panbar_setter.emit()
                        self.siglauncher.vitesse_recue_panbar_setter.emit()
                    else:
                        self.siglauncher.vitesse_setter.emit()
                        self.siglauncher.vitesse_recue_setter.emit()

                    self.ctn_affichage = 0

                if not self.flag_signal_settings:
                    self.flag_signal_settings = True

                if self.settings.iris_on:
                    tosend = "DEN"
                    self.senderudp.txsend(bytes(tosend, encoding='utf-8'), self.mainapp.machine_selected)
                    self.settings.iris_on = False
                if not self.settings.iris_off:
                    # tosend = "DDI"
                    # self.senderudp.txSend(bytes(tosend, encoding='utf-8'), self.mainapp.machine_selected)
                    self.settings.iris_off = False
                    self.mainapp.switch_diaph.setValue(1)

                if self.settings.enablemotors != "":
                    for button in (self.settings.btn_enable_pan, self.settings.btn_enable_tilt, self.settings.btn_enable_track, self.settings.btn_enable_lift, self.settings.btn_enable_all):
                        if button.text() == self.settings.enablemotors and button.isChecked():
                            whitchoneisenable = {
                                self.settings.btn_enable_pan: b'PSEN',
                                self.settings.btn_enable_tilt: b'TSEN',
                                self.settings.btn_enable_track: b'BSEN',
                                self.settings.btn_enable_lift: b'CSEN',
                                self.settings.btn_enable_all: [b'PSEN', b'TSEN', b'BSEN', b'CSEN'],
                            }
                            tosend = whitchoneisenable.get(button, "unknown button")
                            if type(tosend) == list:
                                for message in tosend:
                                    self.senderudp.txsend(message, self.settings.machine_selected)
                            else:
                                self.senderudp.txsend(tosend, self.settings.machine_selected)
                            break
                        elif button.text() == self.settings.enablemotors and not button.isChecked():
                            whitchoneisdisable = {
                                self.settings.btn_enable_pan: b'PSDI',
                                self.settings.btn_enable_tilt: b'TSDI',
                                self.settings.btn_enable_track: b'BSDI',
                                self.settings.btn_enable_lift: b'CSDI',
                                self.settings.btn_enable_all: [b'PSDI', b'TSDI', b'BSDI', b'CSDI'],
                            }
                            tosend = whitchoneisdisable.get(button, "unknown button")
                            if type(tosend) == list:
                                for message in tosend:
                                    self.senderudp.txsend(message, self.settings.machine_selected)
                            else:
                                self.senderudp.txsend(tosend, self.settings.machine_selected)
                            break
                        else:
                            pass
                    self.settings.enablemotors = ""

                '''if self.settings.machine_selected_changes:
                    self.mainapp.btn_machine_list[self.settings.machines_list.index(self.settings.machine_selected)].click()
                    self.mainapp.index = self.settings.index
                    self.mainapp.old_index = self.settings.old_index
                    self.settings.machine_selected_changes = False
                    self.mainapp.machine_selected_changes = False'''

                # Envoie des demande de maj seuil pour n'importe quel boitier connecté
                if any(self.settings.list_seuil):
                    index = self.settings.list_seuil.index(True)

                    witchseuil = {
                        0: 0,
                        1: 1,
                        2: (2, 'DL'),
                        3: (2, 'DR'),
                        4: (2, 'DU'),
                        5: (2, 'DD'),
                        6: 1,
                        7: 3,
                    }
                    cmdlistidx = witchseuil.get(index, "No index for that key")
                    if index < 2 or index == 7:
                        tosend = bytes("SD" + self.settings.label_edit_seuil_list[index].text(), encoding='utf-8')
                        self.senderudp.txsend(tosend, self.mainapp.cmd_list[cmdlistidx])
                    elif index == 6:
                        tosend = bytes("SM" + self.settings.label_edit_seuil_list[index].text(), encoding='utf-8')
                        self.senderudp.txsend(tosend, self.mainapp.cmd_list[cmdlistidx])
                    else:
                        idex, axes = cmdlistidx
                        tosend = bytes("S" + axes + self.settings.label_edit_seuil_list[index].text(), encoding='utf-8')
                        self.senderudp.txsend(tosend, self.mainapp.cmd_list[idex])
                    self.settings.list_seuil[self.settings.list_seuil.index(True)] = False

                if self.settings.reset:
                    self.mainapp.machines_list = []
                    self.mainapp.cmd_list = [''] * 5
                    self.senderudp.txsend(b'R', '200.200.255.255')
                    self.settings.machines_list = []
                    self.flag_full_machine = False
                    self.settings.reset = False
                    self.mainapp.poignee_deport_conn[0] = False
                    self.mainapp.poignee_deport_conn[1] = False

                if self.settings.flag_value_changed:
                    self.mainapp.param_vitesse = self.settings.set_param_vitesse
                    self.mainapp.param_ratio = self.settings.set_param_ratio
                    self.mainapp.param_courbe = self.settings.set_param_courbe
                    self.mainapp.param_vitessepan = self.settings.set_param_vitesse_pan
                    self.mainapp.param_ratiocmd = self.settings.set_param_ratio_cmd
                    self.mainapp.param_vitessetilt = self.settings.set_param_vitesse_tilt
                    self.ratio_zoom, _ = self.settings.set_param_ratio[2]
                    self.courbe_zoom, _ = self.settings.set_param_courbe[2]

                    self.settings.flag_value_changed = False

                    if self.settings.flag_deceleration == True:
                        tosend = "BDEC" + str(self.settings.set_param_accel_furio[3])
                        self.senderudp.txsend(bytes(tosend, encoding='utf-8'), self.mainapp.machine_selected)

                        self.settings.flag_deceleration = False

                if self.status_iris and not self.flag_stop:
                    self.settings.iris_set(True)
                    self.flag_stop = True

                if self.settings.iris_onoff:
                    self.mainapp.switch_diaph.show()
                    self.status_iris = True
                else:
                    self.mainapp.switch_diaph.hide()
                    self.status_iris = False

                if self.settings.flag_set_domaine:
                    # sudo nano /etc/dhcpcd.conf
                    # sudo systemctl restart dhcpcd.service
                    # sudo ip addr flush dev eth0

                    newdomaine = str(self.settings.val_domaine) + "." + str(self.settings.val_domaine)
                    tosend = 'W' + str(self.settings.val_domaine)
                    domaine = self.myip.split(".")[0] + "." + self.myip.split(".")[1]
                    self.senderudp.txsend(bytes(tosend, encoding='utf-8'), domaine + '.255.255')
                    try:
                        for line in fileinput.input('/etc/systemd/network/wired.network', inplace=True):
                            line = line.replace(domaine, newdomaine)
                            sys.stdout.write(line)
                        fileinput.close()
                        os.system("systemctl restart systemd-networkd")
                    except:
                        print("error networking")
                    self.settings.flag_set_domaine = False

                if self.settings.flag_resetdomaine:
                    tosend = 'WRESET'
                    dom = str(os.popen("""ifconfig | grep "inet " | cut -c 14-26""").read()).split(".")[0]
                    self.senderudp.txsend(bytes(tosend, encoding='utf-8'), dom + '.' + dom + '.255.255')
                    self.settings.btn_edit_ip.setText("200.200")
                    try:
                        os.system("cp /etc/systemd/network/network.backup /etc/systemd/network/wired.network")
                        os.system("systemctl restart systemd-networkd")
                    except:
                        print("error networking")
                    self.settings.flag_resetdomaine = False

            # fenetre targetting (vouée a disparaitre in fine) =================================================================== Targetting
            if self.win.gotargeting:
                if self.targetwin.asking_snapshot is True:
                    tosend = "XS" + str(self.targetwin.get_vignette_number())
                    self.senderudp.txsend(bytes(tosend, encoding='utf-8'), self.mainapp.machine_selected)
                    self.targetwin.asking_snapshot = False
                if self.targetwin.target_locked:
                    if self.targetwin.previous_target != "":

                        tosend = "XDI" + str(self.targetwin.previous_target())
                        self.senderudp.txsend(bytes(tosend, encoding='utf-8'), self.mainapp.machine_selected)
                    tosend = "XEN" + str(self.targetwin.get_vignette_number())
                    self.senderudp.txsend(bytes(tosend, encoding='utf-8'), self.mainapp.machine_selected)
                    self.targetwin.previous_target = self.targetwin.previous_target
                    self.targetwin.target_locked = False

                if self.targetwin.release_target:
                    print("release target n°", self.targetwin.get_vignette_number())
                    tosend = "XDI" + str(self.targetwin.get_vignette_number())
                    self.senderudp.txsend(bytes(tosend, encoding='utf-8'), self.mainapp.machine_selected)
                    self.targetwin.release_target = False
                    # print("XDI")

            # Main app ============================================================================================================== Main app
            # on met a jour les machines connectées a chaque "top" du flag machine
            if self.flag_machines and not self.flag_full_machine:
                self.siglauncher.emitsignal('machine')
                self.siglauncher.emitsignal('machine_setting')
                self.current_index_machine = self.mainapp.index
                self.settings.index = self.mainapp.index
                if len(self.mainapp.machines_list) == 5:
                    self.flag_full_machine = True
                self.flag_machines = False

            # on met a jour les commandes connectées
            if self.flag_cmd:
                self.siglauncher.emitsignal('button')
                self.flag_cmd = False

            if self.switch_machine != 0:
                if len(self.mainapp.machines_list) > 1 and self.mainapp.machine_selected != "":
                    for i in range(len(self.mainapp.machine_layouts)):
                        if self.mainapp.machine_layouts[i].itemAt(0).widget().isChecked():
                            tmp_index = self.mainapp.machine_layouts.index(self.mainapp.machine_layouts[i])
                    if self.switch_machine == 1:
                        #self.mainapp.btn_machine_list[tmp_index + 1].click() if tmp_index != len(self.mainapp.machines_list) - 1 else self.mainapp.btn_machine_list[0].click()
                        self.mainapp.machine_layouts[tmp_index + 1].itemAt(0).widget().click() if tmp_index != len(self.mainapp.machines_list) - 1 else self.mainapp.machine_layouts[0].itemAt(0).widget().click()
                    else:
                        #self.mainapp.btn_machine_list[tmp_index - 1].click() if tmp_index != 0 else self.mainapp.btn_machine_list[len(self.mainapp.machines_list) - 1].click()
                        self.mainapp.machine_layouts[tmp_index - 1].itemAt(0).widget().click() if tmp_index != 0 else self.mainapp.machine_layouts[len(self.mainapp.machines_list) - 1].itemAt(0).widget().click()

                self.switch_machine = 0

            if self.mainapp.slider_0 != "":  # envoi du Pv0 de sécurité si le slider est mis à 0 et que la commande n'est pas touchée donc pas MAJ
                witchslider = {
                    'vitessepan': 'PV0',
                    'vitessetilt': 'TV0',
                    'vitessetrack': 'BV0',
                    'vitesselift': 'CV0',
                }
                tosend = witchslider.get(self.mainapp.slider_0, 'slider inconnu')
                self.senderudp.txsend(bytes(tosend, encoding='utf-8'), self.mainapp.machine_selected)
                self.mainapp.slider_0 = ""

            if self.mainapp.flag_change_machine or self.settings.flag_change_machine:
                self.senderudp.txsend(bytes('PV0', encoding='utf-8'), self.mainapp.machines_list[self.current_index_machine])
                self.senderudp.txsend(bytes('TV0', encoding='utf-8'), self.mainapp.machines_list[self.current_index_machine])
                self.senderudp.txsend(bytes('ZV0', encoding='utf-8'), self.mainapp.machines_list[self.current_index_machine])

                self.current_index_machine = self.mainapp.index
                self.settings.index = self.mainapp.index

                self.mainapp.flag_change_machine = False
                self.settings.flag_change_machine = False

            if self.mainapp.error_dial.flag_choose_machine:
                self.senderudp.txsend(b'R', '200.200.255.255')
                self.mainapp.cmd_list[0] = ''
                self.mainapp.cmd_list[1] = ''
                self.mainapp.cmd_list[3] = ''
                self.mainapp.cmd_list[4] = ''
                self.mainapp.error_dial.flag_choose_machine = False
                self.flag_waiting_reponse = False

            if self.mainapp.zoomassistIsEnable and self.ctn_zass >= 2:
                self.senderudp.txsend(b'ZGP', self.mainapp.machine_selected)
                self.ctn_zass = 0

            if self.mainapp.rstopt:
                self.senderudp.txsend(b'ZR', self.mainapp.machine_selected)
                self.mainapp.rstopt = False

            if self.mainapp.call_memory_position:
                self.senderudp.txsend(bytes("PSA" + str(round(self.mainapp.accel_memoire)), encoding='utf-8'), self.mainapp.machine_selected)
                self.senderudp.txsend(b'PGP', self.mainapp.machine_selected)
                self.senderudp.txsend(b'TGP', self.mainapp.machine_selected)
                self.senderudp.txsend(b'ZGP', self.mainapp.machine_selected)
                # asking snapshot
                self.senderudp.txsend(b'XS', self.mainapp.machine_selected)

                self.mainapp.call_memory_position = False

            if self.mainapp.recall_memory_position:
                self.senderudp.txsend(bytes("PSA" + str(round(self.mainapp.accel_memoire)), encoding='utf-8'), self.mainapp.machine_selected)
                valuepan, valuetilt, valuezoom, valuefocus = self.mainapp.current_memory_pos_button.memorized_pos
                self.senderudp.txsend(bytes("PSP" + str(valuepan), encoding='utf-8'), self.mainapp.machine_selected)
                self.senderudp.txsend(bytes("TSP" + str(valuetilt), encoding='utf-8'), self.mainapp.machine_selected)
                self.senderudp.txsend(bytes("ZP" + str(valuezoom), encoding='utf-8'), self.mainapp.machine_selected)
                self.senderudp.txsend(bytes("FP" + str(valuefocus), encoding='utf-8'), self.mainapp.machine_selected)
                self.computing_data_focus(valuefocus)
                print("Sending recall memoire: \n" + "pan : " + str(valuepan) + "\ntilt : " + str(valuetilt) + "\nzoom : " + str(valuezoom) + "\npoint : " + str(valuefocus))

                self.mainapp.recall_memory_position = False

            if self.pan_position != "" and self.tilt_position != "" and self.memo_zoom != "":

                self.mainapp.current_memory_pos_button.memorized_pos = (self.pan_position, self.tilt_position, self.memo_zoom, self.focus_data)
                print("memorized it ", self.mainapp.current_memory_pos_button.memorized_pos)
                self.pan_position = ""
                self.tilt_position = ""
                self.memo_zoom = ""

            if self.mainapp.call_memory_focus:
                self.focus = self.mainapp.memory_value
                tosend = ""
                if self.mainapp.flag_focus:
                    tosend = "FP" + str(round(self.focus * 60000 / 16383))
                if not self.mainapp.flag_focus:
                    tosend = "DP" + str(round(self.focus * 60000 / 16383))

                self.senderudp.txsend(bytes(tosend, encoding='utf-8'), self.mainapp.machine_selected)
                self.mainapp.call_memory_focus = False

            if self.mainapp.motor_release:
                if self.mainapp.btn_release.isChecked():
                    self.mainapp.state_motor_per_machine[self.current_index_machine] = True
                    self.senderudp.txsend(b'PSEN', self.mainapp.machine_selected)
                    self.senderudp.txsend(b'TSEN', self.mainapp.machine_selected)
                    self.senderudp.txsend(b'BSEN', self.mainapp.machine_selected)
                    self.senderudp.txsend(b'CSEN', self.mainapp.machine_selected)
                    self.mainapp.btn_release.setText("Motor\nON")
                else:
                    self.mainapp.state_motor_per_machine[self.current_index_machine] = False
                    self.senderudp.txsend(b'PSDI', self.mainapp.machine_selected)
                    self.senderudp.txsend(b'TSDI', self.mainapp.machine_selected)
                    self.senderudp.txsend(b'BSDI', self.mainapp.machine_selected)
                    self.senderudp.txsend(b'CSDI', self.mainapp.machine_selected)
                    self.mainapp.btn_release.setText("Motor\nOFF")
                self.mainapp.motor_release = False

            if self.mainapp.flaglimdiag:
                if self.mainapp.limitdial.but_settop.isChecked() and not self.mainapp.lim_haut[self.current_index_machine]:
                    self.mainapp.lim_haut[self.current_index_machine] = True
                    self.senderudp.txsend(b'TLH1', self.mainapp.machine_selected)
                elif not self.mainapp.limitdial.but_settop.isChecked() and self.mainapp.lim_haut[self.current_index_machine]:
                    self.mainapp.lim_haut[self.current_index_machine] = False
                    self.senderudp.txsend(b'TLH0', self.mainapp.machine_selected)
                if self.mainapp.limitdial.but_setbot.isChecked() and not self.mainapp.lim_bas[self.current_index_machine]:
                    self.mainapp.lim_bas[self.current_index_machine] = True
                    self.senderudp.txsend(b'TLB1', self.mainapp.machine_selected)
                elif not self.mainapp.limitdial.but_setbot.isChecked() and self.mainapp.lim_bas[self.current_index_machine]:
                    self.mainapp.lim_bas[self.current_index_machine] = False
                    self.senderudp.txsend(b'TLB0', self.mainapp.machine_selected)
                if self.mainapp.limitdial.but_setleft.isChecked() and not self.mainapp.lim_gauche[self.current_index_machine]:
                    self.mainapp.lim_gauche[self.current_index_machine] = True
                    self.senderudp.txsend(b'PLH1', self.mainapp.machine_selected)
                elif not self.mainapp.limitdial.but_setleft.isChecked() and self.mainapp.lim_gauche[self.current_index_machine]:
                    self.mainapp.lim_gauche[self.current_index_machine] = False
                    self.senderudp.txsend(b'PLH0', self.mainapp.machine_selected)
                if self.mainapp.limitdial.but_setright.isChecked() and not self.mainapp.lim_droite[self.current_index_machine]:
                    self.mainapp.lim_droite[self.current_index_machine] = True
                    self.senderudp.txsend(b'PLB1', self.mainapp.machine_selected)
                elif not self.mainapp.limitdial.but_setright.isChecked() and self.mainapp.lim_droite[self.current_index_machine]:
                    self.mainapp.lim_droite[self.current_index_machine] = False
                    self.senderudp.txsend(b'PLB0', self.mainapp.machine_selected)

                if self.mainapp.limitdial.sendokay:
                    self.senderudp.txsend(b'PLS1', self.mainapp.machine_selected)
                    self.mainapp.limitdial.sendokay = False
                    self.mainapp.flaglimdiag = False

                if self.mainapp.limitdial.sendcancel:
                    self.senderudp.txsend(b'PLS0', self.mainapp.machine_selected)
                    self.mainapp.lim_haut[self.current_index_machine] = self.mainapp.save_state_top[self.current_index_machine]
                    self.mainapp.lim_bas[self.current_index_machine] = self.mainapp.save_state_bot[self.current_index_machine]
                    self.mainapp.lim_gauche[self.current_index_machine] = self.mainapp.save_state_left[self.current_index_machine]
                    self.mainapp.lim_droite[self.current_index_machine] = self.mainapp.save_state_right[self.current_index_machine]
                    self.mainapp.limitdial.sendcancel = False
                    self.mainapp.flaglimdiag = False

            if self.mainapp.quit_app:  # si l'interface graphique passe la variable quitapp a vrai on ferme tout
                self.mainapp.quit_gui()  # on éteint l'interface graphique
                sys.exit()  # on coupe la boucle while du Maestro

            time.sleep(0.001)  # petite tampo pour pas faire tourner le while trop vite et bouffer toute la memoire de ce bon vieux rasp


"""CLASSES DE CREATION DES SOCKETS D'ENVOI & RECEPTION UDP=================================================================================== UDP"""


# https://stackoverflow.com/questions/40305424/using-one-socket-in-udp-chat-using-threading
class UdpSending:
    def __init__(self, port):
        self.port = port
        self.txSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.txSocket.setblocking(0)
        self.txSocket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

    def txsend(self, msg, addr):
        try:
            self.txSocket.sendto(msg, (addr, self.port))
            #  print("sending", msg)
        except:
            self.txSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.txSocket.setblocking(0)
            self.txSocket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

    """def txSendImg(self, image):
        msg = b'IMG' + image
        self.txsend(msg, "127.0.0.1")
        with open(image, 'rb') as fp:
            image_data = fp.read(1024)
            leng = 0
            while image_data:
                msg = b'IMG' + image_data
                if self.txSocket.sendto(msg, ('127.0.0.1', self.port)):
                    leng += len(msg)
                    image_data = fp.read(1024)
            self.txSocket.sendto(b'DONE', ('127.0.0.1', self.port))
            #self.txSocket.sendto(b'EOIMG\r\n', ('200.200.2.6', self.port))
        print("sending done")"""


class UdpReceive:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.rxSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.rxSocket.bind(("", self.port))
        self.p = psutil.Process(os.getpid())
        self.thread_info = ""
        self.total_percent = 0
        self.total_time = 0
        # self.rxSocket.setblocking(0) <-- envoit le processeur du rasp à 90 % ne pas decommenter

    def rxthread(self):
        global flag_logging_udp
        while True:
            if flag_logging_udp == True and self.thread_info is not str:
                calc = round(self.p.cpu_percent(0.1) * ((self.thread_info.system_time + self.thread_info.user_time) / sum(self.p.cpu_times())), 1)
                logging.info("CPU Usage:" + str(calc) + "% ") if calc > 10 else None
                flag_logging_udp = False
            try:
                data, addr = self.rxSocket.recvfrom(40000)
                request_buffer.append((data, addr[0]))
                time.sleep(0.005)
            except socket.error:
                pass
            except:
                self.rxSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                self.rxSocket.bind(("", self.port))

    def run(self):
        th1 = threading.Thread(name='udp receive thread', target=self.rxthread)
        th1.daemon = True
        th1.start()

        for threads in self.p.threads():
            if threads[0] == libc.syscall(thread_ID_number):  # 224 on rasp
                self.thread_info = threads
                break
        return
