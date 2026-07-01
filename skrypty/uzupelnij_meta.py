from qgis.core import QgsProject, Qgis
import os
from datetime import datetime
from PyQt5.QtWidgets import QFileDialog, QInputDialog
from .ustaw_mape import UstawMape


def uaktualnij_mapy(iface):
    projects_folder = QFileDialog.getExistingDirectory(
        iface.mainWindow(), "Wybierz katalog: ")
    if not projects_folder:
        return

    stan_na, ok = QInputDialog.getText(
        iface.mainWindow(), 'Stan na:', 'Data stanu:',
        text='01.01.' + str(datetime.now().year))
    if not ok:
        return

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
    iface.mapCanvas().setRenderFlag(False)
    proj = QgsProject.instance()
    for projectPath in sorted(projectPaths):
        proj.read(projectPath)
        u = UstawMape(iface)
        if u.sprawdz_warstwy():
            if u.znajdz_bazy():
                u.pobierz_meta()
                u.zmien_meta(stan_na)
                proj.write()
                wykonane += 1

            else:
                bledne += 1
        else:
            bledne += 1

    iface.mapCanvas().setRenderFlag(True)
    if wykonane > 0 and bledne == 0:
        iface.messageBar().pushMessage(
            'OK', 'Zaktualizowano map: '+str(wykonane),
            Qgis.Success)
    else:
        iface.messageBar().pushMessage(
            'PROBLEMY', 'Zauktualizowano map: '+str(wykonane) +
            ' błędów/problemów: ' + str(bledne),
            Qgis.Warning)
