# ***************************************************************************
# *   Copyright (c) 2023 Syres                              *
# *                                                                         *
# *   This program is free software; you can redistribute it and/or modify  *
# *   it under the terms of the GNU Lesser General Public License (LGPL)    *
# *   as published by the Free Software Foundation; either version 2 of     *
# *   the License, or (at your option) any later version.                   *
# *   for detail see the LICENCE text file.                                 *
# *                                                                         *
# *   This program is distributed in the hope that it will be useful,       *
# *   but WITHOUT ANY WARRANTY; without even the implied warranty of        *
# *   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the         *
# *   GNU Library General Public License for more details.                  *
# *                                                                         *
# *   You should have received a copy of the GNU Library General Public     *
# *   License along with this program; if not, write to the Free Software   *
# *   Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  *
# *   USA                                                                   *
# *                                                                         *
# ***************************************************************************
"""Provides the TechDraw FillTemplateFields GuiCommand."""

__title__ = "TechDrawTools.CommandFillTemplateFields"
__author__ = "Syres"
__url__ = "https://www.freecad.org"
__version__ = "00.01"
__date__ = "2023/11/23"

from PySide.QtCore import QT_TRANSLATE_NOOP

import FreeCAD as App
import FreeCADGui as Gui
import datetime

class CommandFillTemplateFields:
    """Use document info to populate the tempate fields."""

    def GetResources(self):
        """Return a dictionary with data that will be used by the button or menu item."""
        return {'Pixmap': 'actions/TechDraw_FillTemplateFields.svg',
                'Accel': "",
                'MenuText': QT_TRANSLATE_NOOP("TechDraw_FillTemplateFields", "Update template fields"),
                'ToolTip': QT_TRANSLATE_NOOP("TechDraw_FillTemplateFields", "Use document info to populate the tempate fields<br>\
                - ")}

    def Activated(self):
        """Run the following code when the command is activated (button press)."""
        objs = App.ActiveDocument.Objects
        for obj in objs:
            if obj.TypeId == "TechDraw::DrawPage":
                page = obj
                texts = page.Template.EditableTexts
                projgrp_view = page.Views[0]
                for key, value in texts.items():
                    App.Console.PrintLog("{0} = {1} | ".format(key, value))
                    if key == "AUTHOR_NAME" or key == "NomAuteur":
                        texts[key] = App.ActiveDocument.CreatedBy
                    if key == "FC-SC" or key == "Echelle" or key == "Масштаб" or key == "ESCALA" or key == "SCALE":
                        if projgrp_view:
                            if projgrp_view.Scale < 1:
                                texts[key] = "1 : " + str(int(1 / projgrp_view.Scale))
                            else:
                                texts[key] = str(int(projgrp_view.Scale)) + " : 1"
                    if key == "DRAWING_TITLE" or key == "DOCUMENT_TYPE" or key == "Titre" or key == "Название" or key == "TITULO" or key == "DRAWING_NAME":
                        texts[key] = App.ActiveDocument.Label
                    if key == "FreeCAD_DRAWING" or key == "TITLELINE-1" or key == "Sous_titre" or key == "SUBTITULO" or key == "SUBTITLE":
                        texts[key] = App.ActiveDocument.Comment
                    if key == "NomSuperviseur" or key == "COMPANYNAME":
                        texts[key] = App.ActiveDocument.Company
                    if key == "COPYRIGHT" or key == "RIGHTS":
                        texts[key] = App.ActiveDocument.License
                    if key == "FC-DATE" or key == "DATE" or key == "DateVerification" or key == "Дата" or key == "FECHA3" or key == "DATE-2":
                        dt = datetime.datetime.strptime(App.ActiveDocument.LastModifiedDate, '%Y-%m-%dT%H:%M:%SZ')
                        if value == "MM/DD/YYYY":
                             texts[key] = ('{0}/{1}/{2:02}'.format(dt.month, dt.day, dt.year % 100))
                        elif value == "YYYY-MM-DD":
                             texts[key] = ('{0}-{1}-{2:02}'.format(dt.year, dt.month, dt.day % 100))
                        else:
                             texts[key] = ('{0}/{1}/{2:02}'.format(dt.day, dt.month, dt.year % 100))
                    if key == "DateDeCreation" or key == "FECHA2" or key == "DATE-1":
                        dt = datetime.datetime.strptime(App.ActiveDocument.CreationDate, '%Y-%m-%dT%H:%M:%SZ')
                        if value == "MM/DD/YYYY":
                            texts[key] = ('{0}/{1}/{2:02}'.format(dt.month, dt.day, dt.year % 100))
                        elif value == "YYYY-MM-DD":
                             texts[key] = ('{0}-{1}-{2:02}'.format(dt.year, dt.month, dt.day % 100))
                        else:
                            texts[key] = ('{0}/{1}/{2:02}'.format(dt.day, dt.month, dt.year % 100))
                page.Template.EditableTexts = texts



    def IsActive(self):
        """Return True when the command should be active or False when it should be disabled (greyed)."""
        if App.ActiveDocument:
            objs = App.ActiveDocument.Objects
            for obj in objs:
                if obj.TypeId == "TechDraw::DrawPage":
                    page = obj
                    texts = page.Template.EditableTexts
                    if texts:
                        return True
        else:
            return False

#
# The command must be "registered" with a unique name by calling its class.
Gui.addCommand('TechDraw_FillTemplateFields', CommandFillTemplateFields())
