# -*- coding: utf-8 -*-

"""
***************************************************************************
*   Korto19 27.08.2022                                                                      *
*   This program is free software; you can redistribute it and/or modify  *
*   it under the terms of the GNU General Public License as published by  *
*   the Free Software Foundation; either version 2 of the License, or     *
*   (at your option) any later version.                                   *
*                                                                         *
***************************************************************************
"""
from PyQt5.QtCore import *
from qgis.PyQt.QtCore import QCoreApplication
from qgis.core import (QgsProject,
                       QgsMapLayerType,
                       QgsProcessingParameterLayout,
                       QgsLayoutItemHtml,
                       QgsProcessingParameterBoolean,
                       QgsProcessingParameterField,
                       QgsProcessingParameterFile,
                       QgsLayoutFrame,
                       QgsLayoutMeasurement,
                       QgsUnitTypes,
                       QgsFields,
                       QgsField,
                       QgsFeature,
                       QgsFeatureRequest,
                       QgsProcessing,
                       QgsFeatureSink,
                       QgsProcessingException,
                       QgsProcessingAlgorithm,
                       QgsProcessingParameterFeatureSource,
                       QgsProcessingParameterFeatureSink)
from qgis import processing
from qgis.PyQt.QtGui import QIcon

class TransposeHTML(QgsProcessingAlgorithm):
    """
    This is an example algorithm that takes a vector layer and
    creates a new identical one.

    It is meant to be used as an example of how to create your own
    algorithms and explain methods and variables used to do it. An
    algorithm like this will be available in all elements, and there
    is not need for additional work.

    All Processing algorithms should extend the QgsProcessingAlgorithm
    class.
    """

    # Constants used to refer to parameters and outputs. They will be
    # used when calling the algorithm from another algorithm, or when
    # calling from the QGIS console.

    INPUT   = 'INPUT'
    INPUT_A = 'INPUT_A'
    INPUT_F = 'INPUT_F'
    INPUT_L = 'INPUT_L'
    INPUT_C = 'INPUT_C'
    OUTPUT  = 'OUTPUT'

    def tr(self, string):
        """
        Returns a translatable string with the self.tr() function.
        """
        return QCoreApplication.translate('Processing', string)

    #icona dell'algoritmo di processing
    def icon(self):
        icon = QIcon(":images/themes/default/mIconHtml.svg")
        return icon
        
    def createInstance(self):
        return TransposeHTML()

    def name(self):
        """
        Returns the algorithm name, used for identifying the algorithm. This
        string should be fixed for the algorithm, and must not be localised.
        The name should be unique within each provider. Names should contain
        lowercase alphanumeric characters only and no spaces or other
        formatting characters.
        """
        return 'TransposeHTML'

    def displayName(self):
        """
        Returns the translated algorithm name, which should be used for any
        user-visible display of the algorithm name.
        """
        return self.tr('TransposeHTML')

    def group(self):
        """
        Returns the name of the group this algorithm belongs to. This string
        should be localised.
        """
        return self.tr('Korto19')

    def groupId(self):
        """
        Returns the unique ID of the group this algorithm belongs to. This
        string should be fixed for the algorithm, and must not be localised.
        The group id should be unique within each provider. Group id should
        contain lowercase alphanumeric characters only and no spaces or other
        formatting characters.
        """
        return 'Korto19'

    def shortHelpString(self):
        """
        Returns a localised short helper string for the algorithm. This string
        should provide a basic description about what the algorithm does and the
        parameters and outputs associated with it..
        """
        header = '''
            <img src=":images/themes/default/mIconHtml.svg" width="30" height="30" style="float:right">
        '''
        return self.tr(header + "Create a dynamic HTML frame in composer with transposed select data fields\
                                <br>Optionally personal css file by modifying the one attached and save as css file\
                                <br>By default if present field alias is used\
                                <br><strong><mark style='color:red'>Input layer must by related to Atlas\
                                \n<strong><mark style='color:black'>Default css style\n\
                                \n<mark style='color:blue'>table.KortoTable {<br>border: 1px solid #1C6EA4;\
                                background-color: #EEEEEE;<br> width: 100%;text-align: left;border-collapse: collapse;}\
                                <br>td, table.blueTable th {border: 1px solid #AAAAAA; padding: 3px 2px;}\
                                <br>td{nfont-size: 13px;}\
                                <br>td.desc {font-size: 15px; font-weight: bold;}\
                                <br>tr:nth-child(even){background: #D0E4F5;}")
   
    def flags(self):
        return super().flags() | QgsProcessingAlgorithm.FlagNoThreading
   
    def initAlgorithm(self, config=None):
        """
        Here we define the inputs and output of the algorithm, along
        with some other properties.
        """

        # We add the input vector features source. It can have any kind of
        # geometry.
        self.addParameter(
            QgsProcessingParameterFeatureSource(
                self.INPUT,
                self.tr('Input Layer for data'),
                [QgsProcessing.TypeMapLayer]
            )
        )

        self.addParameter(
            QgsProcessingParameterField(
                self.INPUT_F,
                self.tr('Select fields for Html frame'),
                allowMultiple = True,
                defaultToAllFields = True,
                parentLayerParameterName=self.INPUT
            )
        )

        self.addParameter(
            QgsProcessingParameterBoolean(
                self.INPUT_A,
                'Field alias default Yes/[N]',
                1
            )
        )

        self.addParameter(
            QgsProcessingParameterLayout(
                self.INPUT_L,
                self.tr('Select Atlas Layout where insert Html frame'),
            )
        )

        self.addParameter(
            QgsProcessingParameterFile(
                self.INPUT_C,
                'CSS file',
                behavior=QgsProcessingParameterFile.File, fileFilter='Css file (*.css)',
                optional = True
            )
        )

    def processAlgorithm(self, parameters, context, feedback):
        """
        Here is where the processing itself takes place.
        """

        # Retrieve the feature source and sink. The 'dest_id' variable is used
        # to uniquely identify the feature sink, and must be included in the
        # dictionary returned by the processAlgorithm function.
        source = self.parameterAsSource(
            parameters,
            self.INPUT,
            context
        )

        sourceF = self.parameterAsMatrix(
            parameters,
            self.INPUT_F,
            context)
            
        comp_layout = self.parameterAsString(
            parameters,
            self.INPUT_L,
            context)
        
        alias_v = self.parameterAsBool(
            parameters,
            self.INPUT_A,
            context)
    
        fogliocss = self.parameterAsString(
            parameters,
            self.INPUT_C,
            context)

        # If source was not found, throw an exception to indicate that the algorithm
        # encountered a fatal error. The exception text can be any string, but in this
        # case we use the pre-built invalidSourceError method to return a standard
        # helper text for when a source cannot be evaluated
        if source is None:
            raise QgsProcessingException(self.invalidSourceError(parameters, self.INPUT))
        
        features = source.getFeatures()
        
        HTML_string = '<table class="KortoTable"><tbody>'
        
        for field in source.fields():
            if field.name() in sourceF:
                if alias_v and len(field.alias())!= 0:
                    field_name = field.alias()
                else:
                    field_name = field.name()
                HTML_string = HTML_string + '<tr><td class="desc">'+ field_name + ': </td><td>[% "'+ field_name + '" %]<br></td></tr>'

        HTML_string = HTML_string + '</tbody></table>'
        
        
        if not fogliocss:
            user_css = '''table.KortoTable {
            border: 1px solid #1C6EA4;
            background-color: #EEEEEE;
            width: 100%;
            text-align: left;
            border-collapse: collapse;
            }
            td, table.blueTable th {
            border: 1px solid #AAAAAA;
            padding: 3px 2px;
            }
            td {
            font-size: 13px;
            }
            td.desc {
            font-size: 15px;
            font-weight: bold;
            }
            tr:nth-child(even) {
            background: #D0E4F5;
            }'''
        else:
            with open(fogliocss) as f:
                user_css = f.read()
            f.close()
        
        proj = QgsProject.instance()
        lmgr = proj.layoutManager()
        
        layout = lmgr.layoutByName(str(comp_layout))

        layout_html = QgsLayoutItemHtml(layout)
        
        html_frame = QgsLayoutFrame(layout, layout_html)
        html_frame.attemptSetSceneRect(QRectF(10, 10, 30, 20))
        html_frame.setFrameEnabled(True)
        html_frame.setFrameStrokeWidth(QgsLayoutMeasurement(0.1, QgsUnitTypes.LayoutMillimeters))
        
        layout_html.setUserStylesheetEnabled(True)
        layout_html.setUserStylesheet(user_css)
        layout_html.addFrame(html_frame)
        layout_html.setContentMode(QgsLayoutItemHtml.ManualHtml)
        layout_html.setHtml(HTML_string)
        layout_html.loadHtml()
        
        return{}