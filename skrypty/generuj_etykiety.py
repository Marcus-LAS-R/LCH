import os
from qgis.core import QgsSpatialIndex, QgsGeometry, QgsRectangle, \
    QgsMessageLog, QgsPointXY, QgsFields, QgsField, QgsFeature, QgsProject, \
    Qgis, QgsVectorLayer, QgsCoordinateReferenceSystem, QgsVectorFileWriter, \
    QgsVectorLayerJoinInfo
from PyQt5.QtCore import QVariant


class GenerujPunkty():
    def generuj_punkty(self, oczko=20):  # noqa
        '''Metoda generuje pkt, na podstawie, których będzie wybrana
        lokalizacja etykiety'''

        yMax = self.feat.geometry().boundingBox().yMaximum()
        yMin = self.feat.geometry().boundingBox().yMinimum()
        xMax = self.feat.geometry().boundingBox().xMaximum()
        xMin = self.feat.geometry().boundingBox().xMinimum()

        if yMax - yMin < oczko:
            oczko = (yMax - yMin) / 2
            if oczko < 1:
                oczko = 1

        # bufory dla wydzielenia +10m i -10m
        self.bufor_10mniej = self.feat.geometry().buffer(-10, 0)
        # self.bufor_10wiecej = self.feat.geometry().buffer(10, 0)

        # obliczenie pkt w skoku o podane oczko, po 10m od kazdej ze strony
        # wydz i na środku, idziemy od dolu do gory
        for val in range(
                int(yMin)+int(oczko/2), int(yMax), int(oczko)):
            geom = QgsGeometry().fromPolylineXY([QgsPointXY(xMin, val),
                                                 QgsPointXY(xMax, val)])

            inter = geom.intersection(self.bufor_10mniej)

            if inter.length() > 5:
                try:
                    self.g_pkt_z_linii(inter)
                except:  # noqa
                    if 'ADR_LES' in self.pola:
                        wyps = self.feat['ADR_LES']
                    else:
                        wyps = self.feat['PARCELID']
                    QgsMessageLog.logMessage(
                        'Nie udało się wygenerować pkt poziomych dla: ' +
                        wyps,
                        'LCH'
                    )
            else:
                inter = geom.intersection(self.feat.geometry())
                # wygeneruj pkt srodkowy o ile linia ma 5 m
                if inter.length() > 0:
                    try:
                        self.g_pkt_z_linii(inter, 'sr')
                    except:  # noqa
                        if 'ADR_LES' in self.pola:
                            wyps = self.feat['ADR_LES']
                        else:
                            wyps = self.feat['PARCELID']
                        QgsMessageLog.logMessage(
                            'Nie udało się wygenerować pkt poziomych dla: ' +
                            wyps,
                            'LCH'
                        )
                else:
                    continue

        # dodaj centroid
        centroid = self.feat.geometry().centroid()
        if centroid.intersects(self.feat.geometry()):
            pkt = Punkt()
            pkt.x = centroid.boundingBox().xMinimum()
            pkt.y = centroid.boundingBox().yMinimum()
            self.tpkt.append(pkt)

        if len(self.tpkt) > 5:
            return

        # jezeli wygenerowano ponizej 5 pkt, sprobuj wygenerowac pkt w poziome
        for val in range(
                int(xMin)+int(oczko/2), int(xMax), int(oczko)):
            geom = QgsGeometry().fromPolylineXY([QgsPointXY(val, yMin),
                                                 QgsPointXY(val, yMax)])

            inter = geom.intersection(self.bufor_10mniej)

            if inter.length() > 5:
                try:
                    self.g_pkt_z_linii(inter)
                except Exception:
                    pass
            else:
                inter = geom.intersection(self.feat.geometry())
                # wygeneruj pkt srodkowy o ile linia ma 5 m
                if inter.length() > 0:
                    try:
                        # czasami z geometri robi sie kolekcja - omin
                        self.g_pkt_z_linii(inter, 'sr')
                    except Exception:
                        pass
                else:
                    continue

        # jezeli wydzielenie nie ma zadnych pkt dodaj pierwszy pkt z obwodki
        if len(self.tpkt) == 0:
            self.feat.geometry().convertToMultiType()
            pkt = Punkt()
            pkt.x = self.feat.geometry().asMultiPolygon()[0][0][0][0]
            pkt.y = self.feat.geometry().asMultiPolygon()[0][0][0][1]
            self.tpkt.append(pkt)

    def sortuj(self):
        '''Metoda sortuje liste tpkt od największej wagi do najmniejszej'''
        self.tpkt = sorted(self.tpkt, reverse=True, key=lambda x: x.waga)

    def ustaw_wagi_pktow(self, typ='w'):
        if typ == 'w':
            self._xmin = self.feat.geometry().boundingBox().xMinimum()
            self._ymin = self.feat.geometry().boundingBox().yMinimum()
            odly = (self.feat.geometry().boundingBox().yMaximum() -
                    self.feat.geometry().boundingBox().yMinimum())
            odlx = (self.feat.geometry().boundingBox().xMaximum() -
                    self.feat.geometry().boundingBox().xMinimum())
            self._odlx_3 = odlx / 3
            self._odly_3 = odly / 3
        for pkt in self.tpkt:
            self.g_uzpelnij_wagi_pkt(pkt, typ)

    def g_pkt_z_linii(self, inter, typ='c'):
        '''Metoda generuje na podstawie podanej Multilinii pkt w wydzieleniu
        typ:
            c - generuj 3 pkt na lini
            sr - generuje tylko pkt srodkowy na linii
        '''
        inter.convertToMultiType()
        for odc in inter.asMultiPolyline():
            # pkt srodkowy na lini
            pkt = Punkt()
            pkt.x = (odc[0][0] + odc[1][0]) / 2
            pkt.y = odc[0][1]
            pkt.waga += 5
            self.tpkt.append(pkt)

            # pkt boczne
            if typ == 'c':
                pkt = Punkt()
                pkt.x = odc[0][0]
                pkt.y = odc[0][1]
                pkt.waga += 3
                self.tpkt.append(pkt)

                pkt = Punkt()
                pkt.x = odc[1][0]
                pkt.y = odc[0][1]
                self.tpkt.append(pkt)
    def g_rect_etykiety(self, pkt):
        if pkt.typ_etyk == 1:
            return [
                pkt.x+self.zakres_litera[0],
                pkt.y+self.zakres_litera[1],
                pkt.x+self.zakres_litera[2],
                pkt.y+self.zakres_litera[3],
            ]

        return [
            pkt.x+self.zakres_pelna_etyk[0],
            pkt.y+self.zakres_pelna_etyk[1],
            pkt.x+self.zakres_pelna_etyk[2],
            pkt.y+self.zakres_pelna_etyk[3],
        ]

    def g_rect2geom(self, pkt, rect):
        ''' Konwertuje QgsRectange na Geometrie'''
        return QgsGeometry.fromPolygonXY([[
            QgsPointXY(rect[0], rect[1]),
            QgsPointXY(rect[0], rect[3]),
            QgsPointXY(rect[2], rect[3]),
            QgsPointXY(rect[2], rect[1]),
            QgsPointXY(rect[0], rect[1]),
        ]])

    def g_uzpelnij_wagi_pkt(self, pkt, typ='w'):  # noqa
        ''' Generuj wagę dla każdego pkt w zależności od sąsiedztwa z pnsw,
        linią albo z innym wydzieleniem.
        typ: w - zasieg labelki bedzie sprawdzany z si wydzielen
        dz - zasieg labelki bedzie sprawdzany z istniejacymi labelkami,
        '''

        rect_raw = self.g_rect_etykiety(pkt)
        rect = QgsRectangle(*rect_raw)
        geom = self.g_rect2geom(pkt, rect_raw)

        # sprawdz nakładanie i zawieranie zasiegu etykiety w wydzieleniach
        if typ == 'w' and self.wydzsi is not False:
            if self._xmin + self._odlx_3 < pkt.x < self._xmin+2*self._odlx_3 \
                    and self._ymin+self._odly_3 < \
                    pkt.y < self._ymin+2*self._odly_3:
                pkt.waga += 1

            ids = self.wydzsi.intersects(rect)
            if len(ids) == 0:
                pass
                # print('etykieta poza wydzieleniem???')
            s_przec = 0  # suma przeciecia z zasiegu etyk z innymi wydz
            for id in ids:
                # jezeli etykieta lezy w 90% na wydzieleniu dodaj pkt do wagi
                inter = self.wydzsl[id].geometry().intersection(geom)
                if id == self.feat.id():
                    if (inter.area()/geom.area()) > 0.8999:
                        pkt.waga += 6
                    if (inter.area()/geom.area()) < 0.5999:
                        pkt.waga -= 6
                else:
                    s_przec += inter.area()

                    # jezeli etykieta przykrywa inne wydzielenie skryc etykiete
                    # tylko do litery
                    if inter.area()/self.wydzsl[id].geometry().area() > 0.5:
                        pkt.typ_etyk = 1

            if (s_przec/geom.area()) > 0.1 and pkt.typ_etyk == 2:
                pkt.waga -= 20

        if typ == 'dz' and self.wydzsi is not False:
            # dodaj 1 pkt jezeli pkt jest blisko wydzielenia
            rect_ew = QgsRectangle(
                *[sum(x) for x in zip(rect_raw, [-40, -40, 40, 40])])
            ids = self.wydzsi.intersects(rect_ew)
            if len(ids) > 0:
                pkt.waga += 1

        # sprawdz nakładanie zasięgu etykiety z pnsw
        if self.pnswsi is not False:
            ids = self.pnswsi.intersects(rect)
            for id in ids:
                if self.pnswsl[id].geometry().intersects(geom):
                    pkt.waga -= 20
                    break

        # sprawdz nakładanie zasięgu etykiety z liniami
        if self.liniesi is not False:
            ids = self.liniesi.intersects(rect)
            for id in ids:
                if self.liniesl[id].geometry().intersects(geom):
                    pkt.waga -= 20
                    break

    def dodaj_pnsw(self, pnswsi, pnswsl):
        ''' wskaźnik do spatial indeksu PNSW, i sl z featureami'''
        self.pnswsi = pnswsi
        self.pnswsl = pnswsl

    def dodaj_linie(self, liniesi, liniesl):
        ''' wskaźnik do spatial indeksu LINI, i sl z featureami'''
        self.liniesi = liniesi
        self.liniesl = liniesl

    def dodaj_wydz(self, wydzsi, wydzsl):
        ''' wskaźnik do spatial indeksu WYDZ, i sl z featureami'''
        self.wydzsi = wydzsi
        self.wydzsl = wydzsl

    def dodaj_dzewid(self, dzsi, dzsl):
        ''' wskaźnik do spatial indeksu DZEWID, i sl z featureami'''
        self.dzsi = dzsi
        self.dzsl = dzsl

    def isValid(self):
        '''Sprawdza czy mamy wszystkie niezbędne kolumny do wygenerowania opisu
            Jeżeli nie to False,
            '''
        # TODO: DOpisanie sprawdzenia czy mamy poprawną geometrię? Czy to ma
        # sens, sprawdzanie geometrii?
        braki = [x for x in self.pola
                 if x not in [y.name() for y in self.feat.fields().toList()]
                 ]

        if len(braki) > 0:
            QgsMessageLog.logMessage(
                'Brakuje niezbednych kolumn w featurku - POMIJAM! (' +
                self.feat[self.nazpola]+') [' + ", ".join(braki) + ']',
                "LCH"
            )
            return False
        self.oblicz_ramke_etyk()
        return True


class RoboczeDane():
    def r_pokaz_wszystkie_pkt(self):
        '''Metoda zwraca liste z featurami w postaci pkt wraz z atrybutami'''
        lista = []
        lista_ramki = []
        attr_def = [
            QgsField("ADR_LES", QVariant.String, len=35),
            QgsField("PARCELID", QVariant.String, len=35),
            QgsField("MUNICIP", QVariant.String, len=3),
            QgsField("COMMUNITY", QVariant.String, len=4),
            QgsField("typEtyk", QVariant.Int),
            QgsField("waga", QVariant.Int),
        ]
        fds = QgsFields()
        for fi in attr_def:
            fds.append(fi)

        for pkt in self.tpkt:
            # stworz pkt etykiety wraz z opisem
            for w in [1, 2]:
                f = QgsFeature()
                f.setFields(fds)

                for x in [y.name() for y in attr_def[:4]]:
                    if x in self.feat_attr:
                        f[x] = self.feat[x]
                f['typEtyk'] = pkt.typ_etyk
                f['waga'] = pkt.waga

                f.setGeometry(QgsGeometry().fromPointXY(
                    QgsPointXY(pkt.x, pkt.y)))
                lista.append(f)
                lista_ramki.append(f)

        return lista, lista_ramki


class DzEwidEtyk(GenerujPunkty, RoboczeDane):
    def __init__(self, feat):
        self.feat = feat
        self.feat_attr = [x.name() for x in self.feat.fields().toList()]
        # tablica z pktEtyk wygenerowanymi dla wydzielenia
        self.tpkt = []
        # zdefiniowane domyślne wartości zasięgu etykiety
        # zdefiniowane domyślne wartości zasięgu etykiety (2 cyfry)
        self.zakres_pelna_etyk = [-12, -7, 12, 7]
        self.pnswsi = False
        self.liniesi = False
        self.wydzsi = False

        self.pola = ['PARCELID', 'PARCELNR', 'MUNICIP', 'COMMUNITY', ]
        self.nazpola = 'PARCELID'

    def oblicz_ramke_etyk(self):
        '''Metoda oblicza zakresy etykiety działki
        '''
        nr = self.feat['PARCELNR']
        self.zakres_pelna_etyk = [-6*len(nr)/2, -7, 6*len(nr)/2, 7]


class WydzEtyk(GenerujPunkty, RoboczeDane):
    def __init__(self, feat):
        self.feat = feat
        self.feat_attr = [x.name() for x in self.feat.fields().toList()]
        # tablica z pktEtyk wygenerowanymi dla wydzielenia
        self.zakres_litera = [-5, -5, 5, 5]
        self.zakres_pelna_etyk = [-5, -5, 5, 5]
        self.tpkt = []
        self.pnswsi = False
        self.liniesi = False
        self.wydzsi = False
        self.pola = ['ADR_LES', 'WYDZ', 'GAT', 'UDZIAL', 'WIEK',
                     'ZADRZEW', 'POW_WYDZ', 'TYP_POW', 'SLMN_KOL',
                     'MUNICIP', 'COMMUNITY', ]
        self.nazpola = 'ADR_LES'

    def oblicz_ramke_etyk(self):
        '''Metoda oblicza zakresy etykiety wydzielenia dla samej litery i
        pełenej etykiety, o ile tak wogóle może się pojawić na mapie'''
        wydz = self.feat['WYDZ']
        gat = self.feat['GAT']
        udzial = self.feat['UDZIAL']
        wiek = self.feat['WIEK']
        pow_wydz = self.feat['POW_WYDZ']
        slmn = self.feat['SLMN_KOL']

        # obliczamy poprawki rozmiary opisu tylko dla litery/liter
        if len(wydz) > 1:
            self.zakres_litera = [-7.5, -5, 7.5, 5]

        # obliczamy wielkkosc pelnego opisu w zaleznosci od typu
        # powierzchni, i dlugosci opisu skroconego
        # inne wydzielenia
        if slmn == 580:
            self.zakres_pelna_etyk = [-15, -20,  15, 5]

        # halizny, zreby, plazowiny
        if slmn > 549 and slmn < 580:
            if len(wydz) == 1:
                self.zakres_pelna_etyk = [-5, -12.5,  40, 12.5]
            else:
                self.zakres_pelna_etyk = [-7.5, -12.5,  42.5, 12.5]

        # opisy d-stanowe
        if slmn < 550:
            # ustaw gore i dol, oraz wymiary tabeli
            wymiar = [0, -12.5, 0, 16]

            # w zaleznosci od dlugosci opisu wydzielenia, liczymy dl
            poprawka = 5
            if len(wydz) == 1:
                wymiar[0] = -5
            else:
                wymiar[0] = -7.5
                poprawka = 7.5

            # ustalamy odleglosc z
            licz = len(gat) + len(str(udzial)) + len(str(wiek))
            mian = len(str(pow_wydz))
            dl = max(licz, mian)
            oklad = 35
            if dl > 4:
                oklad += (dl-4) * 5

            wymiar[2] = oklad + poprawka

            self.zakres_pelna_etyk = wymiar


class Punkt():
    def __init__(self):
        self.x = -1
        self.y = -1
        self.waga = 100  # waga etykiety
        # w punkcie jest etykieta
        # 0 - brak etykiety
        # 1 - tylko litera
        # 2 - pelna etykieta
        self.typ_etyk = 2
        self.adr_les = ''
        self.parcelid = ''
        self.parcelnr = ''
        self.geom = False
        self.community = ''
        self.municip = ''
        self.flaga = False  # flaga do sprawdzenia jezeli True

        self.attr_def = [
            QgsField("MUNICIP", QVariant.String, len=3),
            QgsField("COMMUNITY", QVariant.String, len=4),
        ]

    @property
    def point(self):
        return QgsPointXY(self.x, self.y)

    def wydz_feat(self):
        fds = QgsFields()
        for fi in self.attr_def + \
                [QgsField("ADR_LES", QVariant.String, len=35),
                 QgsField("typEtyk", QVariant.Int), ]:
            fds.append(fi)

        f = QgsFeature()
        f.setFields(fds)
        f['MUNICIP'] = self.municip
        f['COMMUNITY'] = self.community
        f['ADR_LES'] = self.adr_les
        f['typEtyk'] = self.typ_etyk
        return f

    def wydz_pft(self):
        f = self.wydz_feat()
        f.setGeometry(QgsGeometry().fromPointXY(QgsPointXY(self.x, self.y)))
        return f

    def wydz_aft(self):
        f = self.wydz_feat()
        f.setGeometry(self.geom)
        return f

    def dzewid_feat(self):
        fds = QgsFields()
        for fi in [
                QgsField("PARCELNR", QVariant.String, len=15)] + self.attr_def:
            fds.append(fi)

        f = QgsFeature()
        f.setFields(fds)
        f['MUNICIP'] = self.municip
        f['COMMUNITY'] = self.community
        f['PARCELNR'] = self.parcelnr
        return f

    def dzewid_pft(self):
        f = self.dzewid_feat()
        f.setGeometry(QgsGeometry().fromPointXY(QgsPointXY(self.x, self.y)))
        return f

    def dzewid_aft(self):
        f = self.dzewid_feat()
        f.setGeometry(self.geom)
        return f


class Etykietownik():
    def __init__(self, iface):
        self.iface = iface
        self.spatial_id = 0  # kolejne id etykiet w si

        # slownik z wygenerowanymi obiektami etyksl dla wydzielen
        self.wysl = {}
        # slownik z wygenerowanymi obiektami etykdzewid
        self.dzsl = {}
        # indeks przestrzenny ramek etykiet - sprawdzanie nakladania
        self.etyksi = QgsSpatialIndex()
        self.etyksl = {}

        self.wydz = False
        self.wydzsi = False
        self.wydzsl = False
        self.pnsw = False
        self.pnswsi = False
        self.pnswsl = False
        self.linie = False
        self.linsi = False
        self.linsl = False
        self.dzewid = False
        self.kat = ''

        # tablica z adr_les wydzielen bez opisow - do sprawdzenia
        self.bl_braku_wydz = []
        # tablica z parcelid dzewid bez opisow - do sprawdzenia
        self.bl_braku_dzewid = []

        # sl z ramkami wydzielen do sprawdzenia nakladania po wygenerowaniu
        # wszystkich etykiet dla wydz i dzewid
        # {spatial_id: pkt, }
        self.l_naklad_wydz = {}

    def znajdz_warstwy(self):
        '''Metoda sprawdza czy w  TOC znajduje sie warstwa WYDZ_POL,
        a następnie szuka w katalogu warstwy innych danych LINIE, PNSW, DZKAT.
        Po odnalezieniu buduje indeksy przestrzenne i slowniki featurkow
        '''

        self.wydz = QgsProject.instance().mapLayersByName('WYDZ_POL')
        if len(self.wydz) != 1:
            self.iface.messageBar().pushMessage(
                'BŁĄD', 'Nie odnalazałem warstwy WYDZ_POL', Qgis.Critical)
            return False
        self.wydz = self.wydz[0]
        self.wydzsl = {x.id(): x for x in self.wydz.getFeatures()}
        self.wydzsi = QgsSpatialIndex(self.wydz.getFeatures())

        sciezka = self.wydz.dataProvider().dataSourceUri().split("|")[0]
        self.kat = os.path.dirname(sciezka)

        sc_dzewid = os.path.join(self.kat, 'DZKAT.shp')
        if not os.path.exists(sc_dzewid):
            self.iface.messageBar().pushMessage(
                'BŁĄD', 'Nie odnalazałem warstwy DZKAT w katalogu z WYDZ_POL',
                Qgis.Critical)
            return False
        self.dzewid = QgsVectorLayer(sc_dzewid, 'DZKAT', 'ogr')

        sc_pnsw = os.path.join(self.kat, 'PNSW.shp')
        if os.path.exists(sc_pnsw):
            self.pnsw = QgsVectorLayer(sc_pnsw, 'PNSW', 'ogr')
            self.pnswsl = {x.id(): x for x in self.pnsw.getFeatures()}
            self.pnswsi = QgsSpatialIndex(self.pnsw.getFeatures())

        sc_linie = os.path.join(self.kat, 'LINIE.shp')
        if os.path.exists(sc_linie):
            self.linie = QgsVectorLayer(sc_linie, 'LINIE', 'ogr')
            self.linsl = {x.id(): x for x in self.linie.getFeatures()}
            self.linsi = QgsSpatialIndex(self.linie.getFeatures())

        return True

    def generuj_pkt_wydz(self):
        '''Metoda generuje pkt i wagi a następnie umieszcza je w slowniku do
        z ktorego beda generowane etykiety wydzielen
        '''
        for feat in self.wydz.getFeatures():
            etyk = WydzEtyk(feat)

            etyk.dodaj_wydz(self.wydzsi, self.wydzsl)
            if self.pnswsi is not False:
                etyk.dodaj_pnsw(self.pnswsi, self.pnswsl)
            if self.linsi is not False:
                etyk.dodaj_linie(self.linsi, self.linsl)

            if etyk.isValid():
                etyk.generuj_punkty()
                etyk.ustaw_wagi_pktow()
                etyk.sortuj()
                self.wysl[feat.id()] = etyk
                if len(etyk.tpkt) == 0:
                    self.bl_braku_wydz.append(feat['ADR_LES'])
            else:
                self.bl_braku_wydz.append(feat['ADR_LES'])

    def generuj_pkt_dzewid(self):
        '''Metoda generuje pkt i wagi a następnie umieszcza je w slowniku do
        z ktorego beda generowane etykiety dzewid
        '''
        for feat in self.dzewid.getFeatures():
            etyk = DzEwidEtyk(feat)

            etyk.dodaj_wydz(self.wydzsi, self.wydzsl)
            if self.pnswsi is not False:
                etyk.dodaj_pnsw(self.pnswsi, self.pnswsl)
            if self.linsi is not False:
                etyk.dodaj_linie(self.linsi, self.linsl)

            if etyk.isValid():
                etyk.generuj_punkty()
                etyk.ustaw_wagi_pktow('dz')
                etyk.sortuj()
                self.dzsl[feat.id()] = etyk
                if len(etyk.tpkt) == 0:
                    self.bl_braku_dzewid.append(feat['PARCELID'])
            else:
                self.bl_braku_dzewid.append(feat['PARCELID'])

    def generuj_etykiety_wydz(self):
        '''Metoda generuje etykiety wydz oraz sprawdza ich nakladanie
        na siebie'''
        for it in self.wysl.values():
            self.generuj_etyk_wydzielenia(it)

    def generuj_etyk_wydzielenia(self, it):
        ok = False

        for pkt in it.tpkt:
            rect_raw = it.g_rect_etykiety(pkt)
            rect = QgsRectangle(*rect_raw)
            ids = self.etyksi.intersects(rect)
            # jezeli analizowana etykieta przecina sie z jakimis innymi
            # sprawdz pow przeciecia
            if len(ids) > 0:
                sum_pow = 0
                powetyk = it.g_rect2geom(pkt, rect_raw)
                for id in ids:
                    inter = powetyk.intersection(
                        self.etyksl[id].geom)
                    if inter.area() == 0:
                        sum_pow += 0.1
                    else:
                        sum_pow += inter.area()
                    # jezeli pow jest mniejsza od 10% dodajemy jako ok
                if sum_pow/powetyk.area() > 0.1:
                    continue

            pkt.adr_les = it.feat['ADR_LES']
            pkt.municip = it.feat['ADR_LES'][3:6]
            pkt.community = it.feat['ADR_LES'][6:10]
            pkt.geom = it.g_rect2geom(pkt, rect_raw)

            self.etyksl[self.spatial_id] = pkt
            self.etyksi.addFeature(self.spatial_id, rect)
            self.l_naklad_wydz[self.spatial_id] = pkt.wydz_aft()
            self.spatial_id += 1
            ok = True
            break

        # jezeli przelecielismy wszystkie etykiety w tabeli i nic nie
        # spasowało dodaj pierwsza z najwiekszą wagą ale tylko jako litera,
        # oflaguj jako do sprawdzenia
        if not ok:
            pkt = it.tpkt[0]
            rect_raw = it.g_rect_etykiety(pkt)
            rect = QgsRectangle(*rect_raw)
            pkt.adr_les = it.feat['ADR_LES']
            pkt.municip = it.feat['ADR_LES'][3:6]
            pkt.community = it.feat['ADR_LES'][6:10]
            pkt.flaga = True
            pkt.geom = it.g_rect2geom(pkt, rect_raw)

            self.etyksl[self.spatial_id] = pkt
            self.etyksi.addFeature(self.spatial_id, rect)
            self.l_naklad_wydz[self.spatial_id] = pkt.wydz_aft()
            self.spatial_id += 1

    def generuj_etykiety_dzewid(self):
        '''Metoda generuje etykiety dzewid oraz sprawdza ich nakladanie
        na siebie'''
        for it in self.dzsl.values():
            ok = False
            for pkt in it.tpkt:
                rect_raw = it.g_rect_etykiety(pkt)
                rect = QgsRectangle(*rect_raw)
                ids = self.etyksi.intersects(rect)
                # jezeli analizowana etykieta przecina sie z jakimis innymi
                # sprawdz pow przeciecia
                if len(ids) > 0:
                    sum_pow = 0
                    powetyk = it.g_rect2geom(pkt, rect_raw)
                    for id in ids:
                        inter = powetyk.intersection(
                            self.etyksl[id].geom)
                        if inter.area() == 0:
                            sum_pow += 0.1
                        else:
                            sum_pow += inter.area()
                        # jezeli pow jest mniejsza od 10% dodajemy jako ok
                    if sum_pow/powetyk.area() > 0.1:
                        continue
                pkt.parcelid = it.feat['PARCELID']
                pkt.parcelnr = it.feat['PARCELNR']
                pkt.municip = it.feat['PARCELID'][4:7]
                pkt.community = it.feat['PARCELID'][7:11]
                pkt.geom = it.g_rect2geom(pkt, rect_raw)

                self.etyksl[self.spatial_id] = pkt
                self.etyksi.addFeature(self.spatial_id, rect)
                self.spatial_id += 1
                ok = True
                break

            # jezeli przelecielismy wszystkie etykiety w tabeli i nic nie
            # spasowało dodaj pierwsza z najwiekszą wagą ale tylko jako litera,
            # oflaguj jako do sprawdzenia
            if not ok:
                pkt = it.tpkt[0]
                rect_raw = it.g_rect_etykiety(pkt)
                rect = QgsRectangle(*rect_raw)
                pkt.parcelid = it.feat['PARCELID']
                pkt.parcelnr = it.feat['PARCELNR']
                pkt.municip = it.feat['PARCELID'][4:7]
                pkt.community = it.feat['PARCELID'][7:11]
                pkt.flaga = True
                pkt.geom = it.g_rect2geom(pkt, rect_raw)

                self.etyksl[self.spatial_id] = pkt
                self.etyksi.addFeature(self.spatial_id, rect)
                self.spatial_id += 1

    def dodaj_warstwy(self):
        '''Metoda dodaje wygenerowane etykiety oraz zasiegi konfliktow dz i
        wydzielen do mapy'''

        ldzewid = []  # lista z featurami labelek dzewid
        ldzewid_ram = []  # lista z featurami ramek dzewid
        lwydz = []  # lista z featurami labelek wydzielen
        lwydz_ram = []  # lista z featurami ramek wydzielen

        self.sprawdz_nakladanie_wydz()

        for key, pkt in self.etyksl.items():
            if pkt.parcelid != '':
                ldzewid.append(pkt.dzewid_pft())
                if pkt.flaga:
                    ldzewid_ram.append(pkt.dzewid_aft())

            if pkt.adr_les != '':
                lwydz.append(pkt.wydz_pft())
                if pkt.flaga:
                    lwydz_ram.append(pkt.wydz_aft())

        crs = QgsCoordinateReferenceSystem("epsg:2180")
        plugin_dir = os.path.dirname(__file__)

        if len(lwydz) > 0:
            wlyr = QgsVectorLayer(
                'Point?crs=epsg:2180&index=yes',
                'pkt_wydz', 'memory'
            )
            wlyr.startEditing()
            wlyr.dataProvider().addAttributes(lwydz[0].fields().toList())
            wlyr.updateFields()
            wlyr.dataProvider().addFeatures(lwydz)
            wlyr.commitChanges()
            QgsVectorFileWriter.writeAsVectorFormat(
                                        wlyr,
                                        os.path.join(self.kat, "WYDZ_OPS.shp"),
                                        "UTF-8",
                                        crs,
                                        "ESRI Shapefile")
            wydzielenia = QgsVectorLayer(
                os.path.join(self.kat, "WYDZ_OPS.shp"), 'WYDZ_OPS', 'ogr')

            # dodaj polaczenie z wydz_pol
            joinObj = QgsVectorLayerJoinInfo()
            joinObj.setJoinFieldName("ADR_LES")
            joinObj.setTargetFieldName("ADR_LES")
            joinObj.setJoinLayerId(self.wydz.id())
            # joinObj.setUsingMemoryCache(True)
            joinObj.setJoinFieldNamesSubset([
                'GRP',
                'ODDZ',
                'WYDZ',
                'L_EWID',
                'UDZIAL',
                'GAT',
                'WIEK',
                'ZADRZEW',
                'POW_WYDZ',
                'TYP_POW',
                'STRUKTUR',
                'SLMN_KOL',
            ])
            joinObj.setJoinLayer(self.wydz)
            wydzielenia.addJoin(joinObj)

            wydzielenia.loadNamedStyle(
                os.path.abspath(
                    os.path.join(plugin_dir, '..', 'qml', 'WYDZ_OPS_gen.qml'))
            )
            QgsProject.instance().addMapLayer(wydzielenia)

        if len(lwydz_ram) > 0:
            wlyrm = QgsVectorLayer(
                'Polygon?crs=epsg:2180&index=yes',
                'wydz_ram', 'memory'
            )
            wlyrm.startEditing()
            wlyrm.dataProvider().addAttributes(lwydz_ram[0].fields().toList())
            wlyrm.updateFields()
            wlyrm.dataProvider().addFeatures(lwydz_ram)
            wlyrm.commitChanges()

            QgsProject.instance().addMapLayer(wlyrm)

        if len(ldzewid) > 0:
            wdz = QgsVectorLayer(
                'Point?crs=epsg:2180&index=yes',
                'pkt_dzewid', 'memory'
            )
            wdz.startEditing()
            wdz.dataProvider().addAttributes(ldzewid[0].fields().toList())
            wdz.updateFields()
            wdz.dataProvider().addFeatures(ldzewid)
            wdz.commitChanges()

            QgsVectorFileWriter.writeAsVectorFormat(
                wdz,
                os.path.join(self.kat, "DZKAT_OPS.shp"),
                "UTF-8",
                crs,
                "ESRI Shapefile")
            lyrdz = QgsVectorLayer(
                os.path.join(self.kat, "DZKAT_OPS.shp"), 'DZKAT_OPS', 'ogr')
            lyrdz.loadNamedStyle(
                os.path.abspath(
                    os.path.join(plugin_dir, '..', 'qml', 'DZKAT_OPS.qml'))
            )
            QgsProject.instance().addMapLayer(lyrdz)

        if len(ldzewid_ram) > 0:
            wdzr = QgsVectorLayer(
                'Polygon?crs=epsg:2180&index=yes',
                'dzewid_ram', 'memory'
            )
            wdzr.startEditing()
            wdzr.dataProvider().addAttributes(ldzewid_ram[0].fields().toList())
            wdzr.updateFields()
            wdzr.dataProvider().addFeatures(ldzewid_ram)
            wdzr.commitChanges()

            QgsProject.instance().addMapLayer(wdzr)

    def sprawdz_nakladanie_wydz(self):
        '''Metoda sprawdza jeszcze raz czy wszystkie wydzielenia mają
        odpowiednie pokrycie z innymi etykietami.'''
        for key, it in self.l_naklad_wydz.items():
            ids = self.etyksi.intersects(
                it.geometry().boundingBox())
            if len(ids) > 1:
                suma_pow = 0
                for id in ids:
                    inter = it.geometry().intersection(
                        self.etyksl[id].wydz_aft().geometry())
                    if id != key:
                        suma_pow += inter.area()

                if suma_pow/it.geometry().area() > 0.1:
                    self.etyksl[key].flaga = True
