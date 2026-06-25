import os
from qgis.core import Qgis, QgsVectorLayer, QgsMessageLog, QgsSpatialIndex
from PyQt5.QtWidgets import QFileDialog
import platform

from .baza_wrapper import Baza

from collections import defaultdict


class recursivedefaultdict(defaultdict):
    def __init__(self):
        self.default_factory = type(self)


class GenerujSpisAtlasow():
    def __init__(self, iface):
        self.iface = iface
        self.kat = QFileDialog.getExistingDirectory(
            self.iface.mainWindow(), "Wybierz katalog roboczy: ")

        try:
            os.stat(self.kat)
        except:  # nopep8
            self.iface.messageBar().pushMessage(
                'Uwaga',
                'Nie udało się znaleźć podanego katalogu',
                level=Qgis.Critical)
            return

        # slownik trzymajacy wszystkie informacje o dzialkach i wydzieleniach
        self.sl = recursivedefaultdict()
        # lista obiektow dla ktorych beda tworzone spisy
        self.obiekty = []
        # lista z nazwa gmin i obrebow pobrana z baz dostepnych
        self.sp = []

        self.pobierz_meta()
        self.generuj()
        self.zapisz()

    def generuj(self):
        # zrob liste obiektow/gmin, dla kazdej gminy/obiektu bedzie tworzony
        # jeden spis
        kk = next(os.walk(self.kat))
        self.obiekty = kk[1]

        for ob in self.obiekty:
            for root, dirs, files in os.walk(os.path.join(self.kat, ob)):
                if "ATLAS_AFT.shp" in files:
                    self.przetnij(ob, root)

    def przetnij(self, ob, root):  # noqa
        # Sprawdz czy dostepne sa wszystkie niezbedne warstwy
        self.wydz = False
        if os.path.isfile(os.path.join(root, "WYDZ_POL.shp")):
            self.wydz = QgsVectorLayer(os.path.join(root, "WYDZ_POL.shp"),
                                       'wydz',
                                       'ogr')
        else:
            QgsMessageLog.logMessage(
                "Nie znaleziono WYDZ_POL.shp w: "+root, "LCH")
            return False

        self.atlas = False
        if os.path.isfile(os.path.join(root, "ATLAS_AFT.shp")):
            self.atlas = QgsVectorLayer(os.path.join(root, "ATLAS_AFT.shp"),
                                        'atlas',
                                        'ogr')
        else:
            QgsMessageLog.logMessage(
                "Nie znaleziono ATLAS_AFT.shp w: "+root, "LCH")
            return False

        self.dzkat = False
        if os.path.isfile(os.path.join(root, "DZKAT.shp")):
            self.dzkat = QgsVectorLayer(os.path.join(root, "DZKAT.shp"),
                                        'dzkat',
                                        'ogr')
        else:
            QgsMessageLog.logMessage(
                "Nie znaleziono DZKAT.shp w: "+root, "LCH")
            return False

        # zbuduj indeks przestrzenny dla wydzielen
        indWydz = QgsSpatialIndex()
        indWydz.addFeatures(self.wydz.getFeatures())
        fwydz = {w.id(): w for w in self.wydz.getFeatures()}

        indDz = QgsSpatialIndex()
        indDz.addFeatures(self.dzkat.getFeatures())
        fdz = {w.id(): w for w in self.dzkat.getFeatures()}

        for atf in self.atlas.getFeatures():
            atg = atf.geometry()

            # sprwdz jakie wydzielenia leza na tym polu atlasowym
            idw = indWydz.intersects(atg.boundingBox())
            for id in idw:
                if fwydz[id].geometry().intersects(atf.geometry()):
                    try:
                        self.sl[ob][fwydz[id]['MUNICIP']][fwydz[id]['COMMUNITY']]['w'][fwydz[id]['ADR_LES']].append(atf['STRONA'])  # nopep8
                    except:  # noqa
                        self.sl[ob][fwydz[id]['MUNICIP']][fwydz[id]['COMMUNITY']]['w'][fwydz[id]['ADR_LES']] = [atf['STRONA']]  # nopep8

            # sprwdz jakie dzialki leza na tym polu atlasowym
            idd = indDz.intersects(atg.boundingBox())
            for id in idd:
                if fdz[id].geometry().intersects(atf.geometry()):
                    try:
                        self.sl[ob][fdz[id]['MUNICIP']][fdz[id]['COMMUNITY']]['d'][fdz[id]['PARCELNR']].append(atf['STRONA'])  # nopep8
                    except:  # noqa
                        self.sl[ob][fdz[id]['MUNICIP']][fdz[id]['COMMUNITY']]['d'][fdz[id]['PARCELNR']] = [atf['STRONA']]  # nopep8

    def zapisz(self):
        for ob in self.obiekty:
            wypWy = 'Gmina\tObręb\tAdres Leśny\tOddział\tWydzielenie\tStrona\n'
            wypDz = 'Gmina\tObręb\tNr działki\tStrona\n'

            for gmi in sorted(self.sl[ob].keys()):
                for obr in sorted(self.sl[ob][gmi].keys()):
                    for adr in sorted(self.sl[ob][gmi][obr]['w'].keys()):
                        if gmi+obr in self.sp:
                            wypWy += "\t".join(self.sp[gmi+obr])
                        else:
                            wypWy += "---"
                        wypWy += '\t' + adr + '\t'
                        wypWy += adr[13:17] + '\t'
                        wypWy += adr[18:22] + '\t'
                        wypWy += ", ".join([
                            str(s) for s in
                            sorted(self.sl[ob][gmi][obr]['w'][adr])])
                        wypWy += '\n'

                    for nr in sorted(self.sl[ob][gmi][obr]['d'].keys()):
                        if gmi+obr in self.sp:
                            wypDz += "\t".join(self.sp[gmi+obr])
                        else:
                            wypDz += "---"
                        wypDz += '\t' + nr + '\t'
                        wypDz += ", ".join([
                            str(s) for s in
                            sorted(self.sl[ob][gmi][obr]['d'][nr])])
                        wypDz += '\n'

            QgsMessageLog.logMessage(
                "Zapisuję spis wydzieleń i dzkat dla obiektu: "+ob, "LCH")
            open(os.path.join(self.kat, ob+'_WYDZ.csv'),
                 'wb').write(wypWy.encode('cp1250'))
            open(os.path.join(self.kat, ob+'_DZKAT.csv'),
                 'wb').write(wypDz.encode('cp1250'))

        self.iface.messageBar().pushMessage(
            'OK',
            'Zapisano spisy wydzieleń i działek w wybranym katalogu',
            level=Qgis.Success)

    def pobierz_meta(self):
        bazy = []
        for root, dirs, files in os.walk(self.kat):
            if platform.system()[:3] == 'Win':
                bazy += [
                    os.path.join(root, f) for f in files if f[-3:] == 'mdb']
            else:
                bazy += [
                    os.path.join(root, f) for f in files if f[-6:] == 'sqlite']

        sql = """
        SELECT
        F_COMMUNITY.MUNICIPALITY_CD,
        F_MUNICIPALITY.MUNICIPALITY_NAME,
        F_COMMUNITY.COMMUNITY_CD,
        F_COMMUNITY.COMMUNITY_NAME
        FROM
            F_MUNICIPALITY INNER JOIN F_COMMUNITY ON
            (F_MUNICIPALITY.MUNICIPALITY_CD = F_COMMUNITY.MUNICIPALITY_CD)
            AND (F_MUNICIPALITY.DISTRICT_CD = F_COMMUNITY.DISTRICT_CD) AND
            (F_MUNICIPALITY.COUNTY_CD = F_COMMUNITY.COUNTY_CD);
        """

        sp = []
        for baza in bazy:
            b = Baza(baza)
            if b.polacz():
                sp += b.pobierz(sql)
                b.zamknij()

        self.sp = {x[0]+x[2]: ["("+x[0]+") "+x[1].upper(),
                               "("+x[2]+") "+x[3].upper()]
                   for x in sp}
