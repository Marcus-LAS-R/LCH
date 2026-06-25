from qgis.core import QgsProject, Qgis, QgsLayoutExporter
import os
from PyQt5.QtWidgets import QFileDialog


def eksportuj_mapy(iface):
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
            os.path.join(root, f) for f in files if f[-3:] in ['qgs', 'qgz']]

    wykonane = 0
    bledne = 0
    # wylacz rysowania mapy w trakcie ustawiania layoutow
    iface.mapCanvas().setRenderFlag(False)
    proj = QgsProject.instance()
    wymiary = [['nazwa', 'wys', 'szer']]
    for projectPath in sorted(projectPaths):
        proj.read(projectPath)
        lay = QgsProject.instance().layoutManager().layouts()[0]
        lay.renderContext().setDpi(500)  # default 300, zakomentować jeśli nie trzeba
        nazwa = projectPath.split(os.sep)[-2] + '_' + lay.name()
        print(nazwa)
        pg_coll = lay.pageCollection()
        wys_stara = pg_coll.maximumPageSize().height()
        szer_stara = pg_coll.maximumPageWidth()
        wymiary.append([nazwa, str(wys_stara), str(szer_stara)])

        exporter = QgsLayoutExporter(lay)
        if lay.atlas().enabled():
            pdf_sett = QgsLayoutExporter(
                lay.atlas().layout()).PdfExportSettings()
            res = exporter.exportToPdf(
                lay.atlas(),
                os.path.join(plot_folder, nazwa+'.pdf'),
                settings=pdf_sett)
            if not res == QgsLayoutExporter.Success:
                bledne += 1
            else:
                wykonane += 1

        else:
            res = exporter.exportToPdf(
                os.path.join(plot_folder, nazwa+'.pdf'),
                QgsLayoutExporter.PdfExportSettings())
            if not res == QgsLayoutExporter.Success:
                bledne += 1
            else:
                wykonane += 1

            if 'LEG' != nazwa[-3:]:
                res = exporter.exportToImage(
                    os.path.join(plot_folder, nazwa+'.tif'),
                    QgsLayoutExporter.ImageExportSettings())
                if not res == QgsLayoutExporter.Success:
                    bledne += 1
                else:
                    wykonane += 1

    fwys = open(os.path.join(plot_folder, 'wymiary.txt'), 'w')
    fwys.write('\n'.join(['\t'.join(x) for x in wymiary]))
    fwys.close()
    iface.mapCanvas().setRenderFlag(True)
    if wykonane > 0 and bledne == 0:
        iface.messageBar().pushMessage(
            'OK', 'Wyeksportowano map: '+str(wykonane),
            Qgis.Success)
    else:
        iface.messageBar().pushMessage(
            'PROBLEMY', 'Wyeksportowano map: '+str(wykonane) +
            ' błędów/problemów: ' + str(bledne),
            Qgis.Warning)
