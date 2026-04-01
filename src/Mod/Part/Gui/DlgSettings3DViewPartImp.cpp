// SPDX-License-Identifier: LGPL-2.1-or-later

/***************************************************************************
 *   Copyright (c) 2002 Jürgen Riegel <juergen.riegel@web.de>              *
 *                                                                         *
 *   This file is part of the FreeCAD CAx development system.              *
 *                                                                         *
 *   This library is free software; you can redistribute it and/or         *
 *   modify it under the terms of the GNU Library General Public           *
 *   License as published by the Free Software Foundation; either          *
 *   version 2 of the License, or (at your option) any later version.      *
 *                                                                         *
 *   This library  is distributed in the hope that it will be useful,      *
 *   but WITHOUT ANY WARRANTY; without even the implied warranty of        *
 *   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the         *
 *   GNU Library General Public License for more details.                  *
 *                                                                         *
 *   You should have received a copy of the GNU Library General Public     *
 *   License along with this library; see the file COPYING.LIB. If not,    *
 *   write to the Free Software Foundation, Inc., 59 Temple Place,         *
 *   Suite 330, Boston, MA  02111-1307, USA                                *
 *                                                                         *
 ***************************************************************************/

#include <QMessageBox>


#include <App/Application.h>
#include <App/Document.h>
#include <Gui/Application.h>
#include <Gui/DlgCheckableMessageBox.h>
#include <Gui/Document.h>

#include "DlgSettings3DViewPartImp.h"
#include "ui_DlgSettings3DViewPart.h"
#include "ViewProvider.h"


using namespace PartGui;

/**
 *  Constructs a DlgSettings3DViewPart which is a child of 'parent', with the
 *  name 'name' and widget flags set to 'f'
 */
DlgSettings3DViewPart::DlgSettings3DViewPart(QWidget* parent)
    : PreferencePage(parent)
    , ui(new Ui_DlgSettings3DViewPart)
    , checkValue(false)
{
    ui->setupUi(this);
    connect(
        ui->maxDeviation,
        qOverload<double>(&QDoubleSpinBox::valueChanged),
        this,
        &DlgSettings3DViewPart::onMaxDeviationValueChanged
    );
    connect(
        ui->maxAngularDeflection,
        qOverload<double>(&QDoubleSpinBox::valueChanged),
        this,
        &DlgSettings3DViewPart::onMaxAngularDeflectionValueChanged
    );
    ParameterGrp::handle hPart = App::GetApplication().GetParameterGroupByPath(
        "User parameter:BaseApp/Preferences/Mod/Part"
    );
    const double minDeviationlowerLimit
        = hPart->GetFloat("MinimumDeviation", ui->maxDeviation->minimum());
    ui->maxDeviation->setMinimum(minDeviationlowerLimit);
    const double minAngleDeflectionlowerLimit
        = hPart->GetFloat("MinimumDeviation", ui->maxAngularDeflection->minimum());
    ui->maxAngularDeflection->setMinimum(minAngleDeflectionlowerLimit);
}

/**
 *  Destroys the object and frees any allocated resources
 */
DlgSettings3DViewPart::~DlgSettings3DViewPart() = default;

void DlgSettings3DViewPart::onMaxDeviationValueChanged(double vMaxDev)
{
    if (!this->isVisible()) {
        return;
    }
    const double maxDevMinThreshold = 0.01;
    if (vMaxDev < maxDevMinThreshold && !checkValue) {
        checkValue = true;
        QMessageBox::warning(
            this,
            tr("Deviation"),
            tr("Setting a too small deviation causes the tessellation to take longer"
               " and thus freezes or slows down the GUI.")
        );
    }
    eitherValueChanged = true;
}

void DlgSettings3DViewPart::onMaxAngularDeflectionValueChanged(double vMaxAngle)
{
    if (!this->isVisible()) {
        return;
    }
    /**
     *  The lower threshold of 2.0 was determined by testing
     *  as laid out in the table as per comment hyperlink:
     *  https://github.com/FreeCAD/FreeCAD/issues/15951#issuecomment-2304308163
     */
    const double vMaxAngleMinThreshold = 2.0;
    if (vMaxAngle < vMaxAngleMinThreshold && !checkValue) {
        checkValue = true;
        QMessageBox::warning(
            this,
            tr("Angle deflection"),
            tr("Setting a too small angle deviation causes the tessellation to take longer"
               " and thus freezes or slows down the GUI.")
        );
    }
    eitherValueChanged = true;
}

void DlgSettings3DViewPart::saveSettings()
{
    ui->maxDeviation->onSave();
    ui->maxAngularDeflection->onSave();

    ParameterGrp::handle hPart = App::GetApplication().GetParameterGroupByPath(
        "User parameter:BaseApp/Preferences/Mod/Part");
    const bool deviationOrDeflectionPrompt = hPart->GetBool("DeviationOrDeflectionPrompt", true);
    const bool autoChangeDevDefl = hPart->GetBool("AutoChangeDevDefl", true);
    if (eitherValueChanged && deviationOrDeflectionPrompt) {
        QMessageBox msgBox(this);
        msgBox.setIcon(QMessageBox::Warning);
        msgBox.setWindowTitle(tr("Update models"));
        msgBox.setText(tr("Are you sure you want to apply shape settings to models in currently "
                          "open documents?"));
        msgBox.setInformativeText(tr(
            "If the existing models on screen are currently high detail "
            "this maybe impacted adversely. Your choice will be recorded in the config settings."));
        msgBox.setStandardButtons(QMessageBox::Yes | QMessageBox::No);
        msgBox.setDefaultButton(QMessageBox::No);
        int ret = msgBox.exec();
        if (ret == QMessageBox::Yes) {
            updateOpenModels();
            notifyUpdateModels();
            hPart->SetBool("AutoChangeDevDefl", autoChangeDevDefl);
        }
        else {
            Base::Console().Warning("User clicked No to updating the open models\n");
            notifyUpdateModels();
            hPart->SetBool("AutoChangeDevDefl", autoChangeDevDefl);
        }
    }
    else if (eitherValueChanged && !deviationOrDeflectionPrompt && autoChangeDevDefl) {
        updateOpenModels();
    }
}
void DlgSettings3DViewPart::loadSettings()
{
    ui->maxDeviation->onRestore();
    ui->maxAngularDeflection->onRestore();
}

/**
 * Sets the strings of the subwidgets using the current language.
 */
void DlgSettings3DViewPart::changeEvent(QEvent* e)
{
    if (e->type() == QEvent::LanguageChange) {
        ui->retranslateUi(this);
    }
    else {
        QWidget::changeEvent(e);
    }
}

void DlgSettings3DViewPart::notifyUpdateModels()
{
    Gui::Dialog::DlgCheckableMessageBox::showMessage(
        QObject::tr("Update models reminder"),
        QObject::tr("Do you want to be promted for this again in the future"),
        QLatin1String("User parameter:BaseApp/Preferences/Mod/Part"),
        QLatin1String("DeviationOrDeflectionPrompt"),
        true,  // Default ParamEntry
        true,  // checkbox state
        QObject::tr("Keep notifying me of model shape setting changes"));
}

void DlgSettings3DViewPart::updateOpenModels()
{
    // search for Part view providers and apply the new settings
    std::vector<App::Document*> docs = App::GetApplication().getDocuments();
    for (std::vector<App::Document*>::iterator it = docs.begin(); it != docs.end(); ++it) {
        Gui::Document* doc = Gui::Application::Instance->getDocument(*it);
        std::vector<Gui::ViewProvider*> views =
            doc->getViewProvidersOfType(ViewProviderPart::getClassTypeId());
        for (std::vector<Gui::ViewProvider*>::iterator jt = views.begin(); jt != views.end();
             ++jt) {
            static_cast<ViewProviderPart*>(*jt)->reload();
        }
    }
}

#include "moc_DlgSettings3DViewPartImp.cpp"
