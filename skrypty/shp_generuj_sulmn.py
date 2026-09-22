import os
import platform

from qgis.core import QgsVectorLayer, QgsVectorFileWriter, Qgis, QgsProject, \
    QgsCoordinateReferenceSystem, QgsField, QgsMessageLog, QgsSpatialIndex, \
    QgsFeature, QgsGeometry, QgsPointXY

import processing

from collections import defaultdict, Counter
from PyQt5.QtWidgets import QFileDialog, QMessageBox
from PyQt5.QtCore import QVariant, QMetaType

from .baza_wrapper import Baza, znajdz_baze_do_wydz


class recursivedefaultdict(defaultdict):
    def __init__(self):
        self.default_factory = type(self)


class GenerujSulmn(object):
    def __init__(self, iface):
        self.iface = iface

        self.wydz = False
        self.kat = False
        wydz_pol = None
        wydz_dopisane = None
        for lyr in QgsProject.instance().mapLayers().values():
            if lyr.name() == "WYDZ_POL":
                wydz_pol = lyr
            elif lyr.name() == "WYDZ_DOPISANE":
                wydz_dopisane = lyr

        if wydz_pol and wydz_dopisane:
            odp = QMessageBox.question(
                self.iface.mainWindow(),
                "Wybierz warstwę",
                "W TOC znajdują się obie warstwy: WYDZ_POL i "
                "WYDZ_DOPISANE.\nUżyć WYDZ_POL?\n"
                "(Nie = użyj WYDZ_DOPISANE)",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.Yes,
            )
            self.wydz = wydz_pol if odp == QMessageBox.Yes else wydz_dopisane
        elif wydz_pol:
            self.wydz = wydz_pol
        elif wydz_dopisane:
            self.wydz = wydz_dopisane

        if self.wydz is False:
            self.iface.messageBar().pushMessage(
                'Error', "Brak warstwy WYDZ_POL/WYDZ_DOPISANE w TOC!",
                level=Qgis.Critical)
            return

        self.wydz.dataProvider().setEncoding('UTF-8')
        self.wydz_path = self.wydz.dataProvider().dataSourceUri().split("|")[0]
        self.kat = os.path.dirname(self.wydz_path)

        self.ustawProj()  # zadeklaruj wszystkie niezbedne zmienne dla klasy

    # noinspection PyPep8Naming
    def isNone(self, a, typ='s'):
        empt = False
        if a in [None, 'NULL', '', ]:
            empt = True
        elif isinstance(a, QVariant):
            if a.isNull():
                empt = True

        if empt:
            if typ == 's':
                return ''
            return 0

        return a

    def ustawProj(self):
        # self.oddz = False
        self.ls = False
        self.pnsw = False
        self.linie = False
        kat = self.kat

        # pobierz od uzyszkodnika katalog docelowy na sulmn
        self.katS = QFileDialog.getExistingDirectory(
            self.iface.mainWindow(),
            "Katalog do zapisania danych:",
            kat)

        # stworz katalog roboczy jezeli nie istnieje
        self.kattemp = os.path.join(self.katS, "temp")
        if not os.path.isdir(os.path.join(self.katS, "temp")):
            os.mkdir(os.path.join(self.katS, "temp"))

        self.crs = QgsCoordinateReferenceSystem("epsg:2180")

        self.slPol = {
            'POW': ['ID', 'ADR_BDL', 'L_EWID'],
            'DZ_EWID': ['ID', 'ADR_ADM', 'NR_EW', ],
            'UZYTKI': ['ID', 'ADR_ADM', 'NR_EW', 'NR_KONT', ],
            # 'ODDZIAL': ['ID', 'ADR_BDL'],
            'PNSW':
                ['ID', 'ADR_BDL', 'KOD_PNSW', 'NR_PNSW', 'NR_EW', 'ADR_ADM'],
            'LINIE': ['ID', 'SZER', 'KOD'],
        }

    def sprawdzDane(self):
        """Metoda sprawdza czy w katalogu z wydz_pol sa inne niezbedne warstwy
        i czy posiadaja odpowiednia strukture
        """

        # sprawdz warstwy niezbedne
        warstwa = ['DZKAT',
                   'LS',
                   # 'ODDZ',
                   ]
        for w in warstwa:
            if not os.path.isfile(os.path.join(self.kat, w+'.shp')):
                self.iface.messageBar().pushMessage(
                    'Error',
                    "Brak warstwy "+w+" w katalogu z WYDZ_POL!",
                    level=Qgis.Critical)
                return False

        self.dzkat = QgsVectorLayer(
            os.path.join(self.kat, "DZKAT.shp"), "DZKAT", "ogr")
        self.ls = QgsVectorLayer(os.path.join(self.kat, "LS.shp"), "LS", "ogr")
        self.ls_dp = self.ls.dataProvider()
        self.ls_dp.setEncoding('UTF-8')
        # self.oddz = QgsVectorLayer(
        #   os.path.join(self.kat, "ODDZ.shp"), "ODDZ", "ogr")

        dzkat_pola = [
            'COUNTY', 'DISTRICT', 'MUNICIP', 'COMMUNITY', 'PARCELNR'
        ]

        if len([x.name() for x in self.dzkat.fields()
                if x.name() in dzkat_pola]) != len(dzkat_pola):
            self.iface.messageBar().pushMessage(
                'Error',
                u'Brakuje niezbędnych kolumn w DZKAT: '+','.join(
                    [w for w in dzkat_pola if w not in
                     [x.name() for x in self.dzkat.fields().toList()]]),
                level=Qgis.Critical)
            return False

        wydz_pola = ['ADR_LES', 'L_EWID', ]
        if len([x.name() for x in self.wydz.fields()
                if x.name() in wydz_pola]) != len(wydz_pola):
            self.iface.messageBar().pushMessage(
                'Error',
                u'Brakuje niezbędnych kolumn w WYDZ_POL: '+','.join(
                    [w for w in wydz_pola if w not in
                     [x.name() for x in self.wydz.fields().toList()]]),
                level=Qgis.Critical)
            return False

        ls_pola = [
            'COMMUNITY',
            'COUNTY',
            'MUNICIP',
            'DISTRICT',
            'PARCELNR',
            'LANDID',
            'SQ',
            'AU',
        ]

        if len([x.name() for x in self.ls.fields() if x.name() in ls_pola]) !=\
                len(ls_pola):

            self.iface.messageBar().pushMessage(
                'Error',
                u'Brakuje niezbędnych kolumn w LS-ach: '+','.join(
                    [w for w in ls_pola if w not in
                     [x.name() for x in self.ls.fields().toList()]]),
                level=Qgis.Critical)
            return False

        # ------------------
        # POMIJAMY WYKONANIE WARSTWY ODDZ - taka warstwa tworzona jest
        # automatycznie we wtyczcie do sprawdzana sulmn - MAPA PU
        # ------------------

        if os.path.isfile(os.path.join(self.kat, 'PNSW.shp')):
            self.pnsw = QgsVectorLayer(
                os.path.join(self.kat, 'PNSW.shp'), 'pnsw', 'ogr')

            pnsw_pola = ['ADR_BDL', 'KOD_PNSW', 'NR_PNSW', 'ID', ]
            if len([x.name() for x in self.pnsw.fields()
                    if x.name() in pnsw_pola]) != 4:
                self.iface.messageBar().pushMessage(
                    'Error',
                    'Brakuje niezbędnych kolumn w PNSW: '+','.join([
                        w for w in pnsw_pola if w not in
                        [x.name() for x in self.pnsw.fields().toList()]]),
                    level=Qgis.Critical)
                return False

        if os.path.isfile(os.path.join(self.kat, 'LINIE.shp')):
            self.linie = QgsVectorLayer(os.path.join(self.kat, 'LINIE.shp'),
                                        'linie',
                                        'ogr')

        # spradz polaczenie z baza na samym koncu
        baza_sc = znajdz_baze_do_wydz(self.iface, self.wydz)
        self.baza = Baza(baza_sc)
        if not self.baza.polacz():
            self.iface.messageBar().pushMessage(
                'Error',
                'Nie udało się połączyć z bazą taksatora',
                level=Qgis.Critical)
            return False

        # Jezeli doszilsmy do konca zwroc OK
        return True

    def pobierz(self):
        self.ospkt_lista = self.baza.pobierz_osob_pkt()

        self.slUz = {k[12]+'.'+self.isNone(k[9])+self.isNone(k[10]): int(k[8])
                     for k in self.baza.uzytki()}

    def przygotujRobocze(self):
        # zapisz warstwy
        sl = {
            'POW': self.wydz,
            'UZYTKI': self.ls,
            'DZ_EWID': self.dzkat,
            'PNSW': self.pnsw,
            # 'oddz': self.oddz,
        }
        for w in sl.keys():
            if sl[w]:
                QgsVectorFileWriter.writeAsVectorFormat(
                    sl[w],
                    os.path.join(self.katS, 'temp', w+"_temp.shp"),
                    'UTF-8',
                    self.crs,
                    'ESRI Shapefile',
                )

        self.wydz = QgsVectorLayer(
            os.path.join(self.katS, 'temp', "POW_temp.shp"), "POW_temp",
            "ogr")
        self.dzkat = QgsVectorLayer(
            os.path.join(self.katS, 'temp', "DZ_EWID_temp.shp"),
            "DZ_EWID_temp",
            "ogr")
        self.ls = QgsVectorLayer(
            os.path.join(self.katS, 'temp', "UZYTKI_temp.shp"), "LS_temp",
            "ogr")
        if self.pnsw:
            self.pnsw = QgsVectorLayer(
                os.path.join(self.katS, 'temp', "PNSW_temp.shp"), "PNSW_temp",
                "ogr")
        if self.linie:
            self.linie = QgsVectorLayer(
                os.path.join(self.katS, 'temp', "LINIE_temp.shp"),
                "LINIE_temp",
                "ogr")

        # noinspection PyArgumentList
        slPolDef = {
            'ID': QgsField("ID", QMetaType.Type.Int),
            'NR_KONT': QgsField("NR_KONT", QMetaType.Type.Int),
            'NR_PNSW': QgsField("NR_PNSW", QMetaType.Type.Int),
            'NR_OSOBL': QgsField("NR_OSOBL", QMetaType.Type.Int),
            'ADR_BDL': QgsField("ADR_BDL", QMetaType.Type.QString, len=25),
            'ADR_ADM': QgsField("ADR_ADM", QMetaType.Type.QString, len=25),
            'L_EWID': QgsField("L_EWID", QMetaType.Type.QString, len=1),
            'NR_EW': QgsField("NR_EW", QMetaType.Type.QString, len=25),
            'KOD_PNSW': QgsField("KOD_PNSW", QMetaType.Type.QString, len=12),
            'KOD_OSOBL': QgsField("KOD_OSOBL", QMetaType.Type.QString, len=12),
            'KOD': QgsField("KOD", QMetaType.Type.QString, len=12),
            'SZER': QgsField("SZER", QMetaType.Type.Double, 'double', 4, 1),
        }

        # popraw odwolania do aktualnych danych
        sl = {
            'POW': self.wydz,
            'UZYTKI': self.ls,
            'DZ_EWID': self.dzkat,
            'PNSW': self.pnsw,
            # 'oddz': self.oddz,
        }

        # sprawdz czy w warstwach sa wszystkie pola, jesli nie dodaj brakujace
        for key in self.slPol.keys():
            warstwa = False
            if key in sl:
                warstwa = sl[key]

            if warstwa:
                niewpisane = [x for x in self.slPol[key] if x not in
                              [f.name() for f in warstwa.fields().toList()]
                              ]
                if len(niewpisane) > 0:
                    warstwa.startEditing()
                    warstwaDP = warstwa.dataProvider()
                    warstwaDP.addAttributes([slPolDef[x] for x in niewpisane])
                    warstwa.updateFields()
                    warstwa.commitChanges()

    def przygotujDzkat(self):
        fnm = self.dzkat.dataProvider().fieldNameMap()
        zmiany = {}
        for f in self.dzkat.getFeatures():
            zmiany[f.id()] = {
                fnm['ADR_ADM']:
                "-".join([
                    f['COUNTY'],
                    f['DISTRICT'],
                    f['MUNICIP'],
                    f['COMMUNITY'],
                ]),
                fnm['NR_EW']: f['PARCELNR'],
                fnm['ID']: f.id()+1
            }

        for k, it in zmiany.items():
            self.dzkat.dataProvider().changeAttributeValues({k: it})
        self.przygOstat(self.dzkat, 'DZ_EWID')

    def przygOstat(self, warstwa, nazwa):
        # usun nadmiarowe pola i zapisz we wskazanym folderze
        warstwa.startEditing()
        nadmiarowe = sorted([warstwa.dataProvider().fieldNameIndex(x.name())
                             for x in warstwa.fields().toList()
                             if x.name() not in self.slPol[nazwa]],
                            reverse=True)
        warstwa.dataProvider().deleteAttributes(nadmiarowe)
        warstwa.updateFields()
        warstwa.commitChanges()

        error = QgsVectorFileWriter.writeAsVectorFormat(
            warstwa,
            os.path.join(self.katS, nazwa+".shp"),
            "UTF-8",
            self.crs,
            "ESRI Shapefile")
        if error == QgsVectorFileWriter.NoError:
            QgsMessageLog.logMessage('Utworzono warstwę '+nazwa, 'LCH')
        else:
            QgsMessageLog.logMessage(
                'UWAGA - coś poszło nie tak z warstwą ' + nazwa +
                ' - nie została zapisana', 'LCH')

    def przygotujWydz(self):
        fnm = self.wydz.dataProvider().fieldNameMap()
        zmiany = {}
        for f in self.wydz.getFeatures():
            zmiany[f.id()] = {
                fnm['ADR_BDL']: f['ADR_LES'],
                fnm['ID']: f.id()+1,
            }

        for k, it in zmiany.items():
            self.wydz.dataProvider().changeAttributeValues({k: it})

        self.przygOstat(self.wydz, 'POW')

    def przygotujUzytki(self):
        fnm = self.ls.dataProvider().fieldNameMap()
        zmiany = {}
        for f in self.ls.getFeatures():
            adr1 = "".join(map(str, [
                f['COUNTY'], f['DISTRICT'], f['MUNICIP'], f['COMMUNITY']
            ]))
            ark = '' if str(f['ARK']) == 'NULL' else str(f['ARK'])
            dz = f['PARCELNR']
            klu = f['AU'] + self.isNone(f['SQ'])

            if ark != '':
                kod_landid = ".".join([adr1, ark, dz, klu])
            else:
                kod_landid = ".".join([adr1, dz, klu])

            nr_kont = -1
            if kod_landid in self.slUz:
                nr_kont = self.slUz[kod_landid]

            if nr_kont == -1:
                QgsMessageLog.logMessage(
                    f'Nie odnaleziono konturu w bazie: {kod_landid}', "LCH"
                )

            zmiany[f.id()] = {
                fnm['ADR_ADM']:
                "-".join([
                    f['COUNTY'],
                    f['DISTRICT'],
                    f['MUNICIP'],
                    f['COMMUNITY'],
                ]),
                fnm['NR_EW']: f['PARCELNR'],
                fnm['NR_KONT']: nr_kont,
                fnm['ID']: f.id()+1,
            }

        for k, it in zmiany.items():
            self.ls.dataProvider().changeAttributeValues({k: it})

        self.przygOstat(self.ls, 'UZYTKI')

    def przygotujPnsw(self):
        if not self.pnsw:
            return False

        self.slKodyPnsw = {
            "dL": "D LUKA",
            "G": "GNIA",
            "K": 'KĘPA',
            "dP": "D PRZEZ",
            "L": "LUKA",
            "Bg": "BAGNO",
            "Rm": "REMIZA",
            "Sz": "SZK",
            "Go": "OD GNIA",
            'Pł': 'POL ŁOW',
            "Gcz": "GNIA CZ",
            "Gocz": "OD G CZ",
        }

        # przygotuj spatial index dla dzkat
        dzkat_si = QgsSpatialIndex(self.dzkat.getFeatures())
        wydz_si = QgsSpatialIndex(self.wydz.getFeatures())

        fnm = self.pnsw.dataProvider().fieldNameMap()
        zmiany = {}
        for f in self.pnsw.getFeatures():
            # przetnij pnsw z dzialka i wpisz pierwsza z brzegu
            dzkat = -1
            dzkat_adr = '0-0-0-0'
            adr_les = 'O00000'

            inters = dzkat_si.intersects(f.geometry().boundingBox())
            for ids in inters:
                dz = self.dzkat.getFeature(ids)
                if f.geometry().intersects(dz.geometry()):
                    dzkat = dz['NR_EW']
                    dzkat_adr = dz['ADR_ADM']
                    break

            # przetnij pnsw z wydz_pol i wpisz adr_les
            inters = wydz_si.intersects(f.geometry().boundingBox())
            for ids in inters:
                w = self.wydz.getFeature(ids)
                try:
                    if f.geometry().buffer(-0.1, 1).intersects(w.geometry()):
                        adr_les = w['ADR_BDL']
                        break
                except:  # noqa
                    print('PNSW leży na wydz z błędną geometrią??')

            zmiany[f.id()] = {
                fnm['ADR_ADM']: dzkat_adr,
                fnm['ADR_BDL']: adr_les,
                fnm['NR_EW']: dzkat,
                fnm['ID']: f.id()+1,
                fnm['KOD_PNSW']: self.slKodyPnsw[f['KOD_PNSW']],
            }

        for k, it in zmiany.items():
            self.pnsw.dataProvider().changeAttributeValues({k: it})
        self.przygOstat(self.pnsw, 'PNSW')

    def przygotujOsPkt(self):
        # przygotuj warstwe osobliwosci pkt na podstawie spisu w bazie
        try:
            max_points = Counter([x[0] for x in self.ospkt_lista]
                                 ).most_common()[0][1]
        except:  # noqa
            max_points = 0

        if max_points == 0:
            return

        processing.run(
            "qgis:randompointsinsidepolygons",
            {'INPUT':  os.path.join(self.katS, 'temp', 'POW_temp.shp'),
             'STRATEGY': 0,
             'EXPRESSION': max_points+3,
             'MIN_DISTANCE': 2,
             'OUTPUT': os.path.join(self.katS,
                                    'temp', 'PKTOS_temp.shp'),
             }
        )
        pkttemp = processing.run(
            "qgis:intersection",
            {'INPUT': os.path.join(self.katS, 'temp',
                                   'PKTOS_temp.shp'),
             'OVERLAY': os.path.join(self.katS, 'temp',
                                     'POW_temp.shp'),
             'INPUT_FIELDS': '',
             'OVERLAY_FIELDS': '',
             'OUTPUT':  os.path.join(self.katS, 'temp',
                                     'PKTOSwydz_temp.shp'),
             }
        )

        pkttemp = QgsVectorLayer(
            os.path.join(self.katS, 'temp', 'PKTOSwydz_temp.shp'),
            'ospkt_temp', 'ogr')

        slPktOs = {}
        for f in pkttemp.getFeatures():
            if f['ADR_BDL'] not in slPktOs:
                slPktOs[f['ADR_BDL']] = []
            slPktOs[f['ADR_BDL']].append([
                f.geometry().boundingBox().xMinimum(),
                f.geometry().boundingBox().yMinimum()
            ])

        self.pktos = QgsVectorLayer(
            "Point?crs=epsg:2180&index=yes",
            "ospkt",
            "memory")
        self.pktosPr = self.pktos.dataProvider()
        self.pktos.startEditing()
        self.pktosPr.addAttributes([
            QgsField("ID", QMetaType.Type.Int),
            QgsField("ADR_BDL", QMetaType.Type.QString, len=25),
            QgsField("KOD_OSOBL", QMetaType.Type.QString, len=12),
            QgsField("NR_OSOBL", QMetaType.Type.Int),
        ])
        self.pktos.updateFields()

        etykFeat = []
        iditer = 1
        idadr = 0
        adr = ""
        for pkt in self.ospkt_lista:
            if adr != pkt[0]:
                idadr = 0

            feat = QgsFeature()
            try:
                # jeżeli wygenerowanych pkt jest mniej niz wpisanych roslin w
                # bazie to zacznik brac wygenerowane pkt od poczatku.
                # Przypadek ma miejsce gdy są małe wydzielenia a mają duzo ops
                if idadr > len(slPktOs[pkt[0]]) - 1:
                    idadr = 0
                geom = QgsGeometry().fromPointXY(QgsPointXY(
                    slPktOs[pkt[0]][idadr][0],
                    slPktOs[pkt[0]][idadr][1]))

                feat.setGeometry(geom)
                feat.setFields(self.pktos.fields())
                feat['ID'] = iditer
                feat['ADR_BDL'] = pkt[0]
                feat['NR_OSOBL'] = pkt[1]
                feat['KOD_OSOBL'] = pkt[2]
                etykFeat.append(feat)
                idadr += 1
                adr = pkt[0]
                iditer += 1

            except Exception:
                pass

        self.pktosPr.addFeatures(etykFeat)
        self.pktos.commitChanges()

        # noinspection PyTypeChecker
        QgsVectorFileWriter.writeAsVectorFormat(
            self.pktos,
            os.path.join(self.katS, "OS_PKT.shp"),
            "UTF-8",
            self.crs,
            "ESRI Shapefile")

    def przygotujOpodst(self):
        # processing.runalg('saga:intersect',
        #                   os.path.join(self.katS, 'POW.shp'),
        #                   os.path.join(self.katS, 'UZYTKI.shp'),
        #                   True,
        #                   os.path.join(self.katS, 'O_PODST.shp'),
        #                   )

        # self.opodst = QgsVectorLayer(os.path.join(self.katS, 'O_PODST.shp'),
                                     # 'O_PODST', 'ogr')

        alg_params = {
            '-t': False,
            'GRASS_MIN_AREA_PARAMETER': 0.1,
            'GRASS_OUTPUT_TYPE_PARAMETER': 0,
            'GRASS_REGION_PARAMETER': None,
            'GRASS_SNAP_TOLERANCE_PARAMETER': 0.01,
            'GRASS_VECTOR_DSCO': '',
            'GRASS_VECTOR_EXPORT_NOCAT': False,
            'GRASS_VECTOR_LCO': '',
            'ainput': os.path.join(self.katS, 'POW.shp'),
            'atype': 0,
            'binput': os.path.join(self.katS, 'UZYTKI.shp'),
            'btype': 0,
            'operator': 0,
            'snap': 0.01,
            'output': os.path.join(self.katS,
                                   'temp',
                                   'O_PODST_geom_not_fixed.shp')
        }
        processing.run('grass7:v.overlay', alg_params)
        processing.run(
            "native:fixgeometries",
            {'INPUT': os.path.join(self.katS,
                                   'temp',
                                   'O_PODST_geom_not_fixed.shp'),
             'METHOD':0,
             'OUTPUT': os.path.join(self.katS, 'O_PODST.shp')
             }
        )

        self.opodst = QgsVectorLayer(
            os.path.join(self.katS, 'O_PODST.shp'),
            'o_podst',
            'ogr')

        if platform.system()[:3] == 'Win':
            self.opodst.dataProvider().setEncoding('UTF-8')
        fnm = self.opodst.dataProvider().fieldNameMap()
        self.opodst.startEditing()
        for old, id in fnm.items():
            if old[:2] in ['a_', 'b_', ]:
                self.opodst.renameAttribute(id, old[2:])
        self.opodst.commitChanges()

        self.opodst.startEditing()
        self.opodst.updateFields()

        # skasuj nadmiarowe pola
        nadmiarowe = sorted(
            [self.opodst.dataProvider().fieldNameIndex(x.name())
             for x in self.opodst.fields().toList()
             if x.name() not in ['ID',
                                 'ADR_BDL',
                                 'ADR_ADM',
                                 'NR_EW',
                                 'NR_KONT',
                                 ]],
        )

        self.opodst.dataProvider().deleteAttributes(nadmiarowe)
        self.opodst.updateFields()
        self.opodst.commitChanges()
        fnm = self.opodst.dataProvider().fieldNameMap()

        # uaktualnij wszystkie id w warstwie
        zmiany = {}
        for f in self.opodst.getFeatures():
            zmiany[f.id()] = {fnm['ID']: f.id()+1}

        for k, it in zmiany.items():
            self.opodst.dataProvider().changeAttributeValues({k: it})

        QgsMessageLog.logMessage('Utworzono warstwę O_PODST', 'LCH')

    def przygotujUzytkiOpodst(self):

        processing.run(
            "native:dissolve",
            {
                'INPUT':self.opodst,
                'FIELD': ['ADR_ADM','NR_EW','NR_KONT'],
                'SEPARATE_DISJOINT': False,
                'OUTPUT': os.path.join(self.katS, "UZYTKI.shp"),
            })

        uz = QgsVectorLayer(
            os.path.join(self.katS, 'UZYTKI.shp'), 'uzytki', 'ogr'
        )

        uz.startEditing()
        uz.updateFields()
        # skasuj nadmiarowe pola
        nadmiarowe = sorted(
            [uz.dataProvider().fieldNameIndex(x.name())
             for x in uz.fields().toList()
             if x.name() not in ['ID', 'ADR_ADM', 'NR_EW', 'NR_KONT', ]],
        )

        uz.dataProvider().deleteAttributes(nadmiarowe)
        uz.updateFields()

        zmiany = {}
        fnm = uz.dataProvider().fieldNameMap()
        for f in uz.getFeatures():
            zmiany[f.id()] = {fnm['ID']: f.id()+1}

        for k, it in zmiany.items():
            uz.dataProvider().changeAttributeValues({k: it})
        uz.commitChanges()

    def generujWarstwy(self):
        # metoda zbiorcza do wygenerowania wszystkich warstwy do SULMN
        self.iface.messageBar().pushMessage(
            'Przetwarzam', 'DZKAT', Qgis.Success,
        )
        self.przygotujDzkat()
        self.iface.messageBar().clearWidgets()
        self.iface.messageBar().pushMessage(
            'Przetwarzam', 'WYDZ', Qgis.Success,
        )
        self.przygotujWydz()
        self.iface.messageBar().clearWidgets()
        self.iface.messageBar().pushMessage(
            'Przetwarzam', 'Uzytki', Qgis.Success,
        )
        self.przygotujUzytki()
        self.iface.messageBar().clearWidgets()
        self.iface.messageBar().pushMessage(
            'Przetwarzam', 'PNSW', Qgis.Success,
        )
        self.przygotujPnsw()
        self.iface.messageBar().clearWidgets()
        self.iface.messageBar().pushMessage(
            'Przetwarzam', 'OsPKT', Qgis.Success,
        )
        self.przygotujOsPkt()
        self.iface.messageBar().clearWidgets()
        self.iface.messageBar().pushMessage(
            'Przetwarzam', 'O_PODST', Qgis.Success,
        )
        self.przygotujOpodst()
        self.iface.messageBar().clearWidgets()
        self.iface.messageBar().pushMessage(
            'Przetwarzam', 'DOTNIJ_UZYTKI', Qgis.Success,
        )
        self.przygotujUzytkiOpodst()
        self.iface.messageBar().clearWidgets()
        self.iface.messageBar().pushMessage(
            'ZAKONCZONO', 'sukcesem', Qgis.Success, 10
        )

        self.iface.messageBar().pushMessage(
            'OK', 'Zakończono generowanie SULMN', level=Qgis.Success)
