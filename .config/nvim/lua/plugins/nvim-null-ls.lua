local null_ls_status_ok, null_ls = pcall(require, "null-ls")
if not null_ls_status_ok then
	return
end

local formatting = null_ls.builtins.formatting
local diagnostics = null_ls.builtins.diagnostics

local augroup = vim.api.nvim_create_augroup("LspFormatting", {})

null_ls.setup({
	debug = false,
	sources = {
		formatting.black.with({ extra_args = { "--fast" } }),
		--formatting.prettier.with({ extra_args = {"--semi=false"}}),
    formatting.prettierd.with({ extra_args = {"--semi-false"}}),
		formatting.stylua,
		diagnostics.flake8,
	},
})

vim.cmd([[ command! Format execute 'lua vim.lsp.buf.format { async = true }']])

vim.cmd([[ command! Standard execute 'silent !standard --fix %']])
