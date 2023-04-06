local status_ok, color_scheme = pcall(require, "onedark")
-- local status_ok, color_scheme = pcall(require, "catppuccin")
if not status_ok then
	return
end

-- color_scheme.setup({
-- 	flavour = "mocha",
-- 	background = {
-- 		dark = "#ff0000",
-- 	},
-- })

color_scheme.setup({
	colors = {
		bg0 = "#181a1f",
	},
	style = "cool",
})
color_scheme.load()
--color_scheme.setup({
--	colors = {
--		onedark = {
--			bg = "#181a1f",
--		},
--	},
--  plugins = {
--    all = false,
--    -- native_lsp = true,
--    nvim_lsp = true,
--    treesitter = true
--  },
--})
--
--color_scheme.load()

-- Treesitter Context colors
vim.api.nvim_set_hl(0, "TreesitterContext", { bg = "#313244" })
vim.api.nvim_set_hl(0, "TreesitterContextBottom", { underline = true })
