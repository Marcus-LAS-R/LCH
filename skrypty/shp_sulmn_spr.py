import os
import glob
import platform
import shutil
from datetime import datetime

from qgis.core import QgsVectorLayer, QgsVectorFileWriter, Qgis, QgsProject, \
    QgsCoordinateReferenceSystem, QgsField, QgsMessageLog, QgsSpatialIndex, \
    QgsFeature, QgsGeometry, QgsPointXY
from qgis.PyQt.QtWidgets import QApplication

import processing

from collections import defaultdict, Counter
from PyQt5.QtWidgets import QFileDialog
from PyQt5.QtCore import QVariant

from .baza_wrapper import Baza, znajdz_baze_do_wydz
from .shp_generuj_sulmn import GenerujSulmn


class GenerujSulmnSpr(GenerujSulmn):
    def __init__(self, iface):
        super(GenerujSulmnSpr, self).__init__(iface)
        self.iface = iface

        self.wydz = False
        self.kat = False
        for lyr in QgsProject.instance().mapLayers().values():
            if lyr.name() == "WYDZ_POL":
                self.wydz = lyr

        if self.wydz is False:
            self.iface.messageBar().pushMessage(
                'Error', "Brak warstwy WYDZ_POl w TOC!", level=Qgis.Critical)
            return

        self.wydz.dataProvider().setEncoding('UTF-8')
        self.wydz_path = self.wydz.dataProvider().dataSourceUri().split("|")[0]
        self.kat = os.path.dirname(self.wydz_path)

        self.ustawProj()  # zadeklaruj wszystkie niezbedne zmienne dla klasy

    def ustawProj(self):
        # self.oddz = False
        self.ls = False
        self.pnsw = False
        self.linie = False
        if platform.system()[:3] == 'Win':
            kat = 'e:/UPUL/'
        else:
            kat = self.kat

        self.czas = datetime.now().isoformat(
            ).replace(":", "")[:-7].replace('-', '')

        # pobierz od uzyszkodnika katalog docelowy na sulmn
        self.katS = os.path.join(
            os.path.dirname(self.kat), f'sulmn_{self.czas}'
        )
        if not os.path.isdir(self.katS):
            os.mkdir(self.katS)

        # stworz katalog roboczy jezeli nie istnieje
        self.kattemp = os.path.join(self.katS, "temp")
        if not os.path.isdir(os.path.join(self.katS, "temp")):
            os.mkdir(os.path.join(self.katS, "temp"))

        self.crs = QgsCoordinateReferenceSystem("epsg:2180")

        self.slPol = {
            'POW': ['ID', 'ADR_BDL', 'L_EWID'],
            'DZ_EWID': ['ID', 'ADR_ADM', 'NR_EW', ],
            'UZYTKI': ['ID', 'ADR_ADM', 'NR_EW', 'NR_KONT', ],
            # 'ODDZIAL': ['ID', 'ADR_BDL'],
            'PNSW':
                ['ID', 'ADR_BDL', 'KOD_PNSW', 'NR_PNSW', 'NR_EW', 'ADR_ADM'],
            'LINIE': ['ID', 'SZER', 'KOD'],
        }

    def przygotuj_projekt(self):
        """Ustaw projekt tak aby MapaPU mogła go łyknąć i łatwo było uruchomić
        sprawdzenia atrybutowe z poziomu wtyczki z BDLa
        """
        self.catsulmn = os.path.join(self.katS, "UPUL")
        if not os.path.isdir(self.catsulmn):
            os.mkdir(self.catsulmn)
            os.mkdir(os.path.join(self.catsulmn, 'Warstwy'))
            os.mkdir(os.path.join(self.catsulmn, 'Rastry'))
            os.mkdir(os.path.join(self.catsulmn, 'TaksatorPU'))

        # skopiuj puste pliki do folderu
        pth = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'supul', '*')
        fls = list(glob.glob(pth))
        for fl in fls:
            if fl[-3:] == 'QGS':
                shutil.copy(
                    fl,
                    os.path.join(self.catsulmn, 'UPUL.QGS')
                )
                continue

            shutil.copyfile(
                fl,
                os.path.join(self.catsulmn, 'Warstwy', os.path.basename(fl))
            )

        # skopiuj dane wygenerowane na podstawie projektu
        fls = list(glob.glob(os.path.join(self.katS, '*')))
        for fl in fls:
            if os.path.isfile(fl):
                shutil.copy(fl, os.path.join(self.catsulmn, 'Warstwy'))

        # skopiuj baze w odpowiednie miejsce
        shutil.copy(
            self.baza.baza,
            os.path.join(self.catsulmn, 'TaksatorPU', 'UPUL.MDB')
        )

        clipboard = QApplication.clipboard()
        clipboard.setText(self.catsulmn)
        self.iface.messageBar().clearWidgets()
        self.iface.messageBar().pushMessage(
            'OK',
            'Sciezka do wygenerowanego projektu zostala skopiowana do schowka',
            Qgis.Success
        )
        QApplication.processEvents()
        QApplication.processEvents()

        try:
            from Mapa_PU.upul_modul import upul
            uu = upul(self.iface)
            uu.otworzProjekt()
        except Exception as e:
            print('ZONK - nie da sie otworzyc Mapa_PU! Zainstalowana? inny system niż Windows?')
