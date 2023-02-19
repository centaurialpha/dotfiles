pcall(require, 'impatient')


require('packer_init')
require('core/options')
require('core/keymaps')
require('core/autocmds')
require('core/colors')


require('plugins/nvim-tree')
require('plugins/statusbar')
require('plugins/nvim-mason')
require('plugins/nvim-treesitter')
require('plugins/nvim-treesitter-context')
require('plugins/nvim-lspconfig')
require('plugins/nvim-null-ls')
require('plugins/nvim-fzf')
require('plugins/nvim-gitsigns')
