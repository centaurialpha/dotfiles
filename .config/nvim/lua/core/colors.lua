local status_ok, color_scheme = pcall(require, "onedarkpro")
if not status_ok then
	return
end

--color_scheme.setup({
--	flavour = "mocha",
--	background = {
--		dark = "mocha",
--	},
	--color_overrides = {
	--	all = {
	--		base = "#181a1f",
	--	},
	--},
-- })
--
color_scheme.setup({
	colors = {
		onedark = {
			bg = "#181a1f",
		},
	},
  plugins = {
    all = false,
    native_lsp = true,
    treesitter = true
  },
})

color_scheme.load()

-- Treesitter Context colors
vim.api.nvim_set_hl(0, "TreesitterContext", { bg = "#2a2d32" })
vim.api.nvim_set_hl(0, "TreesitterContextBottom", { underline = true })
