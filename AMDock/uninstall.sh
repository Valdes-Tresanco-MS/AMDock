#!/bin/bash

if [ -z "$SUDO_COMMAND" ]
then
    mntusr=$(id -u) grpusr=$(id -g) sudo $0 $*
    exit 0
fi

SCRIPT_LOCATION=$0

if [ -x "$READLINK" ]; then
  while [ -L "$SCRIPT_LOCATION" ]; do
    SCRIPT_LOCATION=`"$READLINK" -e "$SCRIPT_LOCATION"`
  done
fi

script_path=`readlink -f $SCRIPT_LOCATION`
AMDock_InstallDir=`dirname $script_path`

install_confirmation=`zenity --question --title="AMDock Uninstaller" --text="The AMDock program will be uninstalled.\n Do you wish to continue?"`

if [ $? -ne 0 ]; then
    exit 0
fi

## check that AMDock files not exits in destinity
echo $AMDock_InstallDir
if [ -d "$AMDock_InstallDir" ];then
    rm -r "$AMDock_InstallDir" -f | zenity --progress --pulsate --title="AMDock Uninstaller" --text="Deleting AMDock files..." --auto-close --no-cancel
    if [ -f $HOME/.pymol/startup/grid_amdock.py ];then
        rm $HOME/.pymol/startup/grid_amdock.py
    elif [ -f $HOME/.pymol/startup/grid_amdock.pyc ];then
        rm $HOME/.pymol/startup/grid_amdock.pyc
    fi
else    
    zenity --error --title="AMDock Uninstaller" --text="AMDock cann't be deleted.\n Delete all files manually."
    exit 1
fi 


desktop_apps=$HOME/.local/share/applications
if [ -f "$desktop_apps/AMDock.desktop" ]
  then
  rm $desktop_apps/AMDock.desktop
else
  message "AMDock application launcher cann't be deleted. Delete manually."
  
fi

if [ -f "$desktop_apps/AMDock_Uninstaller.desktop" ]
  then
  rm $desktop_apps/AMDock_Uninstaller.desktop
else
  message "AMDock application launcher cann't be deleted. Delete manually."
  
fi

zenity --info --title="AMDock Installer" --text="Done!!!"


