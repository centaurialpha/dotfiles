vim.cmd [[
  augroup packer_user_config
    autocmd!
    autocmd BufWritePost packer_init.lua source <afile> | PackerSync
  augroup end
]]

local status_ok, packer = pcall(require, 'packer')
if not status_ok then
  return
end

return packer.startup(function(use)
  use 'wbthomason/packer.nvim'
  use 'nvim-lua/plenary.nvim'

  use {
    'kyazdani42/nvim-tree.lua',
    requires = {
      'kyazdani42/nvim-web-devicons',
    },
  }

  use 'navarasu/onedark.nvim'
  use 'Mofiqul/dracula.nvim'

  use {
    'goolord/alpha-nvim',
    requires = { 'kyazdani42/nvim-web-devicons' },
  }

  use {
    'nvim-lualine/lualine.nvim',
    requires = { 'kyazdani42/nvim-web-devicons', opt = true }
  }

  use 'nvim-treesitter/nvim-treesitter'
  use 'nvim-treesitter/nvim-treesitter-context'

  use {
    'neovim/nvim-lspconfig', -- Configurations for Nvim LSP
    "williamboman/mason.nvim",
    "williamboman/mason-lspconfig.nvim",
  }

  use 'jose-elias-alvarez/null-ls.nvim'
  use 'hrsh7th/nvim-cmp'
  use 'onsails/lspkind.nvim'
  use 'hrsh7th/cmp-nvim-lsp'
  use 'hrsh7th/cmp-buffer'
  use 'hrsh7th/cmp-path'
  -- use { 'ms-jpq/coq_nvim', run = 'python3 -m coq deps' }
  -- use 'ms-jpq/coq.artifacts'
  -- use 'ms-jpq/coq.thirdparty'

  use {
    'ibhagwan/fzf-lua',
    requires = { 'kyazdani42/nvim-web-devicons' }
  }

  use {
    'lewis6991/gitsigns.nvim',
    config = function()
      require('gitsigns').setup()
    end
  }
  use {
    'TimUntersberger/neogit',
    requires = 'nvim-lua/plenary.nvim'
  }

  use {
    "windwp/nvim-autopairs",
      config = function() require("nvim-autopairs").setup {} end
  }

  use 'norcalli/nvim-colorizer.lua'
end)

