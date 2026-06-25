# -*- coding: utf-8 -*-
import os
import platform
import glob
from PyQt5.QtWidgets import QFileDialog
from qgis.core import Qgis

from .baza_wrapper import Baza


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


def stworz_drzewo(iface):
    S = ['EWID', 'SHP', ]

    # opis gdzie sie laczymy
    sciezka = QFileDialog.getExistingDirectory(
        iface.mainWindow(),
        "Katalog z bazami taksatora:",
        # "c:/"
        '/home/pawel/upul/temp/testy/'
    )
    if not os.path.isdir(sciezka):
        iface.messageBar().pushMessage(
            'BŁĄD', 'Niepoprawna ścieżka do folderu z bazami TPU',
            Qgis.Critical)
        return

    if platform.system()[:3] == 'Win':
        bazy = glob.glob(os.path.join(sciezka, '*.mdb'))
    else:
        bazy = glob.glob(os.path.join(sciezka, '*.sqlite'))

    sp = []
    for baza_sc in bazy:
        baza = Baza(baza_sc)
        if not baza.polacz():
            continue

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

    struktura = [[s[0]+"_"+zamien(s[1].upper()),
                  s[2]+"_"+zamien(s[3].upper()), ]
                 for s in sp]
    folderPath_all = os.path.abspath(os.path.join(sciezka, ".."))

    for spis in struktura:
        if not os.path.exists(os.path.join(
                folderPath_all, "PLOTOWANIE", spis[0])):
            os.makedirs(os.path.join(folderPath_all, "PLOTOWANIE", spis[0]))
        if not os.path.exists(os.path.join(sciezka, spis[0], spis[1])):
            os.makedirs(os.path.join(sciezka, spis[0], spis[1]))
        if not os.path.exists(os.path.join(sciezka, spis[0], "OGOLNE")):
            os.makedirs(os.path.join(sciezka, spis[0], 'OGOLNE'))
        for si in S:
            if not os.path.exists(os.path.join(sciezka, spis[0], spis[1], si)):
                os.makedirs(os.path.join(sciezka, spis[0], spis[1], si))
