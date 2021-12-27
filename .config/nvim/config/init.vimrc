call plug#begin()
Plug 'preservim/nerdtree'
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
Plug 'stevearc/vim-arduino'
Plug 'peterhoeg/vim-qml'
Plug 'preservim/tagbar'
Plug 'voldikss/vim-translator'
Plug 'cespare/vim-toml'
Plug 'norcalli/nvim-colorizer.lua'
Plug 'dracula/vim', { 'as': 'dracula' }
Plug 'psf/black', { 'branch': 'stable' }
" HTML & CSS
Plug 'mattn/emmet-vim'
Plug 'turbio/bracey.vim'
" RUST
Plug 'rust-lang/rust.vim'
Plug 'mhinz/vim-startify'

Plug 'dbeniamine/cheat.sh-vim'
Plug 'drewtempelmeyer/palenight.vim'

Plug 'farmergreg/vim-lastplace'
Plug 'ryanoasis/vim-devicons'
Plug 'tiagofumo/vim-nerdtree-syntax-highlight'

Plug 'nvim-lualine/lualine.nvim'

call plug#end()
