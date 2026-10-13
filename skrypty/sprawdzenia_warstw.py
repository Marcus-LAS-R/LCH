"""Sprawdzenia warstwy wydzieleń przed dopisaniem metadanych.

Port części wydzieleniowej z wtyczki LAS-R (skrypty/sprawdzenia_warstw.py,
klasa SprawdzWydzielenia), żeby "Dopisz kody" w LCH sprawdzał warstwę tak
samo jak w LAS-R. Poprawka względem LAS-R: "Kontynuuj" w oknie
o rozbieżnościach warstwa-baza faktycznie kontynuuje (w LAS-R procedura i tak
się przerywała).
"""
from collections import Counter

from qgis.core import Qgis, QgsMessageLog, QgsFeatureRequest
from PyQt5.QtWidgets import QMessageBox


class SprawdzWydzielenia():
    """Klasa poboczna wymaga aby klasa dziedzicząca miałą już dodany wskaznik
    do wydz i bazy taksatora. Sprawdza poprawność pól w wydzieleniach, czy nie
    ma niepołączonych wydzieleń."""

    def __init__(self):
        pass

    def poprawne_wydz(self):
        """Metoda grupujaca wszystkie sprawdzenia danych i bazy"""
        spr = [
            self.spr_baza_polacz,
            self.spr_popr,
            self.spr_kolumn,
            self.spr_crs,
            self.spr_wydz_baza,
            self.spr_wydz_duble,
            self.spr_wydz_na_nielasach,
        ]

        self.wypis_sprawdzenia_wydz = ''

        komunikaty = [
            'Połączenie z bazą: OK',
            'Sprawdzenie poprawności warstwy wydz: OK',
            'Sprawdzenie obecności niezbędnych kolumn: OK',
            'Sprawdzenie układu wspł. (EPSG:2180) : OK',
            'Porównanie wydzieleń w warstwie z bazą: OK',
            'Sprawdzenie zdublowanych wydzieleń w warstwie: OK',
            'Sprawdzanie wydz innych niż D-STAN, na użytkach nieleśnych: OK',
        ]

        # sprawdzenia, przy ktorych uzytkownik moze zdecydowac o kontynuacji:
        # indeks: (pytanie, wpis do raportu przy przerwaniu)
        do_decyzji = {
            4: ('W bazie lub w warstwie są niełączące się wydzielenia'
                ', kontynuować?',
                '[BŁĄD] w bazie lub warstwie są niepołączone wydzielenia!\n'),
            6: ('W bazie są wydzielenia na użytkach nieleśnych'
                ', kontynuować?',
                '[BŁĄD] wydzielenia na użytkach nieleśnych\n'),
        }

        for i, s in enumerate(spr):
            if s():
                QgsMessageLog.logMessage(komunikaty[i], 'LCH', Qgis.Info)
                self.wypis_sprawdzenia_wydz += komunikaty[i] + '\n'
                continue

            if i not in do_decyzji:
                self.przerwij()
                return False

            pytanie, wpis = do_decyzji[i]
            message = QMessageBox()
            message.setIcon(QMessageBox.Information)
            message.setWindowTitle('Błąd')
            message.setText(pytanie)
            btn_przerwij = message.addButton('Przerwij', QMessageBox.ActionRole)
            message.addButton('Kontynuuj', QMessageBox.ActionRole)
            message.exec_()

            if message.clickedButton() == btn_przerwij:
                self.wypis_sprawdzenia_wydz += wpis
                self.przerwij()
                return False
        return True

    def przerwij(self):
        if self.baza.con:
            self.baza.zamknij()
        QgsMessageLog.logMessage(
            'Warstwa wydzieleń niepoprawna!',
            'LCH')

    def spr_baza_polacz(self):
        if not self.baza.polacz():
            self.iface.messageBar().pushMessage(
                'BAZA',
                'Nie udało się połączyć ze wskazaną bazą!',
                Qgis.Critical,
                10)
            QgsMessageLog.logMessage(
                        'Brak dostepu do bazy',
                        'LCH')
            return False
        return True

    def spr_popr(self):
        if not self.wydz.isValid():
            self.iface.messageBar().pushMessage(
                'Wydzielenia',
                'Nie mogę otworzyć warstwy do odczytu',
                Qgis.Critical,
                10)
            return False
        return True

    def spr_crs(self):
        """Metoda sprwdza układ wspł. warstwy, jeżeli nie jest to EPSG:2180,
        zwraca False"""
        if '2180' not in self.wydz.crs().authid().upper():
            self.iface.messageBar().pushMessage(
                'Wydzielenia',
                'Warstwa ma inny układ współrzędnych niż PUWG92 (EPSG:2180)'
                f' [Ustawiony w warstwie: {self.wydz.crs().authid()}]',
                Qgis.Critical,
                10)
            return False
        return True

    def spr_kolumn(self):
        pola = [x for x in ['WYDZ', 'ODDZ', 'ADR_LES']
                if x not in self.wydz.dataProvider().fieldNameMap()]
        if len(pola) > 0:
            self.iface.messageBar().pushMessage(
                'Wydzielenia',
                'Brak kolumn '+', '.join(pola)+' w warstwie',
                Qgis.Critical,
                10)
            return False
        return True

    def spr_wydz_baza(self):
        request = QgsFeatureRequest().setFlags(QgsFeatureRequest.NoGeometry
                                               ).setSubsetOfAttributes(
                                                   ['ADR_LES'],
                                                   self.wydz.fields()
                                               )
        adr_w = [x['ADR_LES'] for x in self.wydz.getFeatures(request)]
        adr_b = self.baza.pobierz_wydzielenia()
        brakiw = [x for x in adr_w if x not in adr_b]
        brakib = [x for x in adr_b if x not in adr_w]

        QgsMessageLog.logMessage(
            '   Znaleziono poligonów w shp: ' + str(len(adr_w)),
            'LCH',
            Qgis.Info
        )
        self.wypis_sprawdzenia_wydz +=  \
            '\n   Znaleziono poligonów w shp: ' + str(len(adr_w))
        QgsMessageLog.logMessage(
            '   Znaleziono wydzieleń w shp: ' + str(len(set(adr_w))),
            'LCH',
            Qgis.Info
        )
        self.wypis_sprawdzenia_wydz +=  \
            '\n   Znaleziono wydzieleń w shp: ' + str(len(set(adr_w)))
        QgsMessageLog.logMessage(
            '   Znaleziono wydzieleń w bazie: ' + str(len(adr_b)),
            'LCH',
            Qgis.Info
        )
        self.wypis_sprawdzenia_wydz +=  \
            '\n   Znaleziono wydzieleń w bazie: ' + str(len(adr_b)) + '\n\n'

        if len(brakiw) > 0:
            self.iface.messageBar().pushMessage(
                'BAZA',
                'W shp znajdują się wydzielenia, które nie są dopisane do ' +
                'Bazy! Patrz log LCH',
                Qgis.Critical,
                10)

            self.wypis_sprawdzenia_wydz +=  \
                '\nW shp znajdują się wydzielenia, które nie są ' + \
                'dopisane do Bazy! Patrz log LCH\n'
            QgsMessageLog.logMessage('Brakujące wydzielenia w bazie:',
                                     'LCH',
                                     Qgis.Critical)
            self.wypis_sprawdzenia_wydz += 'Brakujące wydzielenia w bazie:\n'
            for b in brakiw:
                QgsMessageLog.logMessage(str(b), 'LCH', Qgis.Critical)
                self.wypis_sprawdzenia_wydz += str(b) + '\n'

        if len(brakib) > 0:
            self.iface.messageBar().pushMessage(
                'BAZA',
                'W bazie znajdują się wydzielenia, które nie są dopisane do ' +
                'warstwy! Patrz log LCH',
                Qgis.Critical,
                10)

            QgsMessageLog.logMessage('Brakujące wydzielenia w warstwie:',
                                     'LCH',
                                     Qgis.Critical)

            self.wypis_sprawdzenia_wydz += \
                'Brakujące wydzielenia w warstwie:\n'
            for b in brakib:
                QgsMessageLog.logMessage(b, 'LCH', Qgis.Critical)
                self.wypis_sprawdzenia_wydz += b + '\n'

        if len(brakib) > 0 or len(brakiw) > 0:
            return False

        return True

    def spr_wydz_duble(self):
        request = QgsFeatureRequest().setFlags(QgsFeatureRequest.NoGeometry
                                               ).setSubsetOfAttributes(
                                                   ['ADR_LES'],
                                                   self.wydz.fields()
                                               )
        adr_w = [x['ADR_LES'] for x in self.wydz.getFeatures(request)]
        adr_b = self.baza.pobierz_wydzielenia()

        if len(adr_w) != len(set(adr_b)):
            self.iface.messageBar().pushMessage(
                'wydzielenia [shp]',
                'Połącz wydzielenia w multipoligony! (Spis w logu)',
                Qgis.Critical,
                10)

            self.wypis_sprawdzenia_wydz += \
                'Połącz wydzielenia w multipoligony:\n'
            QgsMessageLog.logMessage(
                '\nNiepołączone wydzielenia: \n' + '\n'.join(
                    [y[0] + '   (x' + str(y[1]) + ')'
                     for y in Counter(adr_w).most_common() if y[1] > 1]),
                'LCH'
            )
            self.wypis_sprawdzenia_wydz += '\n'.join([
                y[0] + '   (x' + str(y[1]) + ')'
                for y in Counter(adr_w).most_common() if y[1] > 1
            ])

            return False
        return True

    def spr_wydz_na_nielasach(self):
        rozl = self.baza.pobierz_rozliczenie_wydz()
        if len(rozl) == 0:
            return True

        tab = self.baza.pobierz_wydz_na_innych_uz()

        if len(tab) > 0:
            self.iface.messageBar().pushMessage(
                'WYDZIELENIA NIELEŚNE',
                'Odnaleziono wydzielenia nieleśne na użytkach nieleśnych',
                Qgis.Critical,
                10)
            self.wypis_sprawdzenia_wydz += \
                'Odnaleziono wydzielenia nieleśne na użytkach nieleśnych\n'

            QgsMessageLog.logMessage(
                '\nWydzielenia nieleśne na nielasach:\n' +
                '\n'.join('  '.join(map(str, y)) for y in tab),
                'LCH'
            )
            self.wypis_sprawdzenia_wydz += \
                '\n'.join('  '.join(map(str, y)) for y in tab)
            return False

        return True
