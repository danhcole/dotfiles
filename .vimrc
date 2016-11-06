set nocompatible

set backspace=indent,eol,start

if &t_Co > 2 || has("gui_running")
  syntax on
  set hlsearch
endif

if has("autocmd")

  filetype plugin indent on

  augroup vimrcEx
  au!

  autocmd FileType text setlocal textwidth=78

  autocmd BufReadPost *
     \ if line("'\"") > 1 && line("'\"") <= line("$") |
     \  exe "normal! g'\"" |
     \ endif

   augroup END

else

   set autoindent

endif

set runtimepath+=~/dotfiles/vim

" Color Scheme
colo monokai

" Line Numbers
set number

"auto-indent by 8 spaces
set shiftwidth=4

"set tab to 8 spaces
set tabstop=4

"repalce tab with 8 spaces, except for makefiles
set expandtab
autocmd FileType make setlocal noexpandtab

" My settings when editing *.txt files
"   - automatically indent lines according to previous lines
"   - replace tab with 8 spaces
"   - when I hit tab key, move 2 spaces instead of 8
"   - wrap text if I go longer than 76 columns
"   - check spelling
autocmd FileType text setlocal autoindent expandtab softtabstop=2 textwidth=76 nospell spelllang=en_us

" Don't do spell-checking on Vim help files
autocmd FileType help setlocal nospell

" clang-format integration
map <C-K> :pyf /usr/share/vim/addons/syntax/clang-format-3.8.py<cr>
imap <C-K> <c-o>:pyf /usr/share/vim/addons/syntax/clang-format-3.8.py<cr>
