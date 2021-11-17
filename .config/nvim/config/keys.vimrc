" INSERT SPACE IN NORMAL MODE
nnoremap <leader>p li<space><esc>
" Enter normal Mode
inoremap jj <Esc>
" Telescope

lua << EOF
local actions = require('telescope.actions')
local previewers = require('telescope.previewers')
local Job = require('plenary.job')
local new_maker = function(filepath, bufnr, opts)
  filepath = vim.fn.expand(filepath)
  Job:new({
    command = 'file',
    args = { '--mime-type', '-b', filepath },
    on_exit = function(j)
      local mime_type = vim.split(j:result()[1], '/')[1]
      if mime_type == "text" then
        previewers.buffer_previewer_maker(filepath, bufnr, opts)
      else
        -- maybe we want to write something to the buffer here
        vim.schedule(function()
          vim.api.nvim_buf_set_lines(bufnr, 0, -1, false, { 'BINARY' })
        end)
      end
    end
  }):sync()
end

require('telescope').setup{
  defaults = {
    buffer_previewer_maker = new_maker,
    layout_config = {
	preview_width = 70,
	prompt_position = 'top'
    },
    mappings = {
      i = {
        ["<esc>"] = actions.close,
	["<C-j>"] = actions.move_selection_next,
	["<C-k>"] = actions.move_selection_previous
      },
    },
  }
}
EOF

nnoremap <leader>ff <cmd>Telescope find_files<cr>
nnoremap <silent> <C-p> <cmd>Telescope find_files<cr>

" TagBar
nnoremap <silent> <F8> :TagbarToggle<CR>
