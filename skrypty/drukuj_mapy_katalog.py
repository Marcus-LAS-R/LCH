import os
import subprocess
from qgis.core import Qgis, QgsMessageLog, QgsSettings
from PyQt5.QtWidgets import (QDialog, QDialogButtonBox, QVBoxLayout, QHBoxLayout,
                              QLabel, QLineEdit, QPushButton, QComboBox, QFileDialog,
                              QSpinBox, QCheckBox, QListWidget, QListWidgetItem,
                              QWidget)
from PyQt5.QtCore import Qt

_SUMATRA_PATHS = [
    r'C:\Program Files\SumatraPDF\SumatraPDF.exe',
    r'C:\Program Files (x86)\SumatraPDF\SumatraPDF.exe',
    os.path.expanduser(r'~\AppData\Local\SumatraPDF\SumatraPDF.exe'),
]
_PLIK_SUMATRA = os.path.join(os.path.dirname(__file__), 'sumatra_path.txt')

# Grupy formatów - każda drukowana na swojej drukarce
_GRUPY = ['WF', 'A3', 'A4']
_OPIS_GRUPY = {'WF': 'wielki format', 'A3': 'A3', 'A4': 'A4'}
_NIE_DRUKUJ = '— nie drukuj —'
_KLUCZ_DRUKARKI = 'LCH/drukuj_mapy/drukarka_'
# DMPAPER_A4 / DMPAPER_A3
_PAPIER_STD = {'A4': 9, 'A3': 8}
# Atlasy rozpoznawane po nazwie layoutu (koniec nazwy pliku) lub folderze eksportu
_SUFIKSY_ATLASU = ('_ATLAS', '_LEG')
_FOLDER_ATLASOW = 'Atlasy'


def _wczytaj_sumatra():
    if os.path.isfile(_PLIK_SUMATRA):
        p = open(_PLIK_SUMATRA).read().strip()
        if os.path.isfile(p):
            return p
    for p in _SUMATRA_PATHS:
        if os.path.isfile(p):
            return p
    return ''


def _zapisz_sumatra(path):
    open(_PLIK_SUMATRA, 'w').write(path)


def _lista_drukarek():
    try:
        import win32print
        printers = win32print.EnumPrinters(
            win32print.PRINTER_ENUM_LOCAL | win32print.PRINTER_ENUM_CONNECTIONS)
        return [p[2] for p in printers]
    except Exception:
        return []


def _ustaw_rozmiar(drukarka, w_mm, h_mm, grupa):
    try:
        import win32print
        hPrinter = win32print.OpenPrinter(drukarka)
        try:
            info = win32print.GetPrinter(hPrinter, 2)
            dm = info['pDevMode']
            dm.Orientation = 2 if w_mm > h_mm else 1    # DMORIENT_LANDSCAPE / PORTRAIT
            # Kopie liczy Sumatra — domyślne kopie drukarki muszą być 1,
            # inaczej każdy wydruk się mnoży
            dm.Copies = 1
            if grupa in _PAPIER_STD:
                # Standardowy papier - drukarki biurowe często nie obsługują
                # rozmiaru użytkownika. Bez DM_PAPERLENGTH/DM_PAPERWIDTH,
                # inaczej sterownik bierze stary rozmiar użytkownika
                dm.PaperSize = _PAPIER_STD[grupa]
                # DM_ORIENTATION | DM_PAPERSIZE | DM_COPIES
                dm.Fields = (dm.Fields & ~0x000C) | 0x0103
            else:
                # Papier zawsze opisany pionowo (szer = krótszy bok), a poziomą
                # mapę obsługuje orientacja — inaczej sterownik nie obraca
                # strony i obcina mapę
                dm.PaperSize = 256          # DMPAPER_USER
                dm.PaperWidth = int(min(w_mm, h_mm) * 10)   # w dziesiątych mm
                dm.PaperLength = int(max(w_mm, h_mm) * 10)  # w dziesiątych mm
                # DM_ORIENTATION | DM_PAPERSIZE | DM_PAPERLENGTH | DM_PAPERWIDTH | DM_COPIES
                dm.Fields = dm.Fields | 0x010F
            win32print.SetPrinter(hPrinter, 2, info, 0)
        finally:
            win32print.ClosePrinter(hPrinter)
    except Exception as e:
        QgsMessageLog.logMessage(f'Błąd ustawiania rozmiaru papieru: {e}', 'LCH', Qgis.Warning)


def _lista_pdf(folder):
    # Ścieżki względne PDF ze wskazanego folderu i podfolderów Mapy/Atlasy.
    # Tylko oryginały (nie _x2), _x2 obsługiwane automatycznie przy druku
    if not folder or not os.path.isdir(folder):
        return []
    pliki = []
    for podfolder in ('', 'Mapy', _FOLDER_ATLASOW):
        d = os.path.join(folder, podfolder)
        if not os.path.isdir(d):
            continue
        pliki += [os.path.join(podfolder, f) for f in sorted(os.listdir(d))
                  if f.lower().endswith('.pdf') and not f[:-4].endswith('_x2')]
    return pliki


def _folder_x2(folder):
    # Pary _x2 leza w PLOTOWANIE/<gmina>_x2 - przy wskazaniu podfolderu
    # Mapy/Atlasy gmina jest poziom wyzej
    gmina_folder = os.path.normpath(folder)
    if os.path.basename(gmina_folder) in ('Mapy', _FOLDER_ATLASOW):
        gmina_folder = os.path.dirname(gmina_folder)
    return gmina_folder + '_x2'


def _czy_atlas(pdf_path):
    if os.path.basename(os.path.dirname(os.path.normpath(pdf_path))) == _FOLDER_ATLASOW:
        return True
    nazwa = os.path.basename(pdf_path)[:-4]
    # LEG bez atlasu dostaje przy eksporcie przyrostek _A3
    if nazwa.endswith('_A3'):
        nazwa = nazwa[:-3]
    return nazwa.endswith(_SUFIKSY_ATLASU)


def _grupa(w_mm, h_mm):
    # 1 mm tolerancji na zaokrąglenia eksportu
    krotszy, dluzszy = sorted((w_mm, h_mm))
    if krotszy <= 211 and dluzszy <= 298:
        return 'A4'
    if krotszy <= 298 and dluzszy <= 421:
        return 'A3'
    return 'WF'


class _DrukujDialog(QDialog):
    def __init__(self, parent):
        super().__init__(parent)
        self.setWindowTitle('Drukuj mapy (katalog)')
        self.setMinimumWidth(500)
        layout = QVBoxLayout()

        row = QHBoxLayout()
        row.addWidget(QLabel('Folder z PDF:'))
        self.folder_edit = QLineEdit()
        row.addWidget(self.folder_edit)
        btn = QPushButton('...')
        btn.setFixedWidth(30)
        btn.clicked.connect(self._wybierz_folder)
        row.addWidget(btn)
        layout.addLayout(row)

        layout.addWidget(QLabel('Pliki do druku:'))
        self.lista = QListWidget()
        self.lista.setMinimumHeight(200)
        layout.addWidget(self.lista)
        row_zazn = QHBoxLayout()
        btn_wsz = QPushButton('Zaznacz wszystkie')
        btn_wsz.clicked.connect(lambda: self._zaznacz(Qt.Checked))
        row_zazn.addWidget(btn_wsz)
        btn_zad = QPushButton('Odznacz wszystkie')
        btn_zad.clicked.connect(lambda: self._zaznacz(Qt.Unchecked))
        row_zazn.addWidget(btn_zad)
        row_zazn.addStretch()
        layout.addLayout(row_zazn)

        # Wiersze drukarek widoczne tylko dla formatów obecnych w folderze
        drukarki = _lista_drukarek()
        ustawienia = QgsSettings()
        self.cmb_drukarki = {}
        self.wiersze_drukarek = {}
        for grupa in _GRUPY:
            wiersz = QWidget()
            row_dr = QHBoxLayout(wiersz)
            row_dr.setContentsMargins(0, 0, 0, 0)
            row_dr.addWidget(QLabel(f'Drukarka ({_OPIS_GRUPY[grupa]}):'))
            cmb = QComboBox()
            cmb.addItem(_NIE_DRUKUJ)
            cmb.addItems(drukarki)
            zapisana = ustawienia.value(_KLUCZ_DRUKARKI + grupa, '')
            if zapisana == _NIE_DRUKUJ or zapisana in drukarki:
                cmb.setCurrentText(zapisana)
            elif grupa == 'WF' and drukarki:
                cmb.setCurrentIndex(1)
            row_dr.addWidget(cmb, 1)
            wiersz.setVisible(False)
            layout.addWidget(wiersz)
            self.cmb_drukarki[grupa] = cmb
            self.wiersze_drukarek[grupa] = wiersz

        row_kop = QHBoxLayout()
        row_kop.addWidget(QLabel('Liczba kopii:'))
        self.spin_kopie = QSpinBox()
        self.spin_kopie.setMinimum(1)
        self.spin_kopie.setMaximum(99)
        self.spin_kopie.setValue(1)
        row_kop.addWidget(self.spin_kopie)
        row_kop.addStretch()
        layout.addLayout(row_kop)

        self.chk_duplex = QCheckBox('Druk dwustronny atlasów (ATLAS, LEG)')
        self.chk_duplex.setChecked(True)
        self.chk_duplex.setVisible(False)
        layout.addWidget(self.chk_duplex)

        row2 = QHBoxLayout()
        row2.addWidget(QLabel('SumatraPDF:'))
        self.sumatra_edit = QLineEdit(_wczytaj_sumatra())
        row2.addWidget(self.sumatra_edit)
        btn2 = QPushButton('...')
        btn2.setFixedWidth(30)
        btn2.clicked.connect(self._wybierz_sumatra)
        row2.addWidget(btn2)
        layout.addLayout(row2)

        przyciski = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        przyciski.accepted.connect(self.accept)
        przyciski.rejected.connect(self.reject)
        layout.addWidget(przyciski)

        self.setLayout(layout)
        self.folder_edit.textChanged.connect(self._odswiez_liste)

    def _wybierz_folder(self):
        d = QFileDialog.getExistingDirectory(
            self, 'Wybierz folder z PDF:', self.folder_edit.text())
        if d:
            self.folder_edit.setText(d)

    def _odswiez_liste(self):
        self.lista.clear()
        grupy = set()
        ma_atlas = False
        pliki = _lista_pdf(self.folder)
        try:
            from pypdf import PdfReader
        except ImportError:
            PdfReader = None
            if pliki:
                self.lista.addItem('Brak biblioteki pypdf — nie można odczytać formatów')
            pliki = []

        for rel in pliki:
            pdf_path = os.path.join(self.folder, rel)
            atlas = _czy_atlas(pdf_path)
            try:
                grupa = _grupa(*_wymiary_mm(pdf_path, PdfReader))
            except Exception:
                grupa = None
            opis = _OPIS_GRUPY[grupa] if grupa else 'błąd odczytu'
            if atlas:
                opis += ', atlas'
            item = QListWidgetItem(f'{rel[:-4]}   [{opis}]')
            item.setData(Qt.UserRole, (rel, grupa, atlas))
            if grupa:
                item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
                item.setCheckState(Qt.Checked)
                grupy.add(grupa)
                ma_atlas = ma_atlas or atlas
            else:
                item.setFlags(item.flags() & ~Qt.ItemIsEnabled)
            self.lista.addItem(item)

        for grupa, wiersz in self.wiersze_drukarek.items():
            wiersz.setVisible(grupa in grupy)
        self.chk_duplex.setVisible(ma_atlas)

    def _zaznacz(self, stan):
        for i in range(self.lista.count()):
            item = self.lista.item(i)
            if item.flags() & Qt.ItemIsUserCheckable:
                item.setCheckState(stan)

    def _wybierz_sumatra(self):
        p, _ = QFileDialog.getOpenFileName(
            self, 'SumatraPDF.exe', '', 'SumatraPDF (SumatraPDF.exe)')
        if p:
            self.sumatra_edit.setText(p)

    def zapisz_drukarki(self):
        ustawienia = QgsSettings()
        for grupa, cmb in self.cmb_drukarki.items():
            ustawienia.setValue(_KLUCZ_DRUKARKI + grupa, cmb.currentText())

    @property
    def folder(self):
        return self.folder_edit.text()

    @property
    def wybrane(self):
        # [(ścieżka względna, grupa, atlas)]
        return [self.lista.item(i).data(Qt.UserRole)
                for i in range(self.lista.count())
                if self.lista.item(i).flags() & Qt.ItemIsUserCheckable
                and self.lista.item(i).checkState() == Qt.Checked]

    @property
    def kopie(self):
        return self.spin_kopie.value()

    @property
    def drukarki(self):
        # {grupa: nazwa drukarki} - '' gdy "nie drukuj"
        return {grupa: '' if cmb.currentText() == _NIE_DRUKUJ else cmb.currentText()
                for grupa, cmb in self.cmb_drukarki.items()}

    @property
    def dwustronnie_atlasy(self):
        return self.chk_duplex.isChecked()

    @property
    def sumatra(self):
        return self.sumatra_edit.text()


def _wymiary_mm(pdf_path, PdfReader):
    page = PdfReader(pdf_path).pages[0]
    w_mm = float(page.mediabox.width) * 25.4 / 72
    h_mm = float(page.mediabox.height) * 25.4 / 72
    if int(page.get('/Rotate', 0) or 0) % 180:
        w_mm, h_mm = h_mm, w_mm
    return round(w_mm), round(h_mm)


def _drukuj_plik(pdf_path, drukarka, sumatra, kopie, PdfReader, grupa,
                 dwustronnie=False):
    w_mm, h_mm = _wymiary_mm(pdf_path, PdfReader)
    _ustaw_rozmiar(drukarka, w_mm, h_mm, grupa)
    orient = 'landscape' if w_mm > h_mm else 'portrait'
    ustawienia = ['noscale', orient, f'{kopie}x']
    if grupa in _PAPIER_STD:
        ustawienia.append('paper=' + grupa)
    # Atlasy zawsze pionowe - obracanie po długim boku. Jawny simplex, żeby
    # domyślny duplex drukarki nie łapał zwykłych map
    ustawienia.append('duplexlong' if dwustronnie else 'simplex')
    subprocess.run(
        [sumatra, '-print-to', drukarka, '-print-settings', ','.join(ustawienia),
         pdf_path],
        check=True, timeout=60)


def drukuj_mapy(iface):
    dlg = _DrukujDialog(iface.mainWindow())
    if dlg.exec_() != QDialog.Accepted:
        return

    folder = dlg.folder
    drukarki = dlg.drukarki
    sumatra = dlg.sumatra
    kopie = dlg.kopie
    dwustronnie_atlasy = dlg.dwustronnie_atlasy
    _zapisz_sumatra(sumatra)
    dlg.zapisz_drukarki()

    if not folder or not os.path.isdir(folder):
        iface.messageBar().pushMessage('BŁĄD', 'Nieprawidłowy folder', Qgis.Critical)
        return
    if not os.path.isfile(sumatra):
        iface.messageBar().pushMessage(
            'BŁĄD', 'Nie znaleziono SumatraPDF.exe', Qgis.Critical)
        return

    try:
        from pypdf import PdfReader
    except ImportError:
        iface.messageBar().pushMessage(
            'BŁĄD', 'Brak biblioteki pypdf', Qgis.Critical)
        return

    pliki = dlg.wybrane
    if not pliki:
        iface.messageBar().pushMessage(
            'BŁĄD', 'Nie wybrano żadnego pliku do druku', Qgis.Warning)
        return

    wykonane = 0
    bledne = 0
    pominiete = 0

    folder_x2 = _folder_x2(folder)

    for rel, grupa, atlas in pliki:
        drukarka = drukarki[grupa]
        if not drukarka:
            QgsMessageLog.logMessage(
                f'Pominięto ({_OPIS_GRUPY[grupa]} - nie drukuj): {rel}',
                'LCH', Qgis.Info)
            pominiete += 1
            continue

        pdf_path = os.path.join(folder, rel)
        dwustronnie = atlas and dwustronnie_atlasy

        # Pary _x2 tylko dla wielkiego formatu: najpierw PLOTOWANIE/<gmina>_x2,
        # potem stary uklad (_x2 obok oryginalu)
        x2_path = None
        if grupa == 'WF' and kopie >= 2:
            x2_name = os.path.basename(pdf_path)[:-4] + '_x2.pdf'
            for p in (os.path.join(folder_x2, x2_name),
                      os.path.join(os.path.dirname(pdf_path), x2_name)):
                if os.path.isfile(p):
                    x2_path = p
                    break

        try:
            if x2_path:
                pary = kopie // 2
                reszta = kopie % 2
                _drukuj_plik(x2_path, drukarka, sumatra, pary, PdfReader, grupa)
                if reszta:
                    _drukuj_plik(pdf_path, drukarka, sumatra, 1, PdfReader, grupa)
                QgsMessageLog.logMessage(
                    f'Wydrukowano: {rel} ({pary}×_x2'
                    + (f' + 1×oryg' if reszta else '') + ')',
                    'LCH', Qgis.Info)
            else:
                _drukuj_plik(pdf_path, drukarka, sumatra, kopie, PdfReader, grupa,
                             dwustronnie)
                QgsMessageLog.logMessage(
                    f'Wydrukowano: {rel} ({kopie}×'
                    + (', dwustronnie' if dwustronnie else '') + f') na {drukarka}',
                    'LCH', Qgis.Info)
            wykonane += 1
        except Exception as e:
            QgsMessageLog.logMessage(f'Błąd: {rel}: {e}', 'LCH', Qgis.Warning)
            bledne += 1

    info = f'Wydrukowano: {wykonane}'
    if pominiete:
        info += f', pominięto (nie drukuj): {pominiete}'
    if bledne == 0:
        iface.messageBar().pushMessage('OK', info, Qgis.Success)
    else:
        iface.messageBar().pushMessage(
            'PROBLEMY', f'{info}, błędów: {bledne}', Qgis.Warning)
