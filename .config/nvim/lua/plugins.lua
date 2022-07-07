local Plug = vim.fn['plug#']

vim.call('plug#begin')

Plug('junegunn/fzf', {
    ['do'] = function()
        vim.cmd('fzf#install')
    end
})
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
Plug('dracula/vim', { as = 'dracula' })
Plug 'psf/black'
Plug 'mhinz/vim-startify'
Plug 'dbeniamine/cheat.sh-vim'
Plug 'drewtempelmeyer/palenight.vim'
Plug 'farmergreg/vim-lastplace'
Plug 'nvim-lualine/lualine.nvim'
Plug 'kyazdani42/nvim-web-devicons'
Plug 'kyazdani42/nvim-tree.lua'
Plug 'jpalardy/vim-slime'

vim.call('plug#end')
