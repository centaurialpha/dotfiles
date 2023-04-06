vim.cmd([[
  augroup packer_user_config
    autocmd!
    autocmd BufWritePost packer_init.lua source <afile> | PackerSync
  augroup end
]])

local status_ok, packer = pcall(require, "packer")
if not status_ok then
	return
end

return packer.startup(function(use)
	use("wbthomason/packer.nvim")
	use("nvim-lua/plenary.nvim")
	--use("olimorris/onedarkpro.nvim") -- Packer
  use 'navarasu/onedark.nvim'

  use { "catppuccin/nvim", as = "catppuccin" }
	use({
		"kyazdani42/nvim-tree.lua",
		requires = {
			"kyazdani42/nvim-web-devicons",
		},
	})
	use({
		"nvim-lualine/lualine.nvim",
		requires = { "kyazdani42/nvim-web-devicons", opt = true },
	})
	use({
		"neovim/nvim-lspconfig", -- Configurations for Nvim LSP
		"williamboman/mason.nvim",
		"jose-elias-alvarez/null-ls.nvim",
		"williamboman/mason-lspconfig.nvim",
		"jayp0521/mason-null-ls.nvim",
	})
	use("nvim-treesitter/nvim-treesitter")
	use("nvim-treesitter/nvim-treesitter-context")
	use("hrsh7th/nvim-cmp")
	use("onsails/lspkind.nvim")
	use("hrsh7th/cmp-nvim-lsp")
	use("hrsh7th/cmp-buffer")
	use("hrsh7th/cmp-path")
	use("L3MON4D3/LuaSnip")
	use({ "saadparwaiz1/cmp_luasnip" })
	use("rafamadriz/friendly-snippets")

	use({
		"ibhagwan/fzf-lua",
		requires = { "kyazdani42/nvim-web-devicons" },
	})
	use({
		"windwp/nvim-autopairs",
		config = function()
			require("nvim-autopairs").setup({})
		end,
	})
	use("lewis6991/gitsigns.nvim")
	use("p00f/nvim-ts-rainbow")
	use("Vimjas/vim-python-pep8-indent")

	use("lewis6991/impatient.nvim")

	use({
		"mrshmllow/document-color.nvim",
		config = function()
			require("document-color").setup({
				-- Default options
				mode = "background", -- "background" | "foreground" | "single"
			})
		end,
	})
  use("uga-rosa/translate.nvim")
  use {'kevinhwang91/nvim-ufo', requires = 'kevinhwang91/promise-async'}
end)
