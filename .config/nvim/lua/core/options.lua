local g = vim.g
local opt = vim.opt

opt.clipboard = "unnamedplus"
opt.swapfile = false

-- NeoVim UI
-- opt.showmatch = true
opt.number = true
opt.relativenumber = true
opt.ignorecase = true
opt.smartcase = true
opt.linebreak = true
opt.termguicolors = true
opt.laststatus = 3

-- Tabs, indent
opt.expandtab = true
opt.shiftwidth = 4
opt.tabstop = 4
opt.smartindent = true

-- Memory, CPU
-- opt.hidden = true
opt.history = 100
opt.lazyredraw = true
opt.synmaxcol = 240
opt.updatetime = 700

opt.shortmess:append "sI"

-- Neovide
opt.guifont = { "CaskaydiaCove Nerd Font Mono:h18" }
g.airline_powerline_fonts = 1
g.neovide_cursor_antialiasing = true
g.neovide_transparency = 0.90
g.neovide_no_idle = true
g.neovide_cursor_animation_length = 0.10
g.neovide_cursor_vfx_particle_density = 30.0
g.neovide_hide_mouse_when_typing = true
-- g.neovide_confirm_quit = true
g.neovide_cursor_vfx_mode = "railgun"

-- Disable builtins plugins
local disabled_built_ins = {
  "netrw",
  "netrwPlugin",
  "netrwSettings",
  "netrwFileHandlers",
  "gzip",
  "zip",
  "zipPlugin",
  "tar",
  "tarPlugin",
  "getscript",
  "getscriptPlugin",
  "vimball",
  "vimballPlugin",
  "2html_plugin",
  "logipat",
  "rrhelper",
  "spellfile_plugin",
  "matchit"
}

for _, plugin in pairs(disabled_built_ins) do
  g["loaded_" .. plugin] = 1
end
