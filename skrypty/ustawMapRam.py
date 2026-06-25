from qgis.core import Qgis, QgsProject, QgsPointXY, QgsMessageLog, \
    QgsGeometry, QgsFeature
from PyQt5.QtWidgets import QInputDialog


def dodajWyniesienie(iface):
    # self.wydz = self.iface.activeLayer()
    wydz, mr = False, False

    for lyr in QgsProject.instance().mapLayers().values():
        if lyr.name() == "WYDZ_POL":
            wydz = lyr
        if lyr.name() == "MapRam":
            mr = lyr

    if wydz is False or mr is False:
        iface.messageBar().pushMessage(
            'Uwaga',
            u'W TOC nie ma warstw WYDZ_POL lub MapRam',
            level=Qgis.Warning)
        QgsMessageLog.logMessage("W TOC nie ma warsty WYDZ_POL lub MapRam",
                                 "LCH")
        return False

    if len(wydz.selectedFeatures()) == 0:
        iface.messageBar().pushMessage(
            'Uwaga',
            u'Brak zaznaczonych wydzieleń dla Wyniesienia',
            level=Qgis.Warning)
        QgsMessageLog.logMessage(
            "Prosze zaznaczyc wydzielenia dla wyniesienia", "LCH")
        return False

    try:
        ff = next(mr.getFeatures())
        skala = int(ff['SKALA'])
    except:  # nopep8
        skala = 5000

    xmin = []
    xmax = []
    ymin = []
    ymax = []
    gmi = []
    obr = []
    for feat in wydz.selectedFeatures():
        bb = feat.geometry().boundingBox()
        xmin.append(bb.xMinimum())
        xmax.append(bb.xMaximum())
        ymin.append(bb.yMinimum())
        ymax.append(bb.yMaximum())
        if feat['MUNICIP'] not in gmi:
            gmi.append(feat['MUNICIP'])
        if feat['COMMUNITY'] not in obr:
            obr.append(feat['COMMUNITY'])

    xmin = min(xmin) - (skala/100)
    xmax = max(xmax) + (skala/100)
    ymin = min(ymin) - (skala/100)
    ymax = max(ymax) + (skala/100)
    if len(gmi) > 1 or len(obr) > 1:
        iface.messageBar().pushMessage(
            'Uwaga',
            u'Stwierdzono wiele kodów gmin lub obrębów',
            level=Qgis.Warning)

    feat = QgsFeature()
    feat.setFields(mr.fields())
    geom = QgsGeometry().fromPolygonXY([[
                                    QgsPointXY(xmin, ymin),
                                    QgsPointXY(xmin, ymax),
                                    QgsPointXY(xmax, ymax),
                                    QgsPointXY(xmax, ymin),
    ]])

    feat.setGeometry(geom)
    feat['COMMUNITY'] = obr[0]
    feat['MUNICIP'] = gmi[0]
    feat['mapa_wys'] = (xmax-xmin) / (skala/100)  # cm
    feat['mapa_szer'] = (ymax-ymin) / (skala/100)  # cm
    feat['SKALA'] = 5000
    mr.startEditing()
    mr.addFeatures([feat])
    mr.commitChanges()


def dopiszXY(iface):
    mr = False
    for lyr in QgsProject.instance().mapLayers().values():
        if lyr.name() == "MapRam":
            mr = lyr

    if not mr:
        iface.messageBar().pushMessage(
            'Uwaga',
            u'W TOC nie ma warstwy MapRam',
            level=Qgis.Warning)
        QgsMessageLog.logMessage("W TOC nie ma warsty MapRam",
                                 "LCH")
        return False

    if len(mr.selectedFeatures()) == 0:
        iface.messageBar().pushMessage(
            'Uwaga',
            u'Brak zaznaczonych wyniesień w MapRam',
            level=Qgis.Warning)
        QgsMessageLog.logMessage("Prosze zaznaczyc wyniesienia",
                                 "LCH")
        return False

    i = 0
    fnm = mr.dataProvider().fieldNameMap()
    for feat in mr.selectedFeatures():
        i += 1
        bb = feat.geometry().boundingBox()
        mr.dataProvider().changeAttributeValues(
            {feat.id(): {fnm['xpocz']: bb.xMinimum(),
                         fnm['ypocz']: bb.yMaximum()
                         }
             }
        )

    iface.messageBar().pushMessage(
        'Uwaga',
        u'Dopisano koordynaty w wyniesieniach w liczbie: '+str(i),
        level=Qgis.Success)


def ustawSzer(iface, szer=''):
    # szerokość powinna być podana w cm mapy
    skala = 5000
    mr = False
    for lyr in QgsProject.instance().mapLayers().values():
        if lyr.name() == "MapRam":
            mr = lyr

    if not mr:
        iface.messageBar().pushMessage(
            'Uwaga',
            u'W TOC nie ma warstwy MapRam',
            level=Qgis.Warning)
        QgsMessageLog.logMessage("W TOC nie ma warsty MapRam",
                                 "LCH")
        return False

    if len(mr.selectedFeatures()) == 0:
        iface.messageBar().pushMessage(
            'Uwaga',
            'Brak zaznaczonych wyniesień w MapRam',
            level=Qgis.Warning)
        QgsMessageLog.logMessage("Prosze zaznaczyc wyniesienia", "LCH")
        return False

    szerSl = {
        '900': 89,
        'A3': 38.56,
    }

    feat = mr.selectedFeatures()[0]
    try:
        skala = feat['SKALA']
    except:  # nopep8
        pass

    ok = True
    if szer not in szerSl and szer != '':
        iface.messageBar().pushMessage(
            'Uwaga',
            'Źle podany kod szerokości',
            Qgis.Warning)
        QgsMessageLog.logMessage("Zle podany kod szerokosci", "LCH")
        return False
    elif szer == '':
        odl, ok = QInputDialog.getInt(
            iface.mainWindow(),
            'Zdefiniuj rozmiar',
            'Podaj szerokość w cm:',
            value=60
        )
    elif szer in szerSl:
        odl = szerSl[szer]
    else:
        iface.messageBar().pushMessage(
            'Uwaga',
            'Nierozpoznana szerokość - koniec!',
            Qgis.Warning)
        return False

    if ok:
        pass
    else:
        iface.messageBar().pushMessage(
            'Uwaga',
            'Użytkownik zrezygnował z poszerzania',
            Qgis.Warning)
        return False

    szer_m = odl * (skala/100)

    i = 0
    fnm = mr.dataProvider().fieldNameMap()
    mr.startEditing()
    for feat in mr.selectedFeatures():
        i += 1
        bb = feat.geometry().boundingBox()
        xmin = bb.xMinimum()
        # xmax = bb.xMaximum()
        ymin = bb.yMinimum()
        ymax = bb.yMaximum()
        geom_new = QgsGeometry().fromPolygonXY([[
                                    QgsPointXY(xmin, ymin),
                                    QgsPointXY(xmin, ymax),
                                    QgsPointXY(xmin+szer_m, ymax),
                                    QgsPointXY(xmin+szer_m, ymin),
                                    ]])
        mr.changeGeometry(feat.id(), geom_new)

        mr.dataProvider().changeAttributeValues({
            feat.id(): {
                fnm['mapa_szer']: odl,
                fnm['mapa_wys']: (ymax-ymin)/(skala/100),
            }
        }
        )

    mr.commitChanges()
    iface.messageBar().pushMessage('Uwaga',
                                   u'Ustawiono szerokość na '
                                   + str(szer_m) +
                                   ' cm w wyniesieniach w liczbie: '
                                   + str(i),
                                   level=Qgis.Success)


def ustawWys(iface, wys=''):
    skala = 5000
    mr = False
    for lyr in QgsProject.instance().mapLayers().values():
        if lyr.name() == "MapRam":
            mr = lyr

    if not mr:
        iface.messageBar().pushMessage(
            'Uwaga',
            u'W TOC nie ma warstwy MapRam',
            level=Qgis.Warning)
        QgsMessageLog.logMessage("W TOC nie ma warsty MapRam",
                                 "LCH")
        return False

    if len(mr.selectedFeatures()) == 0:
        iface.messageBar().pushMessage(
            'Uwaga',
            u'Brak zaznaczonych wyniesień w MapRam',
            level=Qgis.Warning)
        QgsMessageLog.logMessage("Prosze zaznaczyc wyniesienia",
                                 "LCH")
        return False

    feat = mr.selectedFeatures()[0]
    try:
        skala = feat['SKALA']
    except:  # nopep8
        pass

    wysSl = {
        '900': 81,
        'A3': 19.813,
    }

    ok = True
    if wys not in wysSl and wys != '':
        iface.messageBar().pushMessage(
            'Uwaga',
            'Źle podany kod wysokości',
            Qgis.Warning)
        QgsMessageLog.logMessage("Zle podany kod wysokosci", "LCH")
        return False
    elif wys == '':
        odl, ok = QInputDialog.getInt(
            iface.mainWindow(),
            'Zdefiniuj rozmiar',
            'Podaj wysokość w cm:',
            value=60
        )
    elif wys in wysSl:
        odl = wysSl[wys]
    else:
        iface.messageBar().pushMessage(
            'Uwaga',
            'Nierozpoznana wysokość - koniec!',
            Qgis.Warning)
        return False

    if ok:
        pass
    else:
        iface.messageBar().pushMessage(
            'Uwaga',
            'Użytkownik zrezygnował z poszerzania',
            Qgis.Warning)
        return False

    wys_m = odl * (skala/100)
    i = 0
    fnm = mr.dataProvider().fieldNameMap()
    mr.startEditing()
    for feat in mr.selectedFeatures():
        i += 1
        bb = feat.geometry().boundingBox()
        xmin = bb.xMinimum()
        xmax = bb.xMaximum()
        ymin = bb.yMinimum()
        geom_new = QgsGeometry().fromPolygonXY([[
                                    QgsPointXY(xmin, ymin),
                                    QgsPointXY(xmin, ymin+wys_m),
                                    QgsPointXY(xmax, ymin+wys_m),
                                    QgsPointXY(xmax, ymin),
                                    ]])
        mr.changeGeometry(feat.id(), geom_new)

        mr.dataProvider().changeAttributeValues({
            feat.id(): {
                fnm['mapa_szer']: (xmax-xmin)/(skala/100),
                fnm['mapa_wys']: odl,
            }
        }
        )

    mr.commitChanges()
    iface.messageBar().pushMessage(
        'Uwaga',
        u'Ustawiono wysokość na ' +
        str(wys) +
        u' cm w wyniesieniach w liczbie: '
        + str(i),
        level=Qgis.Success)
