local function map(mode, lhs, rhs, opts)
  local options = { noremap = true, silent = true }
  if opts then
    options = vim.tbl_extend('force', options, opts)
  end
  vim.api.nvim_set_keymap(mode, lhs, rhs, options)
end

vim.g.mapleader = ','

map('i', 'jj', '<Esc>')

-- NvimTree
map('n', '<C-n>', ':NvimTreeToggle<CR>')
map('n', '<leader>f', ':NvimTreeRefresh<CR>')
map('n', '<leader>n', ':NvimTreeFindFile<CR>')

-- FZF
map('n', '<c-P>',
    "<cmd>lua require('fzf-lua').files()<CR>")
map('n', '<c-k>', ":FzfLua grep<CR><CR>")
map('n', '<c-l>', ":FzfLua buffers<CR>")
map('n', '<leader>c', ":FzfLua git_commits<CR>")
map('n', '<c-j>', ":FzfLua lsp_references<CR>")
