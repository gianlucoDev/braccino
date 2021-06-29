#!/bin/bash
# script dependencies: arduino-cli, jq

# board information
port="/dev/ttyACM1"
fqbn="arduino:avr:mega"
platform="arduino:avr"

# sketch
sketch=$(pwd)

# from https://stackoverflow.com/a/32708121
prompt_confirm() {
  while true; do
    read -r -n 1 -p "${1:-Continue?} [y/n]: " REPLY
    case $REPLY in
      [yY]) echo ; return 0 ;;
      [nN]) echo ; return 1 ;;
      *) printf " \033[31m %s \n\033[0m" "invalid input"
    esac 
  done  
}

# ask confirmation
echo "selected board: $fqbn at $port"
prompt_confirm "do you want to upload?" || exit 0

printf "\n%s\n\n" "installing libraries"
arduino-cli core install $platform
arduino-cli lib install Servo@1.1.7
arduino-cli lib install PacketSerial@1.4.0
# you also need to intall https://github.com/cgxeiji/CGx-InverseK.git

printf "\n%s\n\n" "compiling and uploading"
arduino-cli compile --fqbn $fqbn $sketch
arduino-cli upload -p $port --fqbn $fqbn $sketch

printf "\n%s\n\n" "done."
