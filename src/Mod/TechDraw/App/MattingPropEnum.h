/***************************************************************************
 *   Copyright (c) 2020 WandererFan <wandererfan@gmail.com>                *
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

#ifndef MATTINGENUMS_H_
#define MATTINGENUMS_H_

#include <string>
#include <vector>
#include <QCoreApplication>

#include <Mod/TechDraw/TechDrawGlobal.h>


namespace TechDraw
{

enum MattingType { CircleMattingStyle = 0,
                 SquareMattingStyle};

class TechDrawExport MattingPropEnum {
    Q_DECLARE_TR_FUNCTIONS(TechDraw::MattingPropEnum)

    public:
        static const char* MattingTypeEnums[];
        static const int   MattingCount;
        static const std::vector<std::string> MattingTypeIcons;

private:

};

} //end namespace TechDraw
#endif
