local status_ok, nvim_tc = pcall(require, 'treesitter-context')

if not status_ok then
  return
end

nvim_tc.setup {
  enable = true,
}
