import os
import math
from qgis.core import QgsPointXY, QgsFeature, QgsGeometry, QgsVectorLayer,\
    QgsVectorFileWriter, QgsProject, QgsWkbTypes


def wygeneruj_powierzchnie(iface):
    lyr = iface.activeLayer()

    if 'pow_krzew' not in lyr.dataProvider().fieldNameMap().keys():
        iface.messageBar().pushCritical(
            'Błąd',
            'Brak kolumny "pow_krzew" w atrybutach'
        )
        return

    if lyr.geometryType() not in [QgsWkbTypes.Point,
                                  QgsWkbTypes.PointGeometry,
                                  QgsWkbTypes.MultiPoint]:
        iface.messageBar().pushCritical(
            'Błąd', 'Warstwa z drzewami musi być punktowa'
        )
        return

    fts = []
    for feat in lyr.getFeatures():
        val = str(feat['pow_krzew'])
        if val.isdigit():
            fts.append(feat)

    feats = []
    for pnt in fts:
        try:
            r = math.sqrt(int(pnt['pow_krzew'])/math.pi)
        except Exception:
            continue

        k = Krzew([pnt.geometry().asPoint().x(), pnt.geometry().asPoint().y()],
                  r)
        k.oblicz_krzew()
        linia = [QgsPointXY(x[0], x[1]) for x in k.obwod]
        fe = QgsFeature()
        fe.setGeometry(QgsGeometry.fromPolygonXY([linia]))
        fe.setFields(lyr.dataProvider().fields())
        fe.setAttributes(pnt.attributes())
        feats.append(fe)

    vector = QgsVectorLayer('Polygon?crs=epsg:2180&index=yes',
                            'drzewa_aft',
                            'memory')
    vector.startEditing()
    vector.dataProvider().addAttributes(lyr.dataProvider().fields())
    vector.updateFields()
    vector.addFeatures(feats)
    vector.commitChanges()

    kat = os.path.dirname(lyr.dataProvider().dataSourceUri().split("|")[0])
    QgsVectorFileWriter.writeAsVectorFormat(
       vector,
       os.path.join(kat, "drzewa_opis_aft.shp"),
       "UTF-8",
       lyr.sourceCrs(),
       "ESRI Shapefile")

    QgsProject.instance().addMapLayer(
        QgsVectorLayer(
            os.path.join(kat, "drzewa_opis_aft.shp"), "drzewa_opis_aft", "ogr")
    )


class Krzew:
    def __init__(self, pkt, r):
        self.pkt = pkt  # [x, y]
        self.r = r  # promien krzaka

        self.kat = 60  # kat na jakim bedzie generowany jeden platek
        self.obwod = []  # tablica z calym obwodem krzewu

    def oblicz_kat(self):
        """Sprawdza ile platkow moze sie zmiescic przy konkretnym r"""
        if self.r <= 4:
            self.kat = 60
        elif 4 < self.r < 6:
            self.kat = 45
        else:
            self.kat = 30

    def oblicz_krzew(self):
        """Oblicza cały obwód krzewu"""
        obw = 0
        self.oblicz_kat()
        self.obwod = []
        while obw != 360:
            self.obwod += self.oblicz_platek(obw)
            obw += self.kat

    def oblicz_platek(self, offset=0):
        """Generuje płatek dla podanego offsetu konta od azymutu
        zwraca liste z wspolrzednymi 10 pkt
        """

        if self.r > 3:
            ksztalt = [-0.5, -0.2, 0, 0.2, 0.5, ]
        else:
            ksztalt = [-0.2, -0.1, 0, 0.1, 0.2, ]

        kat = [
            0.0001,
            self.kat/25,
            self.kat/19,
            self.kat/12,
            self.kat/4,
        ]

        platek = []
        # prawa strona platka
        for ii, ki in enumerate(ksztalt):
            if self.r + ki < 0:
                ki = 0.1

            # pkt = self.oblicz_wsp(offset+ii*(self.kat/9), self.r+ki)
            pkt = self.oblicz_wsp(offset+kat[ii], self.r+ki)
            platek.append(pkt)

        # lewa strona platka
        for ii, ki in enumerate(sorted(ksztalt, reverse=True)):
            if self.r + ki < 0:
                ki = 0.1

            pkt = self.oblicz_wsp(
                # offset+self.kat-(5-ii)*(self.kat/9), self.r+ki
                offset+self.kat-kat[4-ii], self.r+ki
            )
            platek.append(pkt)

        return platek

    def oblicz_wsp(self, kat, r):
        """zwraca liste wspolrzednych [x, y]
        """
        rad = (kat*math.pi) / 180
        return [
            self.pkt[0] + r * math.cos(rad), self.pkt[1] + r * math.sin(rad)
        ]


if __name__ == '__console__':
    # kr = Krzew(pkt, 4.1)
    # kr.oblicz_krzew()
    # linia = [QgsPointXY(x[0], x[1]) for x in kr.obwod]
    # fe.setGeometry(QgsGeometry.fromPolygonXY([linia]))
    # iface.activeLayer().addFeatures([fe])
    wygeneruj_powierzchnie(iface)  # noqa