from datetime import datetime
import os
from PyQt5.QtWidgets import QFileDialog, QInputDialog

from qgis.core import QgsProject, Qgis, QgsLayoutExporter

from .ustaw_mape import UstawMape
from .ustaw_mape import ustaw_leg as ustaw_leg_poj


def ustaw_mapy(iface):
    projects_folder = QFileDialog.getExistingDirectory(
        iface.mainWindow(), "Wybierz katalog: ")

    # stworz folder plotowania oIle nie istnieje
    plot_folder = os.path.abspath(
        os.path.join(projects_folder, '..', '..', 'PLOTOWANIE'))
    if not os.path.exists(plot_folder):
        os.mkdir(plot_folder)

    # znajdz wszystkie projekty w podanym katalogu.
    projectPaths = []
    for root, dirs, files in os.walk(projects_folder):
        projectPaths += [
            os.path.join(root, f) for f in files
            if f[-3:] in ['qgs', 'qgz'] and 'MAPA' in f]

    wykonane = 0
    bledne = 0
    # wylacz rysowania mapy w trakcie ustawiania layoutow
    proj = QgsProject.instance()
    stan_na, ok = QInputDialog.getText(
        None, 'Podaj stan na:', 'Stan na:',
        text='01.01.'+str(int(datetime.now().year)+1)
    )
    if not ok:
        return

    iface.mapCanvas().setRenderFlag(False)
    for projectPath in sorted(projectPaths):
        proj.read(projectPath)
        u = UstawMape(iface)
        if u.sprawdz_warstwy():
            if u.znajdz_bazy():
                u.pobierz_meta()
                u.zmien_meta(stan_na)
                u.przesun_elem()
                proj.write()
                wykonane += 1

                nazwa = projectPath.split(os.sep)[-2] + '_' + u.lay.name()
                exporter = QgsLayoutExporter(u.lay)
                exporter.exportToImage(os.path.join(plot_folder, nazwa+'.jpg'),
                                       QgsLayoutExporter.ImageExportSettings())

            else:
                bledne += 1
        else:
            bledne += 1

    iface.mapCanvas().setRenderFlag(True)
    if wykonane > 0 and bledne == 0:
        iface.messageBar().pushMessage(
            'OK', 'Ustawiono map: '+str(wykonane),
            Qgis.Success)
    else:
        iface.messageBar().pushMessage(
            'PROBLEMY', 'Ustawiono map: '+str(wykonane) +
            ' błędów/problemów: ' + str(bledne),
            Qgis.Warning)


def ustaw_leg(iface):
    projects_folder = QFileDialog.getExistingDirectory(
        iface.mainWindow(), "Wybierz katalog: ")

    # stworz folder plotowania oIle nie istnieje
    plot_folder = os.path.abspath(
        os.path.join(projects_folder, '..', '..', 'PLOTOWANIE'))
    if not os.path.exists(plot_folder):
        os.mkdir(plot_folder)

    # znajdz wszystkie projekty w podanym katalogu.
    projectPaths = []
    for root, dirs, files in os.walk(projects_folder):
        projectPaths += [
            os.path.join(root, f) for f in files
            if f[-3:] in ['qgs', 'qgz'] and f[:3] == 'LEG']

    # wylacz rysowania mapy w trakcie ustawiania layoutow
    iface.mapCanvas().setRenderFlag(False)
    proj = QgsProject.instance()

    wykonane = 0
    bledne = 0
    for projectPath in sorted(projectPaths):
        proj.read(projectPath)
        mn = QgsProject.instance().layoutManager()
        lay = mn.layouts()[0]
        if lay.name()[:3] == 'LEG':
            ustaw_leg_poj(iface)
            wykonane += 1
            proj.write()
            nazwa = projectPath.split(os.sep)[-2] + '_' + lay.name()
            print(nazwa)
            pg_coll = lay.pageCollection()
            exporter = QgsLayoutExporter(lay)
            res = exporter.exportToPdf(
                os.path.join(plot_folder, nazwa + '.pdf'),
                QgsLayoutExporter.PdfExportSettings())
            if not res == QgsLayoutExporter.Success:
                bledne += 1


    iface.mapCanvas().setRenderFlag(True)
    if wykonane > 0:
        iface.messageBar().pushMessage(
            'OK', f'Ustawiono legend: {wykonane}, babole: {bledne}',
            Qgis.Success)
    else:
        iface.messageBar().pushMessage(
            'PROBLEMY', 'Ustawiono map: '+str(wykonane),
            Qgis.Warning)
