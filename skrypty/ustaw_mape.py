import platform
from datetime import datetime
from qgis.core import QgsProject, Qgis, QgsLayoutSize, QgsUnitTypes, \
    QgsRectangle, QgsLayoutItemMap, QgsLayoutPoint, QgsLayoutItemLabel
from lasr.skrypty.baza_wrapper import Baza, znajdz_baze_do_wydz
from PyQt5.QtGui import QFont, QColor
from PyQt5.QtWidgets import QInputDialog


class UstawMape():
    def __init__(self, iface):
        self.iface = iface
        self.mapy = [
            'MAPA_PPOZ',
            'MAPA_FOCHRONY',
            'MAPA_OGOLNA',
            'MAPA_ZABIEGI',
        ]

    def sprawdz_warstwy(self):
        '''Metoda sprawdza jaka mape ustawiam i na tej podstawie wyszukuje
        niezbędne warstwy w TOC'''

        # wyszukaj niezbedne warstwy w TOC
        self.mr = False
        self.oddz = False
        self.wydz = False

        for key, val in QgsProject.instance().mapLayers().items():
            if key[:4] == 'ODDZ':
                self.oddz = val
            if key[:8] == 'WYDZ_POL':
                self.wydz = val
            if key[:6] == 'MapRam':
                self.mr = val

        if self.oddz is False:
            self.iface.messageBar().pushMessage(
                'BŁĄD', 'Nie znaleziono warstwy ODDZ w TOC!', Qgis.Warning, 0
            )
            return False

        feat = next(self.oddz.getFeatures())
        self.gmi = feat['MUNICIP']
        self.obr = feat['COMMUNITY']
        return True

    def przesun_elem(self):  # noqa
        '''Przesuwa elementy mapy i generuj wyniesienia na podstawie warstwy
        MapRam, niezależnie od rodzaju mapy'''

        # slownik z rozmiarami mapy i wydzielen
        # sl[''] = [xpocz, ypocz, szer, wys, xmapa, ymapa]
        sr = {}
        space = 0  # poprawka na przesunicie layoutu
        if self.mr.featureCount() == 0:
            self.iface.messageBar().pushMessage('Error',
                                                u'Brak poligonów w MapRamie',
                                                level=Qgis.Critical)
            return False

        for f in self.mr.getFeatures():
            # zachowanie kompatybilnosci z poprzednia wersja z qgis2
            try:
                skala = f['skala']
            except Exception:
                skala = 5000

            bb = f.geometry().boundingBox()
            sr[f['RAMKA']] = [
                bb.xMinimum(),
                bb.yMaximum(),
                bb.xMaximum() - bb.xMinimum(),
                bb.yMaximum() - bb.yMinimum(),
                f['xpocz'],
                f['ypocz'],
                skala
            ]

        pg_coll = self.lay.pageCollection()
        pg = pg_coll.page(0)
        wys_stara = pg_coll.maximumPageSize().height()
        szer_stara = pg_coll.maximumPageWidth()

        try:
            szer_nowa = (sr['M'][2] / (sr['M'][6]/1000)) + 10 + 10
            wys_nowa = (sr['M'][3] / (sr['M'][6]/1000)) + 10 + 80 + 10
        except:  # noqa
            szer_nowa = (sr['Mr'][2] / (sr['Mr'][6]/1000)) + 10 + 10
            wys_nowa = (sr['Mr'][3] / (sr['Mr'][6]/1000)) + 10 + 80 + 10
        pg.setPageSize(
            QgsLayoutSize(szer_nowa, wys_nowa, QgsUnitTypes.LayoutMillimeters)
        )
        self.lay.refresh()

        poprx = szer_nowa - szer_stara
        popry = wys_nowa - wys_stara

        # lista id elementow nie przesuwanych w pionie
        wysPomin = ['ramka', 'NORTH_N', 'NORTH_ARROW', 'GLOWNA']
        # lista id z elementami do przesuniecia w poziomie
        szerPrzes = ['NORTH_N', 'NORTH_ARROW', 'ramkaP', 'zamawiajacy',
                     'wykonawca', ]

        # przesun elementy w pionie
        for it in self.lay.items():
            try:
                if it.id() not in wysPomin and len(it.id()) > 2:
                    it.attemptMoveBy(0, popry+space)
                if it.id() in szerPrzes and len(it.id()) > 2:
                    it.attemptMoveBy(poprx, 0)
            except:  # nopep8
                pass

        ramka = self.lay.itemById('ramka')
        ramka.attemptResize(
                QgsLayoutSize(szer_nowa-10,
                              wys_nowa-10,
                              QgsUnitTypes.LayoutMillimeters)
        )

        ramka = self.lay.itemById('ramkaD')
        ramka.attemptResize(
            QgsLayoutSize(szer_nowa-10, 80, QgsUnitTypes.LayoutMillimeters)
        )

        # ustaw mapke pogladowa o ile taka znajduje sie na mapie
        it = self.lay.itemById('POGLAD')
        if it is not None:
            oe = self.oddz.extent()
            szer = oe.width()
            wys = oe.height()
            # jezeli szerokosc obrebu jest wieksza niz wysokosc, srodkujemy
            # w pionie na wysokosc
            if wys < szer:
                szer = szer + (szer/10)
                wys_calk_m = (78.8 * szer) / 68.9
                poprawka_wys_m = wys_calk_m - wys
                poglad_ramka = QgsRectangle(
                    oe.xMinimum()-((oe.width()/10)/2),
                    oe.yMinimum()-(poprawka_wys_m/2),
                    oe.xMaximum()+((oe.width()/10)/2),
                    oe.yMaximum()+(poprawka_wys_m/2))
            else:
                wys = wys + (wys/10)
                szer_calk_m = (68.9 * wys) / 78.8
                poprawka_szer_m = szer_calk_m - szer
                poglad_ramka = QgsRectangle(
                    oe.xMinimum()-(poprawka_szer_m/2),
                    oe.yMinimum()-((oe.height()/10)/2),
                    oe.xMaximum()+(poprawka_szer_m/2),
                    oe.yMaximum()+((oe.height()/10)/2))

            it.setExtent(poglad_ramka)
            # it.setItemPosition(it.x(), popry+it.y(), 68.9, 78.8)

        # ustaw główne okno mapy wraz ze skalą zapisana w mapramie
        it = self.lay.itemById('GLOWNA')
        try:
            srm = sr['M']
        except:  # noqa
            srm = sr['Mr']

        if it is not None:
            it.attemptResize(
                QgsLayoutSize(szer_nowa-20, wys_nowa-100,
                              QgsUnitTypes.LayoutMillimeters)
            )
            it.setExtent(QgsRectangle(
                srm[0],
                srm[1]-srm[3],
                srm[0]+srm[2],
                srm[1]
            ))
            it.setScale(srm[6])

        # dodaj nowe wyniesienia do mapy o ile takie znajduja sie w mapramie
        for w in [k for k in sorted(sr.keys()) if k not in ["Mr", 'M']]:
            wyn = sr[w]
            wyn_it = QgsLayoutItemMap(self.lay)
            wyn_it.attemptMove(
                QgsLayoutPoint(
                    int(10+(wyn[4]-srm[0])/(srm[6]/1000))+space,
                    int(10+(srm[1]-wyn[5])/(srm[6]/1000))+space,
                    QgsUnitTypes.LayoutMillimeters
                )
            )
            wyn_it.attemptResize(
                QgsLayoutSize(
                    wyn[2]/(wyn[6]/1000),
                    wyn[3]/(wyn[6]/1000),
                    QgsUnitTypes.LayoutMillimeters)
            )
            wyn_it.setExtent(
                QgsRectangle(wyn[0],
                             wyn[1]-wyn[3],
                             wyn[0]+wyn[2],
                             wyn[1])
            )
            wyn_it.setScale(wyn[6])
            wyn_it.setId('wyn'+w+'_Map')
            wyn_it.setBackgroundColor(QColor('white'))
            wyn_it.setFrameEnabled(True)
            self.lay.addItem(wyn_it)

            wLab = QgsLayoutItemLabel(self.lay)
            wLab.setText("Wyniesienie "+w)
            wLab.setFont(QFont('Arial', 12, QFont.Bold))

            wLab.attemptMove(
                QgsLayoutPoint(
                    36+(wyn[4]-srm[0])/(srm[6]/1000),
                    2+(srm[1]-wyn[5]+wyn[3])/(srm[6]/1000),
                    QgsUnitTypes.LayoutMillimeters
                ))
            wLab.attemptResize(
                QgsLayoutSize(50, 8, QgsUnitTypes.LayoutMillimeters)
            )
            wLab.setId('wyn'+w+'_Lab')
            self.lay.addItem(wLab)

    def znajdz_bazy(self):
        '''Metoda szuka bazy danych w zalezności od nazwy layoutu w projekcie
        '''
        db_path = False
        self.mn = QgsProject.instance().layoutManager()
        self.lay = self.mn.layouts()[0]
        if len(self.mn.layouts()) != 1:
            self.iface.messageBar().pushMessage(
                'Błąd',
                'Obsługiwany jest tylko jeden layout w pliku projektu',
                Qgis.Critical,
                0
            )
            return False

        # jezeli ustawiamy map przegladowa dla obrebu, baza jest 2 poziomy
        # wyzej
        if self.lay.name()[:16] == 'MAPA_PRZEGLADOWA':
            if self.wydz is False:
                self.iface.messageBar().pushMessage(
                    'BŁĄD',
                    'Nie udało się odnaleźć warstwy WYDZ_POL w TOC',
                    Qgis.Critical,
                    10
                )
                return False

            db_path = znajdz_baze_do_wydz(self.iface, self.wydz)

        # a jezeli jakas mape dla gminy to baza powinna byc tylko jeden poziom
        # powyzej warstwy
        # elif self.lay.name() in self.mapy:
        else:
            db_path = znajdz_baze_do_wydz(self.iface, self.oddz)

            # self.iface.messageBar().pushMessage(
                # 'BŁĄD',
                # 'Nie rozpoznałem typu mapy, napewno masz kompatybilny layout?',
                # Qgis.Critical,
                # 10
            # )
            # return False

        if db_path is False:
            self.iface.messageBar().pushMessage(
                'BŁĄD',
                'Nie udało się odnaleźć bazy (w przegladadowej 2 poziomy, w innych 1 poziom wyzej)',
                Qgis.Critical,
                10
            )
            return False

        # sprawdz czy pobrana sciezka do bazy jest poprawna
        self.baza = Baza(db_path)
        if not self.baza.polacz():
            self.iface.messageBar().pushMessage(
                'BŁĄD',
                'Nie udało się połączyć z bazą',
                Qgis.Critical,
                10
            )
            return False
        return True

    def pobierz_meta(self):
        _pow = self.baza.pobierz_pow_oprac()
        _nagl = self.baza.pobierz_naglowek()
        self.baza.zamknij()

        self._nagl = {x[4]+x[5]: list(x[:4])+['0.00 ha   (0.0000 ha)']
                      for x in _nagl}

        # baza byla dlubana i sa zmiany w kwerendach
        if platform.system()[:3] == 'Win':
            _pow = [[x[0], x[2], x[4], x[5], x[6]] for x in _pow]

        pow_oprac = 0.000
        if _pow is not False:
            if len(_pow) > 0:
                pow_oprac = sum([p[2]+p[3]-p[4] for p in _pow])

        self._naglc = [
            _nagl[0][0],
            _nagl[0][1],
            _nagl[0][2],
            _nagl[0][3],
            pow_oprac,
        ]

        for p in _pow:
            if p[0] + p[1] in self._nagl:
                self._nagl[p[0]+p[1]][4] = \
                    str(round(p[2]+p[3]-p[4], 2)).replace(".", ",")+" ha    ("\
                    + \
                    str(round(p[2]+p[3]-p[4], 4)).replace(".", ",") +\
                    (4-len(str(round(p[2]+p[3]-p[4], 4)).split('.')[-1])) * \
                    '0' + " ha)"

    def zmien_meta_data(self):
        """Zmien date w mapie"""
        stan_na, ok = QInputDialog.getText(
            None, 'Podaj stan na:', 'Stan na:',
            text='01.01.'+str(datetime.now().year)
        )
        if not ok:
            self.zmien_meta()
            return
        self.zmien_meta(stan_na)

    def zmien_meta(self, stan=None):
        """metoda pomienia dane opisowe na tez zgone z baza taksatora dla
        danego obrebu lub gminy
        """
        kodList = [
            'zm-wojewodztwo',
            'zm-powiat',
            'zm-gmina',
            'zm-obreb',
            'zm-pow',
        ]

        if self.lay.name().upper()[:16] == 'MAPA_PRZEGLADOWA':
            for i, val in enumerate(kodList):
                it = self.lay.itemById(val)
                if it is not None:
                    it.setText(self._nagl[self.gmi+self.obr][i])

        elif self.lay.name().upper() in self.mapy:
            # pobierz unikalene nazwy z bazy
            woj = ', '.join(list(set([x[0] for x in self._nagl.values()])))
            powi = ', '.join(list(set([x[1] for x in self._nagl.values()])))
            gm = ', '.join(list(set([x[2] for x in self._nagl.values()])))
            pow_temp = self._naglc[4]
            pow_adm = str(round(pow_temp, 2)).replace(".", ",")+" ha    (" \
                + str(round(pow_temp, 4)).replace(".", ",") + \
                (4-len(str(round(pow_temp, 4)).split('.')[-1]))*'0' + " ha)"

            ogol = [woj, powi, gm, pow_adm, ]

            for i, val in enumerate(kodList[:3]+[kodList[4]]):
                it = self.lay.itemById(val)
                if it is not None:
                    it.setText(str(ogol[i]))

        # zmien stan na na poczatek nowego roku
        it = self.lay.itemById('zm-stan')
        if it is not None:
            if stan in [None, '']:
                stan = '01.01.' + str(datetime.now().year)
            it.setText(f'Stan na: {stan}')


def ustaw_leg(iface):
    atlas = False
    for key, val in QgsProject.instance().mapLayers().items():
        if key[:9] == 'ATLAS_AFT':
            atlas = val

    if atlas is False:
        iface.messageBar().pushMessage(
            'BŁĄD',
            'Nie udało się odnaleźć ATLAS_AFT',
            Qgis.Critical,
            10
        )
        return

    mn = QgsProject.instance().layoutManager()
    lay = mn.layouts()[0]
    it = lay.itemById('LEGENDA')
    if it is not None:
        oe = atlas.extent()
        szer = oe.width()
        wys = oe.height()
        # jezeli szerokosc obrebu jest wieksza niz wysokosc, srodkujemy
        # w pionie na wysokosc
        if wys < szer:
            szer = szer + (szer/10)
            wys_calk_m = (175.151 * szer) / 195.418
            poprawka_wys_m = wys_calk_m - wys
            poglad_ramka = QgsRectangle(
                oe.xMinimum()-((oe.width()/10)/2),
                oe.yMinimum()-(poprawka_wys_m/2),
                oe.xMaximum()+((oe.width()/10)/2),
                oe.yMaximum()+(poprawka_wys_m/2))
        else:
            wys = wys + (wys/10)
            szer_calk_m = (195.418 * wys) / 175.151
            poprawka_szer_m = szer_calk_m - szer
            poglad_ramka = QgsRectangle(
                oe.xMinimum()-(poprawka_szer_m/2),
                oe.yMinimum()-((oe.height()/10)/2),
                oe.xMaximum()+(poprawka_szer_m/2),
                oe.yMaximum()+((oe.height()/10)/2))

        it.setExtent(poglad_ramka)
        # it.setItemPosition(it.x(), popry+it.y(), 68.9, 78.8)

    lay.refresh()
