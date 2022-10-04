local status_ok, nvim_treesitter = pcall(require, 'fzf-lua')
if not status_ok then
  return
end

local actions = require "fzf-lua.actions"
require'fzf-lua'.setup {
  files = {
    previewer = "bat",
    prompt = 'Files❯ ',
    rg_opts           = "--color=never --files --hidden --follow -g '!.git/' -g '!.pytest_cache/'",
  },
}
