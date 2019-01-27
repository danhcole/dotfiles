set nocompatible

set backspace=indent,eol,start

if &t_Co > 2 || has("gui_running")
  syntax on
  set hlsearch
endif

if has("autocmd")

  execute pathogen#infect()

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

" Folding
set foldmethod=syntax
set foldlevelstart=99
nnoremap <silent> <Space> @=(foldlevel('.')?'za':"\<Space>")<CR>

" Set tabs to 4 spaces
set shiftwidth=4
set tabstop=4
set expandtab

" 
autocmd FileType make setlocal noexpandtab

" Set text-file specific options
autocmd FileType text setlocal autoindent expandtab softtabstop=2 textwidth=76 nospell spelllang=en_us

" Don't do spell-checking on Vim help files
autocmd FileType help setlocal nospell

" set tabstops for ruby
autocmd FileType ruby set softtabstop=2
autocmd FileType ruby set sw=2
autocmd FileType ruby set ts=2 

" highlight extranious whitespace
highlight ExtraWhitespace ctermbg=red guibg=red
match ExtraWhitespace /\s\+$/
autocmd BufWinEnter * match ExtraWhitespace /\s\+$/
autocmd InsertEnter * match ExtraWhitespace /\s\+\%#\@<!$/
autocmd InsertLeave * match ExtraWhitespace /\s\+$/
autocmd BufWinLeave * call clearmatches()

" sane splits
set splitright
set splitbelow
