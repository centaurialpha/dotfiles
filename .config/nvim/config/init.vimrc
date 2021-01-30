call plug#begin()
Plug 'itchyny/lightline.vim'
Plug 'junegunn/fzf', { 'do': { -> fzf#install() } }
Plug 'junegunn/fzf.vim'
Plug 'davidhalter/jedi-vim'
Plug 'tpope/vim-fugitive'
Plug 'mhinz/vim-signify'
Plug 'nvie/vim-flake8'
Plug 'vim-python/python-syntax'
Plug 'jiangmiao/auto-pairs'
Plug 'Vimjas/vim-python-pep8-indent'
Plug 'mboughaba/i3config.vim'
Plug 'preservim/nerdtree'
Plug 'stevearc/vim-arduino'
Plug 'fisadev/vim-isort'
Plug 'peterhoeg/vim-qml'
Plug 'preservim/tagbar'
" Colorschemes
Plug 'dracula/vim', {'as': 'dracula'}
Plug 'tyrannicaltoucan/vim-deep-space'
Plug 'rakr/vim-one'
Plug 'joshdick/onedark.vim'
Plug 'voldikss/vim-translator'
Plug 'cespare/vim-toml'
call plug#end()
