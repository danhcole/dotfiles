#!/bin/bash

DATE=`date +%Y-%m-%d:%H:%M:%S`

echo ""
echo "Setting up dotfiles..."
echo ""
echo "Backing up old dotfiles..."

if [[ -f ~/.bashrc && ! -L ~/.bashrc ]]; then
    mv ~/.bashrc ~/.bashrc.$DATE
fi
if [[ -f ~/.zshrc && ! -L ~/.zshrc ]]; then
    mv ~/.zshrc ~/.zshrc.$DATE
fi
if [[ -f ~/.vimrc && ! -L ~/.vimrc ]]; then
    mv ~/.vimrc ~/.vimrc.$DATE
fi
if [[ -d ~/.vim && ! -L ~/.vim ]]; then
    mv ~/.vim ~/.vim.$DATE
fi
if [[ -d ~/.sh && ! -L ~/.sh ]]; then
    mv ~/.sh ~/.sh.$DATE
fi
if [[ -d ~/.bash && ! -L ~/.bash ]]; then
    mv ~/.bash ~/.bash.$DATE
fi
if [[ -d ~/.zsh && ! -L ~/.zsh ]]; then
    mv ~/.zsh ~/.zsh.$DATE
fi

echo "Linking .rc files..."
if [[ ! -e ~/.bashrc ]]; then ln -s ~/git/danhcole/dotfiles/.bashrc ~/.bashrc; fi
if [[ ! -e ~/.vimrc ]]; then ln -s ~/git/danhcole/dotfiles/.vimrc ~/.vimrc; fi
if [[ ! -e ~/.zshrc ]]; then ln -s ~/git/danhcole/dotfiles/.zshrc ~/.zshrc; fi

echo "Linking shell shell config files..."
if [[ ! -e ~/.sh ]]; then ln -s ~/git/danhcole/dotfiles/sh ~/.sh; fi
if [[ ! -e ~/.bash ]]; then ln -s ~/git/danhcole/dotfiles/bash/ ~/.bash; fi
if [[ ! -e ~/.zsh ]]; then ln -s ~/git/danhcole/dotfiles/zsh ~/.zsh; fi

echo "Linking vim environment..."
if [[ ! -e ~/.vim ]]; then ln -s ~/git/danhcole/dotfiles/vim ~/.vim; fi

echo ""
echo "done"
