#!/bin/sh

echo ""
echo "Setting up dotfiles..."
echo ""
echo "Linking .rc files..."
rm -f ~/.bashrc
rm -f ~/.vimrc
ln -s ~/dotfiles/.bashrc ~/.bashrc
ln -s ~/dotfiles/.vimrc ~/.vimrc
echo "done"

