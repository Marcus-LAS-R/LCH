from qgis.core import QgsProject, Qgis, QgsLayoutExporter, QgsMessageLog
import os
from PyQt5.QtWidgets import (QFileDialog, QDialog, QDialogButtonBox,
                              QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
                              QPushButton, QCheckBox)

PROG_PASA_MM = 420


def _usun_aux(pdf_path):
    """Usuwa sidecar .aux.xml, ktory GDAL dopisuje przy eksporcie PDF."""
    aux_path = pdf_path + '.aux.xml'
    if os.path.isfile(aux_path):
        os.remove(aux_path)


class _EksportDialog(QDialog):
    def __init__(self, parent):
        super().__init__(parent)
        self.setWindowTitle('Eksportuj mapy (katalog)')
        self.setMinimumWidth(400)

        layout = QVBoxLayout()

        folder_layout = QHBoxLayout()
        folder_layout.addWidget(QLabel('Katalog projektów:'))
        self.folder_edit = QLineEdit()
        folder_layout.addWidget(self.folder_edit)
        btn = QPushButton('...')
        btn.setFixedWidth(30)
        btn.clicked.connect(self._wybierz_folder)
        folder_layout.addWidget(btn)
        layout.addLayout(folder_layout)

        self.chk_tiff = QCheckBox('Wyeksportuj TIFF')
        self.chk_tiff.setChecked(False)
        layout.addWidget(self.chk_tiff)

        self.chk_paruj = QCheckBox('Paruj pasy (2 mapy na arkuszu)')
        self.chk_paruj.setChecked(True)
        layout.addWidget(self.chk_paruj)

        przyciski = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        przyciski.accepted.connect(self.accept)
        przyciski.rejected.connect(self.reject)
        layout.addWidget(przyciski)

        self.setLayout(layout)

    def _wybierz_folder(self):
        folder = QFileDialog.getExistingDirectory(
            self, 'Wybierz katalog projektów:', self.folder_edit.text())
        if folder:
            self.folder_edit.setText(folder)

    @property
    def folder(self):
        return self.folder_edit.text()

    @property
    def eksportuj_tiff(self):
        return self.chk_tiff.isChecked()

    @property
    def paruj_pasy(self):
        return self.chk_paruj.isChecked()


def eksportuj_mapy(iface):
    dlg = _EksportDialog(iface.mainWindow())
    if dlg.exec_() != QDialog.Accepted:
        return

    projects_folder = dlg.folder
    if not projects_folder:
        return
    eksportuj_tiff = dlg.eksportuj_tiff
    paruj_pasy = dlg.paruj_pasy

    plot_folder = os.path.abspath(
        os.path.join(projects_folder, '..', '..', 'PLOTOWANIE'))
    if not os.path.exists(plot_folder):
        os.makedirs(plot_folder)

    projectPaths = []
    for root, dirs, files in os.walk(projects_folder):
        projectPaths += [
            os.path.join(root, f) for f in files if f[-3:] in ['qgs', 'qgz']]

    wykonane = 0
    bledne = 0
    pomiete = []
    pasy = []  # (nazwa, pdf_path, width_mm, height_mm) — single-page, nie-atlas

    iface.mapCanvas().setRenderFlag(False)
    proj = QgsProject.instance()
    wymiary = [['nazwa', 'wys', 'szer']]
    for projectPath in sorted(projectPaths):
        proj.read(projectPath)
        layouts = QgsProject.instance().layoutManager().layouts()
        if not layouts:
            pomiete.append(os.path.basename(projectPath))
            continue
        for lay in layouts:
            lay.renderContext().setDpi(500)
            nazwa = projectPath.split(os.sep)[-2] + '_' + lay.name()
            QgsMessageLog.logMessage(nazwa, 'LCH', Qgis.Info)
            pg_coll = lay.pageCollection()
            wys_mm = pg_coll.maximumPageSize().height()
            szer_mm = pg_coll.maximumPageWidth()
            wymiary.append([nazwa, str(wys_mm), str(szer_mm)])

            exporter = QgsLayoutExporter(lay)
            if lay.atlas().enabled():
                pdf_path = os.path.join(plot_folder, nazwa + '.pdf')
                pdf_sett = QgsLayoutExporter(
                    lay.atlas().layout()).PdfExportSettings()
                res = exporter.exportToPdf(
                    lay.atlas(),
                    pdf_path,
                    settings=pdf_sett)
                if res != QgsLayoutExporter.Success:
                    bledne += 1
                else:
                    wykonane += 1
                    _usun_aux(pdf_path)

            else:
                pdf_path = os.path.join(plot_folder, nazwa + '.pdf')
                res = exporter.exportToPdf(
                    pdf_path,
                    QgsLayoutExporter.PdfExportSettings())
                if res != QgsLayoutExporter.Success:
                    bledne += 1
                else:
                    wykonane += 1
                    _usun_aux(pdf_path)
                    if min(szer_mm, wys_mm) < PROG_PASA_MM:
                        pasy.append((nazwa, pdf_path, szer_mm, wys_mm))

                if eksportuj_tiff and 'LEG' != nazwa[-3:]:
                    res = exporter.exportToImage(
                        os.path.join(plot_folder, nazwa + '.tif'),
                        QgsLayoutExporter.ImageExportSettings())
                    if res != QgsLayoutExporter.Success:
                        bledne += 1
                    else:
                        wykonane += 1

    fwys = open(os.path.join(plot_folder, 'wymiary.txt'), 'w')
    fwys.write('\n'.join(['\t'.join(x) for x in wymiary]))
    fwys.close()

    if paruj_pasy and pasy:
        _polacz_pasy(pasy, plot_folder)

    iface.mapCanvas().setRenderFlag(True)
    if pomiete:
        QgsMessageLog.logMessage(
            'Pominięte (brak layoutu): ' + ', '.join(pomiete), 'LCH', Qgis.Warning)
    if wykonane > 0 and bledne == 0 and not pomiete:
        iface.messageBar().pushMessage(
            'OK', 'Wyeksportowano map: ' + str(wykonane), Qgis.Success)
    else:
        msg = 'Wyeksportowano: ' + str(wykonane)
        if bledne:
            msg += ', błędów: ' + str(bledne)
        if pomiete:
            msg += ', pominięto (brak layoutu): ' + str(len(pomiete))
        iface.messageBar().pushMessage('PROBLEMY', msg, Qgis.Warning)


def _polacz_pasy(pasy, plot_folder):
    try:
        from pypdf import PdfReader, PdfWriter, Transformation
    except ImportError:
        QgsMessageLog.logMessage(
            'Brak biblioteki pypdf — pomijam dublowanie pasów.', 'LCH', Qgis.Warning)
        return

    for m in pasy:
        _dubluj(m, plot_folder)


def _dubluj(m, plot_folder):
    from pypdf import PdfReader, PdfWriter, Transformation

    nazwa, path, szer_mm, wys_mm = m
    page = PdfReader(path).pages[0]
    w = float(page.mediabox.width)
    h = float(page.mediabox.height)

    writer = PdfWriter()

    if szer_mm <= wys_mm:  # pionowy pas → dwie kopie obok siebie
        new_page = writer.add_blank_page(w * 2, h)
        new_page.merge_transformed_page(page, Transformation())
        new_page.merge_transformed_page(page, Transformation().translate(w, 0))
    else:  # poziomy pas → dwie kopie jedna pod drugą
        new_page = writer.add_blank_page(w, h * 2)
        new_page.merge_transformed_page(page, Transformation().translate(0, h))
        new_page.merge_transformed_page(page, Transformation())

    out_name = nazwa + '_x2.pdf'
    with open(os.path.join(plot_folder, out_name), 'wb') as f:
        writer.write(f)
    QgsMessageLog.logMessage('Zdublowano: ' + out_name, 'LCH', Qgis.Info)
