<!DOCTYPE qgis PUBLIC 'http://mrcc.com/qgis.dtd' 'SYSTEM'>
<qgis labelsEnabled="1" simplifyDrawingHints="1" maxScale="1000" minScale="10001" simplifyDrawingTol="1" version="3.8.3-Zanzibar" hasScaleBasedVisibilityFlag="1" readOnly="0" styleCategories="AllStyleCategories" simplifyMaxScale="1" simplifyAlgorithm="0" simplifyLocal="1">
  <flags>
    <Identifiable>1</Identifiable>
    <Removable>1</Removable>
    <Searchable>1</Searchable>
  </flags>
  <renderer-v2 forceraster="0" symbollevels="0" type="singleSymbol" enableorderby="0">
    <symbols>
      <symbol force_rhr="0" name="0" type="fill" alpha="1" clip_to_extent="1">
        <layer locked="0" enabled="1" pass="0" class="SimpleLine">
          <prop v="square" k="capstyle"/>
          <prop v="5;2" k="customdash"/>
          <prop v="3x:0,0,0,0,0,0" k="customdash_map_unit_scale"/>
          <prop v="MM" k="customdash_unit"/>
          <prop v="0" k="draw_inside_polygon"/>
          <prop v="bevel" k="joinstyle"/>
          <prop v="210,210,210,255" k="line_color"/>
          <prop v="solid" k="line_style"/>
          <prop v="0" k="line_width"/>
          <prop v="MM" k="line_width_unit"/>
          <prop v="0" k="offset"/>
          <prop v="3x:0,0,0,0,0,0" k="offset_map_unit_scale"/>
          <prop v="MM" k="offset_unit"/>
          <prop v="0" k="ring_filter"/>
          <prop v="0" k="use_custom_dash"/>
          <prop v="3x:0,0,0,0,0,0" k="width_map_unit_scale"/>
          <data_defined_properties>
            <Option type="Map">
              <Option value="" name="name" type="QString"/>
              <Option name="properties"/>
              <Option value="collection" name="type" type="QString"/>
            </Option>
          </data_defined_properties>
        </layer>
      </symbol>
    </symbols>
    <rotation/>
    <sizescale/>
  </renderer-v2>
  <labeling type="simple">
    <settings>
      <text-style fontSizeUnit="Point" blendMode="0" multilineHeight="1" fontUnderline="0" fontCapitals="0" fieldName="if(&quot;DZKAT_PARCELID&quot; is NULL, &quot;NUMER&quot;, '')" fontSizeMapUnitScale="3x:0,0,0,0,0,0" fontStrikeout="0" textColor="0,0,0,255" textOpacity="1" fontWeight="50" fontItalic="0" useSubstitutions="0" namedStyle="Normalny" fontFamily="Arial Narrow" isExpression="1" fontLetterSpacing="0" previewBkgrdColor="#ffffff" fontWordSpacing="0" fontSize="5">
        <text-buffer bufferOpacity="1" bufferBlendMode="0" bufferColor="255,255,255,255" bufferNoFill="1" bufferDraw="0" bufferSize="1" bufferSizeMapUnitScale="3x:0,0,0,0,0,0" bufferSizeUnits="MM" bufferJoinStyle="128"/>
        <background shapeBorderWidthUnit="MM" shapeRotationType="0" shapeBorderWidthMapUnitScale="3x:0,0,0,0,0,0" shapeDraw="0" shapeOpacity="1" shapeSizeX="0" shapeOffsetUnit="MM" shapeRadiiX="0" shapeBorderWidth="0" shapeRadiiY="0" shapeType="0" shapeOffsetX="0" shapeSizeType="0" shapeRotation="0" shapeOffsetY="0" shapeBorderColor="128,128,128,255" shapeOffsetMapUnitScale="3x:0,0,0,0,0,0" shapeSizeMapUnitScale="3x:0,0,0,0,0,0" shapeSizeY="0" shapeBlendMode="0" shapeSizeUnit="MM" shapeJoinStyle="64" shapeRadiiUnit="MM" shapeSVGFile="" shapeRadiiMapUnitScale="3x:0,0,0,0,0,0" shapeFillColor="255,255,255,255"/>
        <shadow shadowRadiusMapUnitScale="3x:0,0,0,0,0,0" shadowDraw="0" shadowUnder="0" shadowOffsetDist="1" shadowOffsetUnit="MM" shadowOffsetAngle="135" shadowOffsetMapUnitScale="3x:0,0,0,0,0,0" shadowOpacity="0.7" shadowScale="100" shadowRadiusAlphaOnly="0" shadowColor="0,0,0,255" shadowRadius="1.5" shadowOffsetGlobal="1" shadowRadiusUnit="MM" shadowBlendMode="6"/>
        <substitutions/>
      </text-style>
      <text-format reverseDirectionSymbol="0" addDirectionSymbol="0" wrapChar="" rightDirectionSymbol=">" useMaxLineLengthForAutoWrap="1" placeDirectionSymbol="0" formatNumbers="0" multilineAlign="4294967295" plussign="0" autoWrapLength="0" leftDirectionSymbol="&lt;" decimals="3"/>
      <placement predefinedPositionOrder="TR,TL,BR,BL,R,L,TSR,BSR" centroidWhole="0" xOffset="0" offsetType="0" centroidInside="1" priority="5" repeatDistance="0" distMapUnitScale="3x:0,0,0,0,0,0" geometryGenerator="" preserveRotation="1" repeatDistanceMapUnitScale="3x:0,0,0,0,0,0" placement="0" geometryGeneratorEnabled="0" maxCurvedCharAngleIn="25" maxCurvedCharAngleOut="-25" distUnits="MM" geometryGeneratorType="PointGeometry" labelOffsetMapUnitScale="3x:0,0,0,0,0,0" repeatDistanceUnits="MM" yOffset="0" rotationAngle="0" quadOffset="4" offsetUnits="MM" dist="0" placementFlags="10" fitInPolygonOnly="0"/>
      <rendering scaleVisibility="1" minFeatureSize="0" limitNumLabels="0" mergeLines="0" upsidedownLabels="0" fontLimitPixelSize="0" obstacleType="0" fontMaxPixelSize="10000" displayAll="0" drawLabels="1" maxNumLabels="2000" obstacle="1" labelPerPart="0" obstacleFactor="1" zIndex="0" scaleMin="0" scaleMax="5050" fontMinPixelSize="3"/>
      <dd_properties>
        <Option type="Map">
          <Option value="" name="name" type="QString"/>
          <Option name="properties"/>
          <Option value="collection" name="type" type="QString"/>
        </Option>
      </dd_properties>
    </settings>
  </labeling>
  <customproperties>
    <property key="dualview/previewExpressions">
      <value>'[Please define preview text]'</value>
    </property>
    <property key="embeddedWidgets/count" value="0"/>
    <property key="variableNames"/>
    <property key="variableValues"/>
  </customproperties>
  <blendMode>0</blendMode>
  <featureBlendMode>0</featureBlendMode>
  <layerOpacity>1</layerOpacity>
  <SingleCategoryDiagramRenderer attributeLegend="1" diagramType="Histogram">
    <DiagramCategory minScaleDenominator="100000" height="15" minimumSize="0" lineSizeType="MM" scaleDependency="Area" penAlpha="255" opacity="1" lineSizeScale="3x:0,0,0,0,0,0" labelPlacementMethod="XHeight" scaleBasedVisibility="0" sizeType="MM" enabled="0" backgroundAlpha="255" backgroundColor="#ffffff" penColor="#000000" maxScaleDenominator="1e+08" sizeScale="3x:0,0,0,0,0,0" rotationOffset="270" width="15" penWidth="0" diagramOrientation="Up" barWidth="5">
      <fontProperties style="" description="MS Shell Dlg 2,8.25,-1,5,50,0,0,0,0,0"/>
      <attribute color="#000000" label="" field=""/>
    </DiagramCategory>
  </SingleCategoryDiagramRenderer>
  <DiagramLayerSettings priority="0" placement="0" showAll="1" obstacle="0" dist="0" linePlacementFlags="2" zIndex="0">
    <properties>
      <Option type="Map">
        <Option value="" name="name" type="QString"/>
        <Option name="properties"/>
        <Option value="collection" name="type" type="QString"/>
      </Option>
    </properties>
  </DiagramLayerSettings>
  <geometryOptions geometryPrecision="0" removeDuplicateNodes="0">
    <activeChecks/>
    <checkConfiguration/>
  </geometryOptions>
  <fieldConfiguration>
    <field name="NUMER">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="G5IDD">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="MUNICIP">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="COMMUNITY">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="DZKAT_COUNTY">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="DZKAT_DISTRICT">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="DZKAT_MUNICIP">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="DZKAT_COMMUNITY">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="DZKAT_PARCELID">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="DZKAT_GRP">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="DZKAT_ARK">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="DZKAT_NIELES">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="DZKAT_UWAGI">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="DZKAT_PARCEL_AR">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="DZKAT_PARCEL_POW">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
  </fieldConfiguration>
  <aliases>
    <alias name="" field="NUMER" index="0"/>
    <alias name="" field="G5IDD" index="1"/>
    <alias name="" field="MUNICIP" index="2"/>
    <alias name="" field="COMMUNITY" index="3"/>
    <alias name="" field="DZKAT_COUNTY" index="4"/>
    <alias name="" field="DZKAT_DISTRICT" index="5"/>
    <alias name="" field="DZKAT_MUNICIP" index="6"/>
    <alias name="" field="DZKAT_COMMUNITY" index="7"/>
    <alias name="" field="DZKAT_PARCELID" index="8"/>
    <alias name="" field="DZKAT_GRP" index="9"/>
    <alias name="" field="DZKAT_ARK" index="10"/>
    <alias name="" field="DZKAT_NIELES" index="11"/>
    <alias name="" field="DZKAT_UWAGI" index="12"/>
    <alias name="" field="DZKAT_PARCEL_AR" index="13"/>
    <alias name="" field="DZKAT_PARCEL_POW" index="14"/>
  </aliases>
  <excludeAttributesWMS/>
  <excludeAttributesWFS/>
  <defaults>
    <default field="NUMER" expression="" applyOnUpdate="0"/>
    <default field="G5IDD" expression="" applyOnUpdate="0"/>
    <default field="MUNICIP" expression="" applyOnUpdate="0"/>
    <default field="COMMUNITY" expression="" applyOnUpdate="0"/>
    <default field="DZKAT_COUNTY" expression="" applyOnUpdate="0"/>
    <default field="DZKAT_DISTRICT" expression="" applyOnUpdate="0"/>
    <default field="DZKAT_MUNICIP" expression="" applyOnUpdate="0"/>
    <default field="DZKAT_COMMUNITY" expression="" applyOnUpdate="0"/>
    <default field="DZKAT_PARCELID" expression="" applyOnUpdate="0"/>
    <default field="DZKAT_GRP" expression="" applyOnUpdate="0"/>
    <default field="DZKAT_ARK" expression="" applyOnUpdate="0"/>
    <default field="DZKAT_NIELES" expression="" applyOnUpdate="0"/>
    <default field="DZKAT_UWAGI" expression="" applyOnUpdate="0"/>
    <default field="DZKAT_PARCEL_AR" expression="" applyOnUpdate="0"/>
    <default field="DZKAT_PARCEL_POW" expression="" applyOnUpdate="0"/>
  </defaults>
  <constraints>
    <constraint constraints="0" field="NUMER" unique_strength="0" notnull_strength="0" exp_strength="0"/>
    <constraint constraints="0" field="G5IDD" unique_strength="0" notnull_strength="0" exp_strength="0"/>
    <constraint constraints="0" field="MUNICIP" unique_strength="0" notnull_strength="0" exp_strength="0"/>
    <constraint constraints="0" field="COMMUNITY" unique_strength="0" notnull_strength="0" exp_strength="0"/>
    <constraint constraints="0" field="DZKAT_COUNTY" unique_strength="0" notnull_strength="0" exp_strength="0"/>
    <constraint constraints="0" field="DZKAT_DISTRICT" unique_strength="0" notnull_strength="0" exp_strength="0"/>
    <constraint constraints="0" field="DZKAT_MUNICIP" unique_strength="0" notnull_strength="0" exp_strength="0"/>
    <constraint constraints="0" field="DZKAT_COMMUNITY" unique_strength="0" notnull_strength="0" exp_strength="0"/>
    <constraint constraints="0" field="DZKAT_PARCELID" unique_strength="0" notnull_strength="0" exp_strength="0"/>
    <constraint constraints="0" field="DZKAT_GRP" unique_strength="0" notnull_strength="0" exp_strength="0"/>
    <constraint constraints="0" field="DZKAT_ARK" unique_strength="0" notnull_strength="0" exp_strength="0"/>
    <constraint constraints="0" field="DZKAT_NIELES" unique_strength="0" notnull_strength="0" exp_strength="0"/>
    <constraint constraints="0" field="DZKAT_UWAGI" unique_strength="0" notnull_strength="0" exp_strength="0"/>
    <constraint constraints="0" field="DZKAT_PARCEL_AR" unique_strength="0" notnull_strength="0" exp_strength="0"/>
    <constraint constraints="0" field="DZKAT_PARCEL_POW" unique_strength="0" notnull_strength="0" exp_strength="0"/>
  </constraints>
  <constraintExpressions>
    <constraint field="NUMER" exp="" desc=""/>
    <constraint field="G5IDD" exp="" desc=""/>
    <constraint field="MUNICIP" exp="" desc=""/>
    <constraint field="COMMUNITY" exp="" desc=""/>
    <constraint field="DZKAT_COUNTY" exp="" desc=""/>
    <constraint field="DZKAT_DISTRICT" exp="" desc=""/>
    <constraint field="DZKAT_MUNICIP" exp="" desc=""/>
    <constraint field="DZKAT_COMMUNITY" exp="" desc=""/>
    <constraint field="DZKAT_PARCELID" exp="" desc=""/>
    <constraint field="DZKAT_GRP" exp="" desc=""/>
    <constraint field="DZKAT_ARK" exp="" desc=""/>
    <constraint field="DZKAT_NIELES" exp="" desc=""/>
    <constraint field="DZKAT_UWAGI" exp="" desc=""/>
    <constraint field="DZKAT_PARCEL_AR" exp="" desc=""/>
    <constraint field="DZKAT_PARCEL_POW" exp="" desc=""/>
  </constraintExpressions>
  <expressionfields/>
  <attributeactions>
    <defaultAction key="Canvas" value="{00000000-0000-0000-0000-000000000000}"/>
  </attributeactions>
  <attributetableconfig sortOrder="1" sortExpression="&quot;DZKAT_PARCELID&quot;" actionWidgetStyle="dropDown">
    <columns>
      <column hidden="1" type="actions" width="-1"/>
      <column hidden="0" name="NUMER" type="field" width="-1"/>
      <column hidden="0" name="MUNICIP" type="field" width="-1"/>
      <column hidden="0" name="COMMUNITY" type="field" width="-1"/>
      <column hidden="0" name="DZKAT_COUNTY" type="field" width="-1"/>
      <column hidden="0" name="DZKAT_DISTRICT" type="field" width="-1"/>
      <column hidden="0" name="DZKAT_MUNICIP" type="field" width="-1"/>
      <column hidden="0" name="DZKAT_COMMUNITY" type="field" width="-1"/>
      <column hidden="0" name="DZKAT_PARCELID" type="field" width="-1"/>
      <column hidden="0" name="DZKAT_GRP" type="field" width="-1"/>
      <column hidden="0" name="DZKAT_ARK" type="field" width="-1"/>
      <column hidden="0" name="DZKAT_NIELES" type="field" width="-1"/>
      <column hidden="0" name="DZKAT_UWAGI" type="field" width="-1"/>
      <column hidden="0" name="DZKAT_PARCEL_AR" type="field" width="-1"/>
      <column hidden="0" name="DZKAT_PARCEL_POW" type="field" width="-1"/>
      <column hidden="0" name="G5IDD" type="field" width="-1"/>
    </columns>
  </attributetableconfig>
  <conditionalstyles>
    <rowstyles/>
    <fieldstyles/>
  </conditionalstyles>
  <editform tolerant="1">/home/qnox/upul/bielsko_biala_2019/_ROBOCZE/011_SZCZYRK/0001_SZCZYRK</editform>
  <editforminit/>
  <editforminitcodesource>0</editforminitcodesource>
  <editforminitfilepath>/home/qnox/upul/bielsko_biala_2019/_ROBOCZE/011_SZCZYRK/0001_SZCZYRK</editforminitfilepath>
  <editforminitcode><![CDATA[# -*- coding: utf-8 -*-
"""
QGIS forms can have a Python function that is called when the form is
opened.

Use this function to add extra logic to your forms.

Enter the name of the function in the "Python Init function"
field.
An example follows:
"""
from qgis.PyQt.QtWidgets import QWidget

def my_form_open(dialog, layer, feature):
	geom = feature.geometry()
	control = dialog.findChild(QWidget, "MyLineEdit")
]]></editforminitcode>
  <featformsuppress>0</featformsuppress>
  <editorlayout>generatedlayout</editorlayout>
  <editable>
    <field name="COMMUNITY" editable="1"/>
    <field name="DATAMOD" editable="1"/>
    <field name="DATAUTW" editable="1"/>
    <field name="DATA_OD" editable="1"/>
    <field name="DZKAT_ARK" editable="0"/>
    <field name="DZKAT_COMMUNITY" editable="0"/>
    <field name="DZKAT_COUNTY" editable="0"/>
    <field name="DZKAT_DISTRICT" editable="0"/>
    <field name="DZKAT_GRP" editable="0"/>
    <field name="DZKAT_MUNICIP" editable="0"/>
    <field name="DZKAT_NIELES" editable="0"/>
    <field name="DZKAT_PARCELID" editable="0"/>
    <field name="DZKAT_PARCEL_AR" editable="0"/>
    <field name="DZKAT_PARCEL_POW" editable="0"/>
    <field name="DZKAT_UWAGI" editable="0"/>
    <field name="G5IDD" editable="1"/>
    <field name="GMINA" editable="1"/>
    <field name="IDENTYFIKA" editable="1"/>
    <field name="ILOSCPT" editable="1"/>
    <field name="MUNICIP" editable="1"/>
    <field name="NUMER" editable="1"/>
    <field name="NUMERROZP" editable="1"/>
    <field name="OBJECTID" editable="1"/>
    <field name="OPERAT" editable="1"/>
    <field name="OZNACZENIE" editable="1"/>
    <field name="POW" editable="1"/>
    <field name="POWIAT" editable="1"/>
    <field name="POWIERZCHN" editable="1"/>
    <field name="POWPOPR" editable="1"/>
    <field name="Shape_Area" editable="1"/>
    <field name="Shape_Leng" editable="1"/>
    <field name="TERYT" editable="1"/>
    <field name="WOJEWODZTW" editable="1"/>
    <field name="XMAX" editable="1"/>
    <field name="XMIN" editable="1"/>
    <field name="YMAX" editable="1"/>
    <field name="YMIN" editable="1"/>
  </editable>
  <labelOnTop>
    <field name="COMMUNITY" labelOnTop="0"/>
    <field name="DATAMOD" labelOnTop="0"/>
    <field name="DATAUTW" labelOnTop="0"/>
    <field name="DATA_OD" labelOnTop="0"/>
    <field name="DZKAT_ARK" labelOnTop="0"/>
    <field name="DZKAT_COMMUNITY" labelOnTop="0"/>
    <field name="DZKAT_COUNTY" labelOnTop="0"/>
    <field name="DZKAT_DISTRICT" labelOnTop="0"/>
    <field name="DZKAT_GRP" labelOnTop="0"/>
    <field name="DZKAT_MUNICIP" labelOnTop="0"/>
    <field name="DZKAT_NIELES" labelOnTop="0"/>
    <field name="DZKAT_PARCELID" labelOnTop="0"/>
    <field name="DZKAT_PARCEL_AR" labelOnTop="0"/>
    <field name="DZKAT_PARCEL_POW" labelOnTop="0"/>
    <field name="DZKAT_UWAGI" labelOnTop="0"/>
    <field name="G5IDD" labelOnTop="0"/>
    <field name="GMINA" labelOnTop="0"/>
    <field name="IDENTYFIKA" labelOnTop="0"/>
    <field name="ILOSCPT" labelOnTop="0"/>
    <field name="MUNICIP" labelOnTop="0"/>
    <field name="NUMER" labelOnTop="0"/>
    <field name="NUMERROZP" labelOnTop="0"/>
    <field name="OBJECTID" labelOnTop="0"/>
    <field name="OPERAT" labelOnTop="0"/>
    <field name="OZNACZENIE" labelOnTop="0"/>
    <field name="POW" labelOnTop="0"/>
    <field name="POWIAT" labelOnTop="0"/>
    <field name="POWIERZCHN" labelOnTop="0"/>
    <field name="POWPOPR" labelOnTop="0"/>
    <field name="Shape_Area" labelOnTop="0"/>
    <field name="Shape_Leng" labelOnTop="0"/>
    <field name="TERYT" labelOnTop="0"/>
    <field name="WOJEWODZTW" labelOnTop="0"/>
    <field name="XMAX" labelOnTop="0"/>
    <field name="XMIN" labelOnTop="0"/>
    <field name="YMAX" labelOnTop="0"/>
    <field name="YMIN" labelOnTop="0"/>
  </labelOnTop>
  <widgets/>
  <previewExpression>'[Please define preview text]'</previewExpression>
  <mapTip>ET_ID</mapTip>
  <layerGeometryType>2</layerGeometryType>
</qgis>
