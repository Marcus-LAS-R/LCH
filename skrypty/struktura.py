# -*- coding: utf-8 -*-
import os
from shutil import copytree
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

    # katalog roboczy map - tworzony obok bazy, zamiast wymagac od
    # uzytkownika recznego przygotowania kopii bazy/SHP w tym miejscu
    mapy_root = os.path.join(sciezka, "_MAPY")
    os.makedirs(mapy_root, exist_ok=True)

    zrodlo_shp = os.path.join(sciezka, "SHP")
    cel_shp = os.path.join(mapy_root, "SHP")
    if os.path.isdir(zrodlo_shp) and not os.path.isdir(cel_shp):
        copytree(zrodlo_shp, cel_shp)
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

    iface.messageBar().pushMessage(
        'OK',
        f'Wygenerowano strukturę dla {len(struktura)} obrębów w _MAPY',
        Qgis.Success)
