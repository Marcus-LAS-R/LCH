import os
from qgis.core import (
    QgsProject, Qgis, QgsVectorFileWriter, QgsVectorLayer,
    QgsCoordinateReferenceSystem, QgsFeatureRequest, QgsField,
)
from PyQt5.QtCore import QMetaType
from PyQt5.QtWidgets import QInputDialog
import processing


def uzupelnij_municip_community(iface, warstwa):
    """Dodaje pola MUNICIP/COMMUNITY (jeśli brak) i uzupełnia je na
    podstawie pola adresowego (G5IDD -> IDENTYFIKA -> IDKONTURU -> pytanie
    dialogiem). Zwraca True po powodzeniu, False jeśli przerwano."""

    # 1. Dodaj MUNICIP i COMMUNITY jeśli brak
    pola_nazwy = [f.name() for f in warstwa.fields()]
    do_dodania = []
    if 'MUNICIP' not in pola_nazwy:
        do_dodania.append(QgsField('MUNICIP', QMetaType.Type.QString, len=3))
    if 'COMMUNITY' not in pola_nazwy:
        do_dodania.append(QgsField('COMMUNITY', QMetaType.Type.QString, len=4))

    if do_dodania:
        warstwa.startEditing()
        warstwa.dataProvider().addAttributes(do_dodania)
        warstwa.updateFields()
        warstwa.commitChanges()

    # 2. Uzupełnij MUNICIP i COMMUNITY z pola adresowego
    flds_map = {x.name().upper(): x.name()
                for x in warstwa.dataProvider().fields().toList()}
    if 'G5IDD' in flds_map:
        pole = flds_map['G5IDD']
    elif 'IDENTYFIKA' in flds_map:
        pole = flds_map['IDENTYFIKA']
    elif 'IDKONTURU' in flds_map:
        pole = flds_map['IDKONTURU']
    else:
        kols = sorted(warstwa.dataProvider().fieldNameMap().keys())
        dlg = QInputDialog(iface.mainWindow())
        dlg.setWindowTitle('Wybierz kolumnę z adresem administracyjnym')
        dlg.setLabelText('Nazwa kolumny')
        dlg.setComboBoxItems(kols)
        dlg.resize(500, dlg.height())
        if not dlg.exec_():
            return False
        pole = dlg.textValue()

    fnm = warstwa.dataProvider().fieldNameMap()
    sl = {}
    for feat in warstwa.getFeatures(
            QgsFeatureRequest().setFlags(QgsFeatureRequest.NoGeometry)):
        adr = feat[pole]
        if adr and len(str(adr)) >= 14:
            sl[feat.id()] = {
                fnm['COMMUNITY']: str(adr)[9:13],
                fnm['MUNICIP']: str(adr)[4:8].replace('_', ''),
            }

    warstwa.startEditing()
    warstwa.dataProvider().changeAttributeValues(sl)
    warstwa.commitChanges()
    return True


def przetworz_klu(klu, kat):
    """Z podanej warstwy KLU (z uzupełnionym MUNICIP/COMMUNITY) tworzy w
    katalogu kat pliki KLU_AFT.shp i KLU_LFT.shp. Zwraca parę warstw
    (klu_aft, klu_lft) wczytanych z dysku."""

    klu_aft_path = os.path.join(kat, 'KLU_AFT.shp')
    crs = QgsCoordinateReferenceSystem('epsg:2180')
    QgsVectorFileWriter.writeAsVectorFormat(
        klu, klu_aft_path, 'UTF-8', crs, 'ESRI Shapefile')
    klu_aft = QgsVectorLayer(klu_aft_path, 'KLU_AFT', 'ogr')

    klu_lft_path = os.path.join(kat, 'KLU_LFT.shp')
    processing.run('model:klu_aft2klu_lft', {
        'kluaft': klu_aft_path,
        'qgis:deleteduplicategeometries_1:KLU_LFT': klu_lft_path,
    })
    klu_lft = QgsVectorLayer(klu_lft_path, 'KLU_LFT', 'ogr')

    return klu_aft, klu_lft


def przygotuj_klu_lft(iface):
    # 1. Znajdź warstwę KLU* w TOC
    klu = None
    for lyr in QgsProject.instance().mapLayers().values():
        if lyr.name().upper().startswith('KLU'):
            klu = lyr
            break

    if not klu:
        iface.messageBar().pushMessage(
            'BŁĄD', 'Nie znaleziono warstwy KLU w TOC', Qgis.Critical)
        return

    kat = os.path.dirname(klu.dataProvider().dataSourceUri().split("|")[0])

    if not uzupelnij_municip_community(iface, klu):
        return

    klu_aft, klu_lft = przetworz_klu(klu, kat)
    QgsProject.instance().addMapLayer(klu_aft)
    QgsProject.instance().addMapLayer(klu_lft)

    iface.messageBar().pushMessage(
        'OK', 'KLU_AFT i KLU_LFT przygotowane', Qgis.Success)
