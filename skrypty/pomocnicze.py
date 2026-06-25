import processing  # noqa
import os
import platform
import glob
from qgis.core import QgsProject, Qgis, QgsCoordinateReferenceSystem, \
    QgsGeometry, QgsPointXY, QgsFeature, QgsVectorLayer, QgsVectorFileWriter, \
    QgsFeatureRequest
from PyQt5.QtWidgets import QFileDialog


class SciezkaPomocnicze:
    def __init__(self):
        self.sciezka = ''
        self.plik = os.path.join(os.path.dirname(__file__), 'pomocnicze.txt')
        self.odczytaj_sciezke()

    def odczytaj_sciezke(self):
        if os.path.isfile(self.plik):
            self.sciezka = open(self.plik).readlines()[0].rstrip('\r\n \t')
        else:
            self.sciezka = QFileDialog.getExistingDirectory(
                None,
                "Katalog z warstwami pomocniczymi:",
                "c:\\"
            )
            open(self.plik, 'w').write(self.sciezka)


class WarstwyPomocnicze():
    def __init__(self, iface):
        self.iface = iface
        self._WARSTWY = {
            'ODDZIALY': 'LASY_INNE_AFT',
            'DROGI_LFT': 'DROGI_LFT',
            'F_OCHRONY': 'F_OCHRONY',
            'miejscowosci': 'MIEJSCOWOSCI_PFT',
            'NADLESNICTWA': 'NADLESNICTWA',
            'WODA_AFT': 'WODA_AFT',
            'RZEKI_LFT': 'RZEKI_LFT',
            'OSP_PFT': 'OSP_PFT',
        }
        self.maska = False
        self.oddz_kat = ''

        if platform.system()[:3] == 'Win':
            sc = SciezkaPomocnicze()
            if sc.sciezka is False:
                self.iface.messageBar().pushMessage(
                    'BŁĄD',
                    'Niepoprawna ścieżka do folderu z danymi pomocniczymi',
                    Qgis.Critical)
                return
            self.kat_dane = sc.sciezka
        else:
            self.kat_dane = '/home/pawel/upul/_dane'

    def znajdz_oddz(self):
        self.oddz = QgsProject.instance().mapLayersByName('ODDZ')
        if len(self.oddz) != 1:
            self.iface.messageBar().pushMessage(
                'BŁĄD', 'Nie znalazłem warstwy ODDZ w TOC!', Qgis.Critical)
            return False
        self.oddz = self.oddz[0]
        if not self.oddz.isValid():
            self.iface.messageBar().pushMessage(
                'BŁĄD', 'Niepoprawna wartwa ODDZ!', Qgis.Critical)
            return False
        self.oddz_kat = os.path.dirname(
            self.oddz.dataProvider().dataSourceUri().split("|")[0])
        return True

    def sprawdz_maske(metoda):
        def wrap(*args):
            self = args[0]
            if len(self.maska) is not False:
                metoda(args[1])
            else:
                print('Najpierw musisz wygenerować maskę na podstawie oddz')
        return wrap

    def przygotuj_upul(self):
        self.pobierz_katalog()
        self.przygotuj_maske()
        for war in ['DROGI_LFT', 'ODDZIALY', ]:
            self.przetnij_warstwe(war)

    def przygotuj_fochr(self):
        self.kat = self.oddz_kat
        self.przygotuj_maske()
        for war in ['F_OCHRONY', 'miejscowosci', 'WODA_AFT', 'RZEKI_LFT', ]:
            self.przetnij_warstwe(war)

    def przygotuj_ppoz(self):
        self.kat = self.oddz_kat
        self.przygotuj_maske()
        for war in ['OSP_PFT', 'miejscowosci', 'WODA_AFT', 'RZEKI_LFT', ]:
            self.przetnij_warstwe(war)

    def pobierz_katalog(self):
        self.kat = QFileDialog.getExistingDirectory(
            self.iface.mainWindow(),
            "Katalog do zapisania danych:",
            self.oddz_kat)

    def przygotuj_maske(self):
        ext = self.oddz.extent()
        xmin = ext.xMinimum() - 2000
        xmax = ext.xMaximum() + 2000
        ymin = ext.yMinimum() - 2000
        ymax = ext.yMaximum() + 2000

        # warstwa maska z wagami
        self.maska = QgsVectorLayer(
            "Polygon?crs=epsg:2180&index=yes", "maska", "memory")
        self.maskaPr = self.maska.dataProvider()
        self.maska.startEditing()

        feat = QgsFeature()
        maskaPoly = [
            QgsPointXY(xmin, ymin),
            QgsPointXY(xmin, ymax),
            QgsPointXY(xmax, ymax),
            QgsPointXY(xmax, ymin),
        ]
        geom = QgsGeometry.fromPolygonXY([maskaPoly])
        feat.setGeometry(geom)
        self.maskaPr.addFeatures([feat])
        self.maska.commitChanges()

        # zapisz maske na dysku, moze bedzie potrzebna
        crs = QgsCoordinateReferenceSystem("epsg:2180")
        QgsVectorFileWriter.writeAsVectorFormat(self.maska,
                                                os.path.join(self.kat,
                                                             "MASKA_AFT.shp"),
                                                "UTF-8",
                                                crs,
                                                "ESRI Shapefile")
        self.maska = QgsVectorLayer(os.path.join(self.kat, "MASKA_AFT.shp"),
                                    "MASKA_AFT",
                                    "ogr")
        QgsProject.instance().addMapLayer(self.maska)

    # @sprawdz_maske
    def przetnij_warstwe(self, war):
        if war not in self._WARSTWY:
            self.iface.messageBar().pushMessage(
                'BŁĄD', 'Nierozpoznana warstwa', Qgis.Critical)
            return

        sc = glob.glob(os.path.join(self.kat_dane, war+'.shp'))
        if len(sc) > 0:
            warstwa = QgsVectorLayer(sc[0], 'ciecie', 'ogr')
            if warstwa.isValid():
                ext = self.maska.extent()
                req = QgsFeatureRequest().setFilterRect(ext)
                feats = [f for f in warstwa.getFeatures(req)]

                if len(feats) == 0:
                    return

                t = 'MultiPolygon'
                if war in ['miejscowosci', 'OSP_PFT']:
                    t = "Point"
                if war in ['RZEKI_LFT', 'DROGI_LFT']:
                    t = "MultiLineString"
                lyr = QgsVectorLayer(
                    t+"?crs=epsg:2180&index=yes", war, 'memory')
                lyr.startEditing()
                lyrPr = lyr.dataProvider()
                lyrPr.addAttributes(warstwa.dataProvider().fields().toList())
                lyr.updateFields()
                lyrPr.addFeatures(feats)
                lyr.commitChanges()
                crs = QgsCoordinateReferenceSystem("epsg:2180")
                QgsVectorFileWriter.writeAsVectorFormat(
                    lyr,
                    os.path.join(self.kat, self._WARSTWY[war]+'.shp'),
                    "UTF-8",
                    crs,
                    "ESRI Shapefile")

        else:
            self.iface.messageBar().pushMessage(
                'BŁĄD', 'Nieodnalzłem warstwy '+war+' w kat. roboczym',
                Qgis.Critical)
            return

    def wytnij_maske(self):
        processing.run("saga:difference", {
                            'A': self.maska,
                            'B': self.oddz,
                            'SPLIT': False,
                            'RESULT': os.path.join(
                                self.kat, 'MASKA_DIFF_AFT.shp'
                            )
            })
