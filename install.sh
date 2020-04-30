#!/bin/bash

if [ -z "$SUDO_COMMAND" ]
then
    mntusr=$(id -u) grpusr=$(id -g) sudo $0 $*
    exit 0
fi

python module_checker.py
if [ $? -ne 0 ]; then
    exit 0
fi

message()
{
  TITLE="Cannot install AMDock"
  if [ -n "`which zenity`" ]; then
    zenity --error --title="$TITLE" --text="$1"
  elif [ -n "`which kdialog`" ]; then
    kdialog --error "$1" --title "$TITLE"
  elif [ -n "`which xmessage`" ]; then
    xmessage -center "ERROR: $TITLE: $1"
  elif [ -n "`which notify-send`" ]; then
    notify-send "ERROR: $TITLE: $1"
  else
    echo "ERROR: $TITLE\n$1"
  fi
}

READLINK=`which readlink`

if [ -z "$READLINK" ]; then
  message "Required tools are missing - check beginning if readlink are installed."
  exit 1
fi

SCRIPT_LOCATION=$0

if [ -x "$READLINK" ]; then
  while [ -L "$SCRIPT_LOCATION" ]; do
    SCRIPT_LOCATION=`"$READLINK" -e "$SCRIPT_LOCATION"`
  done
fi

script_path=`readlink -f $SCRIPT_LOCATION`
AMDock_InstallDir=`dirname $script_path`

install_confirmation=`zenity --question --title="AMDock Installer" --text="The AMDock program will be intalled in your computer.\n Do you wish to continue?" --width=400 --height=100`
if [ $? -ne 0 ]; then
    exit 0
fi

install_directory=`zenity --file-selection --title="Select directory for AMDock installation" --directory`

## check that AMDock files not exits in destiny
pymol_plugin=$HOME/.pymol/startup
if [ ! -d "~/.pymol/$pymol_plugin" ]
    then
      if [ ! -d "~/.pymol/" ]
        then
          mkdir $HOME/.pymol
      fi
    mkdir $pymol_plugin
fi
# change permissions of directory
chmod -R ugo+rw $pymol_plugin

if [ ! -d "$install_directory/AMDock" ];then
    cp -p -r "$AMDock_InstallDir/AMDock" $install_directory | zenity --progress --pulsate --title="AMDock Installer" --text="Coping AMDock files..." --auto-close --no-cancel
    
    if [ ! -f  "$pymol_plugin/grid_amdock.py" ];then
        cp -p "$AMDock_InstallDir/grid_amdock.py" $pymol_plugin
    fi
else    
    zenity --error --title="AMDock Installer" --text="AMDock already exits in select directory.\n Please select a new directory for installation." --width=400 --height=100
    exit 1
fi 

if [ -f "$install_directory/AMDock/AMDock.sh" ] && [ -f "$install_directory/AMDock/uninstall.sh" ]
then
  chmod 755 "$install_directory"/AMDock/*.sh
fi

# check permission of docking programs
if [ -f "$install_directory/AMDock/AMDock/programs/vina" ]
then
  chmod 755 "$install_directory"/AMDock/AMDock/programs/vina
fi
if [ -f "$install_directory/AMDock/AMDock/programs/autodock4" ]
then
  chmod 755 "$install_directory"/AMDock/AMDock/programs/autodock4
fi
if [ -f "$install_directory/AMDock/AMDock/programs/autogrid4" ]
then
  chmod 755 "$install_directory"/AMDock/AMDock/programs/autogrid4
fi


desktop_apps=/usr/share/applications
if [ ! -f "$desktop_apps/AMDock.desktop" ]
  then
  echo -e '[Desktop Entry]\n
          Version=1.4.96\n
          Type=Application\n
          Name=AMDock\n
          Icon='"$install_directory"'/AMDock/AMDock/images/amdock_icon.png\n
          Exec="'"$install_directory"'/AMDock/AMDock.sh" %f\n
          Comment=Program for performace a Assited Molecular Docking with AutoDock4 and AutoDock Vina\n
          Categories=Science\n
          Terminal=false' >> $desktop_apps/AMDock.desktop

else
  message "Already exist various version of AMDock application launcher. PLease check this."
  exit 1
fi
#if [ ! -f "$desktop_apps/AMDock_Uninstaller.desktop" ]
#    then 
#    echo -e '[Desktop Entry]\nVersion=1.0\nType=Application\nName=AMDock Unistaller\nIcon='$install_directory'/AMDock/AMDock/images/amdock_uninstall_icon.png\nExec="'$install_directory'/AMDock/uninstall.sh" %f\nComment=Program for performace a Assited Molecular Docking with AutoDock4 and AutoDock Vina\nCategories=Science\nTerminal=false' >> $desktop_apps/AMDock_Uninstaller.desktop
#fi

# chmod 555 $install_directory/AMDock

zenity --info --title="AMDock Installer" --text="Done!!! Enjoy."
exit 0

