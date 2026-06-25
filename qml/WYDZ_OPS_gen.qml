<!DOCTYPE qgis PUBLIC 'http://mrcc.com/qgis.dtd' 'SYSTEM'>
<qgis labelsEnabled="1" readOnly="0" minScale="10001" simplifyMaxScale="1" hasScaleBasedVisibilityFlag="1" styleCategories="AllStyleCategories" simplifyDrawingTol="1" simplifyDrawingHints="0" simplifyAlgorithm="0" simplifyLocal="1" maxScale="1000" version="3.6.0-Noosa">
  <flags>
    <Identifiable>1</Identifiable>
    <Removable>1</Removable>
    <Searchable>1</Searchable>
  </flags>
  <renderer-v2 symbollevels="0" enableorderby="0" type="singleSymbol" forceraster="0">
    <symbols>
      <symbol name="0" force_rhr="0" alpha="1" clip_to_extent="1" type="marker">
        <layer pass="0" locked="0" class="SimpleMarker" enabled="1">
          <prop k="angle" v="0"/>
          <prop k="color" v="166,206,227,255"/>
          <prop k="horizontal_anchor_point" v="1"/>
          <prop k="joinstyle" v="bevel"/>
          <prop k="name" v="circle"/>
          <prop k="offset" v="0,0"/>
          <prop k="offset_map_unit_scale" v="3x:0,0,0,0,0,0"/>
          <prop k="offset_unit" v="MM"/>
          <prop k="outline_color" v="0,0,0,255"/>
          <prop k="outline_style" v="solid"/>
          <prop k="outline_width" v="0"/>
          <prop k="outline_width_map_unit_scale" v="3x:0,0,0,0,0,0"/>
          <prop k="outline_width_unit" v="MM"/>
          <prop k="scale_method" v="area"/>
          <prop k="size" v="0"/>
          <prop k="size_map_unit_scale" v="3x:0,0,0,0,0,0"/>
          <prop k="size_unit" v="MM"/>
          <prop k="vertical_anchor_point" v="1"/>
          <data_defined_properties>
            <Option type="Map">
              <Option name="name" value="" type="QString"/>
              <Option name="properties"/>
              <Option name="type" value="collection" type="QString"/>
            </Option>
          </data_defined_properties>
        </layer>
      </symbol>
    </symbols>
    <rotation/>
    <sizescale/>
  </renderer-v2>
  <labeling type="rule-based">
    <rules key="{26b708f7-5ff9-4ffd-9eb6-afe7b0256e0d}">
      <rule key="{5fccb711-b208-4428-8dda-818d9b3da653}" description="LITERA">
        <settings>
          <text-style fontSizeMapUnitScale="3x:0,0,0,0,0,0" fontFamily="Arial Narrow" fontItalic="0" fieldName="CASE&#xd;&#xa; WHEN  &quot;WYDZ_POL_TYP_POW&quot; IN ('PŁAZ', 'HAL', 'ZRĄB', 'D-STAN' ) THEN &quot;WYDZ_POL_WYDZ&quot;&#xd;&#xa; WHEN &quot;WYDZ_POL_TYP_POW&quot; NOT IN ('PŁAZ', 'HAL', 'ZRĄB', 'D-STAN' ) THEN concat('   ' , &quot;WYDZ_POL_WYDZ&quot; , '   ')&#xd;&#xa; WHEN &quot;WYDZ_POL_TYP_POW&quot; IN ('INNE_WYL', 'SUKCESJA') AND &quot;typEtyk&quot; = 2 THEN concat('   ' , &quot;WYDZ_POL_WYDZ&quot; , '   ')&#xd;&#xa; WHEN  &quot;typEtyk&quot; = 1 THEN &quot;WYDZ_POL_WYDZ&quot;&#xd;&#xa;END" fontUnderline="0" fontCapitals="0" fontLetterSpacing="0" multilineHeight="1" fontSizeUnit="Point" fontStrikeout="0" fontWordSpacing="0" useSubstitutions="0" namedStyle="Narrow" textOpacity="1" isExpression="1" blendMode="0" fontSize="9" previewBkgrdColor="#ffffff" fontWeight="50" textColor="0,0,0,255">
            <text-buffer bufferSizeMapUnitScale="3x:0,0,0,0,0,0" bufferNoFill="0" bufferJoinStyle="128" bufferSize="1" bufferColor="255,255,255,255" bufferSizeUnits="MM" bufferBlendMode="0" bufferDraw="0" bufferOpacity="1"/>
            <background shapeSVGFile="" shapeRadiiUnit="MM" shapeSizeY="0" shapeOffsetUnit="MM" shapeRadiiMapUnitScale="3x:0,0,0,0,0,0" shapeRotationType="0" shapeRadiiY="0" shapeOpacity="1" shapeBorderWidthMapUnitScale="3x:0,0,0,0,0,0" shapeRadiiX="0" shapeOffsetX="0" shapeBlendMode="0" shapeSizeMapUnitScale="3x:0,0,0,0,0,0" shapeJoinStyle="64" shapeBorderWidthUnit="MM" shapeRotation="0" shapeOffsetY="0" shapeBorderColor="128,128,128,255" shapeOffsetMapUnitScale="3x:0,0,0,0,0,0" shapeSizeX="0" shapeSizeUnit="MM" shapeBorderWidth="0" shapeDraw="0" shapeType="0" shapeSizeType="0" shapeFillColor="255,255,255,255"/>
            <shadow shadowBlendMode="6" shadowOpacity="0.7" shadowUnder="0" shadowRadiusMapUnitScale="3x:0,0,0,0,0,0" shadowColor="0,0,0,255" shadowOffsetMapUnitScale="3x:0,0,0,0,0,0" shadowOffsetGlobal="1" shadowOffsetAngle="135" shadowRadiusAlphaOnly="0" shadowOffsetUnit="MM" shadowRadiusUnit="MM" shadowScale="100" shadowDraw="0" shadowRadius="1.5" shadowOffsetDist="1"/>
            <substitutions/>
          </text-style>
          <text-format leftDirectionSymbol="&lt;" decimals="3" useMaxLineLengthForAutoWrap="1" addDirectionSymbol="0" plussign="0" multilineAlign="2" rightDirectionSymbol=">" placeDirectionSymbol="0" wrapChar="" reverseDirectionSymbol="0" autoWrapLength="0" formatNumbers="0"/>
          <placement placementFlags="10" repeatDistanceMapUnitScale="3x:0,0,0,0,0,0" offsetType="0" predefinedPositionOrder="TR,TL,BR,BL,R,L,TSR,BSR" quadOffset="4" centroidInside="0" maxCurvedCharAngleOut="-25" priority="10" repeatDistance="0" dist="0" fitInPolygonOnly="0" maxCurvedCharAngleIn="25" xOffset="0" rotationAngle="0" distUnits="MM" repeatDistanceUnits="MM" preserveRotation="1" centroidWhole="0" labelOffsetMapUnitScale="3x:0,0,0,0,0,0" yOffset="0" placement="1" distMapUnitScale="3x:0,0,0,0,0,0" offsetUnits="MapUnit"/>
          <rendering displayAll="1" maxNumLabels="2000" fontLimitPixelSize="0" scaleMin="1" mergeLines="0" fontMaxPixelSize="10000" scaleMax="5001" zIndex="0" fontMinPixelSize="3" upsidedownLabels="0" minFeatureSize="0" drawLabels="1" obstacle="0" labelPerPart="0" limitNumLabels="0" scaleVisibility="1" obstacleFactor="1" obstacleType="0"/>
          <dd_properties>
            <Option type="Map">
              <Option name="name" value="" type="QString"/>
              <Option name="properties" type="Map">
                <Option name="Color" type="Map">
                  <Option name="active" value="true" type="bool"/>
                  <Option name="expression" value="CASE &#xd;&#xa;WHEN &quot;WYDZ_POL_L_EWID&quot; = 'T' THEN color_rgb(0,0,0)&#xd;&#xa;WHEN &quot;WYDZ_POL_L_EWID&quot; = 'N' THEN color_rgb(255,0,0)&#xd;&#xa;END" type="QString"/>
                  <Option name="type" value="3" type="int"/>
                </Option>
                <Option name="Italic" type="Map">
                  <Option name="active" value="false" type="bool"/>
                  <Option name="expression" value="1" type="QString"/>
                  <Option name="type" value="3" type="int"/>
                </Option>
                <Option name="Underline" type="Map">
                  <Option name="active" value="true" type="bool"/>
                  <Option name="expression" value="CASE&#xd;&#xa; WHEN  &quot;WYDZ_POL_TYP_POW&quot; IN ('PŁAZ', 'HAL', 'ZRĄB', 'D-STAN' )  THEN 0&#xd;&#xa; WHEN &quot;WYDZ_POL_TYP_POW&quot; NOT IN ('PŁAZ', 'HAL', 'ZRĄB', 'D-STAN' ) AND  &quot;typEtyk&quot; = 2 THEN 1&#xd;&#xa;END" type="QString"/>
                  <Option name="type" value="3" type="int"/>
                </Option>
              </Option>
              <Option name="type" value="collection" type="QString"/>
            </Option>
          </dd_properties>
        </settings>
      </rule>
      <rule key="{829282d0-7a09-48a5-89c6-59b52db0ff18}" description="LICZNIK">
        <settings>
          <text-style fontSizeMapUnitScale="3x:0,0,0,0,0,0" fontFamily="Arial Narrow" fontItalic="0" fieldName="CASE&#xd;&#xa;WHEN  &quot;WYDZ_POL_TYP_POW&quot; = 'D-STAN' AND  &quot;typEtyk&quot; = 2 AND &quot;WYDZ_POL_STRUKTUR&quot; NOT IN ('KO', 'KDO')  THEN &quot;WYDZ_POL_UDZIAL&quot; || &quot;WYDZ_POL_GAT&quot; || &quot;WYDZ_POL_WIEK&quot; &#xd;&#xa;WHEN  &quot;WYDZ_POL_TYP_POW&quot; = 'D-STAN' AND  &quot;typEtyk&quot; = 2 AND &quot;WYDZ_POL_STRUKTUR&quot; IN ('KO', 'KDO')  THEN &quot;WYDZ_POL_UDZIAL&quot; || &quot;WYDZ_POL_GAT&quot; || &quot;WYDZ_POL_STRUKTUR&quot; &#xd;&#xa;WHEN  &quot;WYDZ_POL_TYP_POW&quot; IN ('PŁAZ', 'HAL') AND  &quot;typEtyk&quot; = 2  THEN  lower(&quot;WYDZ_POL_TYP_POW&quot; ) || '.'&#xd;&#xa;WHEN  &quot;WYDZ_POL_TYP_POW&quot; = 'ZRĄB' AND  &quot;typEtyk&quot; = 2  THEN  lower(&quot;WYDZ_POL_TYP_POW&quot; ) &#xd;&#xa;END&#xd;&#xa;" fontUnderline="1" fontCapitals="0" fontLetterSpacing="0" multilineHeight="1" fontSizeUnit="Point" fontStrikeout="0" fontWordSpacing="0" useSubstitutions="0" namedStyle="Normalny" textOpacity="1" isExpression="1" blendMode="0" fontSize="9" previewBkgrdColor="#ffffff" fontWeight="50" textColor="0,0,0,255">
            <text-buffer bufferSizeMapUnitScale="3x:0,0,0,0,0,0" bufferNoFill="0" bufferJoinStyle="128" bufferSize="1" bufferColor="255,255,255,255" bufferSizeUnits="MM" bufferBlendMode="0" bufferDraw="0" bufferOpacity="1"/>
            <background shapeSVGFile="" shapeRadiiUnit="MM" shapeSizeY="0" shapeOffsetUnit="MM" shapeRadiiMapUnitScale="3x:0,0,0,0,0,0" shapeRotationType="0" shapeRadiiY="0" shapeOpacity="1" shapeBorderWidthMapUnitScale="3x:0,0,0,0,0,0" shapeRadiiX="0" shapeOffsetX="0" shapeBlendMode="0" shapeSizeMapUnitScale="3x:0,0,0,0,0,0" shapeJoinStyle="64" shapeBorderWidthUnit="MM" shapeRotation="0" shapeOffsetY="0" shapeBorderColor="128,128,128,255" shapeOffsetMapUnitScale="3x:0,0,0,0,0,0" shapeSizeX="0" shapeSizeUnit="MM" shapeBorderWidth="0" shapeDraw="0" shapeType="0" shapeSizeType="0" shapeFillColor="255,255,255,255"/>
            <shadow shadowBlendMode="6" shadowOpacity="0.7" shadowUnder="0" shadowRadiusMapUnitScale="3x:0,0,0,0,0,0" shadowColor="0,0,0,255" shadowOffsetMapUnitScale="3x:0,0,0,0,0,0" shadowOffsetGlobal="1" shadowOffsetAngle="135" shadowRadiusAlphaOnly="0" shadowOffsetUnit="MM" shadowRadiusUnit="MM" shadowScale="100" shadowDraw="0" shadowRadius="1.5" shadowOffsetDist="1"/>
            <substitutions/>
          </text-style>
          <text-format leftDirectionSymbol="&lt;" decimals="3" useMaxLineLengthForAutoWrap="1" addDirectionSymbol="0" plussign="0" multilineAlign="0" rightDirectionSymbol=">" placeDirectionSymbol="0" wrapChar="" reverseDirectionSymbol="0" autoWrapLength="0" formatNumbers="0"/>
          <placement placementFlags="10" repeatDistanceMapUnitScale="3x:0,0,0,0,0,0" offsetType="0" predefinedPositionOrder="TR,TL,BR,BL,R,L,TSR,BSR" quadOffset="2" centroidInside="0" maxCurvedCharAngleOut="-25" priority="10" repeatDistance="0" dist="0" fitInPolygonOnly="0" maxCurvedCharAngleIn="25" xOffset="1" rotationAngle="0" distUnits="MM" repeatDistanceUnits="MM" preserveRotation="1" centroidWhole="0" labelOffsetMapUnitScale="3x:0,0,0,0,0,0" yOffset="0" placement="1" distMapUnitScale="3x:0,0,0,0,0,0" offsetUnits="MM"/>
          <rendering displayAll="1" maxNumLabels="2000" fontLimitPixelSize="0" scaleMin="1" mergeLines="0" fontMaxPixelSize="10000" scaleMax="5001" zIndex="0" fontMinPixelSize="3" upsidedownLabels="0" minFeatureSize="0" drawLabels="1" obstacle="0" labelPerPart="0" limitNumLabels="0" scaleVisibility="1" obstacleFactor="1" obstacleType="0"/>
          <dd_properties>
            <Option type="Map">
              <Option name="name" value="" type="QString"/>
              <Option name="properties" type="Map">
                <Option name="Color" type="Map">
                  <Option name="active" value="true" type="bool"/>
                  <Option name="expression" value="CASE &#xd;&#xa;WHEN &quot;WYDZ_POL_L_EWID&quot; = 'T' THEN color_rgb(0,0,0)&#xd;&#xa;WHEN &quot;WYDZ_POL_L_EWID&quot; = 'N' THEN color_rgb(255,0,0)&#xd;&#xa;END" type="QString"/>
                  <Option name="type" value="3" type="int"/>
                </Option>
                <Option name="OffsetXY" type="Map">
                  <Option name="active" value="true" type="bool"/>
                  <Option name="expression" value="CASE &#xa; WHEN length(&quot;WYDZ_POL_WYDZ&quot; ) = 2 THEN  '2, 0'&#xa; WHEN length(&quot;WYDZ_POL_WYDZ&quot; ) = 1 THEN  '1, 0'&#xa;END" type="QString"/>
                  <Option name="type" value="3" type="int"/>
                </Option>
              </Option>
              <Option name="type" value="collection" type="QString"/>
            </Option>
          </dd_properties>
        </settings>
      </rule>
      <rule key="{4e8a9399-e57f-40cf-a0dc-6ae9061cbe21}" description="MIAN_PELNY">
        <settings>
          <text-style fontSizeMapUnitScale="3x:0,0,0,0,0,0" fontFamily="Arial Narrow" fontItalic="0" fieldName="CASE&#xd;&#xa;WHEN  &quot;WYDZ_POL_TYP_POW&quot; IN ('ZRĄB', 'HAL', 'PŁAZ', 'D-STAN') AND &quot;typEtyk&quot; = 2 THEN  &quot;WYDZ_POL_POW_WYDZ&quot;&#xd;&#xa;END" fontUnderline="0" fontCapitals="0" fontLetterSpacing="0" multilineHeight="1" fontSizeUnit="Point" fontStrikeout="0" fontWordSpacing="0" useSubstitutions="0" namedStyle="Normalny" textOpacity="1" isExpression="1" blendMode="0" fontSize="9" previewBkgrdColor="#ffffff" fontWeight="50" textColor="0,0,0,255">
            <text-buffer bufferSizeMapUnitScale="3x:0,0,0,0,0,0" bufferNoFill="0" bufferJoinStyle="128" bufferSize="1" bufferColor="255,255,255,255" bufferSizeUnits="MM" bufferBlendMode="0" bufferDraw="0" bufferOpacity="1"/>
            <background shapeSVGFile="" shapeRadiiUnit="MM" shapeSizeY="0" shapeOffsetUnit="MM" shapeRadiiMapUnitScale="3x:0,0,0,0,0,0" shapeRotationType="0" shapeRadiiY="0" shapeOpacity="1" shapeBorderWidthMapUnitScale="3x:0,0,0,0,0,0" shapeRadiiX="0" shapeOffsetX="0" shapeBlendMode="0" shapeSizeMapUnitScale="3x:0,0,0,0,0,0" shapeJoinStyle="64" shapeBorderWidthUnit="MM" shapeRotation="0" shapeOffsetY="0" shapeBorderColor="128,128,128,255" shapeOffsetMapUnitScale="3x:0,0,0,0,0,0" shapeSizeX="0" shapeSizeUnit="MM" shapeBorderWidth="0" shapeDraw="0" shapeType="0" shapeSizeType="0" shapeFillColor="255,255,255,255"/>
            <shadow shadowBlendMode="6" shadowOpacity="0.7" shadowUnder="0" shadowRadiusMapUnitScale="3x:0,0,0,0,0,0" shadowColor="0,0,0,255" shadowOffsetMapUnitScale="3x:0,0,0,0,0,0" shadowOffsetGlobal="1" shadowOffsetAngle="135" shadowRadiusAlphaOnly="0" shadowOffsetUnit="MM" shadowRadiusUnit="MM" shadowScale="100" shadowDraw="0" shadowRadius="1.5" shadowOffsetDist="1"/>
            <substitutions/>
          </text-style>
          <text-format leftDirectionSymbol="&lt;" decimals="2" useMaxLineLengthForAutoWrap="1" addDirectionSymbol="0" plussign="0" multilineAlign="0" rightDirectionSymbol=">" placeDirectionSymbol="0" wrapChar="" reverseDirectionSymbol="0" autoWrapLength="0" formatNumbers="1"/>
          <placement placementFlags="10" repeatDistanceMapUnitScale="3x:0,0,0,0,0,0" offsetType="0" predefinedPositionOrder="TR,TL,BR,BL,R,L,TSR,BSR" quadOffset="8" centroidInside="0" maxCurvedCharAngleOut="-25" priority="10" repeatDistance="0" dist="0" fitInPolygonOnly="0" maxCurvedCharAngleIn="25" xOffset="1.3" rotationAngle="0" distUnits="MM" repeatDistanceUnits="MM" preserveRotation="1" centroidWhole="0" labelOffsetMapUnitScale="3x:0,0,0,0,0,0" yOffset="-0.3" placement="1" distMapUnitScale="3x:0,0,0,0,0,0" offsetUnits="MM"/>
          <rendering displayAll="1" maxNumLabels="2000" fontLimitPixelSize="0" scaleMin="1" mergeLines="0" fontMaxPixelSize="10000" scaleMax="5001" zIndex="0" fontMinPixelSize="3" upsidedownLabels="0" minFeatureSize="0" drawLabels="1" obstacle="1" labelPerPart="0" limitNumLabels="0" scaleVisibility="1" obstacleFactor="1" obstacleType="0"/>
          <dd_properties>
            <Option type="Map">
              <Option name="name" value="" type="QString"/>
              <Option name="properties" type="Map">
                <Option name="Color" type="Map">
                  <Option name="active" value="true" type="bool"/>
                  <Option name="expression" value="CASE &#xd;&#xa;WHEN &quot;WYDZ_POL_L_EWID&quot; = 'T' THEN color_rgb(0,0,0)&#xd;&#xa;WHEN &quot;WYDZ_POL_L_EWID&quot; = 'N' THEN color_rgb(255,0,0)&#xd;&#xa;END" type="QString"/>
                  <Option name="type" value="3" type="int"/>
                </Option>
                <Option name="OffsetXY" type="Map">
                  <Option name="active" value="true" type="bool"/>
                  <Option name="expression" value="CASE &#xd;&#xa;WHEN &quot;WYDZ_POL_TYP_POW&quot; = 'D-STAN' and length(&quot;WYDZ_POL_WYDZ&quot;) = 2 THEN  &#xd;&#xa; CASE&#xd;&#xa;  WHEN length(  &quot;WYDZ_POL_UDZIAL&quot;  ||  &quot;WYDZ_POL_GAT&quot;  ||  &quot;WYDZ_POL_WIEK&quot;  ) &lt; 6 THEN concat('2, ', if( @qgis_os_name ='windows', '-0.8', '-0.3'))&#xd;&#xa;  WHEN length( &quot;WYDZ_POL_UDZIAL&quot; || &quot;WYDZ_POL_GAT&quot; || &quot;WYDZ_POL_WIEK&quot; ) = 6 THEN concat('3.1, ', if( @qgis_os_name ='windows', '-0.8', '-0.3'))&#xd;&#xa;  WHEN length( &quot;WYDZ_POL_UDZIAL&quot; || &quot;WYDZ_POL_GAT&quot; || &quot;WYDZ_POL_WIEK&quot; ) = 7 THEN concat('3.8, ', if( @qgis_os_name ='windows', '-0.8', '-0.3'))&#xd;&#xa;  WHEN length( &quot;WYDZ_POL_UDZIAL&quot; || &quot;WYDZ_POL_GAT&quot; || &quot;WYDZ_POL_WIEK&quot; ) > 7 THEN concat('5.2, ', if( @qgis_os_name ='windows', '-0.8', '-0.3'))&#xd;&#xa;&#xd;&#xa; END&#xa; &#xa; WHEN &quot;WYDZ_POL_TYP_POW&quot; = 'D-STAN' and length(&quot;WYDZ_POL_WYDZ&quot;) = 1 THEN  &#xa; CASE&#xa;  WHEN length(  &quot;WYDZ_POL_UDZIAL&quot;  ||  &quot;WYDZ_POL_GAT&quot;  ||  &quot;WYDZ_POL_WIEK&quot;  ) &lt; 5 THEN concat('1, ', if( @qgis_os_name ='windows', '-0.8', '-0.3'))&#xa;  WHEN length( &quot;WYDZ_POL_UDZIAL&quot; || &quot;WYDZ_POL_GAT&quot; || &quot;WYDZ_POL_WIEK&quot; ) = 5 THEN concat('2.1, ', if( @qgis_os_name ='windows', '-0.8', '-0.3'))&#xa;  WHEN length( &quot;WYDZ_POL_UDZIAL&quot; || &quot;WYDZ_POL_GAT&quot; || &quot;WYDZ_POL_WIEK&quot; ) = 6 THEN concat('2.8, ', if( @qgis_os_name ='windows', '-0.8', '-0.3'))&#xa;  WHEN length( &quot;WYDZ_POL_UDZIAL&quot; || &quot;WYDZ_POL_GAT&quot; || &quot;WYDZ_POL_WIEK&quot; ) > 6 THEN concat('4.2, ', if( @qgis_os_name ='windows', '-0.8', '-0.3'))&#xd;&#xa;&#xa; END&#xd;&#xa;  WHEN &quot;WYDZ_POL_TYP_POW&quot; IN ('PŁAZ', 'HAL', 'ZRĄB')  THEN&#xd;&#xa;  CASE&#xd;&#xa;   WHEN  length(&quot;WYDZ_POL_WYDZ&quot;) = 1  THEN  concat('1.3, ', if( @qgis_os_name ='windows', '-0.8', '-0.3'))&#xd;&#xa;   WHEN   length(&quot;WYDZ_POL_WYDZ&quot;) = 2 THEN  concat('1.9, ', if( @qgis_os_name ='windows', '-0.8', '-0.3'))&#xd;&#xa;  END&#xd;&#xa;END" type="QString"/>
                  <Option name="type" value="3" type="int"/>
                </Option>
              </Option>
              <Option name="type" value="collection" type="QString"/>
            </Option>
          </dd_properties>
        </settings>
      </rule>
      <rule key="{ea124ba0-894a-4092-82a0-d46bd6917ccd}" description="MIAN_SKROC">
        <settings>
          <text-style fontSizeMapUnitScale="3x:0,0,0,0,0,0" fontFamily="Arial Narrow" fontItalic="0" fieldName="CASE&#xd;&#xa; WHEN &quot;WYDZ_POL_TYP_POW&quot; NOT IN ('PŁAZ', 'HAL', 'ZRĄB', 'D-STAN' ) AND  &quot;typEtyk&quot; = 2 THEN  &quot;WYDZ_POL_POW_WYDZ&quot; &#xd;&#xa;END" fontUnderline="0" fontCapitals="0" fontLetterSpacing="0" multilineHeight="1" fontSizeUnit="Point" fontStrikeout="0" fontWordSpacing="0" useSubstitutions="0" namedStyle="Normalny" textOpacity="1" isExpression="1" blendMode="0" fontSize="9" previewBkgrdColor="#ffffff" fontWeight="50" textColor="0,0,0,255">
            <text-buffer bufferSizeMapUnitScale="3x:0,0,0,0,0,0" bufferNoFill="0" bufferJoinStyle="128" bufferSize="1" bufferColor="255,255,255,255" bufferSizeUnits="MM" bufferBlendMode="0" bufferDraw="0" bufferOpacity="1"/>
            <background shapeSVGFile="" shapeRadiiUnit="MM" shapeSizeY="0" shapeOffsetUnit="MM" shapeRadiiMapUnitScale="3x:0,0,0,0,0,0" shapeRotationType="0" shapeRadiiY="0" shapeOpacity="1" shapeBorderWidthMapUnitScale="3x:0,0,0,0,0,0" shapeRadiiX="0" shapeOffsetX="0" shapeBlendMode="0" shapeSizeMapUnitScale="3x:0,0,0,0,0,0" shapeJoinStyle="64" shapeBorderWidthUnit="MM" shapeRotation="0" shapeOffsetY="0" shapeBorderColor="128,128,128,255" shapeOffsetMapUnitScale="3x:0,0,0,0,0,0" shapeSizeX="0" shapeSizeUnit="MM" shapeBorderWidth="0" shapeDraw="0" shapeType="0" shapeSizeType="0" shapeFillColor="255,255,255,255"/>
            <shadow shadowBlendMode="6" shadowOpacity="0.7" shadowUnder="0" shadowRadiusMapUnitScale="3x:0,0,0,0,0,0" shadowColor="0,0,0,255" shadowOffsetMapUnitScale="3x:0,0,0,0,0,0" shadowOffsetGlobal="1" shadowOffsetAngle="135" shadowRadiusAlphaOnly="0" shadowOffsetUnit="MM" shadowRadiusUnit="MM" shadowScale="100" shadowDraw="0" shadowRadius="1.5" shadowOffsetDist="1"/>
            <substitutions/>
          </text-style>
          <text-format leftDirectionSymbol="&lt;" decimals="2" useMaxLineLengthForAutoWrap="1" addDirectionSymbol="0" plussign="0" multilineAlign="1" rightDirectionSymbol=">" placeDirectionSymbol="0" wrapChar="" reverseDirectionSymbol="0" autoWrapLength="0" formatNumbers="1"/>
          <placement placementFlags="10" repeatDistanceMapUnitScale="3x:0,0,0,0,0,0" offsetType="0" predefinedPositionOrder="TR,TL,BR,BL,R,L,TSR,BSR" quadOffset="7" centroidInside="0" maxCurvedCharAngleOut="-25" priority="10" repeatDistance="0" dist="0" fitInPolygonOnly="0" maxCurvedCharAngleIn="25" xOffset="0" rotationAngle="0" distUnits="MM" repeatDistanceUnits="MM" preserveRotation="1" centroidWhole="0" labelOffsetMapUnitScale="3x:0,0,0,0,0,0" yOffset="1.4" placement="1" distMapUnitScale="3x:0,0,0,0,0,0" offsetUnits="MM"/>
          <rendering displayAll="1" maxNumLabels="2000" fontLimitPixelSize="0" scaleMin="1" mergeLines="0" fontMaxPixelSize="10000" scaleMax="5001" zIndex="0" fontMinPixelSize="3" upsidedownLabels="0" minFeatureSize="0" drawLabels="1" obstacle="1" labelPerPart="0" limitNumLabels="0" scaleVisibility="1" obstacleFactor="1" obstacleType="0"/>
          <dd_properties>
            <Option type="Map">
              <Option name="name" value="" type="QString"/>
              <Option name="properties" type="Map">
                <Option name="Color" type="Map">
                  <Option name="active" value="true" type="bool"/>
                  <Option name="expression" value="CASE &#xd;&#xa;WHEN &quot;WYDZ_POL_L_EWID&quot; = 'T' THEN color_rgb(0,0,0)&#xd;&#xa;WHEN &quot;WYDZ_POL_L_EWID&quot; = 'N' THEN color_rgb(255,0,0)&#xd;&#xa;END" type="QString"/>
                  <Option name="type" value="3" type="int"/>
                </Option>
                <Option name="OffsetXY" type="Map">
                  <Option name="active" value="true" type="bool"/>
                  <Option name="expression" value="CASE &#xa;WHEN &quot;WYDZ_POL_TYP_POW&quot; = 'D-STAN' THEN  &#xa; CASE&#xa;  WHEN length(  &quot;WYDZ_POL_UDZIAL&quot;  ||  &quot;WYDZ_POL_GAT&quot;  ||  &quot;WYDZ_POL_WIEK&quot;  ) &lt; 6 THEN concat('2, ', if( @qgis_os_name ='windows', '-0.8', '-0.3'))&#xa;  WHEN length( &quot;WYDZ_POL_UDZIAL&quot; || &quot;WYDZ_POL_GAT&quot; || &quot;WYDZ_POL_WIEK&quot; ) = 6 THEN concat('3.1, ', if( @qgis_os_name ='windows', '-0.8', '-0.3'))&#xa;  WHEN length( &quot;WYDZ_POL_UDZIAL&quot; || &quot;WYDZ_POL_GAT&quot; || &quot;WYDZ_POL_WIEK&quot; ) = 7 THEN concat('3.8, ', if( @qgis_os_name ='windows', '-0.8', '-0.3'))&#xa;  WHEN length( &quot;WYDZ_POL_UDZIAL&quot; || &quot;WYDZ_POL_GAT&quot; || &quot;WYDZ_POL_WIEK&quot; ) > 7 THEN concat('5.2, ', if( @qgis_os_name ='windows', '-0.8', '-0.3'))&#xa; END&#xa;WHEN &quot;WYDZ_POL_TYP_POW&quot; IN ('PŁAZ', 'HAL', 'ZRĄB') AND  &quot;WYDZ_POL_POW_WYDZ&quot; > 0.1 THEN  concat('2, ', if( @qgis_os_name ='windows', '-0.8', '-0.3'))&#xa;END" type="QString"/>
                  <Option name="type" value="3" type="int"/>
                </Option>
              </Option>
              <Option name="type" value="collection" type="QString"/>
            </Option>
          </dd_properties>
        </settings>
      </rule>
    </rules>
  </labeling>
  <customproperties>
    <property value="COALESCE( &quot;ET_ID&quot;, '&lt;NULL>' )" key="dualview/previewExpressions"/>
    <property value="0" key="embeddedWidgets/count"/>
    <property value="false" key="labeling/addDirectionSymbol"/>
    <property value="0" key="labeling/angleOffset"/>
    <property value="0" key="labeling/blendMode"/>
    <property value="0" key="labeling/bufferBlendMode"/>
    <property value="255" key="labeling/bufferColorA"/>
    <property value="255" key="labeling/bufferColorB"/>
    <property value="255" key="labeling/bufferColorG"/>
    <property value="255" key="labeling/bufferColorR"/>
    <property value="false" key="labeling/bufferDraw"/>
    <property value="128" key="labeling/bufferJoinStyle"/>
    <property value="false" key="labeling/bufferNoFill"/>
    <property value="1" key="labeling/bufferSize"/>
    <property value="false" key="labeling/bufferSizeInMapUnits"/>
    <property value="0,0,0,0,0,0" key="labeling/bufferSizeMapUnitScale"/>
    <property value="0" key="labeling/bufferTransp"/>
    <property value="false" key="labeling/centroidInside"/>
    <property value="false" key="labeling/centroidWhole"/>
    <property value="3" key="labeling/decimals"/>
    <property value="false" key="labeling/displayAll"/>
    <property value="0" key="labeling/dist"/>
    <property value="false" key="labeling/distInMapUnits"/>
    <property value="0,0,0,0,0,0" key="labeling/distMapUnitScale"/>
    <property value="false" key="labeling/drawLabels"/>
    <property value="False" key="labeling/enabled"/>
    <property value="" key="labeling/fieldName"/>
    <property value="false" key="labeling/fitInPolygonOnly"/>
    <property value="0" key="labeling/fontCapitals"/>
    <property value="MS Shell Dlg 2" key="labeling/fontFamily"/>
    <property value="false" key="labeling/fontItalic"/>
    <property value="0" key="labeling/fontLetterSpacing"/>
    <property value="false" key="labeling/fontLimitPixelSize"/>
    <property value="10000" key="labeling/fontMaxPixelSize"/>
    <property value="3" key="labeling/fontMinPixelSize"/>
    <property value="8.25" key="labeling/fontSize"/>
    <property value="false" key="labeling/fontSizeInMapUnits"/>
    <property value="0,0,0,0,0,0" key="labeling/fontSizeMapUnitScale"/>
    <property value="false" key="labeling/fontStrikeout"/>
    <property value="false" key="labeling/fontUnderline"/>
    <property value="50" key="labeling/fontWeight"/>
    <property value="0" key="labeling/fontWordSpacing"/>
    <property value="false" key="labeling/formatNumbers"/>
    <property value="true" key="labeling/isExpression"/>
    <property value="true" key="labeling/labelOffsetInMapUnits"/>
    <property value="0,0,0,0,0,0" key="labeling/labelOffsetMapUnitScale"/>
    <property value="false" key="labeling/labelPerPart"/>
    <property value="&lt;" key="labeling/leftDirectionSymbol"/>
    <property value="false" key="labeling/limitNumLabels"/>
    <property value="25" key="labeling/maxCurvedCharAngleIn"/>
    <property value="-25" key="labeling/maxCurvedCharAngleOut"/>
    <property value="2000" key="labeling/maxNumLabels"/>
    <property value="false" key="labeling/mergeLines"/>
    <property value="0" key="labeling/minFeatureSize"/>
    <property value="3" key="labeling/multilineAlign"/>
    <property value="1" key="labeling/multilineHeight"/>
    <property value="Normal" key="labeling/namedStyle"/>
    <property value="true" key="labeling/obstacle"/>
    <property value="1" key="labeling/obstacleFactor"/>
    <property value="0" key="labeling/obstacleType"/>
    <property value="0" key="labeling/offsetType"/>
    <property value="0" key="labeling/placeDirectionSymbol"/>
    <property value="6" key="labeling/placement"/>
    <property value="10" key="labeling/placementFlags"/>
    <property value="false" key="labeling/plussign"/>
    <property value="TR,TL,BR,BL,R,L,TSR,BSR" key="labeling/predefinedPositionOrder"/>
    <property value="true" key="labeling/preserveRotation"/>
    <property value="#ffffff" key="labeling/previewBkgrdColor"/>
    <property value="5" key="labeling/priority"/>
    <property value="4" key="labeling/quadOffset"/>
    <property value="0" key="labeling/repeatDistance"/>
    <property value="0,0,0,0,0,0" key="labeling/repeatDistanceMapUnitScale"/>
    <property value="1" key="labeling/repeatDistanceUnit"/>
    <property value="false" key="labeling/reverseDirectionSymbol"/>
    <property value=">" key="labeling/rightDirectionSymbol"/>
    <property value="10000000" key="labeling/scaleMax"/>
    <property value="1" key="labeling/scaleMin"/>
    <property value="false" key="labeling/scaleVisibility"/>
    <property value="6" key="labeling/shadowBlendMode"/>
    <property value="0" key="labeling/shadowColorB"/>
    <property value="0" key="labeling/shadowColorG"/>
    <property value="0" key="labeling/shadowColorR"/>
    <property value="false" key="labeling/shadowDraw"/>
    <property value="135" key="labeling/shadowOffsetAngle"/>
    <property value="1" key="labeling/shadowOffsetDist"/>
    <property value="true" key="labeling/shadowOffsetGlobal"/>
    <property value="0,0,0,0,0,0" key="labeling/shadowOffsetMapUnitScale"/>
    <property value="1" key="labeling/shadowOffsetUnits"/>
    <property value="1.5" key="labeling/shadowRadius"/>
    <property value="false" key="labeling/shadowRadiusAlphaOnly"/>
    <property value="0,0,0,0,0,0" key="labeling/shadowRadiusMapUnitScale"/>
    <property value="1" key="labeling/shadowRadiusUnits"/>
    <property value="100" key="labeling/shadowScale"/>
    <property value="30" key="labeling/shadowTransparency"/>
    <property value="0" key="labeling/shadowUnder"/>
    <property value="0" key="labeling/shapeBlendMode"/>
    <property value="255" key="labeling/shapeBorderColorA"/>
    <property value="128" key="labeling/shapeBorderColorB"/>
    <property value="128" key="labeling/shapeBorderColorG"/>
    <property value="128" key="labeling/shapeBorderColorR"/>
    <property value="0" key="labeling/shapeBorderWidth"/>
    <property value="0,0,0,0,0,0" key="labeling/shapeBorderWidthMapUnitScale"/>
    <property value="1" key="labeling/shapeBorderWidthUnits"/>
    <property value="false" key="labeling/shapeDraw"/>
    <property value="255" key="labeling/shapeFillColorA"/>
    <property value="255" key="labeling/shapeFillColorB"/>
    <property value="255" key="labeling/shapeFillColorG"/>
    <property value="255" key="labeling/shapeFillColorR"/>
    <property value="64" key="labeling/shapeJoinStyle"/>
    <property value="0,0,0,0,0,0" key="labeling/shapeOffsetMapUnitScale"/>
    <property value="1" key="labeling/shapeOffsetUnits"/>
    <property value="0" key="labeling/shapeOffsetX"/>
    <property value="0" key="labeling/shapeOffsetY"/>
    <property value="0,0,0,0,0,0" key="labeling/shapeRadiiMapUnitScale"/>
    <property value="1" key="labeling/shapeRadiiUnits"/>
    <property value="0" key="labeling/shapeRadiiX"/>
    <property value="0" key="labeling/shapeRadiiY"/>
    <property value="0" key="labeling/shapeRotation"/>
    <property value="0" key="labeling/shapeRotationType"/>
    <property value="" key="labeling/shapeSVGFile"/>
    <property value="0,0,0,0,0,0" key="labeling/shapeSizeMapUnitScale"/>
    <property value="0" key="labeling/shapeSizeType"/>
    <property value="1" key="labeling/shapeSizeUnits"/>
    <property value="0" key="labeling/shapeSizeX"/>
    <property value="0" key="labeling/shapeSizeY"/>
    <property value="0" key="labeling/shapeTransparency"/>
    <property value="0" key="labeling/shapeType"/>
    <property value="&lt;substitutions/>" key="labeling/substitutions"/>
    <property value="255" key="labeling/textColorA"/>
    <property value="0" key="labeling/textColorB"/>
    <property value="0" key="labeling/textColorG"/>
    <property value="0" key="labeling/textColorR"/>
    <property value="0" key="labeling/textTransp"/>
    <property value="0" key="labeling/upsidedownLabels"/>
    <property value="false" key="labeling/useSubstitutions"/>
    <property value="" key="labeling/wrapChar"/>
    <property value="0" key="labeling/xOffset"/>
    <property value="0" key="labeling/yOffset"/>
    <property value="0" key="labeling/zIndex"/>
    <property key="variableNames">
      <value>__wielk_pow</value>
      <value>_wielk_pow</value>
      <value>wielk_pow</value>
    </property>
    <property key="variableValues">
      <value>0.1</value>
      <value>0,1</value>
      <value>0.1</value>
    </property>
  </customproperties>
  <blendMode>0</blendMode>
  <featureBlendMode>0</featureBlendMode>
  <layerOpacity>1</layerOpacity>
  <SingleCategoryDiagramRenderer diagramType="Histogram" attributeLegend="1">
    <DiagramCategory diagramOrientation="Up" sizeType="MM" scaleDependency="Area" labelPlacementMethod="XHeight" penColor="#000000" width="15" penAlpha="255" height="15" opacity="1" sizeScale="3x:0,0,0,0,0,0" minScaleDenominator="1000" lineSizeScale="3x:0,0,0,0,0,0" lineSizeType="MM" barWidth="5" enabled="0" maxScaleDenominator="1e+08" minimumSize="0" rotationOffset="270" penWidth="0" scaleBasedVisibility="0" backgroundColor="#ffffff" backgroundAlpha="255">
      <fontProperties style="" description="MS Shell Dlg 2,8.25,-1,5,50,0,0,0,0,0"/>
      <attribute label="" color="#000000" field=""/>
    </DiagramCategory>
  </SingleCategoryDiagramRenderer>
  <DiagramLayerSettings zIndex="0" priority="0" dist="0" showAll="1" linePlacementFlags="2" placement="0" obstacle="0">
    <properties>
      <Option type="Map">
        <Option name="name" value="" type="QString"/>
        <Option name="properties"/>
        <Option name="type" value="collection" type="QString"/>
      </Option>
    </properties>
  </DiagramLayerSettings>
  <geometryOptions removeDuplicateNodes="0" geometryPrecision="0">
    <activeChecks/>
    <checkConfiguration/>
  </geometryOptions>
  <fieldConfiguration>
    <field name="ADR_LES">
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
    <field name="typEtyk">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="WYDZ_POL_COUNTY">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="WYDZ_POL_DISTRICT">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="WYDZ_POL_MUNICIP">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="WYDZ_POL_COMMUNITY">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="WYDZ_POL_GRP">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="WYDZ_POL_COUNTY_L">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="WYDZ_POL_ODDZ">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="WYDZ_POL_WYDZ">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="WYDZ_POL_POW_GRAF">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="WYDZ_POL_ST_ODDZ">
      <editWidget type="TextEdit">
        <config>
          <Option type="Map">
            <Option name="IsMultiline" value="0" type="QString"/>
            <Option name="UseHtml" value="0" type="QString"/>
          </Option>
        </config>
      </editWidget>
    </field>
    <field name="WYDZ_POL_ST_WYDZ">
      <editWidget type="TextEdit">
        <config>
          <Option type="Map">
            <Option name="IsMultiline" value="0" type="QString"/>
            <Option name="UseHtml" value="0" type="QString"/>
          </Option>
        </config>
      </editWidget>
    </field>
    <field name="WYDZ_POL_ST_ADR_LES">
      <editWidget type="TextEdit">
        <config>
          <Option type="Map">
            <Option name="IsMultiline" value="0" type="QString"/>
            <Option name="UseHtml" value="0" type="QString"/>
          </Option>
        </config>
      </editWidget>
    </field>
    <field name="WYDZ_POL_L_EWID">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="WYDZ_POL_UDZIAL">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="WYDZ_POL_GAT">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="WYDZ_POL_WIEK">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="WYDZ_POL_ZADRZEW">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="WYDZ_POL_POW_WYDZ">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="WYDZ_POL_TYP_POW">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="WYDZ_POL_STRUKTUR">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="WYDZ_POL_SLMN_KOL">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
  </fieldConfiguration>
  <aliases>
    <alias name="" index="0" field="ADR_LES"/>
    <alias name="" index="1" field="MUNICIP"/>
    <alias name="" index="2" field="COMMUNITY"/>
    <alias name="" index="3" field="typEtyk"/>
    <alias name="" index="4" field="WYDZ_POL_COUNTY"/>
    <alias name="" index="5" field="WYDZ_POL_DISTRICT"/>
    <alias name="" index="6" field="WYDZ_POL_MUNICIP"/>
    <alias name="" index="7" field="WYDZ_POL_COMMUNITY"/>
    <alias name="" index="8" field="WYDZ_POL_GRP"/>
    <alias name="" index="9" field="WYDZ_POL_COUNTY_L"/>
    <alias name="" index="10" field="WYDZ_POL_ODDZ"/>
    <alias name="" index="11" field="WYDZ_POL_WYDZ"/>
    <alias name="" index="12" field="WYDZ_POL_POW_GRAF"/>
    <alias name="" index="13" field="WYDZ_POL_ST_ODDZ"/>
    <alias name="" index="14" field="WYDZ_POL_ST_WYDZ"/>
    <alias name="" index="15" field="WYDZ_POL_ST_ADR_LES"/>
    <alias name="" index="16" field="WYDZ_POL_L_EWID"/>
    <alias name="" index="17" field="WYDZ_POL_UDZIAL"/>
    <alias name="" index="18" field="WYDZ_POL_GAT"/>
    <alias name="" index="19" field="WYDZ_POL_WIEK"/>
    <alias name="" index="20" field="WYDZ_POL_ZADRZEW"/>
    <alias name="" index="21" field="WYDZ_POL_POW_WYDZ"/>
    <alias name="" index="22" field="WYDZ_POL_TYP_POW"/>
    <alias name="" index="23" field="WYDZ_POL_STRUKTUR"/>
    <alias name="" index="24" field="WYDZ_POL_SLMN_KOL"/>
  </aliases>
  <excludeAttributesWMS/>
  <excludeAttributesWFS/>
  <defaults>
    <default expression="" applyOnUpdate="0" field="ADR_LES"/>
    <default expression="" applyOnUpdate="0" field="MUNICIP"/>
    <default expression="" applyOnUpdate="0" field="COMMUNITY"/>
    <default expression="" applyOnUpdate="0" field="typEtyk"/>
    <default expression="" applyOnUpdate="0" field="WYDZ_POL_COUNTY"/>
    <default expression="" applyOnUpdate="0" field="WYDZ_POL_DISTRICT"/>
    <default expression="" applyOnUpdate="0" field="WYDZ_POL_MUNICIP"/>
    <default expression="" applyOnUpdate="0" field="WYDZ_POL_COMMUNITY"/>
    <default expression="" applyOnUpdate="0" field="WYDZ_POL_GRP"/>
    <default expression="" applyOnUpdate="0" field="WYDZ_POL_COUNTY_L"/>
    <default expression="" applyOnUpdate="0" field="WYDZ_POL_ODDZ"/>
    <default expression="" applyOnUpdate="0" field="WYDZ_POL_WYDZ"/>
    <default expression="" applyOnUpdate="0" field="WYDZ_POL_POW_GRAF"/>
    <default expression="" applyOnUpdate="0" field="WYDZ_POL_ST_ODDZ"/>
    <default expression="" applyOnUpdate="0" field="WYDZ_POL_ST_WYDZ"/>
    <default expression="" applyOnUpdate="0" field="WYDZ_POL_ST_ADR_LES"/>
    <default expression="" applyOnUpdate="0" field="WYDZ_POL_L_EWID"/>
    <default expression="" applyOnUpdate="0" field="WYDZ_POL_UDZIAL"/>
    <default expression="" applyOnUpdate="0" field="WYDZ_POL_GAT"/>
    <default expression="" applyOnUpdate="0" field="WYDZ_POL_WIEK"/>
    <default expression="" applyOnUpdate="0" field="WYDZ_POL_ZADRZEW"/>
    <default expression="" applyOnUpdate="0" field="WYDZ_POL_POW_WYDZ"/>
    <default expression="" applyOnUpdate="0" field="WYDZ_POL_TYP_POW"/>
    <default expression="" applyOnUpdate="0" field="WYDZ_POL_STRUKTUR"/>
    <default expression="" applyOnUpdate="0" field="WYDZ_POL_SLMN_KOL"/>
  </defaults>
  <constraints>
    <constraint notnull_strength="0" unique_strength="0" constraints="0" exp_strength="0" field="ADR_LES"/>
    <constraint notnull_strength="0" unique_strength="0" constraints="0" exp_strength="0" field="MUNICIP"/>
    <constraint notnull_strength="0" unique_strength="0" constraints="0" exp_strength="0" field="COMMUNITY"/>
    <constraint notnull_strength="0" unique_strength="0" constraints="0" exp_strength="0" field="typEtyk"/>
    <constraint notnull_strength="0" unique_strength="0" constraints="0" exp_strength="0" field="WYDZ_POL_COUNTY"/>
    <constraint notnull_strength="0" unique_strength="0" constraints="0" exp_strength="0" field="WYDZ_POL_DISTRICT"/>
    <constraint notnull_strength="0" unique_strength="0" constraints="0" exp_strength="0" field="WYDZ_POL_MUNICIP"/>
    <constraint notnull_strength="0" unique_strength="0" constraints="0" exp_strength="0" field="WYDZ_POL_COMMUNITY"/>
    <constraint notnull_strength="0" unique_strength="0" constraints="0" exp_strength="0" field="WYDZ_POL_GRP"/>
    <constraint notnull_strength="0" unique_strength="0" constraints="0" exp_strength="0" field="WYDZ_POL_COUNTY_L"/>
    <constraint notnull_strength="0" unique_strength="0" constraints="0" exp_strength="0" field="WYDZ_POL_ODDZ"/>
    <constraint notnull_strength="0" unique_strength="0" constraints="0" exp_strength="0" field="WYDZ_POL_WYDZ"/>
    <constraint notnull_strength="0" unique_strength="0" constraints="0" exp_strength="0" field="WYDZ_POL_POW_GRAF"/>
    <constraint notnull_strength="0" unique_strength="0" constraints="0" exp_strength="0" field="WYDZ_POL_ST_ODDZ"/>
    <constraint notnull_strength="0" unique_strength="0" constraints="0" exp_strength="0" field="WYDZ_POL_ST_WYDZ"/>
    <constraint notnull_strength="0" unique_strength="0" constraints="0" exp_strength="0" field="WYDZ_POL_ST_ADR_LES"/>
    <constraint notnull_strength="0" unique_strength="0" constraints="0" exp_strength="0" field="WYDZ_POL_L_EWID"/>
    <constraint notnull_strength="0" unique_strength="0" constraints="0" exp_strength="0" field="WYDZ_POL_UDZIAL"/>
    <constraint notnull_strength="0" unique_strength="0" constraints="0" exp_strength="0" field="WYDZ_POL_GAT"/>
    <constraint notnull_strength="0" unique_strength="0" constraints="0" exp_strength="0" field="WYDZ_POL_WIEK"/>
    <constraint notnull_strength="0" unique_strength="0" constraints="0" exp_strength="0" field="WYDZ_POL_ZADRZEW"/>
    <constraint notnull_strength="0" unique_strength="0" constraints="0" exp_strength="0" field="WYDZ_POL_POW_WYDZ"/>
    <constraint notnull_strength="0" unique_strength="0" constraints="0" exp_strength="0" field="WYDZ_POL_TYP_POW"/>
    <constraint notnull_strength="0" unique_strength="0" constraints="0" exp_strength="0" field="WYDZ_POL_STRUKTUR"/>
    <constraint notnull_strength="0" unique_strength="0" constraints="0" exp_strength="0" field="WYDZ_POL_SLMN_KOL"/>
  </constraints>
  <constraintExpressions>
    <constraint exp="" desc="" field="ADR_LES"/>
    <constraint exp="" desc="" field="MUNICIP"/>
    <constraint exp="" desc="" field="COMMUNITY"/>
    <constraint exp="" desc="" field="typEtyk"/>
    <constraint exp="" desc="" field="WYDZ_POL_COUNTY"/>
    <constraint exp="" desc="" field="WYDZ_POL_DISTRICT"/>
    <constraint exp="" desc="" field="WYDZ_POL_MUNICIP"/>
    <constraint exp="" desc="" field="WYDZ_POL_COMMUNITY"/>
    <constraint exp="" desc="" field="WYDZ_POL_GRP"/>
    <constraint exp="" desc="" field="WYDZ_POL_COUNTY_L"/>
    <constraint exp="" desc="" field="WYDZ_POL_ODDZ"/>
    <constraint exp="" desc="" field="WYDZ_POL_WYDZ"/>
    <constraint exp="" desc="" field="WYDZ_POL_POW_GRAF"/>
    <constraint exp="" desc="" field="WYDZ_POL_ST_ODDZ"/>
    <constraint exp="" desc="" field="WYDZ_POL_ST_WYDZ"/>
    <constraint exp="" desc="" field="WYDZ_POL_ST_ADR_LES"/>
    <constraint exp="" desc="" field="WYDZ_POL_L_EWID"/>
    <constraint exp="" desc="" field="WYDZ_POL_UDZIAL"/>
    <constraint exp="" desc="" field="WYDZ_POL_GAT"/>
    <constraint exp="" desc="" field="WYDZ_POL_WIEK"/>
    <constraint exp="" desc="" field="WYDZ_POL_ZADRZEW"/>
    <constraint exp="" desc="" field="WYDZ_POL_POW_WYDZ"/>
    <constraint exp="" desc="" field="WYDZ_POL_TYP_POW"/>
    <constraint exp="" desc="" field="WYDZ_POL_STRUKTUR"/>
    <constraint exp="" desc="" field="WYDZ_POL_SLMN_KOL"/>
  </constraintExpressions>
  <expressionfields/>
  <attributeactions>
    <defaultAction value="{00000000-0000-0000-0000-000000000000}" key="Canvas"/>
  </attributeactions>
  <attributetableconfig sortExpression="&quot;WYDZ_POL_STRUKTUR&quot;" actionWidgetStyle="dropDown" sortOrder="0">
    <columns>
      <column name="ADR_LES" width="144" type="field" hidden="0"/>
      <column width="-1" type="actions" hidden="1"/>
      <column name="MUNICIP" width="-1" type="field" hidden="0"/>
      <column name="COMMUNITY" width="-1" type="field" hidden="0"/>
      <column name="typEtyk" width="-1" type="field" hidden="0"/>
      <column name="WYDZ_POL_COUNTY" width="-1" type="field" hidden="0"/>
      <column name="WYDZ_POL_DISTRICT" width="-1" type="field" hidden="0"/>
      <column name="WYDZ_POL_MUNICIP" width="-1" type="field" hidden="0"/>
      <column name="WYDZ_POL_COMMUNITY" width="-1" type="field" hidden="0"/>
      <column name="WYDZ_POL_GRP" width="-1" type="field" hidden="0"/>
      <column name="WYDZ_POL_WYDZ" width="-1" type="field" hidden="0"/>
      <column name="WYDZ_POL_ODDZ" width="-1" type="field" hidden="0"/>
      <column name="WYDZ_POL_COUNTY_L" width="-1" type="field" hidden="0"/>
      <column name="WYDZ_POL_POW_GRAF" width="-1" type="field" hidden="0"/>
      <column name="WYDZ_POL_L_EWID" width="-1" type="field" hidden="0"/>
      <column name="WYDZ_POL_UDZIAL" width="-1" type="field" hidden="0"/>
      <column name="WYDZ_POL_GAT" width="-1" type="field" hidden="0"/>
      <column name="WYDZ_POL_WIEK" width="-1" type="field" hidden="0"/>
      <column name="WYDZ_POL_ZADRZEW" width="-1" type="field" hidden="0"/>
      <column name="WYDZ_POL_POW_WYDZ" width="-1" type="field" hidden="0"/>
      <column name="WYDZ_POL_TYP_POW" width="-1" type="field" hidden="0"/>
      <column name="WYDZ_POL_STRUKTUR" width="-1" type="field" hidden="0"/>
      <column name="WYDZ_POL_SLMN_KOL" width="-1" type="field" hidden="0"/>
      <column name="WYDZ_POL_ST_ODDZ" width="-1" type="field" hidden="0"/>
      <column name="WYDZ_POL_ST_WYDZ" width="-1" type="field" hidden="0"/>
      <column name="WYDZ_POL_ST_ADR_LES" width="-1" type="field" hidden="0"/>
    </columns>
  </attributetableconfig>
  <conditionalstyles>
    <rowstyles/>
    <fieldstyles/>
  </conditionalstyles>
  <editform tolerant="1">/home/qnox/upul/testy/ustaw_mapy/_ROBOCZE/022_ALEKSANDROW/0001_ALEKSANDROW_PIERWSZY</editform>
  <editforminit/>
  <editforminitcodesource>0</editforminitcodesource>
  <editforminitfilepath>/home/qnox/upul/testy/ustaw_mapy/_ROBOCZE/022_ALEKSANDROW/0001_ALEKSANDROW_PIERWSZY</editforminitfilepath>
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
    <field name="ADR_LES" editable="1"/>
    <field name="COMMUNITY" editable="1"/>
    <field name="MUNICIP" editable="1"/>
    <field name="WYDZ_POL_COMMUNITY" editable="0"/>
    <field name="WYDZ_POL_COUNTY" editable="0"/>
    <field name="WYDZ_POL_COUNTY_L" editable="0"/>
    <field name="WYDZ_POL_DISTRICT" editable="0"/>
    <field name="WYDZ_POL_GAT" editable="0"/>
    <field name="WYDZ_POL_GRP" editable="0"/>
    <field name="WYDZ_POL_L_EWID" editable="0"/>
    <field name="WYDZ_POL_MUNICIP" editable="0"/>
    <field name="WYDZ_POL_ODDZ" editable="0"/>
    <field name="WYDZ_POL_POW_GRAF" editable="0"/>
    <field name="WYDZ_POL_POW_WYDZ" editable="0"/>
    <field name="WYDZ_POL_SLMN_KOL" editable="0"/>
    <field name="WYDZ_POL_STRUKTUR" editable="0"/>
    <field name="WYDZ_POL_ST_ADR_LES" editable="0"/>
    <field name="WYDZ_POL_ST_ODDZ" editable="0"/>
    <field name="WYDZ_POL_ST_WYDZ" editable="0"/>
    <field name="WYDZ_POL_TYP_POW" editable="0"/>
    <field name="WYDZ_POL_UDZIAL" editable="0"/>
    <field name="WYDZ_POL_WIEK" editable="0"/>
    <field name="WYDZ_POL_WYDZ" editable="0"/>
    <field name="WYDZ_POL_ZADRZEW" editable="0"/>
    <field name="typEtyk" editable="1"/>
  </editable>
  <labelOnTop>
    <field name="ADR_LES" labelOnTop="0"/>
    <field name="COMMUNITY" labelOnTop="0"/>
    <field name="MUNICIP" labelOnTop="0"/>
    <field name="WYDZ_POL_COMMUNITY" labelOnTop="0"/>
    <field name="WYDZ_POL_COUNTY" labelOnTop="0"/>
    <field name="WYDZ_POL_COUNTY_L" labelOnTop="0"/>
    <field name="WYDZ_POL_DISTRICT" labelOnTop="0"/>
    <field name="WYDZ_POL_GAT" labelOnTop="0"/>
    <field name="WYDZ_POL_GRP" labelOnTop="0"/>
    <field name="WYDZ_POL_L_EWID" labelOnTop="0"/>
    <field name="WYDZ_POL_MUNICIP" labelOnTop="0"/>
    <field name="WYDZ_POL_ODDZ" labelOnTop="0"/>
    <field name="WYDZ_POL_POW_GRAF" labelOnTop="0"/>
    <field name="WYDZ_POL_POW_WYDZ" labelOnTop="0"/>
    <field name="WYDZ_POL_SLMN_KOL" labelOnTop="0"/>
    <field name="WYDZ_POL_STRUKTUR" labelOnTop="0"/>
    <field name="WYDZ_POL_ST_ADR_LES" labelOnTop="0"/>
    <field name="WYDZ_POL_ST_ODDZ" labelOnTop="0"/>
    <field name="WYDZ_POL_ST_WYDZ" labelOnTop="0"/>
    <field name="WYDZ_POL_TYP_POW" labelOnTop="0"/>
    <field name="WYDZ_POL_UDZIAL" labelOnTop="0"/>
    <field name="WYDZ_POL_WIEK" labelOnTop="0"/>
    <field name="WYDZ_POL_WYDZ" labelOnTop="0"/>
    <field name="WYDZ_POL_ZADRZEW" labelOnTop="0"/>
    <field name="typEtyk" labelOnTop="0"/>
  </labelOnTop>
  <widgets/>
  <previewExpression>COALESCE( "ET_ID", '&lt;NULL>' )</previewExpression>
  <mapTip>ET_ID</mapTip>
  <layerGeometryType>0</layerGeometryType>
</qgis>
