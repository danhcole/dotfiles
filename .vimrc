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

set runtimepath+=~/git/danhcole/dotfiles/vim
set encoding=utf-8

" Color Scheme
colo monokai_pro

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

" set tabstops for YAML
autocmd FileType yaml set softtabstop=2
autocmd FileType yaml set sw=2
autocmd FileType yaml set ts=2
autocmd FileType yml set softtabstop=2
autocmd FileType yml set sw=2
autocmd FileType yml set ts=2

" set tabstops for json
autocmd FileType json set softtabstop=2
autocmd FileType json set sw=2
autocmd FileType json set ts=2

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

set updatetime=100

" mouse scrolling
set mouse=a

" nerdtree -- https://github.com/scrooloose/nerdtree
map <C-n> :NERDTreeToggle<CR>
let g:NERDTreeNodeDelimiter = "\u00a0"

" airline
let g:airline#extensions#tabline#enabled = 1
let g:airline#extensions#tabline#show_splits = 0
let g:airline#extensions#tabline#show_buffers = 0
let g:airline#extensions#tabline#tabs_label = ' '
"let g:airline#extensions#tabline#left_sep = ' '
"let g:airline#extensions#tabline#left_alt_sep = '|'
let g:airline_powerline_fonts = 1

" https://github.com/vim-airline/vim-airline/issues/1369#issuecomment-277855901
let g:airline_section_x = '%{&filetype}'

" vim-terraform
let g:terraform_align=1
let g:terraform_fmt_on_save=1

let g:go_def_mode='gopls'
let g:go_info_mode='gopls'

" color column at 80 chars
if exists('+colorcolumn')
    set colorcolumn=80
else
    au BufWinEnter * call matchadd('ErrorMsg', '\%>80v.\+', -1)
endif
autocmd InsertLeave * redraw!

" gitgutter for large diffs
let g:gitgutter_max_signs = 750
