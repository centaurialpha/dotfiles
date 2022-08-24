local function map(mode, lhs, rhs, opts)
  local options = { noremap = true, silent = true }
  if opts then
    options = vim.tbl_extend('force', options, opts)
  end
  vim.api.nvim_set_keymap(mode, lhs, rhs, options)
end

vim.g.mapleader = ','
vim.o.completeopt = 'menuone,noinsert,noselect'

map('i', 'jj', '<Esc>')

-- NvimTree
map('n', '<C-n>', ':NvimTreeToggle<CR>')
map('n', '<leader>f', ':NvimTreeRefresh<CR>')
map('n', '<leader>n', ':NvimTreeFindFile<CR>')

-- FZF
map('n', '<c-P>',
    "<cmd>lua require('fzf-lua').files()<CR>")
map('n', '<c-A>', ":FzfLua grep_last<CR><CR>")
map('n', '<c-k>', ":FzfLua grep<CR><CR>")
