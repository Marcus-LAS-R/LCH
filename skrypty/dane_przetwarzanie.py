import os
import shutil
from qgis.core import QgsProject, Qgis, QgsVectorFileWriter, QgsVectorLayer,\
    QgsCoordinateReferenceSystem, QgsExpression, QgsFeatureRequest, \
    QgsSpatialIndex, QgsField
from PyQt5.QtWidgets import QFileDialog
from PyQt5.QtCore import QVariant
import processing
from collections import defaultdict
from .planarize import Planarize


class recursivedefaultdict(defaultdict):
    def __init__(self):
        self.default_factory = type(self)


def podziel_obrebami(iface):  # noqa
    lyrs = QgsProject.instance().mapLayers().values()
    braki = []
    for lyr in lyrs:
        pola = [x.name() for x in lyr.dataProvider().fields().toList()
                if x.name() in ['COMMUNITY', 'MUNICIP']]
        if len(pola) != 2:
            if 'COMMUNITY' not in pola:
                braki.append(lyr.name()+'-COMMUNITY')
            else:
                braki.append(lyr.name()+'-MUNICIP')

    if len(braki) > 0:
        iface.messageBar().pushMessage(
            'BRAK PÓL',
            'Nie odnaleziono pól w warstwach: ' +
            ', '.join(braki),
            Qgis.Critical
        )
        return

    kat = QFileDialog.getExistingDirectory(
        iface.mainWindow(), "Wybierz katalog: ")

    obr = [n for n in os.listdir(kat) if os.path.isdir(os.path.join(kat, n))
           and n != 'OGOLNE']
    slObr = {item.split('_')[0]: item for item in obr}
    gm = os.path.split(kat)[-1][:3]

    # jezeli okd gminy nie jest poprawny konczymy
    if not gm.isdigit():
        iface.messageBar().pushMessage(
            'KOD GMINY',
            'Czy katalog gminy ma odpowiedni format zapisu zaczynający '
            'się od kodu?',
            Qgis.Critical
        )
        return

    w_ob = [
        'WYDZ_OPS',
        'WYDZ_POL',
        'DZKAT',
        'DZKAT_OPS',
        'MapRam',
        'ATLAS_AFT',
        'LIN_ODDZ',
        'ODDZ',
        'PNSW',
        'LINIE',
        'KAS',
        'KLU_LFT',
        'KLU_AFT',
        'EWID',
    ]

    w_ob_pft = [
            u'WYDZ_OPS',
            u'DZKAT_OPS',
    ]
    w_ob_lft = [
            u'LIN_ODDZ',
            u'LINIE',
            u'KAS',
            u'KLU_LFT',
    ]

    lista = []
    for lyr in QgsProject.instance().mapLayers().values():
        nazwa = lyr.name()
        if nazwa == 'LINIE_intersect':
            nazwa = 'LINIE'
        lista.append(nazwa)

    for ob in slObr.keys():
        for b in [x for x in w_ob if x not in lista]:
            # warstwe ewid separujem od innych
            naz_kat = 'SHP'
            if b == 'EWID':
                naz_kat = 'EWID'

            if not os.path.isfile(
                    os.path.join(kat, slObr[ob], naz_kat, b+".shp")):
                t = 'Polygon'
                if b in w_ob_pft:
                    t = "Point"
                if b in w_ob_lft:
                    t = "LineString"
                lyrT = QgsVectorLayer(
                    t+"?crs=epsg:2180&index=yes", b, 'memory')
                crs = QgsCoordinateReferenceSystem("epsg:2180")

                try:
                    QgsVectorFileWriter.writeAsVectorFormat(
                        lyrT,
                        os.path.join(kat, slObr[ob], naz_kat, b+".shp"),
                        "UTF-8",
                        crs,
                        "ESRI Shapefile")
                except:  # noqa
                    pass

    for lyr in QgsProject.instance().mapLayers().values():
        nazwa = lyr.name()
        if nazwa == 'LINIE_intersect':
            nazwa = 'LINIE'

        for ob in slObr.keys():
            exp = QgsExpression("\"COMMUNITY\" = '"+str(ob) +
                                "' AND \"MUNICIP\" = '" + str(gm) + "'")
            feats = [f for f in lyr.getFeatures(QgsFeatureRequest(exp))]

            t = 'Polygon'
            if nazwa in w_ob_pft:
                t = "Point"
            if nazwa in w_ob_lft:
                t = "LineString"
            lyrT = QgsVectorLayer(t+"?crs=epsg:2180&index=yes",
                                    nazwa,
                                    'memory')
            lyrT.startEditing()
            lyrTPr = lyrT.dataProvider()
            lyrTPr.addAttributes(lyr.dataProvider().fields().toList())
            lyrT.updateFields()
            lyrTPr.addFeatures(feats)
            lyrT.commitChanges()

            crs = QgsCoordinateReferenceSystem("epsg:2180")
            katshp = "SHP"
            if nazwa == u'EWID':
                katshp = u'EWID'
            try:
                QgsVectorFileWriter.writeAsVectorFormat(
                    lyrT,
                    os.path.join(kat, slObr[ob], katshp, nazwa+".shp"),
                    "UTF-8",
                    crs,
                    "ESRI Shapefile")
            except:  # noqa
                iface.messageBar().pushMessage(
                    'Uwaga',
                    'Nie udało się zapisać na dysku: '
                    + nazwa + ", obręb: " + str(ob),
                    Qgis.Warning)


class UzupelnijLinPnsw():
    def __init__(self, iface):
        self.iface = iface

        self.wydz = False
        # self.wydz = self.iface.activeLayer()
        for lyr in QgsProject.instance().mapLayers().values():
            if lyr.name() == "WYDZ_POL":
                self.wydz = lyr

        if not self.wydz:
            self.iface.messageBar().pushMessage('Error',
                                                "Brak warstwy WYDZ_POl w TOC!",
                                                level=Qgis.Critical)
            return

        self.wydz.dataProvider().setEncoding(u'UTF-8')
        self.wydz_path = self.wydz.dataProvider().dataSourceUri().split("|")[0]
        self.kat = os.path.dirname(self.wydz_path)

        # zbuduj indeks przestrzenny dla wydzielen
        self.index = QgsSpatialIndex()
        self.fwydz = {w.id(): w for w in self.wydz.getFeatures()}
        for feat in self.wydz.getFeatures():
            self.index.insertFeature(feat)
            self.fwydz[feat.id()] = feat

        operacji = [0, 0]
        self.pnsw = False
        if os.path.isfile(os.path.join(self.kat, "PNSW.shp")):
            self.pnsw = QgsVectorLayer(os.path.join(self.kat, "PNSW.shp"),
                                       "PNSW", "ogr")
            self.dopiszPnsw()
            operacji[0] = 1

        if os.path.isfile(os.path.join(self.kat, "LINIE.shp")):
            self.dopiszLinie()
            operacji[1] = 1

        dopisano = u'Uzupełniono warstwę: '
        if operacji[0] == 1:
            dopisano += 'pnsw'
            if sum(operacji) > 1:
                dopisano += ', '
        if operacji[1] == 1:
            dopisano += 'lini'
        if sum(operacji) > 0:
            self.iface.messageBar().pushMessage(
                'Uwaga', dopisano, level=Qgis.Success)

    def dopiszPnsw(self):
        """
        Metoda dodaje kolumne COMMUNITY i na podstawie wydzielen dopisuje
        w ktorym obrebie leza PNSW
        """

        self.pnswPr = self.pnsw.dataProvider()

        # dodaj kolumne jesli nie ma w warstwie
        self.pnsw.startEditing()
        pola = [f.name() for f in self.pnsw.fields().toList()]
        if 'COMMUNITY' not in pola:
            self.pnswPr.addAttributes([
                QgsField('COMMUNITY', QVariant.String, len=4)])
        if 'MUNICIP' not in pola:
            self.pnswPr.addAttributes([
                QgsField('MUNICIP', QVariant.String, len=3)])

        if u'ADR_BDL' not in pola:
            self.pnswPr.addAttributes([
                QgsField('ADR_BDL', QVariant.String, len=35)])

        self.pnsw.commitChanges()
        # dopisz kody
        self.pnsw.startEditing()
        fnm = self.pnsw.dataProvider().fieldNameMap()
        for feat in self.pnsw.getFeatures():
            ids = self.index.intersects(feat.geometry().boundingBox())
            for id in ids:
                inter = feat.geometry().intersection(self.fwydz[id].geometry())
                if inter.area() > 1:
                    self.pnsw.dataProvider().changeAttributeValues({
                        feat.id(): {
                            fnm['COMMUNITY']: self.fwydz[id]['COMMUNITY'],
                            fnm['MUNICIP']: self.fwydz[id]['MUNICIP'],
                            fnm['ADR_BDL']: self.fwydz[id]['ADR_LES']
                        }
                    })

        self.pnsw.commitChanges()
        QgsProject.instance().addMapLayer(self.pnsw)

    def dopiszLinie(self):
        """
        Metoda dopisuje kolumne COMMUNITY i kod obrebu w ktorym dana linia
        jest zwektoryzowana, na podstawie oddz
        """

        if not os.path.isfile(os.path.join(self.kat, 'ODDZ.shp')):
            self.iface.messageBar().pushMessage(
                'Błąd',
                'Nie znaleziono warstwy ODDZ w katalogu z WYDZ_POL!',
                Qgis.Critical)
            return

        processing.run(
            "native:intersection",
            {
                'INPUT': os.path.join(self.kat, "LINIE.shp"),
                'OVERLAY': os.path.join(self.kat, "ODDZ.shp"),
                'OUTPUT': os.path.join(self.kat, "LINIE_intersect.shp")
            }
        )

        self.linie = self.iface.addVectorLayer(
            os.path.join(self.kat, "LINIE_intersect.shp"),
            "LINIE_intersect",
            "ogr")


def polacz_warstwy(iface):
    kat = QFileDialog.getExistingDirectory(
        iface.mainWindow(), "Wybierz katalog gminy: ")

    nazwy = [
        "WYDZ_POL",
        # "ATLAS_AFT",
        # "OBREBY_AFT",
        "WYDZ_OPS",
        "LINIE",
        "PNSW",
        "DZKAT",
        "KAS",
        # "EWID",
        "ODDZ",
        "LIN_ODDZ",
    ]

    gmi = kat.split(os.sep)[-1]
    out = os.path.abspath(os.path.join(kat, "..", gmi+"_GIS"))
    try:
        os.stat(out)
    except:  # noqa
        os.mkdir(out)

    for n in nazwy:
        # tablica z plikami o okreslonej nazwie
        pliki = []
        for root, dirs, files in os.walk(kat):
            for file in files:
                if file == n + ".shp":
                    pliki.append(os.path.join(root, file))

        if len(pliki) == 0:
            pass

        elif len(pliki) == 1:
            shutil.copy(pliki[0], os.path.join(out, n+".shp"))
            for ext in ['dbf', 'prj', 'shx']:
                if os.isfiel(pliki[0][:-3]+ext):
                    shutil.copy(pliki[0][:-3]+ext, os.path.join(out, n+f".{ext}"))

        elif len(pliki) > 1:
            processing.run(
                "native:mergevectorlayers",
                {'LAYERS': pliki,
                'CRS': None,
                'OUTPUT': os.path.join(out, n+".shp")
                }
            )

    iface.messageBar().pushMessage(
        'OK',
        'Połączono warstwy',
        Qgis.Success)


def linie_oddz(iface):
    oddz = QgsProject.instance().mapLayersByName("ODDZ")
    if len(oddz) == 0:
        iface.messageBar().pushMessage(
            'Error', "Brak warstwy ODDZ w TOC!", Qgis.Critical)
        return
    oddz = oddz[0]

    kat = os.path.dirname(oddz.dataProvider().dataSourceUri().split("|")[0])
    kattemp = os.path.join(kat, "temp")
    if not os.path.isdir(os.path.join(kat, "temp")):
        os.mkdir(os.path.join(kat, "temp"))

    obr = QgsProject.instance().mapLayersByName("OBREBY_AFT")
    if len(obr) != 1:
        obr = QgsVectorLayer(
            os.path.join(kat, "OBREBY_AFT.shp"), "OBREBY_AFT", "ogr")
        if not obr.isValid():
            obr = QgsVectorLayer(
                os.path.join(kat, "OBR.shp"), "OBREBY_AFT", "ogr")
        if not obr.isValid():
            iface.messageBar().pushMessage(
                "Error",
                u'Brak warstwy OBREBY_AFT w katalogu roboczym',
                Qgis.Critical,
            )
    else:
        obr = obr[0]

    processing.run("native:polygonstolines",
                   {'INPUT': oddz,
                    'OUTPUT': os.path.join(kattemp, "ODDZ_na_linie.shp")
                    }
                   )
    processing.run("native:polygonstolines",
                   {'INPUT': obr,
                    'OUTPUT': os.path.join(kattemp, "OBREBY_AFT_na_linie.shp")
                    }
                   )
    processing.run("native:buffer",
                   {'INPUT': os.path.join(kattemp, "OBREBY_AFT_na_linie.shp"),
                    'DISTANCE': 2,
                    'SEGMENTS': 1,
                    'END_CAP_STYLE': 1,
                    'JOIN_STYLE': 1,
                    'DISSOLVE': True,
                    'OUTPUT': os.path.join(kattemp,
                                           "OBREBY_AFT_na_linie_buff2m.shp")
                    }
                   )
    linTemp = QgsVectorLayer(
        os.path.join(kattemp, "ODDZ_na_linie.shp"), "linTemp", "ogr")
    Planarize(iface, linTemp, dodaj=False)
    processing.run("native:difference",
                   {'INPUT': os.path.join(kattemp, "linTemp_planarize.shp"),
                    'OVERLAY': os.path.join(kattemp,
                                            "OBREBY_AFT_na_linie_buff2m.shp"),
                    'OUTPUT': os.path.join(kat, "LIN_ODDZ.shp")
                    }
                   )

    iface.addVectorLayer(os.path.join(kat, "LIN_ODDZ.shp"), "LIN_ODDZ", "ogr")


if __name__ == "__console__":
    a = linie_oddz(iface)  # noqa
