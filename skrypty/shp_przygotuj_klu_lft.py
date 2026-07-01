import os
from qgis.core import (
    QgsProject, Qgis, QgsVectorFileWriter,
    QgsCoordinateReferenceSystem, QgsFeatureRequest, QgsField,
)
from PyQt5.QtCore import QVariant
from PyQt5.QtWidgets import QInputDialog
import processing


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

    # 2. Dodaj MUNICIP i COMMUNITY jeśli brak
    pola_nazwy = [f.name() for f in klu.fields()]
    do_dodania = []
    if 'MUNICIP' not in pola_nazwy:
        do_dodania.append(QgsField('MUNICIP', QVariant.String, len=3))
    if 'COMMUNITY' not in pola_nazwy:
        do_dodania.append(QgsField('COMMUNITY', QVariant.String, len=4))

    if do_dodania:
        klu.startEditing()
        klu.dataProvider().addAttributes(do_dodania)
        klu.updateFields()
        klu.commitChanges()

    # 3. Uzupełnij MUNICIP i COMMUNITY z pola adresowego
    flds_map = {x.name().upper(): x.name()
                for x in klu.dataProvider().fields().toList()}
    if 'G5IDD' in flds_map:
        pole = flds_map['G5IDD']
    elif 'IDENTYFIKA' in flds_map:
        pole = flds_map['IDENTYFIKA']
    else:
        kols = sorted(klu.dataProvider().fieldNameMap().keys())
        kol, ok = QInputDialog.getItem(
            iface.mainWindow(),
            'Wybierz kolumnę z adresem administracyjnym',
            'Nazwa kolumny',
            kols, 0, False)
        if not ok:
            return
        pole = kol

    fnm = klu.dataProvider().fieldNameMap()
    sl = {}
    for feat in klu.getFeatures(
            QgsFeatureRequest().setFlags(QgsFeatureRequest.NoGeometry)):
        adr = feat[pole]
        if adr and len(str(adr)) >= 14:
            sl[feat.id()] = {
                fnm['COMMUNITY']: str(adr)[9:13],
                fnm['MUNICIP']: str(adr)[4:8].replace('_', ''),
            }

    klu.startEditing()
    klu.dataProvider().changeAttributeValues(sl)
    klu.commitChanges()

    # 4. Eksportuj jako KLU_AFT.shp
    klu_aft_path = os.path.join(kat, 'KLU_AFT.shp')
    crs = QgsCoordinateReferenceSystem('epsg:2180')
    QgsVectorFileWriter.writeAsVectorFormat(
        klu, klu_aft_path, 'UTF-8', crs, 'ESRI Shapefile')

    # 5. Uruchom model klu_aft2klu_lft → KLU_LFT.shp
    klu_lft_path = os.path.join(kat, 'KLU_LFT.shp')
    processing.run('model:klu_aft2klu_lft', {
        'kluaft': klu_aft_path,
        'qgis:deleteduplicategeometries_1:KLU_LFT': klu_lft_path,
    })

    iface.messageBar().pushMessage(
        'OK', 'KLU_AFT i KLU_LFT przygotowane', Qgis.Success)
