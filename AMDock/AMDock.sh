#!/bin/bash
# ---------------------------------------------------------------------
# AMDock startup script.
# ---------------------------------------------------------------------
#
message()
{
  TITLE="Cannot start AMDock"
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
script_path=`readlink -f $SCRIPT_LOCATION`
AMDock_HOME=`dirname $script_path`


if [ -x "$READLINK" ]; then
  while [ -L "$SCRIPT_LOCATION" ]; do
    SCRIPT_LOCATION=`"$READLINK" -e "$SCRIPT_LOCATION"`
  done
fi

export PYTHONPATH=$PYTHONPATH:$AMDock_HOME

OBABEL=`which obabel`
PYMOL=`which pymol`

if [ -z "$OBABEL" -o -z "$PYMOL" ]; then
    message "Required external programs are missing - Check if you are installed pymol and openbabel."
fi
# ---------------------------------------------------------------------
# Locate a python2.7 installation directory which will be used to run the program.
# ---------------------------------------------------------------------
PYTHON="python"

#Run the AMDock launcher
$PYTHON $AMDock_HOME/AMDock/Docking_Program.py


