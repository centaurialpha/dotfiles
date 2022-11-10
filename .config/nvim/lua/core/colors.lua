local status_ok, color_scheme = pcall(require, "onedarkpro")
if not status_ok then
	return
end

--vim.cmd([[ autocmd FileType * highlight rainbowcol1 guifg=#FF7B72 ]])

vim.api.nvim_set_hl(0, "TreesitterContext", { bg = "#2a2d32" })
vim.api.nvim_set_hl(0, "TreesitterContextBottom", { underline = true })

color_scheme.setup({
	colors = {
		onedark = {
			bg = "#181a1f",
		},
	},
})

color_scheme.load()
