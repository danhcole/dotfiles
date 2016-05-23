#!/bin/bash

#$1 == kernel version
#$2 == uni / kernel ID

#set stop on error
set -e

#if arg 1 isn't set, get the kernel version from the makefile
KVER=$1
if [ -z "$1" ]; then
    KVER=$(awk 'NR==1{print $3}' Makefile);
    KVER+=.$(awk 'NR==2{print $3}' Makefile);
    KVER+=.$(awk 'NR==3{print $3}' Makefile);
fi

#if arg 2 isn't set, get the the local version from the config
LVER=$2
[ -z "$2" ] && LVER=$(cat .config | grep CONFIG_LOCALVERSION= | sed 's/.*"\(.*\)"[^"]*$/\1/' | cut -c 2- )

#get the number of cpus
PROC=$(nproc)
let PROC=$PROC

#get the dkms version
VBOX=$(sudo pacman -Qs virtualbox-guest-dkms | awk 'NR==1{print$2}' | sed 's/.\{2\}$//')

#echo vars
echo "KVER = $KVER"
echo "LVER = $LVER"
echo "PROC = $PROC"
echo "VBOX = $VBOX"

#make the kernel
make -j$PROC

#install kernel modules
sudo make modules_install -j$PROC

#copy to /boot
sudo cp -v arch/x86/boot/bzImage /boot/vmlinuz-$KVER-$LVER

#make ramdisk
sudo mkinitcpio -k $KVER-$LVER -c /etc/mkinitcpio.conf -g /boot/initramfs-$KVER-$LVER.img

#copy System.map and set up symlink
sudo cp System.map /boot/System.map-$KVER-$LVER
sudo ln -fs /boot/System.map-$KVER-$LVER /boot/System.map

#set up grub config
sudo grub-mkconfig -o /boot/grub/grub.cfg

#update dkms if needed
sudo pacman -S --needed --noconfirm virtualbox-guest-dkms

#turn stop-on-error off, try and remove dkms
set +e
#sudo dkms remove -m vboxguest -v $VBOX_OSE -k $KVER-$LVER
sudo dkms remove -m vboxguest -v 5.0.16_OSE -k $KVER-$LVER
#turn stop-on-error on, install dkms
set -e
#sudo dkms install -m vboxguest -v $VBOX_OSE -k $KVER-$LVER
sudo dkms install -m vboxguest -v 5.0.16_OSE -k $KVER-$LVER
