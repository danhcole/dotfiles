#!/bin/bash

DATE=`date +%Y-%m-%d:%H:%M:%S`

echo ""
echo "Setting up dotfiles..."
echo ""
echo "Backing up old dotfiles..."

if [[ -e ~/.bashrc ]]; then
    mv ~/.bashrc ~/.bashrc.$DATE
fi
if [[ -e ~/.vimrc ]]; then
    mv ~/.vimrc ~/.vimrc.$DATE
fi
if [[ -e ~/.vim ]]; then
    mv ~/.vim ~/.vim.$DATE
fi
if [[ -e ~/.zshrc ]]; then
    mv ~/.zshrc ~/.zshrc.$DATE
fi

echo "Linking .rc files..."
ln -s ~/dotfiles/.bashrc ~/.bashrc
ln -s ~/dotfiles/.vimrc ~/.vimrc
ln -s ~/dotfiles/.zshrc ~/.zshrc
ln -s ~/dotfiles/zsh ~/.zsh

echo "Linking vim environment..."
ln -s ~/dotfiles/vim ~/.vim

echo ""
echo "done"
