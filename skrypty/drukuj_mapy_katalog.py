import os
import subprocess
from qgis.core import Qgis, QgsMessageLog
from PyQt5.QtWidgets import (QDialog, QDialogButtonBox, QVBoxLayout, QHBoxLayout,
                              QLabel, QLineEdit, QPushButton, QComboBox, QFileDialog,
                              QSpinBox, QCheckBox, QListWidget, QListWidgetItem)
from PyQt5.QtCore import Qt

_SUMATRA_PATHS = [
    r'C:\Program Files\SumatraPDF\SumatraPDF.exe',
    r'C:\Program Files (x86)\SumatraPDF\SumatraPDF.exe',
    os.path.expanduser(r'~\AppData\Local\SumatraPDF\SumatraPDF.exe'),
]
_PLIK_SUMATRA = os.path.join(os.path.dirname(__file__), 'sumatra_path.txt')


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


def _ustaw_rozmiar(drukarka, w_mm, h_mm):
    try:
        import win32print
        hPrinter = win32print.OpenPrinter(drukarka)
        try:
            info = win32print.GetPrinter(hPrinter, 2)
            dm = info['pDevMode']
            # Papier zawsze opisany pionowo (szer = krótszy bok), a poziomą
            # mapę obsługuje orientacja — inaczej sterownik nie obraca
            # strony i obcina mapę
            dm.PaperSize = 256          # DMPAPER_USER
            dm.PaperWidth = int(min(w_mm, h_mm) * 10)   # w dziesiątych mm
            dm.PaperLength = int(max(w_mm, h_mm) * 10)  # w dziesiątych mm
            dm.Orientation = 2 if w_mm > h_mm else 1    # DMORIENT_LANDSCAPE / PORTRAIT
            # Kopie liczy Sumatra — domyślne kopie drukarki muszą być 1,
            # inaczej każdy wydruk się mnoży
            dm.Copies = 1
            # DM_ORIENTATION | DM_PAPERSIZE | DM_PAPERLENGTH | DM_PAPERWIDTH | DM_COPIES
            dm.Fields = dm.Fields | 0x010F
            win32print.SetPrinter(hPrinter, 2, info, 0)
        finally:
            win32print.ClosePrinter(hPrinter)
    except Exception as e:
        QgsMessageLog.logMessage(f'Błąd ustawiania rozmiaru papieru: {e}', 'LCH', Qgis.Warning)


def _lista_pdf(folder):
    # Tylko oryginały (nie _x2), _x2 obsługiwane automatycznie przy druku
    if not folder or not os.path.isdir(folder):
        return []
    return sorted(f for f in os.listdir(folder)
                  if f.lower().endswith('.pdf') and not f[:-4].endswith('_x2'))


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

        layout.addWidget(QLabel('Obręby do druku:'))
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
        self.folder_edit.textChanged.connect(self._odswiez_liste)

        layout.addWidget(QLabel('Drukarka:'))
        self.cmb = QComboBox()
        self.cmb.addItems(_lista_drukarek())
        layout.addWidget(self.cmb)

        row_kop = QHBoxLayout()
        row_kop.addWidget(QLabel('Liczba kopii:'))
        self.spin_kopie = QSpinBox()
        self.spin_kopie.setMinimum(1)
        self.spin_kopie.setMaximum(99)
        self.spin_kopie.setValue(1)
        row_kop.addWidget(self.spin_kopie)
        row_kop.addStretch()
        layout.addLayout(row_kop)

        self.chk_a3 = QCheckBox('Drukuj A3 (mapy mieszczące się na arkuszu A3)')
        self.chk_a3.setChecked(False)
        layout.addWidget(self.chk_a3)

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

    def _wybierz_folder(self):
        d = QFileDialog.getExistingDirectory(
            self, 'Wybierz folder z PDF:', self.folder_edit.text())
        if d:
            self.folder_edit.setText(d)

    def _odswiez_liste(self):
        self.lista.clear()
        for pdf_name in _lista_pdf(self.folder):
            item = QListWidgetItem(pdf_name[:-4])
            item.setData(Qt.UserRole, pdf_name)
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
            item.setCheckState(Qt.Checked)
            self.lista.addItem(item)

    def _zaznacz(self, stan):
        for i in range(self.lista.count()):
            self.lista.item(i).setCheckState(stan)

    def _wybierz_sumatra(self):
        p, _ = QFileDialog.getOpenFileName(
            self, 'SumatraPDF.exe', '', 'SumatraPDF (SumatraPDF.exe)')
        if p:
            self.sumatra_edit.setText(p)

    @property
    def folder(self):
        return self.folder_edit.text()

    @property
    def wybrane(self):
        return [self.lista.item(i).data(Qt.UserRole)
                for i in range(self.lista.count())
                if self.lista.item(i).checkState() == Qt.Checked]

    @property
    def kopie(self):
        return self.spin_kopie.value()

    @property
    def drukuj_a3(self):
        return self.chk_a3.isChecked()

    @property
    def drukarka(self):
        return self.cmb.currentText()

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


def _miesci_sie_w_A3(w_mm, h_mm):
    # 1 mm tolerancji na zaokrąglenia eksportu
    return min(w_mm, h_mm) <= 298 and max(w_mm, h_mm) <= 421


def _drukuj_plik(pdf_path, drukarka, sumatra, kopie, PdfReader):
    w_mm, h_mm = _wymiary_mm(pdf_path, PdfReader)
    _ustaw_rozmiar(drukarka, w_mm, h_mm)
    orient = 'landscape' if w_mm > h_mm else 'portrait'
    settings = f'noscale,{orient},{kopie}x'
    subprocess.run(
        [sumatra, '-print-to', drukarka, '-print-settings', settings, pdf_path],
        check=True, timeout=60)


def drukuj_mapy(iface):
    dlg = _DrukujDialog(iface.mainWindow())
    if dlg.exec_() != QDialog.Accepted:
        return

    folder = dlg.folder
    drukarka = dlg.drukarka
    sumatra = dlg.sumatra
    kopie = dlg.kopie
    drukuj_a3 = dlg.drukuj_a3
    _zapisz_sumatra(sumatra)

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

    pdfs = dlg.wybrane
    if not pdfs:
        iface.messageBar().pushMessage(
            'BŁĄD', 'Nie wybrano żadnego obrębu do druku', Qgis.Warning)
        return

    wykonane = 0
    bledne = 0
    pominiete = 0

    for pdf_name in pdfs:
        pdf_path = os.path.join(folder, pdf_name)
        x2_path = os.path.join(folder, pdf_name[:-4] + '_x2.pdf')
        has_x2 = os.path.isfile(x2_path)
        try:
            if not drukuj_a3 and _miesci_sie_w_A3(*_wymiary_mm(pdf_path, PdfReader)):
                QgsMessageLog.logMessage(
                    f'Pominięto (A3): {pdf_name}', 'LCH', Qgis.Info)
                pominiete += 1
                continue
            if has_x2 and kopie >= 2:
                pary = kopie // 2
                reszta = kopie % 2
                _drukuj_plik(x2_path, drukarka, sumatra, pary, PdfReader)
                if reszta:
                    _drukuj_plik(pdf_path, drukarka, sumatra, 1, PdfReader)
                QgsMessageLog.logMessage(
                    f'Wydrukowano: {pdf_name} ({pary}×_x2'
                    + (f' + 1×oryg' if reszta else '') + ')',
                    'LCH', Qgis.Info)
            else:
                _drukuj_plik(pdf_path, drukarka, sumatra, kopie, PdfReader)
                QgsMessageLog.logMessage(
                    f'Wydrukowano: {pdf_name} ({kopie}×)', 'LCH', Qgis.Info)
            wykonane += 1
        except Exception as e:
            QgsMessageLog.logMessage(f'Błąd: {pdf_name}: {e}', 'LCH', Qgis.Warning)
            bledne += 1

    info = f'Wydrukowano: {wykonane}'
    if pominiete:
        info += f', pominięto A3: {pominiete}'
    if bledne == 0:
        iface.messageBar().pushMessage('OK', info, Qgis.Success)
    else:
        iface.messageBar().pushMessage(
            'PROBLEMY', f'{info}, błędów: {bledne}', Qgis.Warning)
