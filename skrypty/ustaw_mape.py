import os
import platform
import re
from datetime import datetime
from qgis.core import QgsProject, Qgis, QgsLayoutSize, QgsUnitTypes, \
    QgsRectangle, QgsLayoutItemMap, QgsLayoutPoint, QgsLayoutItemLabel
from lasr.skrypty.baza_wrapper import Baza, znajdz_baze_do_wydz
from PyQt5.QtGui import QFont, QColor
from PyQt5.QtWidgets import QInputDialog

_ARKUSZ_RE = re.compile(r'^A(\d+)$')


def dopisz_ark_do_nazwy(sciezka):
    '''Dopisuje przyrostek _ARK do nazwy pliku projektu (przed rozszerzeniem),
    o ile jeszcze go nie ma.'''
    folder, plik = os.path.split(sciezka)
    nazwa, ext = os.path.splitext(plik)
    if nazwa.endswith('_ARK'):
        return sciezka
    return os.path.join(folder, nazwa + '_ARK' + ext)


def zapisz_z_przyrostkiem_ark(iface, m):
    '''Jesli ostatnie wywolanie UstawMape.przesun_elem() wygenerowalo
    arkusze, dopisuje do nazwy pliku biezacego projektu przyrostek _ARK
    i zapisuje projekt pod nowa nazwa (usuwajac stary plik).'''
    if not m.arkusze:
        return

    proj = QgsProject.instance()
    stara_sciezka = proj.fileName()
    if not stara_sciezka:
        return

    nowa_sciezka = dopisz_ark_do_nazwy(stara_sciezka)
    if nowa_sciezka == stara_sciezka:
        return

    proj.write(nowa_sciezka)
    if os.path.isfile(stara_sciezka):
        os.remove(stara_sciezka)

    iface.messageBar().pushMessage(
        'OK',
        f'Wykryto {len(m.arkusze)} arkuszy — projekt zapisano jako '
        f'{os.path.basename(nowa_sciezka)}',
        Qgis.Success
    )


class UstawMape():
    def __init__(self, iface):
        self.iface = iface

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

    def _ramka_glowna(self, sr):
        '''Zwraca rekord ramki głównej mapy ze słownika sr (pole RAMKA='M',
        albo starsze 'Mr' dla zgodnosci wstecznej). Zwraca None i wyswietla
        czytelny blad w messageBar, jesli w MapRamie brakuje obu.'''
        for klucz in ('M', 'Mr'):
            if klucz in sr:
                return sr[klucz]

        self.iface.messageBar().pushMessage(
            'BŁĄD',
            "Nie znaleziono ramki głównej mapy w warstwie MapRam "
            "(brak obiektu z polem RAMKA='M')",
            Qgis.Critical,
            0
        )
        return None

    def _wykryj_arkusze(self, sr):
        '''Zwraca posortowana liste (numer, klucz) dla poligonow-arkuszy
        w MapRamie (pole RAMKA='A1', 'A2', ...).'''
        arkusze = []
        for klucz in sr:
            dopasowanie = _ARKUSZ_RE.match(klucz)
            if dopasowanie:
                arkusze.append((int(dopasowanie.group(1)), klucz))
        arkusze.sort()
        return arkusze

    def _zastosuj_ramke(self, lay, srm, sr, pomin_klucze):
        '''Ustawia rozmiar strony, ramki i widok GLOWNA layoutu `lay` na
        podstawie rekordu ramki glownej `srm`, i dopisuje wyniesienia dla
        pozostalych poligonow z MapRamu (pomijajac klucze z pomin_klucze,
        czyli glowna ramke i pozostale arkusze)'''

        pg_coll = lay.pageCollection()
        pg = pg_coll.page(0)
        wys_stara = pg_coll.maximumPageSize().height()
        szer_stara = pg_coll.maximumPageWidth()

        szer_nowa = (srm[2] / (srm[6]/1000)) + 10 + 10
        wys_nowa = (srm[3] / (srm[6]/1000)) + 10 + 80 + 10
        pg.setPageSize(
            QgsLayoutSize(szer_nowa, wys_nowa, QgsUnitTypes.LayoutMillimeters)
        )
        lay.refresh()

        poprx = szer_nowa - szer_stara
        popry = wys_nowa - wys_stara

        # lista id elementow nie przesuwanych w pionie
        wysPomin = ['ramka', 'NORTH_N', 'NORTH_ARROW', 'GLOWNA']
        # lista id z elementami do przesuniecia w poziomie
        szerPrzes = ['NORTH_N', 'NORTH_ARROW', 'ramkaP', 'zamawiajacy',
                     'wykonawca', ]

        # przesun elementy w pionie
        for it in lay.items():
            try:
                if it.id() not in wysPomin and len(it.id()) > 2:
                    it.attemptMoveBy(0, popry)
                if it.id() in szerPrzes and len(it.id()) > 2:
                    it.attemptMoveBy(poprx, 0)
            except:  # nopep8
                pass

        ramka = lay.itemById('ramka')
        ramka.attemptResize(
                QgsLayoutSize(szer_nowa-10,
                              wys_nowa-10,
                              QgsUnitTypes.LayoutMillimeters)
        )

        ramka = lay.itemById('ramkaD')
        ramka.attemptResize(
            QgsLayoutSize(szer_nowa-10, 80, QgsUnitTypes.LayoutMillimeters)
        )

        # ustaw mapke pogladowa o ile taka znajduje sie na mapie
        it = lay.itemById('POGLAD')
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
        it = lay.itemById('GLOWNA')

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
        for w in [k for k in sorted(sr.keys()) if k not in pomin_klucze]:
            wyn = sr[w]
            wyn_it = QgsLayoutItemMap(lay)
            wyn_it.attemptMove(
                QgsLayoutPoint(
                    int(10+(wyn[4]-srm[0])/(srm[6]/1000)),
                    int(10+(srm[1]-wyn[5])/(srm[6]/1000)),
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
            lay.addItem(wyn_it)

            wLab = QgsLayoutItemLabel(lay)
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
            lay.addItem(wLab)

    def przesun_elem(self):  # noqa
        '''Przesuwa elementy mapy i generuje wyniesienia/arkusze na
        podstawie warstwy MapRam, niezależnie od rodzaju mapy.

        Jeżeli w MapRamie znajdują się poligony-arkusze (RAMKA='A1',
        'A2', ...), zamiast ustawiać bieżący layout, klonuje go po jednym
        razie na arkusz (nazwa layoutu + "_ARK_<n>"), ustawia każdy klon
        osobno i usuwa oryginalny (bazowy) layout — wynikowe layouty
        trafiają do self.layouty_do_eksportu.'''

        # slownik z rozmiarami mapy i wydzielen
        # sl[''] = [xpocz, ypocz, szer, wys, xmapa, ymapa]
        sr = {}
        self.arkusze = []
        self.layouty_do_eksportu = []
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

        self.arkusze = self._wykryj_arkusze(sr)

        if not self.arkusze:
            srm = self._ramka_glowna(sr)
            if srm is None:
                return False

            etykieta = self.lay.itemById('zm-obreb-arkusz')
            if etykieta is not None:
                etykieta.setText('')

            self._zastosuj_ramke(self.lay, srm, sr, {'M', 'Mr'})
            self.layouty_do_eksportu = [self.lay]
            return True

        # tryb arkuszy: klonujemy layout po jednym razie na kazdy poligon
        # A1, A2, ... i usuwamy oryginalny (bazowy) layout
        nazwa_bazowa = self.lay.name()
        pomin_klucze = {klucz for _, klucz in self.arkusze} | {'M', 'Mr'}

        for numer, klucz in self.arkusze:
            nazwa_ark = f'{nazwa_bazowa}_ARK_{numer}'
            istniejacy = self.mn.layoutByName(nazwa_ark)
            if istniejacy is not None:
                self.mn.removeLayout(istniejacy)

            klon = self.lay.clone()
            klon.setName(nazwa_ark)
            self.mn.addLayout(klon)

            etykieta = klon.itemById('zm-obreb-arkusz')
            if etykieta is not None:
                etykieta.setText(f'Arkusz {numer}')

            self._zastosuj_ramke(klon, sr[klucz], sr, pomin_klucze)
            self.layouty_do_eksportu.append(klon)

        self.mn.removeLayout(self.lay)
        self.lay = self.layouty_do_eksportu[0]
        return True

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
        else:
            db_path = znajdz_baze_do_wydz(self.iface, self.oddz)

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

        else:
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
