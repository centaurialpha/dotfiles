local status_ok, color_scheme = pcall(require, 'onedark')
if not status_ok then
  return
end

vim.cmd([[ autocmd FileType * highlight rainbowcol1 guifg=#FF7B72 ]])

require('onedark').setup({
  style = "darker",
  --style = "dark",
  --style = "deep",
  --style = "cool",
  --style = "warm",
  --style = "warmer",
  colors = {
    bg0 = "#181a1f",
  },
})

require('onedark').load()
