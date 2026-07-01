import os
import shutil
from qgis.core import QgsProject, Qgis, QgsVectorFileWriter, QgsVectorLayer,\
    QgsCoordinateReferenceSystem, QgsExpression, QgsFeatureRequest, \
    QgsSpatialIndex, QgsField
from PyQt5.QtWidgets import (QFileDialog, QMessageBox, QDialog,
                              QDialogButtonBox, QVBoxLayout, QListWidget,
                              QListWidgetItem, QLabel)
from PyQt5.QtCore import Qt, QVariant
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


class _WybierzWarstwDialog(QDialog):
    DOMYSLNE = {
        "LS", "DZKAT", "WYDZ", "PNSW", "OBR", "ODDZ", "KLU", "UZYTKI",
    }

    def __init__(self, parent, znalezione):
        super().__init__(parent)
        self.setWindowTitle('Wybierz warstwy do połączenia')
        self.setMinimumWidth(300)

        layout = QVBoxLayout()
        layout.addWidget(QLabel('Zaznacz warstwy do połączenia:'))

        self.lista = QListWidget()
        for nazwa in sorted(znalezione):
            item = QListWidgetItem(nazwa)
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
            stan = Qt.Checked if nazwa in self.DOMYSLNE else Qt.Unchecked
            item.setCheckState(stan)
            self.lista.addItem(item)

        layout.addWidget(self.lista)

        przyciski = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        przyciski.accepted.connect(self.accept)
        przyciski.rejected.connect(self.reject)
        layout.addWidget(przyciski)

        self.setLayout(layout)

    def wybrane(self):
        return [
            self.lista.item(i).text()
            for i in range(self.lista.count())
            if self.lista.item(i).checkState() == Qt.Checked
        ]


def _kopiuj_shp(src, dst):
    """Kopiuje plik SHP wraz z plikami towarzyszącymi."""
    base_src = src[:-4]
    base_dst = dst[:-4]
    for ext in ['shp', 'dbf', 'prj', 'shx', 'cpg']:
        s = base_src + '.' + ext
        if os.path.isfile(s):
            shutil.copy(s, base_dst + '.' + ext)


def _scal_liste(pliki, nazwa, out, iface):
    """Scala lub kopiuje listę plików SHP do folderu out."""
    if len(pliki) == 1:
        _kopiuj_shp(pliki[0], os.path.join(out, nazwa + ".shp"))
    elif len(pliki) > 1:
        processing.run(
            "native:mergevectorlayers",
            {
                'LAYERS': pliki,
                'CRS': None,
                'OUTPUT': os.path.join(out, nazwa + ".shp"),
            }
        )


def _polacz_gmina(iface, kat, z_ogolne=False):
    """Tryb 1: folder gminy → foldery obrębów → SHP/ → scal wg stałej listy."""
    nazwy = [
        "WYDZ_POL",
        "WYDZ_OPS",
        "LINIE",
        "PNSW",
        "DZKAT",
        "DZKAT_OPS",
        "KAS",
        "KLU_AFT",
        "ODDZ",
        "LIN_ODDZ",
    ]

    gmi = os.path.basename(kat)
    out = os.path.abspath(os.path.join(kat, "..", gmi + "_GIS"))
    os.makedirs(out, exist_ok=True)

    shp_dirs = []
    for d in sorted(os.listdir(kat)):
        if d == 'OGOLNE':
            continue
        child = os.path.join(kat, d)
        if os.path.isdir(child) and os.path.isdir(os.path.join(child, 'SHP')):
            shp_dirs.append(os.path.join(child, 'SHP'))

    braki = []
    for n in nazwy:
        pliki = [
            os.path.join(d, n + ".shp")
            for d in shp_dirs
            if os.path.isfile(os.path.join(d, n + ".shp"))
        ]
        if not pliki:
            braki.append(n)
        else:
            _scal_liste(pliki, n, out, iface)

    if z_ogolne:
        ogolne_dir = os.path.join(kat, 'OGOLNE')
        if os.path.isdir(ogolne_dir):
            for f in sorted(os.listdir(ogolne_dir)):
                if f.lower().endswith('.shp'):
                    _kopiuj_shp(os.path.join(ogolne_dir, f), os.path.join(out, f))

    if braki:
        iface.messageBar().pushMessage(
            'Uwaga',
            'Nie znaleziono plików: ' + ', '.join(braki),
            Qgis.Warning)

    iface.messageBar().pushMessage('OK', 'Połączono warstwy (tryb gminy)', Qgis.Success)


def _polacz_region(iface, kat):
    """Tryb 2: folder z gminami → SHP/ każdej gminy → dialog wyboru → scal."""
    pliki_wg_nazwy = defaultdict(list)
    for d in sorted(os.listdir(kat)):
        child = os.path.join(kat, d)
        if not os.path.isdir(child):
            continue
        shp_dir = os.path.join(child, 'SHP')
        if not os.path.isdir(shp_dir):
            continue
        for f in sorted(os.listdir(shp_dir)):
            if f.lower().endswith('.shp'):
                pliki_wg_nazwy[os.path.splitext(f)[0]].append(
                    os.path.join(shp_dir, f))

    if not pliki_wg_nazwy:
        iface.messageBar().pushMessage(
            'Błąd', 'Nie znaleziono plików SHP w podfolderach SHP/', Qgis.Critical)
        return

    dlg = _WybierzWarstwDialog(iface.mainWindow(), pliki_wg_nazwy.keys())
    if dlg.exec_() != QDialog.Accepted:
        return

    nazwy = dlg.wybrane()
    if not nazwy:
        return

    out = os.path.join(kat, "SHP_razem")
    os.makedirs(out, exist_ok=True)

    for nazwa in nazwy:
        _scal_liste(pliki_wg_nazwy[nazwa], nazwa, out, iface)

    iface.messageBar().pushMessage('OK', 'Połączono warstwy (tryb regionu)', Qgis.Success)


def polacz_warstwy(iface):
    kat = QFileDialog.getExistingDirectory(
        iface.mainWindow(), "Wybierz katalog: ")
    if not kat:
        return

    # Autowykrywanie: tryb 1 gdy istnieje folder OGOLNE
    # oraz WYDZ_POL.shp i WYDZ_OPS.shp w folderze SHP któregoś obrębu
    dzieci = os.listdir(kat)
    ma_ogolne = 'OGOLNE' in dzieci
    ma_wydz = any(
        os.path.isfile(os.path.join(kat, d, 'SHP', 'WYDZ_POL.shp')) and
        os.path.isfile(os.path.join(kat, d, 'SHP', 'WYDZ_OPS.shp'))
        for d in dzieci
    )
    tryb = 1 if (ma_ogolne and ma_wydz) else 2

    if tryb == 1:
        odp = QMessageBox.question(
            iface.mainWindow(),
            'Warstwy OGÓLNE',
            'Dołączyć warstwy z folderu OGOLNE do folderu wynikowego?',
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No)
        _polacz_gmina(iface, kat, z_ogolne=(odp == QMessageBox.Yes))
    else:
        _polacz_region(iface, kat)


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
