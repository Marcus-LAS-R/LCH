import math
from numpy import arctan2, rad2deg, pi
import os
from qgis.core import QgsProject, QgsGeometry, QgsField, QgsFeature, \
    QgsMessageLog, QgsVectorFileWriter, QgsVectorLayer, QgsPointXY, \
    QgsCoordinateReferenceSystem, Qgis
import processing
from PyQt5.QtCore import QMetaType
from PyQt5.QtGui import QColor
from collections import defaultdict


class recursivedefaultdict(defaultdict):
    def __init__(self):
        self.default_factory = type(self)


class GenerujKasowniki():
    '''creation of a virtual layer'''
    def __init__(self, iface):
        self.iface = iface
        self.wydz = QgsProject.instance().mapLayersByName("WYDZ_POL")
        if len(self.wydz) == 0:
            self.iface.messageBar().pushMessage('Error',
                                                "Brak warstwy WYDZ_POl w TOC!",
                                                Qgis.Critical)
            print("Nie znaleziono warstwy WYDZ_POL w otwartych warstwach!")
            return
        else:
            self.wydz = self.wydz[0]

        self.wydz_path = self.wydz.dataProvider().dataSourceUri().split("|")[0]
        self.proj_path = os.path.dirname(self.wydz_path)
        self.kattemp = os.path.join(self.proj_path, "temp")
        if not os.path.isdir(os.path.join(self.proj_path, "temp")):
            os.mkdir(os.path.join(self.proj_path, "temp"))

        self.interval = 15  # distance of point on border
        self.bBfRadius = -6
        self.sBfRadius = -2
        self.ramie = 4
        self.canLength = 7  # lenght of canceller under line

        self.setLayers()  # create memory layers

        self.arodPoints = recursivedefaultdict()  # dictionary with all points
        self.arodDist = recursivedefaultdict()  # dictionary wit closest dist
        self.generatePoints()
        self.genArodCancellers()
        self.genLineCancellers()
        self.save()

    def setLayers(self):
        # set point buffer layer and canceller layer
        self.layer = QgsVectorLayer("Point?crs=epsg:2180",
                                    "obwodkaPktKas",
                                    "memory")
        self.pr = self.layer.dataProvider()
        self.pr.addAttributes([QgsField("adr_les", QMetaType.Type.QString),
                               QgsField("IDpoly", QMetaType.Type.QString),
                               QgsField("X", QMetaType.Type.Double),
                               QgsField("Y", QMetaType.Type.Double),
                               ])
        self.layer.updateFields()

        self.layerCan = QgsVectorLayer("LineString?crs=epsg:2180&index=yes",
                                       "KAS",
                                       "memory")
        self.prCan = self.layerCan.dataProvider()
        self.prCan.addAttributes([QgsField("ID", QMetaType.Type.Int),
                                  QgsField("COMMUNITY", QMetaType.Type.QString),
                                  QgsField("MUNICIP", QMetaType.Type.QString)])
        self.layerCan.updateFields()

    def save(self):
        self.layerCan.commitChanges()
        crs = QgsCoordinateReferenceSystem("epsg:2180")
        QgsVectorFileWriter.writeAsVectorFormat(
            self.layerCan,
            os.path.join(self.proj_path, "KAS.shp"),
            "UTF-8",
            crs,
            "ESRI Shapefile")
        self.iface.messageBar().pushMessage(
            'Uwaga',
            u'Warstwa kasowników zapisana na dysku',
            Qgis.Success)
        print("Warstwa kasownikow zapisana!")
        self.kasLinie = QgsVectorLayer(
            os.path.join(self.proj_path, "KAS.shp"),
            "KAS",
            "ogr")
        s = self.kasLinie.renderer().symbol()
        s.setColor(QColor.fromRgb(0, 0, 0))
        QgsProject.instance().addMapLayer(self.kasLinie)

    def create_point(self, adrles, idpoly, x, y):
        # add point to the layer
        self.seg = QgsFeature()
        self.seg.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(x, y)))
        self.seg.setAttributes([str(adrles), str(idpoly), x, y])
        self.pr.addFeatures([self.seg])
        self.layer.updateExtents()

    @property
    def disp(self):
        # end of layer and display layer
        QgsProject.instance().addMapLayer(self.layer)
        QgsProject.instance().addMapLayer(self.layerCan)

    def mag(self, point):
        return math.sqrt(point.x()**2 + point.y()**2)

    def diff(self, point2, point1):
        return QgsPointXY(point2.x()-point1.x(), point2.y() - point1.y())

    def length(self, point1, point2):
        return math.sqrt(point1.sqrDist(point2))

    def dircos(self, point):
        cosa = point.x() / self.mag(point)
        cosb = point.y() / self.mag(point)
        return cosa, cosb

    def pairs(self, list):
        for i in range(1, len(list)):
            yield list[i-1], list[i]

    def calcDistance(self, point0, point1):
        return math.sqrt((point0[0]-point1[0])**2+(point0[1]-point1[1])**2)

    def calcAngle(self, tab):
        # # calculating angle of line in cartesian counterclockwise from N
        ang1 = arctan2(tab[0][1], tab[0][0])
        ang2 = arctan2(tab[1][1], tab[1][0])
        angle_org = rad2deg((ang1 - ang2) % (2 * pi))

        return 360 - angle_org

    def calculateCanceller(self, tab):
        if tab[0][0] <= tab[1][0]:
            tab_temp = tab[0]
            tab[0] = tab[1]
            tab[1] = tab_temp

        tabw = [[0, 10], [tab[1][0]-tab[0][0], tab[1][1]-tab[0][1]]]
        angle_org = self.calcAngle(tabw)

        if tab[0][1] <= tab[1][1]:
            # angle = angle_org + 90 + 30
            angle = angle_org + 90 - 30
            if angle > 360:
                angle -= 360

            angle2 = angle_org + 270 - 30
            if angle2 < 0:
                angle2 += 360

        else:
            angle = angle_org + 90 - 30
            if angle > 360:
                angle -= 360

            angle2 = (angle_org - 90) - 30
            if angle2 < 0:
                angle2 += 360

        angle = math.radians(angle)
        angle2 = math.radians(angle2)

        points = []
        points.append(QgsPointXY(tab[0][0]+self.ramie*math.cos(angle),
                                 tab[0][1]+self.ramie*math.sin(angle)))
        points.append(QgsPointXY(tab[0][0], tab[0][1]))
        points.append(QgsPointXY(tab[1][0], tab[1][1]))
        points.append(QgsPointXY(tab[1][0]+self.ramie*math.cos(angle2),
                                 tab[1][1]+self.ramie*math.sin(angle2)))

        return points

    def generatePoints(self):
        # generating points in multipart wydz_pol
        print("Generuje pkt w wydzieleniach")
        for f in self.wydz.getFeatures():
            geom = f.geometry()
            adr = f['ADR_LES']
            if geom.isMultipart() and adr[18:20].upper() != "LZ":
                for nrp, p in enumerate(geom.asMultiPolygon()):

                    # prepare structure of data for point dict
                    self.arodPoints[adr][nrp] = []

                    pBgeom = QgsGeometry.fromPolygonXY(p)
                    bf = pBgeom.buffer(self.bBfRadius, 5)
                    # generate centroids if buffer is empty
                    if not self.checkGenerationMethod(adr, nrp, bf):

                        # check if smaller buffer works
                        if not self.checkGenerationMethod(adr,
                                                          nrp,
                                                          pBgeom.buffer(
                                                              self.sBfRadius,
                                                              5)):
                            # if not, generate centroid
                            self.generateCentroid(adr,
                                                  nrp,
                                                  QgsGeometry.fromPolygonXY(p))

    def checkGenerationMethod(self, adr, nrp, bf):
        "check if buffer is multipolygon or polygon"
        if not bf.isMultipart():
            if len(bf.asPolygon()) > 0 and bf.asPolygon()[0] != []:
                self.generateBufferPoints(adr, nrp, bf)
                return True

        else:
            if len(bf.asMultiPolygon()) > 0 and \
                    bf.asMultiPolygon()[0] != []:
                for pol in bf.asMultiPolygon():
                    self.generateBufferPoints(
                        adr, nrp, QgsGeometry.fromPolygonXY(pol))
                return True
            else:
                return False

    def generateBufferPoints(self, adr, nrp, bf):
        # generate points from buffer polygon
        start_point = False
        for i, pii in enumerate(bf.asPolygon()):
            for j, pj in enumerate(pii):
                if not start_point:
                    start_point = QgsPointXY(
                        pj[0], pj[1]
                        )
                else:
                    line_start = start_point
                    self.arodPoints[adr][nrp].append([
                        line_start.x(),
                        line_start.y()])

                    self.create_point(
                        adr,
                        nrp,
                        line_start.x(),
                        line_start.y())
                    line_end = QgsPointXY(pj[0], pj[1])

                    pointm = self.diff(line_end, line_start)
                    # direction cosines of the segment
                    cosa, cosb = self.dircos(pointm)
                    # length of the segment
                    lg = self.length(line_end, line_start)

                    # generate and add points to the virtual layer
                    for ii in range(self.interval,
                                    int(round(lg, 0)),
                                    self.interval):
                        self.arodPoints[adr][nrp].append([
                                                line_start.x() + (ii*cosa),
                                                line_start.y() + (ii*cosb)])
                        self.create_point(
                            adr,
                            nrp,
                            line_start.x() + (ii*cosa),
                            line_start.y() + (ii*cosb),
                            )
                    start_point = line_end

    def generateCentroid(self, adr, nrp, geom):
        # generate centroid from geometry
        self.arodPoints[adr][nrp].append([
            geom.centroid().asPoint().x(),
            geom.centroid().asPoint().y()])

        self.create_point(
            adr,
            nrp,
            geom.centroid().asPoint().x(),
            geom.centroid().asPoint().y())

    def calculateArodDist(self):
        for wydz_key, wydz in self.arodPoints.items():
            for nrp in wydz.keys():  # numery subpoligonow
                restKeys = list(wydz.keys())
                restKeys.remove(nrp)
                min_odl = {x: [99999, 0, 0] for x in restKeys}
                for i in range(len(wydz[nrp])):
                    point0 = wydz[nrp][i]
                    for nrpi in restKeys:
                        tab = [[self.calcDistance(point0, x), point0, x]
                               for x in wydz[nrpi]]
                        tab = sorted(tab, key=lambda x: x[0])

                        if min_odl[nrpi][0] > tab[0][0]:
                            min_odl[nrpi] = tab[0]

                for k, tab in min_odl.items():
                    self.arodDist[wydz_key][nrp][k] = tab

    def chooseCancellers(self):
        for wydz_key, wydz in self.arodDist.items():
            l_con = [0]
            l_uncon = [x for x in wydz.keys() if x > 0]

            while len(l_uncon) > 0:
                closest = []
                for itc in l_con:
                    closest += [[itc, itu] + x
                                for itu, x in wydz[itc].items()
                                if itu != itc and itu not in l_con]
                closest = sorted(closest, key=lambda x: x[2])

                self.addArodCanceller(closest[0][3:], wydz_key)
                l_con += [closest[0][1]]
                l_uncon.remove(int(closest[0][1]))

    def addArodCanceller(self, tab, wydz_key):
        # draw canceller on layer
        fet = QgsFeature()
        fet.setGeometry(
            QgsGeometry.fromPolylineXY(self.calculateCanceller(tab)))
        fet.setAttributes([0, wydz_key[6:10], wydz_key[3:6]])
        self.prCan.addFeatures([fet])
        self.layerCan.updateExtents()

    def genArodCancellers(self):
        # generate cancellers in arodes
        print("Generuje kasowniki na podstawie punktow")
        self.calculateArodDist()
        self.chooseCancellers()

    def genLineCancellers(self):
        # generate cancellers for lines in wydz_pol
        print("Generuje kasowniki dla lini w wydzieleniach")

        print("\n------------------\n")
        print("Sciezka do pliku wydz_pol: \n" + self.wydz_path)
        print("\n------------------")
        print("Sciezka do katalogu projektu: \n" + self.proj_path)
        print("\n------------------")

        lin = QgsVectorLayer(os.path.join(self.proj_path, "LINIE.shp"),
                             "LINIE", "ogr")
        if not lin.isValid():
            QgsMessageLog.logMessage("Brak warstwy LINIE", "LCH")
            QgsMessageLog.logMessage(self.proj_path+"/LINIE.shp", "LCH")
            print("Brak warstwy LINIE")
            return

        processing.run("native:multiparttosingleparts",
                       {'INPUT':  self.wydz_path,
                        'OUTPUT': os.path.join(self.kattemp,
                                               "wydz_pol_singleparts.shp")
                        }
                       )

        processing.run("native:buffer",
                       {'INPUT': os.path.join(self.kattemp,
                                              "wydz_pol_singleparts.shp"),
                        'DISTANCE': -5.0,
                        'SEGMENTS': 1,
                        'DISSOLVE': False,
                        'OUTPUT': os.path.join(self.kattemp,
                                               "wydz_pol_buffer5.shp"),
                        }
                       )

        processing.run("native:intersection",
                       {'INPUT': os.path.join(self.proj_path, "LINIE.shp"),
                        'OVERLAY': os.path.join(self.kattemp,
                                                "wydz_pol_buffer5.shp"),
                        'INPUT_FIELDS': "",
                        'OVERLAY_FILEDS': "",
                        'OUTPUT': os.path.join(self.kattemp,
                                               "LINIE_CLIP.shp")
                        }
                       )

        processing.run("native:multiparttosingleparts",
                       {'INPUT': os.path.join(self.kattemp, "LINIE_CLIP.shp"),
                        'OUTPUT': os.path.join(self.kattemp,
                                               "LINIE_CLIP_SINGLEPARTS.shp")
                        }
                       )
        linie = QgsVectorLayer(
            os.path.join(self.kattemp, "LINIE_CLIP_SINGLEPARTS.shp"),
            "LINIE_clip", "ogr")

        iter = linie.getFeatures()
        for feat in iter:
            geom = feat.geometry()
            adr = feat['adr_les']
            ll = geom.length()
            distPrev = 0
            trig = True
            for l, line in enumerate(geom.asMultiPolyline()):
                for i, pt in enumerate(line):
                    if i == 0:
                        pt0 = pt
                    else:
                        dist = self.calcDistance(pt0, pt)
                        if distPrev + dist > ll / 2 and trig:
                            distAdd = (ll / 2) - distPrev
                            if pt0[0] <= pt[0]:
                                tab_temp = pt0
                                pt0 = pt
                                pt = tab_temp
                            pp, tab = self.calcPosOnLine([pt0, pt],
                                                         dist-distAdd)
                            self.addArodCanceller(tab, adr)
                            trig = False
                        distPrev += dist
                        pt0 = pt

    def calcPosOnLine(self, tab, ll):
        # calculating 2 perpendicular points to line
        tabw = [[0, 10], [tab[1][0]-tab[0][0], tab[1][1]-tab[0][1]]]
        angle_org = self.calcAngle(tabw)

        if angle_org > 360:
            angle_org -= 360

        # calculate coordinates of crossing two perpendicular lines
        pointm = self.diff(QgsPointXY(tab[1][0], tab[1][1]),
                           QgsPointXY(tab[0][0], tab[0][1]))
        cosa, cosb = self.dircos(pointm)

        ppoint = [tab[0][0]+(ll*cosa), tab[0][1]+(ll*cosb)]

        angle2 = angle_org
        if angle2 > 360:
            angle2 -= 360

        angle3 = angle_org + 180
        if angle3 < 0:
            angle3 += 360

        angle2r = math.radians(angle2)
        angle3r = math.radians(angle3)

        tab2 = [[ppoint[0]+self.canLength*math.cos(angle2r),
                ppoint[1]+self.canLength*math.sin(angle2r)],
                [ppoint[0]+self.canLength*math.cos(angle3r),
                ppoint[1]+self.canLength*math.sin(angle3r)]]

        return [angle_org, ppoint], tab2
