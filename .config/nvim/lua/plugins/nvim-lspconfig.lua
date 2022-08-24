require'lspconfig'.pyright.setup{on_attach=on_attach}

local lspconfig = require('lspconfig')

local map = function(mode, lhs, rhs, opts)
  local options = { noremap = true, silent = true }
  if opts then
    options = vim.tbl_extend('force', options, opts)
  end
  vim.api.nvim_set_keymap(mode, lhs, rhs, options)
end

-- Automatically start coq
vim.g.coq_settings = {
  auto_start = 'shut-up',
  completion = { always = false},
}

local custom_on_attach = function(client)
  map('n','gd','<cmd>lua vim.lsp.buf.definition()<CR>')
  map('n','K','<cmd>lua vim.lsp.buf.hover()<CR>')
  map('n','<leader>ar','<cmd>lua vim.lsp.buf.rename()<CR>')
end

-- Enable some language servers with the additional completion capabilities offered by coq_nvim
lspconfig['pyright'].setup(require('coq').lsp_ensure_capabilities({
    on_attach = custom_on_attach,
}))

-- local lsp_flags = {
--   -- This is the default in Nvim 0.7+
--   debounce_text_changes = 150,
-- }
--
-- require('lspconfig')['pyright'].setup{
--   on_attach = on_attach,
--   flags = lsp_flags,
-- }
--
local null_ls_status_ok, null_ls = pcall(require, "null-ls")
if not null_ls_status_ok then
  return
end
--
-- -- https://github.com/jose-elias-alvarez/null-ls.nvim/tree/main/lua/null-ls/builtins/formatting
local formatting = null_ls.builtins.formatting
-- -- https://github.com/jose-elias-alvarez/null-ls.nvim/tree/main/lua/null-ls/builtins/diagnostics
local diagnostics = null_ls.builtins.diagnostics
--
-- -- https://github.com/prettier-solidity/prettier-plugin-solidity
-- -- npm install --save-dev prettier prettier-plugin-solidity
null_ls.setup {
  debug = false,
  sources = {
    formatting.black.with { extra_args = { "--fast" } },
    diagnostics.flake8,
  },
}

vim.cmd([[ command! Format execute 'lua vim.lsp.buf.formatting()']])
