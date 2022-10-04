require("mason").setup()
require("mason-null-ls").setup({
  ensure_installed = {"python", "javascript"}
})
require("mason-lspconfig").setup()
