local status_ok, nvim_treesitter = pcall(require, 'nvim-treesitter.configs')
if not status_ok then
  return
end

-- See: https://github.com/nvim-treesitter/nvim-treesitter#quickstart
nvim_treesitter.setup {
  -- A list of parser names, or "all"
  ensure_installed = {
    'bash', 'c', 'cpp', 'css', 'html', 'json', 'lua', 'python',
    'vim', 'yaml', 'javascript',
  },
  -- Install parsers synchronously (only applied to `ensure_installed`)
  sync_install = true,
  incremental_selection = {
    enable = true,
  },
  highlight = {
    enable = true,
  },
  rainbow = {
    enable = true,
    max_file_lines = 5000,
    colors = {
      "#8be9fd",
      "#a89984",
      "#b16286",
      "#d79921",
      "#689d6a",
      "#d65d0e",
      "#458588",
    },
    termcolors = {
      "Red",
      "Green",
      "Yellow",
      "Blue",
      "Magenta",
      "Cyan",
      "White",
    }, -- table of colour name strings
  }
}

