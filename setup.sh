#!/bin/sh

DATE=`date +%Y-%m-%d:%H:%M:%S`

echo ""
echo "Setting up dotfiles..."
echo ""
echo "Linking .rc files..."
mv ~/.bashrc ~/.bashrc.$DATE
mv ~/.vimrc ~/.vimrc.$DATE
ln -s ~/dotfiles/.bashrc ~/.bashrc
ln -s ~/dotfiles/.vimrc ~/.vimrc
echo "done"

