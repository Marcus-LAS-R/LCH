import os
from qgis.core import QgsPointXY, Qgis, QgsProject, QgsMessageLog, QgsField, \
    QgsVectorLayer, QgsFeature, QgsGeometry, QgsVectorFileWriter, \
    QgsExpression, QgsCoordinateReferenceSystem, QgsFeatureRequest
from collections import defaultdict
from PyQt5.QtCore import QVariant
from PyQt5.QtWidgets import QDialog, QMessageBox

from .ui.ui_mapram import Ui_Dialog


class recursivedefaultdict(defaultdict):
    def __init__(self):
        self.default_factory = type(self)


class GenerujMapRam():
    def __init__(self, iface):
        self.iface = iface

        # zdefiniowana odgornie odleglosc miedzy wydzieleniami ktora wplywa na
        # tworzenie nowego klastra
        self.minOdl = 600
        self.skala = 5000
        self.typ = 'pogl'

        self.dd = PobierzDane()
        self.dd.exec_()
        if self.dd.ok:
            self.minOdl = int(self.dd.lineEdit_minOdl.text())
            self.skala = int(self.dd.lineEdit_skala.text())
            if self.dd.radioButton_inna.isChecked():
                self.typ = 'inna'

        # jezeli uzytkownik zrezygnował z generowania
        if not self.dd.go_flag:
            return

        # lista [[gm, obr], ...] ktorych nie udalo sie ustawic automatycznie
        self.doSpr = []

        # triger - jezeli jest wiecej niz 4 klastry nie bedzie rysowania
        self.STOP = False

    def wykonaj(self):
        # wybierz warstwe w zaleznosci od mapy jaka wybrał użytkownik
        self.wydz = False
        for lyr in QgsProject.instance().mapLayers().values():
            if self.typ == 'pogl':
                if lyr.name() == "WYDZ_POL":
                    self.wydz = lyr
            else:
                if lyr.name() == "ODDZ":
                    self.wydz = lyr

        if self.wydz is False:
            self.iface.messageBar().pushMessage(
                'Error', "Brak wymaganej warstwy w TOC!",
                level=Qgis.Critical)
            return

        self.wydz.dataProvider().setEncoding(u'UTF-8')
        self.wydz_path = self.wydz.dataProvider().dataSourceUri().split("|")[0]
        self.kat = os.path.dirname(self.wydz_path)

        QgsMessageLog.logMessage("--------------------", "LCH", Qgis.Info)
        QgsMessageLog.logMessage("Rozpoczynam tworzenie MapRama", "LCH",
                                 Qgis.Info)

        if self.typ == 'pogl':
            self.klastruj()
            if not self.ustawKlastry():
                return
        else:
            self.ustaw_duza_mape()
        self.rysujKlastry()

    def klastruj(self):
        """ Metoda tworzy slownik z klastrami z wydzielen pogrupowanych dla
        gmin i obrebow.
        -> sl[gm][obr] = [klaster1, klaster2, ...]
        """

        pola = [x for x in [f.name() for f in self.wydz.fields().toList()]
                if x in ['MUNICIP', 'COMMUNITY', 'ADR_LES', ]]
        if len(pola) != 3:
            self.iface.messageBar().pushMessage(
                'Error',
                "Brak niezbędnych pól w warstwie - "+",".join(
                    [x for x in ['MUNICIP', 'COMMUNITY', 'ADR_LES', ]
                     if x not in pola]),
                level=Qgis.Critical)
            return False

        # slownik trzymajacy boundingBoxy dla kazdego wydzielenia w postaci:
        # sl[gmi][obr][adrLes] = [xmin, ymin, xmax, ymax]
        self.slWy = recursivedefaultdict()
        for feat in self.wydz.getFeatures():
            bound = feat.geometry().boundingBox()

            xmin = bound.xMinimum()
            xmax = bound.xMaximum()
            ymin = bound.yMinimum()
            ymax = bound.yMaximum()
            self.slWy[feat['MUNICIP']][feat['COMMUNITY']][feat['ADR_LES']] = \
                [xmin, ymin, xmax, ymax]

        # slownik z klastrami dla kazdego obrebu
        # sl[gmi][obr] = [klaster, klaster, ...]
        self.slKl = recursivedefaultdict()

        # stworz klastry w kazdym obrebie,
        for gmi in self.slWy.keys():
            for obr in self.slWy[gmi].keys():
                # robocza lista wszystkich wydziele w obrebie
                adrLesRob = []
                wRob = []

                for key, v in self.slWy[gmi][obr].items():
                    wRob.append(v)
                    adrLesRob.append(key)

                klastry = []
                i = 0
                kl = False
                dopis = False

                while len(wRob) > 0:
                    if i == len(wRob):
                        i = 0

                    if i == 0 and not dopis:
                        if isinstance(kl, Klaster):
                            klastry.append(kl)
                        kl = Klaster(self.minOdl)
                        kl.skala = self.skala
                        kl.dodajWydz(adrLesRob[0], wRob[0])
                        wRob.pop(0)
                        adrLesRob.pop(0)

                    if len(wRob) == 0:
                        break

                    dopis = False

                    # wydzielenie w zasiegu klastra
                    if kl.kwalifikuj(wRob[i]):
                        kl.dodajWydz(adrLesRob[i], wRob[i])
                        wRob.pop(i)
                        adrLesRob.pop(i)
                        dopis = True
                        i = -1

                    i += 1
                klastry.append(kl)
                # sortuj odo najwiekszego do najmniejszego
                klastry = sorted(klastry,
                                 reverse=True,
                                 key=lambda x: x.zwrocPow())

                self.slKl[gmi][obr] = klastry

    def ustaw_duza_mape(self):
        '''metoda ustawia duza mape w postaci jednego klastra i oblicza jej
        zasieg w zaleznosci od podanej skali'''
        pola = [x for x in [f.name() for f in self.wydz.fields().toList()]
                if x in ['MUNICIP', 'COMMUNITY', ]]
        if len(pola) != 2:
            self.iface.messageBar().pushMessage(
                'Error',
                "Brak niezbędnych pól w warstwie - "+",".join(
                    [x for x in ['MUNICIP', 'COMMUNITY', ]
                     if x not in pola]),
                level=Qgis.Critical)
            return False

        # znajdz zasieg warstwy oddzialow
        bound = self.wydz.extent()
        xmin = bound.xMinimum()
        xmax = bound.xMaximum()
        ymin = bound.yMinimum()
        ymax = bound.yMaximum()

        feat = next(self.wydz.getFeatures())
        gm = feat['MUNICIP']
        self.slKl = recursivedefaultdict()
        kl = Klaster(self.minOdl)
        kl.skala = self.skala
        kl.dodajWydz('adr', [xmin, ymin, xmax, ymax])
        if not kl.ustawPlot():
            self.doSpr.append(
                [gm, 'all', "Wiekszy niz papier",
                 QgsGeometry.fromPolygonXY([kl.zwrocPoly()])])
        self.slKl[gm]['all'] = [kl, ]

    def ustawKlastry(self):
        """Metoda dopasowuje klastry do rozmiaru papieru, ustawia wydzielenia
        tak aby nie kolidowaly z wydzieleniami na glownej mapie
        """
        klList = []
        for gmi in self.slKl.keys():
            for obr, kl in self.slKl[gmi].items():
                klList.append(len(kl))

        if max(klList) > 8:
            QgsMessageLog.logMessage(
                "Wykryto wiecej niz 8 kalstrow, przerywam",
                "LCH")
            self.STOP = True
            return False

        for gmi in self.slKl.keys():
            for obr in self.slKl[gmi].keys():
                kl = self.slKl[gmi][obr]

                # Jezeli w obrebie jest tylko jeden klaster
                print("Opracowuje obr: "+obr+" Klastrow: 1")
                if len(kl) == 1:
                    # dopasuj do papieru
                    if not kl[0].ustawPlot():
                        # klaster nie miesci sie na zadnym papierze
                        self.doSpr.append(
                            [gmi, obr, "Wiekszy niz papier",
                             QgsGeometry.fromPolygonXY([kl[0].zwrocPoly()])])

                # W obrebie jest wiecej kalstrow
                else:
                    self.dopKlastry(kl)
        return True

    def rysujKlastry(self):  # noqa
        nazwa = "MapRam"
        if self.STOP:
            nazwa = "KLASTRY"
        self.ramkiKl = QgsVectorLayer("Polygon?crs=epsg:2180&index=yes",
                                      nazwa,
                                      "memory")
        self.ramkiKlPr = self.ramkiKl.dataProvider()
        self.ramkiKl.startEditing()
        self.ramkiKlPr.addAttributes([
            QgsField("MUNICIP", QVariant.String, len=3),
            QgsField("COMMUNITY", QVariant.String, len=4),
            QgsField("RAMKA", QVariant.String, len=2),
            QgsField("xpocz", QVariant.Double, 'double', 10, 2),
            QgsField("ypocz", QVariant.Double, 'double', 10, 2),
            QgsField("mapa_szer", QVariant.Double, 'double', 10, 2),
            QgsField("mapa_wys", QVariant.Double, 'double', 10, 2),
            QgsField("skala", QVariant.Int),
            ])
        self.ramkiKl.updateFields()

        slWyn = {0: "M", 1: "A", 2: "B", 3: "C", 4: "D",
                 5: "E", 6: "F", 7: "G", 8: "H"}
        etykFeat = []
        QgsMessageLog.logMessage("Wygenerowano:", "LCH", Qgis.Info)
        for gmi in self.slKl.keys():
            for obr, kl in self.slKl[gmi].items():
                QgsMessageLog.logMessage(gmi+", "+obr+" - " +
                                         str(len(kl))+" klastry",
                                         "LCH",
                                         Qgis.Info)
                for i, k in enumerate(kl):
                    try:
                        feat = QgsFeature()
                        pktPoly = k.zwrocPoly()
                        geom = QgsGeometry.fromPolygonXY([pktPoly])
                        feat.setGeometry(geom)
                        feat.setFields(self.ramkiKl.fields())
                        feat['MUNICIP'] = gmi
                        feat['COMMUNITY'] = obr
                        feat['xpocz'] = k.xpocz
                        feat['ypocz'] = k.ypocz
                        feat['mapa_szer'] = (k.xmax-k.xmin) / (self.skala/100)
                        feat['mapa_wys'] = (k.ymax-k.ymin) / (self.skala/100)
                        feat['skala'] = self.skala
                        if self.typ == 'pogl' and feat['mapa_wys'] < 20 and \
                                feat['mapa_szer'] < 38.6 and i == 0:
                            feat['RAMKA'] = 'Mr'
                        else:
                            feat['RAMKA'] = slWyn[i]
                        etykFeat.append(feat)

                        # sprawdz czy jezeli rozmiar jest przekroczony, obreb
                        # jest dodany do uwag do sprawdzenia
                        if self.typ == 'pogl' and feat['mapa_wys'] > 81 and \
                                feat['mapa_szer'] > 89:
                            wpisane = [x[0]+x[1] for x in self.doSpr]
                            if len([y for y in wpisane if gmi+obr == y]) == 0:
                                self.doSpr.append(
                                    [gmi, obr,  "Wiekszy niz papier", geom]
                                )
                    except:  # noqa
                        QgsMessageLog.logMessage(
                            "--> Nie dodano ramki klastra w: "+gmi+", "+obr,
                            "LCH"
                        )

        if len(self.doSpr) > 0:
            self.iface.messageBar().pushMessage(
                'Uwaga',
                u'Sprawdź log - wystąpiły problemy!',
                level=Qgis.Warning)
            QgsMessageLog.logMessage(
                "Obreby wymagajace uwagi uzytkownika: ",
                "LCH"
            )
            for x in self.doSpr:
                QgsMessageLog.logMessage(
                    x[0]+" - "+x[1]+" - "+x[2],
                    "LCH"
                )

            self._utworzWarstweProblemow()

        self.ramkiKlPr.addFeatures(etykFeat)
        self.ramkiKl.commitChanges()

        crs = QgsCoordinateReferenceSystem("epsg:2180")
        QgsVectorFileWriter.writeAsVectorFormat(
            self.ramkiKl,
            os.path.join(self.kat, "MapRam.shp"),
            "UTF-8",
            crs,
            "ESRI Shapefile")

        if len(self.doSpr) == 0:
            self.iface.messageBar().pushMessage(
                    'OK',
                    u'Warstwa MapRam zapisana na dysku',
                    level=Qgis.Success)

        self.out = QgsVectorLayer(os.path.join(self.kat, "MapRam.shp"),
                                  "MapRam",
                                  "ogr")

        QgsProject.instance().addMapLayer(self.out)
        QgsMessageLog.logMessage("--------------------", "LCH", Qgis.Info)

    def _utworzWarstweProblemow(self):
        """Tworzy warstwe memory z geometriami klastrow, ktore spowodowaly
        wpisy w self.doSpr (nie zmiescily sie na papierze albo nie udalo
        sie ich umiejscowic jako wyniesienie), i dodaje ja do TOC."""
        warstwa = QgsVectorLayer("Polygon?crs=epsg:2180&index=yes",
                                 "PROBLEMY_MAPRAM", "memory")
        pr = warstwa.dataProvider()
        warstwa.startEditing()
        pr.addAttributes([
            QgsField("MUNICIP", QVariant.String, len=3),
            QgsField("COMMUNITY", QVariant.String, len=4),
            QgsField("POWOD", QVariant.String, len=100),
        ])
        warstwa.updateFields()

        feats = []
        for gmi, obr, powod, geom in self.doSpr:
            feat = QgsFeature(warstwa.fields())
            feat.setGeometry(geom)
            feat['MUNICIP'] = gmi
            feat['COMMUNITY'] = obr
            feat['POWOD'] = powod
            feats.append(feat)
        pr.addFeatures(feats)
        warstwa.commitChanges()
        QgsProject.instance().addMapLayer(warstwa)

    def dopKlastry(self, tab): # noqa
        """
        Metoda umiejscawia klastry na najwiekszym, tak aby nie nachodzily na
        wydzielenia i inne klastry
        """
        # stworz slownik wierzcholkow w wydzieleniach z analizowanego obrebu
        # slWierz[y][x] = 1
        self.slWierz = recursivedefaultdict()
        print("Opracowuje obr: "+tab[0].obr+" Klastrow: "+str(len(tab)))
        exp = QgsExpression(
                            "\"MUNICIP\"= '" + tab[0].gmi +
                            "' AND \"COMMUNITY\"= '" + tab[0].obr + "'"
                            )
        for feat in self.wydz.getFeatures(QgsFeatureRequest(exp)):
            if feat.geometry().isMultipart():
                multi = feat.geometry().asMultiPolygon()
                for poly in multi:
                    for ring in poly:
                        for coord in ring:
                            self.slWierz[coord[1]][coord[0]] = 1
            else:
                poly = feat.geometry().asPolygon()
                for ring in poly:
                    for coord in ring:
                        self.slWierz[coord[1]][coord[0]] = 1

        # rzeczywisty zasieg wydzielen w glownym klastrze, przed
        # dopasowaniem do papieru - potrzebny pozniej do wysrodkowania
        # calej grupy (glowny klaster + wyniesienia)
        zak_tresc = tab[0].zwrocZakres()

        # ustaw najwiekszy klaster
        if not tab[0].ustawPlot("l", 'd'):
            self.doSpr.append(
                [tab[0].gmi, tab[0].obr, "Wiekszy niz papier",
                 QgsGeometry.fromPolygonXY([tab[0].zwrocPoly()])])
            return False

        for i in range(1, len(tab)):
            # poszerz odleglosc wydzielenia od ramki o 5cm z kazdej strony
            tab[i].poszerzRamke(150)
            wym = tab[0].zwrocWymiary()

            # najpierw poszerzamy na szerokosc
            xmax = 4450
            if wym[1] < 4050:
                xmax = 10050

            wx = wym[0]
            znalezione = False
            trig = 0

            while wx < xmax:
                if trig == 0:
                    znalezione = self.iterujKlaster(i, tab)
                else:
                    wx = self.poszerzMapRamP(i, tab, xmax)
                    znalezione = self.iterujKlaster(i, tab)

                if znalezione or trig > 100:
                    break

                trig += 1
                if trig % 100 == 0 and trig > 0:
                    print("100, serio?", wx, xmax)

            # potem na wysokosc
            if not znalezione:
                print("poszerzaj na wysokosc")
                st = 0
                while not znalezione and st < 201:
                    self.poszerzMapRamG(i, tab, xmax)
                    znalezione = self.iterujKlaster(i, tab)
                    st += 1
                    if st % 100 == 0:
                        print("100 na wysokosc, serio?", st)

            if not znalezione:
                self.doSpr.append(
                    [tab[i].gmi, tab[i].obr,
                     "Brak mozliwosci umiejscowienia wyn.",
                     QgsGeometry.fromPolygonXY([tab[i].zwrocPoly()])])

        self._wysrodkujGrupe(tab, zak_tresc)

    def _wysrodkujGrupe(self, tab, zak_tresc):
        """Jezeli po rozmieszczeniu wyniesien calosc nadal miesci sie na
        A3 (czyli ramka glownego klastra nie zostala poszerzona), przesuwa
        cala kompozycje (glowny klaster + wyniesienia) tak, aby byla
        wysrodkowana na stronie - zamiast zostawac przyklejona do lewego
        dolnego rogu (efekt wyrownania "l","d" uzywanego do umiejscawiania
        wyniesien). Przesuwana jest tylko ramka glownego klastra - pozycje
        wyniesien (xpocz/ypocz) sa liczone wzgledem niej, wiec podazaja za
        przesunieciem automatycznie, a ich wlasciwa geometria (rzeczywiste
        polozenie wydzielen) pozostaje bez zmian."""
        glowny = tab[0]
        if not glowny.ustawiony:
            return

        wym = glowny.zwrocWymiary()
        mapa_szer = wym[0] / (self.skala / 100)
        mapa_wys = wym[1] / (self.skala / 100)
        if not (mapa_wys < 20 and mapa_szer < 38.6):
            # strona zostala poszerzona ponad A3 przy dostawianiu wyniesien
            return

        comb_xmin, comb_ymin, comb_xmax, comb_ymax = zak_tresc
        for k in tab[1:]:
            if k.xpocz == 0 and k.ypocz == 0:
                continue  # nie udalo sie umiejscowic
            wymi = k.zwrocWymiary()
            comb_xmin = min(comb_xmin, k.xpocz)
            comb_xmax = max(comb_xmax, k.xpocz + wymi[0])
            comb_ymin = min(comb_ymin, k.ypocz - wymi[1])
            comb_ymax = max(comb_ymax, k.ypocz)

        slack_x = (glowny.xmax - glowny.xmin) - (comb_xmax - comb_xmin)
        slack_y = (glowny.ymax - glowny.ymin) - (comb_ymax - comb_ymin)

        delta_x = (comb_xmin - slack_x / 2) - glowny.xmin
        delta_y = (comb_ymax + slack_y / 2) - glowny.ymax

        glowny.xmin += delta_x
        glowny.xmax += delta_x
        glowny.ymin += delta_y
        glowny.ymax += delta_y

    def poszerzMapRamG(self, nr, tab, xmax):
        zak0 = tab[0].zwrocZakres()
        tab[0].poszerzRamkeG(100)
        if nr > 1:
            for i in range(1, nr):
                # jezeli poprzedni klaster jest blisko krawedzi to tez go
                # przesuwamy
                if zak0[3] - tab[i].ypocz < 100:
                    tab[i].ypocz += 100
        return

    def poszerzMapRamP(self, nr, tab, xmax):
        zak0 = tab[0].zwrocZakres()
        if zak0[2] + 100 < xmax:
            tab[0].poszerzRamkeP(100)
            # przesun wszystkie ustawione wyniesienia na prawo
            if nr > 1:
                for i in range(1, nr):
                    # jezeli poprzedni klaster jest blisko krawedzi to tez go
                    # przesuwamy
                    if zak0[2] - tab[i].xpocz + tab[i].zwrocWymiary()[0] < 100:
                        tab[i].xpocz += 100
            return zak0[2] + 100
        # wyrownaj do pelnego zakresu papieru
        elif zak0[2] + 100 < xmax + 99:
            przes = xmax - zak0[2]
            tab[0].poszerzRamkeP(przes)
            # przesun wszystkie ustawione wyniesienia na prawo
            if nr > 1:
                for i in range(1, nr):
                    if zak0[2] - tab[i].xpocz + tab[i].zwrocWymiary()[0] < 100:
                        tab[i].xpocz += przes
            return zak0[2] + przes
        return 9999999

    def iterujKlaster(self, i, tab):
        if self.przesuwajKlasterG(tab, i):
            return True
        if self.przesuwajKlasterP(tab, i):
            return True
        if self.przesuwajKlasterD(tab, i):
            return True
        if self.przesuwajKlasterL(tab, i):
            return True
        return False

    def przesuwajKlasterG(self, tab, nr):
        """
        Metoda przesuwa Klaster z listy o podanym indeksie po granicy 0 Klastra
        az znajdzie polozenie w ktorym nie przecina sie zadnym wydzieleniem ani
        innym Klastrem
        """

        zak0 = tab[0].zwrocZakres()
        wymi = tab[nr].zwrocWymiary()

        # sprawdzamy gorna krawedz glownego klastra
        xdelta = zak0[0] + 25
        ydelta = zak0[3] - 25
        y = [yy for yy in self.slWierz.keys()
             if yy < ydelta and yy > ydelta-wymi[1]]
        x = []

        # dodaj pkt z wydzielen
        for yy in y:
            x += self.slWierz[yy].keys()

        while xdelta + wymi[0] < zak0[2]:
            if len([val for val in x
                    if val > xdelta and val < xdelta+wymi[0]]) == 0:

                if not self.czyKolidujezKlastrami(xdelta, ydelta, nr, tab):
                    tab[nr].ustawWspl(xdelta, ydelta)
                    return True
            xdelta += 50
        return False

    def przesuwajKlasterP(self, tab, nr):
        zak0 = tab[0].zwrocZakres()
        wymi = tab[nr].zwrocWymiary()
        # sprawdzamy prawa krawedz
        xdelta = zak0[2] - wymi[0] - 25
        ydelta = zak0[3] - 25

        y = []
        for yi in self.slWierz.keys():
            if len([xi for xi in self.slWierz[yi].keys()
                    if xi > xdelta and xi < zak0[2] - 25]) > 0:
                y.append(yi)

        while ydelta - wymi[1] > zak0[1]:
            if len([val for val in y
                    if val > ydelta-wymi[1] and val < ydelta]) == 0:

                if not self.czyKolidujezKlastrami(xdelta, ydelta, nr, tab):
                    tab[nr].ustawWspl(xdelta, ydelta)
                    return True
            ydelta -= 50
        return False

    def przesuwajKlasterD(self, tab, nr):
        zak0 = tab[0].zwrocZakres()
        wymi = tab[nr].zwrocWymiary()
        # sprawdzamy dolna krawedz glownego klastra
        xdelta = zak0[2] - wymi[0] - 25
        ydelta = zak0[1] + wymi[1] + 25

        y = [yy for yy in self.slWierz.keys()
             if yy < ydelta and yy > ydelta-wymi[1]]
        x = []

        # dodaj pkt z wydzielen
        for yy in y:
            x += self.slWierz[yy].keys()

        while xdelta + wymi[0] < zak0[2]:
            if len([val for val in x
                    if val > xdelta and val < xdelta + wymi[0]]) == 0:

                if not self.czyKolidujezKlastrami(xdelta, ydelta, nr, tab):
                    tab[nr].ustawWspl(xdelta, ydelta)
                    return True
            xdelta += 50
        return False

    def przesuwajKlasterL(self, tab, nr):
        zak0 = tab[0].zwrocZakres()
        wymi = tab[nr].zwrocWymiary()
        # sprawdzamy lewa krawedz
        xdelta = zak0[0] + 25
        ydelta = zak0[3] - 25

        y = []
        for yi in self.slWierz.keys():
            if len([xi for xi in self.slWierz[yi].keys()
                    if xi > xdelta and xi < zak0[2] - 25]) > 0:
                y.append(yi)

        while ydelta - wymi[1] > zak0[1]:
            if len([val for val in y
                    if val > ydelta-wymi[1] and val < ydelta]) == 0:

                if not self.czyKolidujezKlastrami(xdelta, ydelta, nr, tab):
                    tab[nr].ustawWspl(xdelta, ydelta)
                    return True
            ydelta -= 50
        return False

    def czyKolidujezKlastrami(self, xdelta, ydelta, nr, tab):
        """
        Metoda sprawdza czy analizowany kalster nie naklada sie na poprzednio
        ustawione
        """
        # dodaj pkt z nachodzacych wczesniejszych klastrow
        if nr > 1:
            wymi = tab[0].zwrocWymiary()
            try:
                for n in range(1, nr):
                    k = tab[n]
                    if (k.ypocz >= ydelta-wymi[1]+1 and
                            k.ypocz-k.zwrocWymiary()[1]) <= ydelta + 1:
                        if (k.xpocz <= xdelta+wymi[0]+1 and
                                k.xpocz+k.zwrocWymiary()[0]) >= xdelta - 1:
                            return True
            except:  # noqa
                print("Wiekszy nr niz klastrow:")
                print(nr, len(tab))

        print("niekoliduje")
        return False


class Klaster(object):
    def __init__(self, zasieg=700):
        self.ustawiony = False  # czy klaster jest sprawdzony do mapy
        self.zas = zasieg  # zdefiniowany max zasieg klastrowania
        self.wydzL = []
        self.gmi = ""  # uzupelnianie automatycznie przy dodaniu wydzielenia
        self.obr = ""  # uzupelnianie automatycznie przy dodaniu wydzielenia
        self.xmin = 9999999
        self.xmax = 0
        self.ymin = 9999999
        self.ymax = 0
        self.skala = 5000

        # wspolrzedne lewego gornego rogu klastra do wrysowania na mapie,
        # wspolrzedne sa w metrach epsg:2180
        self.xpocz = 0
        self.ypocz = 0

    def dodajWydz(self, adrLes, tab):
        """
        Dodaje wydz do klastra
        adrLes = ""
        tab = [xmin, ymin, xmax, ymax]
        """
        if adrLes in self.wydzL:
            print("AdrLes juz w bazie: " + adrLes)
            return False

        if self.gmi == "":
            self.gmi = adrLes[3:6]
            self.obr = adrLes[6:10]

        self.wydzL.append(adrLes)
        if self.xmin > tab[0]:
            self.xmin = tab[0]
        if self.ymin > tab[1]:
            self.ymin = tab[1]
        if self.ymax < tab[3]:
            self.ymax = tab[3]
        if self.xmax < tab[2]:
            self.xmax = tab[2]

    def kwalifikuj(self, tab):
        """
        Sprawdza czy wydzielenia kwalifikuje sie do klastra
        tab = [xmin, ymin, xmax, ymax]
        """
        self.rect = [self.xmin, self.ymin, self.xmax, self.ymax]

        odl = []
        if tab[0] > self.xmax:
            odl.append(tab[0]-self.xmax)
        if tab[1] > self.ymax:
            odl.append(tab[1]-self.ymax)
        if tab[2] < self.xmin:
            odl.append(self.xmin-tab[2])
        if tab[3] < self.ymin:
            odl.append(self.ymin-tab[3])

        # jezeli nie dodano zadnej odl, wydzielenie jest juz w zasiegu klastra
        if len(odl) == 0:
            odl = [0]

        if max(odl) < self.zas:
            return True
        return False

    def zwrocPoly(self):
        self.rect = [self.xmin, self.ymin, self.xmax, self.ymax]
        return [
            QgsPointXY(self.rect[0], self.rect[1]),
            QgsPointXY(self.rect[0], self.rect[3]),
            QgsPointXY(self.rect[2], self.rect[3]),
            QgsPointXY(self.rect[2], self.rect[1]),
        ]

    def ustawPlot(self, al="sr", val="m"):  # noqa
        """
        Ustaw mape na plocie 900mm w pionie lub poziomie
        al:
        sr - wysrodkuj
        l - poszerz z prawej strony

        val:
        m - wysrodkuj
        d - przyciagnij do dolu
        """
        szer = self.xmax - self.xmin
        wys = self.ymax - self.ymin

        # w metrach dla 1:5000
        # szerA3 = 1928
        # wysA3 = 990.651

        # w cm dla layoutu
        szerA3_lay = 38.56
        wysA3_lay = 19.81
        self.ustawiony = True

        # wartość 1 cm na mapie w zaleznosci od skali
        posz_1cm = self.skala / 100

        # przelicz na metry dla podanej skali
        szerA3 = szerA3_lay * (self.skala/100)
        wysA3 = wysA3_lay * (self.skala/100)

        # czy zmiesci sie na A3
        if szer < szerA3 and wys < wysA3:
            popry = wysA3 - wys
            poprx = szerA3 - szer
            if val == "m":
                self.ymin -= popry / 2
                self.ymax += popry / 2

            if val == "d":
                # zachowaj centymetr odleglosci od ramki od dolu strony
                if popry > posz_1cm:
                    self.ymin -= posz_1cm
                    self.ymax += (popry - posz_1cm)
                else:
                    self.ymin -= popry / 2
                    self.ymax += popry / 2

            if al == "sr":
                self.xmin -= poprx / 2
                self.xmax += poprx / 2

            if al == "l":
                # zachowaj centymetr odleglosci od ramki z lewej strony
                if poprx > posz_1cm:
                    self.xmin -= posz_1cm
                    self.xmax += poprx - posz_1cm
                else:
                    self.xmin -= poprx / 2
                    self.xmax += poprx / 2

            return True

        # czy zmiesci sie z poszerzeniem 2 cm z kazdej strony
        if wys < 77 * (self.skala/100) or szer < 85 * (self.skala/100):
            poprx, popry = 0, 0
            # sprawdzy czy mapa ma szer min A3
            if self.xmax - self.xmin < szerA3:
                poprx = szerA3 - (self.xmax-self.xmin)
                self.xmin -= poprx / 2
                self.xmax += poprx / 2

            # sprawdzy czy mapa ma wys min A3
            if self.ymax - self.ymin < wysA3:
                popry = wysA3 - (self.ymax-self.ymin)
                self.ymin -= popry / 2
                self.ymax += popry / 2

            if poprx > 0 and popry > 0:
                pass
            elif poprx > 0 and popry == 0:
                self.ymin -= (posz_1cm * 2)
                self.ymax += (posz_1cm * 2)
            elif poprx == 0 and popry > 0:
                self.xmin -= (posz_1cm * 2)
                self.xmax += (posz_1cm * 2)
            else:
                self.poszerzRamke(posz_1cm * 2)
            return True

        # jesli sie nie miesci to sprawdz czy bez poszerzenia wejdzie
        if wys < 81 * (self.skala/100) or szer < 89 * (self.skala/100):
            return True

        self.ustawiony = False
        return False

    def poszerzRamke(self, val):
        """
        Poszerz klaster rownomiernie w kazdym kierunku o zadna ilosc metrow
        """
        if self.xmax - self.xmin < 250:
            poprx = (250 - (self.xmax - self.xmin)) / 2
            if poprx < val:
                poprx = val
        else:
            poprx = val

        if self.ymax - self.ymin < 250:
            popry = (250 - (self.ymax - self.ymin)) / 2
            if popry < val:
                popry = val
        else:
            popry = val

        self.xmin -= poprx
        self.xmax += poprx
        self.ymin -= popry
        self.ymax += popry

    def poszerzRamkeP(self, val):
        self.xmax += val

    def poszerzRamkeG(self, val):
        self.ymax += val

    def zwrocPow(self):
        return (self.xmax-self.xmin) * (self.ymax-self.ymin)

    def przesunRamkeP(self, val):
        self.xmin += val
        self.xmax += val

    def przesunRamkeG(self, val):
        self.ymin += val
        self.ymax += val

    def zwrocWymiary(self):
        return [self.xmax-self.xmin, self.ymax-self.ymin]

    def zwrocZakres(self):
        return [self.xmin, self.ymin, self.xmax, self.ymax]

    def ustawWspl(self, x, y):
        self.xpocz = x
        self.ypocz = y


class PobierzDane(QDialog, Ui_Dialog):
    def __init__(self):
        super(PobierzDane, self).__init__(None)
        self.setupUi(self)
        self.go_flag = False

        self.ok.clicked.connect(self.ook)
        self.pushButton_porzuc.clicked.connect(self.porzuc)
        self.pushButton_2k.clicked.connect(self.ustaw_2k)
        self.pushButton_5k.clicked.connect(self.ustaw_5k)
        self.pushButton_10k.clicked.connect(self.ustaw_10k)
        self.pushButton_20k.clicked.connect(self.ustaw_20k)
        self.pushButton_25k.clicked.connect(self.ustaw_25k)
        self.pushButton_30k.clicked.connect(self.ustaw_30k)
        self.pushButton_50k.clicked.connect(self.ustaw_50k)

    def ook(self):
        if self.lineEdit_minOdl.text().isdigit() and \
                self.lineEdit_minOdl.text().isdigit():
            self.go_flag = True
            self.hide()
        else:
            m = QMessageBox()
            m.setText(
                'Sprawdź czy napewno dobrze wpisana została skala i odległość!'
            )

    def porzuc(self):
        self.hide()

    def ustaw_2k(self):
        self.lineEdit_skala.setText('2000')

    def ustaw_5k(self):
        self.lineEdit_skala.setText('5000')

    def ustaw_10k(self):
        self.lineEdit_skala.setText('10000')

    def ustaw_20k(self):
        self.lineEdit_skala.setText('20000')

    def ustaw_25k(self):
        self.lineEdit_skala.setText('25000')

    def ustaw_30k(self):
        self.lineEdit_skala.setText('30000')

    def ustaw_35k(self):
        self.lineEdit_skala.setText('35000')

    def ustaw_50k(self):
        self.lineEdit_skala.setText('50000')
