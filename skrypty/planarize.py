import os
from qgis.core import Qgis, QgsGeometry, QgsFeature, QgsPointXY,\
    QgsVectorLayer, QgsCoordinateReferenceSystem, QgsVectorFileWriter
from qgis.gui import QgsMessageBar
from collections import defaultdict


class recursivedefaultdict(defaultdict):
    def __init__(self):
        self.default_factory = type(self)


class Planarize(object):
    def __init__(self, iface, warstwa="", dodaj=True):
        self.iface = iface
        self.dodaj = dodaj

        try:
            if warstwa == "":
                self.lyr = self.iface.activeLayer()
            else:
                self.lyr = warstwa
                self.lyr.name()
        except:  # noqa
            self.iface.messageBar().pushMessage(
                'UWAGA',
                u'Brak wskazanej warstwy',
                level=QgsMessageBar.WARNING)
            return

        if self.lyr.wkbType() not in [2, 5]:
            self.iface.messageBar().pushMessage(
                'UWAGA',
                u'Wskazana warstwa nie jest liniowa',
                Qgis.Warning)
            return

        # zasieg w jakim beda szukane pkt
        self.zasieg = 0.1
        fs = self.do()

        self.zapisz(fs)

    def do(self):
        self.sl = recursivedefaultdict()
        self.sl[0][0][0][0] = 0

        # skopiuj ustawienia zaznaczonej warstwy
        feats = []
        for feat in self.lyr.getFeatures():
            tab = feat.geometry().asMultiPolyline()
            if len(tab[0]) == 0:
                tab = feat.geometry().asMultiPolyline()
            fs = self.przetworz(tab)
            for t in fs:
                f = QgsFeature()
                f.setFields(self.lyr.dataProvider().fields())
                g = QgsGeometry().fromPolylineXY(t)
                f.setGeometry(g)
                f.setAttributes(feat.attributes())
                # TODO dodac obsluge przepisywania atrybutow
                feats.append(f)

        return feats

    def przetworz(self, tab):
        lista = []
        for tt in tab:
            # zmienna z ostatnim pktem
            # lista zakwalifikowanych fragmentow lini
            pierwszy = False
            ltemp = []

            for i, p in enumerate(tt):
                if i > 0:
                    if self.sprawdz(p, pierwszy):
                        if len(ltemp) == 0:
                            ltemp = [QgsPointXY(pierwszy[0], pierwszy[1])]
                        ltemp.append(QgsPointXY(p[0], p[1]))
                    else:
                        if len(ltemp) > 1:
                            lista.append(ltemp)
                        ltemp = []
                pierwszy = p

            if len(ltemp) > 1:
                lista.append(ltemp)

        return lista

    def sprawdz(self, p, l):
        for xp in [x for x in self.sl.keys()
                   if x > p[0]-self.zasieg and x < p[0]+self.zasieg]:
            for yp in [y for y in self.sl[xp].keys()
                       if y > p[1]-self.zasieg and y < p[1]+self.zasieg]:
                for xl in [x for x in self.sl[xp][yp].keys()
                           if x > l[0]-self.zasieg and x < l[0]+self.zasieg]:
                    if len([x for x in self.sl[xp][yp][xl].keys()
                            if x > l[1]-self.zasieg and
                            x < l[1]+self.zasieg]) > 0:
                        return False

        for xp in [x for x in self.sl.keys()
                   if x > l[0]-self.zasieg and x < l[0]+self.zasieg]:
            for yp in [y for y in self.sl[xp].keys()
                       if y > p[1]-self.zasieg and y < p[1]+self.zasieg]:
                for xl in [x for x in self.sl[xp][yp].keys()
                           if x > p[0]-self.zasieg and x < p[0]+self.zasieg]:
                    if len([x for x in self.sl[xp][yp][xl].keys()
                            if x > p[1]-self.zasieg and
                            x < p[1]+self.zasieg]) > 0:
                        return False

        # nie znalezlismy tego odcinka w slowniku, mozna dodac pkt
        self.sl[l[0]][l[1]][p[0]][p[1]] = ""
        return True

    def zapisz(self, fs):
        self.kat = os.path.dirname(
            self.lyr.dataProvider().dataSourceUri().split("|")[0])
        wyn = QgsVectorLayer(
            "LineString?crs=epsg:2180", self.lyr.name()+"_planarize", "memory")
        wyn_data = wyn.dataProvider()
        wyn.startEditing()
        attr = self.lyr.dataProvider().fields().toList()
        wyn_data.addAttributes(attr)
        wyn.updateFields()

        wyn_data.addFeatures(fs)
        wyn.commitChanges()

        crs = QgsCoordinateReferenceSystem("epsg:2180")
        QgsVectorFileWriter.writeAsVectorFormat(
            wyn,
            os.path.join(self.kat, self.lyr.name()+"_planarize.shp"),
            "UTF-8",
            crs,
            "ESRI Shapefile")

        if self.dodaj:
            self.iface.addVectorLayer(
                os.path.join(self.kat, self.lyr.name()+"_planarize.shp"),
                self.lyr.name()+"_planarize.shp",
                "ogr")
