<!DOCTYPE qgis PUBLIC 'http://mrcc.com/qgis.dtd' 'SYSTEM'>
<qgis maxScale="1000" minScale="100000" version="3.16.7-Hannover" styleCategories="AllStyleCategories" hasScaleBasedVisibilityFlag="0">
  <flags>
    <Identifiable>1</Identifiable>
    <Removable>1</Removable>
    <Searchable>1</Searchable>
  </flags>
  <temporal enabled="0" fetchMode="0" mode="0">
    <fixedRange>
      <start></start>
      <end></end>
    </fixedRange>
  </temporal>
  <customproperties>
    <property key="WMSBackgroundLayer" value="false"/>
    <property key="WMSPublishDataSourceUrl" value="false"/>
    <property key="embeddedWidgets/count" value="0"/>
    <property key="identify/format" value="Value"/>
  </customproperties>
  <pipe>
    <provider>
      <resampling zoomedOutResamplingMethod="nearestNeighbour" maxOversampling="2" enabled="false" zoomedInResamplingMethod="nearestNeighbour"/>
    </provider>
    <rasterrenderer nodataColor="" classificationMin="0" opacity="1" type="singlebandpseudocolor" band="1" classificationMax="6" alphaBand="-1">
      <rasterTransparency/>
      <minMaxOrigin>
        <limits>None</limits>
        <extent>WholeRaster</extent>
        <statAccuracy>Exact</statAccuracy>
        <cumulativeCutLower>0.02</cumulativeCutLower>
        <cumulativeCutUpper>0.98</cumulativeCutUpper>
        <stdDevFactor>2</stdDevFactor>
      </minMaxOrigin>
      <rastershader>
        <colorrampshader classificationMode="1" labelPrecision="6" clip="0" maximumValue="6" colorRampType="EXACT" minimumValue="0">
          <colorramp type="gradient" name="[source]">
            <prop v="255,255,204,255" k="color1"/>
            <prop v="37,52,148,255" k="color2"/>
            <prop v="0" k="discrete"/>
            <prop v="gradient" k="rampType"/>
            <prop v="0.25;161,218,180,255:0.5;65,182,196,255:0.75;44,127,184,255" k="stops"/>
          </colorramp>
          <item alpha="255" label="0" color="#000000" value="0"/>
          <item alpha="255" label="1" color="#1f8fff" value="1"/>
          <item alpha="255" label="2" color="#cecece" value="2"/>
          <item alpha="255" label="3" color="#176b04" value="3"/>
          <item alpha="255" label="4" color="#92c21a" value="4"/>
          <item alpha="255" label="5" color="#268f84" value="5"/>
          <item alpha="255" label="6" color="#9e5833" value="6"/>
        </colorrampshader>
      </rastershader>
    </rasterrenderer>
    <brightnesscontrast gamma="1" brightness="0" contrast="0"/>
    <huesaturation colorizeOn="0" colorizeStrength="100" grayscaleMode="0" saturation="0" colorizeGreen="128" colorizeRed="255" colorizeBlue="128"/>
    <rasterresampler maxOversampling="2"/>
    <resamplingStage>resamplingFilter</resamplingStage>
  </pipe>
  <blendMode>0</blendMode>
</qgis>
