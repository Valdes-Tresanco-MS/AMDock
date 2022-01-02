# ##############################################################################
#                           GPLv3 LICENSE INFO                                 #
#                                                                              #
#  Copyright (C) 2020  Mario S. Valdes-Tresanco and Mario E. Valdes-Tresanco   #
#  Copyright (C) 2014  Jason Swails, Bill Miller III, and Dwight McGee         #
#                                                                              #
#   Project: https://github.com/Valdes-Tresanco-MS/gmx_MMPBSA                  #
#                                                                              #
#   This program is free software; you can redistribute it and/or modify it    #
#  under the terms of the GNU General Public License version 3 as published    #
#  by the Free Software Foundation.                                            #
#                                                                              #
#  This program is distributed in the hope that it will be useful, but         #
#  WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY  #
#  or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License    #
#  for more details.                                                           #
# ##############################################################################

from setuptools import setup, find_packages
import versioneer
import sys

with open("README.md", "r") as f:
    LONG_DESCRIPTION = f.read()

if sys.version_info[:2] < (3, 8):
    raise RuntimeError("seaborn requires python >= 3.8.")

setup(
    name='AMDock',
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    packages=find_packages(),
    package_data={"AMDock": ["data/*"]},
    license='GPLv3',
    author='Mario S. Valdes-Tresanco and Mario E. Valdes-Tresanco ',
    author_email='mariosergiovaldes145@gmail.com',
    maintainer='Mario S. Valdes-Tresanco',
    maintainer_email='mariosergiovaldes145@gmail.com',
    url='https://github.com/Valdes-Tresanco-MS/AMDock',
    description="AMDock: Assisted Molecular Docking with Autodock4 and Autodock Vina",
    long_description=LONG_DESCRIPTION,
    long_description_content_type='text/markdown',
    keywords=['AMDock', 'AutoDock Vina', 'AutoDock4', 'AutoDock4Zn', 'Docking'],
    install_requires=['PyQt5>=5.15.4'],
    entry_points={
        "gui_scripts": [
            "AMDock=AMDock.Docking_Program:run"
            ]}
)
