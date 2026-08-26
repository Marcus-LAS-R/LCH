# -*- coding: utf-8 -*-
import os
from shutil import copytree, copyfile
from PyQt5.QtWidgets import (
    QFileDialog, QDialog, QVBoxLayout, QCheckBox, QGroupBox, QRadioButton,
    QDialogButtonBox,
)
from qgis.core import Qgis, QgsProject, QgsVectorLayer

from .baza_wrapper import Baza
from .pomocnicze import SciezkaKonfiguracyjna
from .shp_przygotuj_klu_lft import uzupelnij_municip_community, przetworz_klu


def zamien(ciag):
    sl = {
        u'Ł': 'L',
        u'Ó': 'O',
        u'Ę': 'E',
        u'Ć': 'C',
        u'Ą': 'A',
        u'Ś': 'S',
        u'Ż': 'Z',
        u'Ź': 'Z',
        u'Ń': 'N',
        ' ': '_',
        }

    for key, val in sl.items():
        ciag = ciag.replace(key, val)

    return ciag


class OpcjeStrukturyDialog(QDialog):
    """Dialog opcji dla 'Generuj strukturę map' - co dograć/wygenerować
    poza samą strukturą katalogów."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Opcje generowania struktury map')
        self.resize(480, 420)

        layout = QVBoxLayout(self)

        self.cb_toc = QCheckBox('Dograj warstwy do TOC (ODDZ, WYDZ, EWID, '
                                 'DZKAT, KLU_AFT/LFT)')
        self.cb_toc.setChecked(True)
        layout.addWidget(self.cb_toc)

        self.cb_klu = QCheckBox('Twórz KLU_AFT i KLU_LFT')
        self.cb_klu.setChecked(True)
        layout.addWidget(self.cb_klu)

        self.cb_szablony = QCheckBox('Dogranie szablonów map do folderów '
                                      'obrębów')
        self.cb_szablony.setChecked(True)
        layout.addWidget(self.cb_szablony)

        self.cb_mapa_przegladowa = QCheckBox('MAPA_PRZEGLĄDOWA')
        self.cb_mapa_przegladowa.setChecked(True)
        self.cb_atlas_leg = QCheckBox('ATLAS i LEG')
        self.cb_atlas_leg.setChecked(False)
        for cb in (self.cb_mapa_przegladowa, self.cb_atlas_leg):
            cb.setStyleSheet('margin-left: 20px;')
            layout.addWidget(cb)

        self.cb_szablony.toggled.connect(self.cb_mapa_przegladowa.setEnabled)
        self.cb_szablony.toggled.connect(self.cb_atlas_leg.setEnabled)

        self.cb_logotypy = QCheckBox('Wgraj logotypy do OGOLNE')
        self.cb_logotypy.setChecked(True)
        layout.addWidget(self.cb_logotypy)

        grupa_wyk = QGroupBox('Wykonawca')
        wyk_layout = QVBoxLayout(grupa_wyk)
        self.rb_lasr = QRadioButton('LAS-R Sp. z o.o.')
        self.rb_lasr.setChecked(True)
        self.rb_jk = QRadioButton('Krzysztof Janczulewicz')
        wyk_layout.addWidget(self.rb_lasr)
        wyk_layout.addWidget(self.rb_jk)
        layout.addWidget(grupa_wyk)

        przyciski = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        przyciski.accepted.connect(self.accept)
        przyciski.rejected.connect(self.reject)
        layout.addWidget(przyciski)

    def opcje(self):
        dograj_szablony = self.cb_szablony.isChecked()
        return {
            'dograj_toc': self.cb_toc.isChecked(),
            'gen_klu': self.cb_klu.isChecked(),
            'dograj_szablony': dograj_szablony,
            'mapa_przegladowa':
                dograj_szablony and self.cb_mapa_przegladowa.isChecked(),
            'atlas_leg':
                dograj_szablony and self.cb_atlas_leg.isChecked(),
            'wgraj_logotypy': self.cb_logotypy.isChecked(),
            'wykonawca': 'LASR' if self.rb_lasr.isChecked() else 'JK',
        }


def _wczytaj_i_dodaj_do_toc(sciezka, nazwa):
    lyr = QgsVectorLayer(sciezka, nazwa, 'ogr')
    if lyr.isValid():
        QgsProject.instance().addMapLayer(lyr)


def stworz_drzewo(iface):  # noqa: C901
    S = ['EWID', 'SHP', ]

    # wskaz baze taksatora
    baza_plik, _ = QFileDialog.getOpenFileName(
        iface.mainWindow(),
        "Wskaż bazę taksatora:",
        '/home/pawel/upul/temp/testy/',
        "Access MDB (*.mdb);;SQLite (*.sqlite)"
    )
    if not os.path.isfile(baza_plik):
        iface.messageBar().pushMessage(
            'BŁĄD', 'Niepoprawna ścieżka do bazy taksatora',
            Qgis.Critical)
        return

    sciezka = os.path.dirname(baza_plik)

    sp = []
    baza = Baza(baza_plik)
    if not baza.polacz():
        iface.messageBar().pushMessage(
            'BŁĄD', 'Nie udało się połączyć z bazą',
            Qgis.Critical)
        return

    # RODZAJ POWIERZCHNI - ok
    SQL = """
    SELECT F_COMMUNITY.MUNICIPALITY_CD,
        F_MUNICIPALITY.MUNICIPALITY_NAME,
        F_COMMUNITY.COMMUNITY_CD,
        F_COMMUNITY.COMMUNITY_NAME
    FROM F_MUNICIPALITY
    INNER JOIN F_COMMUNITY ON
    (F_MUNICIPALITY.MUNICIPALITY_CD = F_COMMUNITY.MUNICIPALITY_CD)
    AND (F_MUNICIPALITY.DISTRICT_CD = F_COMMUNITY.DISTRICT_CD)
    AND (F_MUNICIPALITY.COUNTY_CD = F_COMMUNITY.COUNTY_CD);
    """
    spt = baza.pobierz(SQL)
    if spt:
        sp += spt
    baza.zamknij()

    struktura = [[s[0].strip()+"_"+zamien(s[1].strip().upper()),
                  s[2].strip()+"_"+zamien(s[3].strip().upper()), ]
                 for s in sp]

    dialog = OpcjeStrukturyDialog(iface.mainWindow())
    if not dialog.exec_():
        return
    opcje = dialog.opcje()

    # katalog roboczy map - tworzony obok bazy, zamiast wymagac od
    # uzytkownika recznego przygotowania kopii bazy/SHP w tym miejscu
    mapy_root = os.path.join(sciezka, "_MAPY")
    os.makedirs(mapy_root, exist_ok=True)

    zrodlo_shp = os.path.join(sciezka, "SHP")
    shp_root = os.path.join(mapy_root, "SHP")
    if os.path.isdir(zrodlo_shp) and not os.path.isdir(shp_root):
        copytree(zrodlo_shp, shp_root)
    elif not os.path.isdir(zrodlo_shp):
        iface.messageBar().pushMessage(
            'UWAGA',
            'Nie znaleziono folderu SHP obok bazy - pomijam kopiowanie',
            Qgis.Warning)

    folderPath_all = sciezka

    for spis in struktura:
        if not os.path.exists(os.path.join(
                folderPath_all, "PLOTOWANIE", spis[0])):
            os.makedirs(os.path.join(folderPath_all, "PLOTOWANIE", spis[0]))
        if not os.path.exists(os.path.join(mapy_root, spis[0], spis[1])):
            os.makedirs(os.path.join(mapy_root, spis[0], spis[1]))
        if not os.path.exists(os.path.join(mapy_root, spis[0], "OGOLNE")):
            os.makedirs(os.path.join(mapy_root, spis[0], 'OGOLNE'))
        for si in S:
            if not os.path.exists(
                    os.path.join(mapy_root, spis[0], spis[1], si)):
                os.makedirs(os.path.join(mapy_root, spis[0], spis[1], si))

    # EWID - te same MUNICIP/COMMUNITY co przy KLU, zawsze (naprawa danych,
    # niezalezna od checkboxow)
    ewid_path = os.path.join(shp_root, 'EWID.shp')
    if os.path.isfile(ewid_path):
        ewid_lyr = QgsVectorLayer(ewid_path, 'EWID', 'ogr')
        if ewid_lyr.isValid():
            uzupelnij_municip_community(iface, ewid_lyr)

    # KLU_AFT / KLU_LFT - zawsze z pliku _MAPY\SHP\KLU.shp, bez szukania w
    # TOC (w przeciwienstwie do samodzielnej akcji "Generuj KLU_LFT")
    klu_aft = klu_lft = None
    if opcje['gen_klu']:
        klu_path = os.path.join(shp_root, 'KLU.shp')
        if os.path.isfile(klu_path):
            klu_lyr = QgsVectorLayer(klu_path, 'KLU', 'ogr')
            if klu_lyr.isValid() and \
                    uzupelnij_municip_community(iface, klu_lyr):
                klu_aft, klu_lft = przetworz_klu(klu_lyr, shp_root)
        else:
            iface.messageBar().pushMessage(
                'UWAGA',
                'Nie znaleziono KLU.shp - pomijam KLU_AFT/KLU_LFT',
                Qgis.Warning)

    if opcje['dograj_toc']:
        for nazwa in ['ODDZ', 'WYDZ', 'EWID', 'DZKAT']:
            _wczytaj_i_dodaj_do_toc(
                os.path.join(shp_root, nazwa + '.shp'), nazwa)
        if klu_aft is not None:
            QgsProject.instance().addMapLayer(klu_aft)
        if klu_lft is not None:
            QgsProject.instance().addMapLayer(klu_lft)

    # szablony map (do folderow obrebow) i logotypy (do OGOLNE per gmina)
    if opcje['dograj_szablony'] or opcje['wgraj_logotypy']:
        podr = SciezkaKonfiguracyjna(
            'PODRECZNIK', 'Wskaż folder Podrecznik/Mapy',
            wymagane_podfoldery=[
                'Szablony_map', 'logotypy_do_wgrywania', 'pomocnicze']
        ).sciezka
        szablony_dir = os.path.join(podr, 'Szablony_map')
        logo_dir = os.path.join(podr, 'logotypy_do_wgrywania')

        szablony_do_skopiowania = []
        if opcje['mapa_przegladowa']:
            szablony_do_skopiowania.append('MAPA_PRZEGLADOWA.qgz')
        if opcje['atlas_leg']:
            szablony_do_skopiowania += ['ATLAS.qgz', 'LEG.qgz']

        for spis in struktura:
            for plik in szablony_do_skopiowania:
                zrodlo = os.path.join(szablony_dir, plik)
                if os.path.isfile(zrodlo):
                    copyfile(zrodlo, os.path.join(
                        mapy_root, spis[0], spis[1], plik))

        if opcje['wgraj_logotypy']:
            gminy = sorted({spis[0] for spis in struktura})
            logotypy_zawsze = [
                'plaz_i.svg', 'plaz_l.svg', 'zrab.svg', 'zleceniodawca.tif',
            ]
            for gmina in gminy:
                ogolne = os.path.join(mapy_root, gmina, 'OGOLNE')
                for plik in logotypy_zawsze:
                    zrodlo = os.path.join(logo_dir, plik)
                    if os.path.isfile(zrodlo):
                        copyfile(zrodlo, os.path.join(ogolne, plik))

                if opcje['atlas_leg']:
                    zrodlo = os.path.join(logo_dir, 'zleceniodawca_a.tif')
                    if os.path.isfile(zrodlo):
                        copyfile(zrodlo, os.path.join(
                            ogolne, 'zleceniodawca_a.tif'))

                if opcje['wykonawca'] == 'LASR':
                    zrodlo = os.path.join(logo_dir, 'wykonawca.jpg')
                else:
                    zrodlo = os.path.join(logo_dir, 'wykonawca_JK.jpg')
                if os.path.isfile(zrodlo):
                    copyfile(zrodlo, os.path.join(ogolne, 'wykonawca.jpg'))

    iface.messageBar().pushMessage(
        'OK',
        f'Wygenerowano strukturę dla {len(struktura)} obrębów w _MAPY',
        Qgis.Success)
