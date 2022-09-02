require("mason").setup()
require("mason-lspconfig").setup()

vim.opt.completeopt = {'menu', 'menuone', 'noselect'}

local cmp = require('cmp')
local select_opts = {behavior = cmp.SelectBehavior.Select}

vim.lsp.handlers['textDocument/hover'] = vim.lsp.with(
  vim.lsp.handlers.hover,
  {border = 'rounded'}
)

vim.lsp.handlers['textDocument/signatureHelp'] = vim.lsp.with(
  vim.lsp.handlers.signature_help,
  {border = 'rounded'}
)
cmp.setup({
--   snippet = {
--     expand = function(args)
--       luasnip.lsp_expand(args.body)
--     end
--   },
  sources = {
    {name = 'path'},
    {name = 'nvim_lsp', keyword_length = 3},
    {name = 'buffer', keyword_length = 3},
    {name = 'luasnip', keyword_length = 2},
  },
  window = {
    completion = {
      -- winhighlight = "Normal:Pmenu,FloatBorder:Pmenu,Search:None",
      col_offset = -3,
      -- side_padding = 0,
    },
    documentation = cmp.config.window.bordered(),
  },
  completion = {
    autocomplete = false,
  },
  formatting = {
    fields = { "kind", "abbr", "menu" },
    format = function(entry, vim_item)
      local kind = require("lspkind").cmp_format({ mode = "symbol_text", maxwidth = 50 })(entry, vim_item)
      local strings = vim.split(kind.kind, "%s", { trimempty = true })
      kind.kind = " " .. strings[1] .. " "
      kind.menu = "    (" .. strings[2] .. ")"
      return kind
    end,
  },
  mapping = {
    ["<c-space>"] = cmp.mapping {
            i = cmp.mapping.complete(),
    },
--     ['<Up>'] = cmp.mapping.select_prev_item(select_opts),
--     ['<Down>'] = cmp.mapping.select_next_item(select_opts),
--
--     ['<C-p>'] = cmp.mapping.select_prev_item(select_opts),
--     ['<C-n>'] = cmp.mapping.select_next_item(select_opts),
--
--     ['<C-u>'] = cmp.mapping.scroll_docs(-4),
--     ['<C-f>'] = cmp.mapping.scroll_docs(4),
--
--     ['<C-e>'] = cmp.mapping.abort(),
--     ['<CR>'] = cmp.mapping.confirm({select = true}),
--
--     ['<C-d>'] = cmp.mapping(function(fallback)
--       if luasnip.jumpable(1) then
--         luasnip.jump(1)
--       else
--         fallback()
--       end
--     end, {'i', 's'}),
--
--     ['<C-b>'] = cmp.mapping(function(fallback)
--       if luasnip.jumpable(-1) then
--         luasnip.jump(-1)
--       else
--         fallback()
--       end
--     end, {'i', 's'}),
--
    ['<CR>'] = cmp.mapping.confirm({select = true}),
    ['<Tab>'] = cmp.mapping(function(fallback)
      local col = vim.fn.col('.') - 1

      if cmp.visible() then
        cmp.select_next_item(select_opts)
      elseif col == 0 or vim.fn.getline('.'):sub(col, col):match('%s') then
        fallback()
      else
        cmp.complete()
      end
    end, {'i', 's'}),
--
--     ['<S-Tab>'] = cmp.mapping(function(fallback)
--       if cmp.visible() then
--         cmp.select_prev_item(select_opts)
--       else
--         fallback()
--       end
--     end, {'i', 's'}),
  },
})

local lspconfig = require('lspconfig')

local capabilities = vim.lsp.protocol.make_client_capabilities()

vim.api.nvim_create_autocmd('User', {
  pattern = 'LspAttached',
  desc = 'LSP actions',
  callback = function()
    local bufmap = function(mode, lhs, rhs)
      local opts = {buffer = true}
      vim.keymap.set(mode, lhs, rhs, opts)
    end

    bufmap('n', 'K', '<cmd>lua vim.lsp.buf.hover()<cr>')
    bufmap('n', 'gd', '<cmd>lua vim.lsp.buf.definition()<cr>')
    bufmap('n', 'gD', '<cmd>lua vim.lsp.buf.declaration()<cr>')
    bufmap('n', 'gi', '<cmd>lua vim.lsp.buf.implementation()<cr>')
    bufmap('n', 'go', '<cmd>lua vim.lsp.buf.type_definition()<cr>')
    bufmap('n', 'gr', '<cmd>lua vim.lsp.buf.references()<cr>')
    bufmap('n', '<C-k>', '<cmd>lua vim.lsp.buf.signature_help()<cr>')
    bufmap('n', '<F2>', '<cmd>lua vim.lsp.buf.rename()<cr>')
    bufmap('n', '<F4>', '<cmd>lua vim.lsp.buf.code_action()<cr>')
    bufmap('x', '<F4>', '<cmd>lua vim.lsp.buf.range_code_action()<cr>')
    bufmap('n', 'gl', '<cmd>lua vim.diagnostic.open_float()<cr>')
    bufmap('n', '[d', '<cmd>lua vim.diagnostic.goto_prev()<cr>')
    bufmap('n', ']d', '<cmd>lua vim.diagnostic.goto_next()<cr>')
  end
})

local lsp_defaults = {
  flags = {
    debounce_text_changes = 300,
  },
  capabilities = require("cmp_nvim_lsp").update_capabilities(capabilities),
  on_attach = function(client, bufnr)
    vim.api.nvim_exec_autocmds('User', {pattern = 'LspAttached'})
  end
}

lspconfig.util.default_config = vim.tbl_deep_extend(
  'force',
  lspconfig.util.default_config,
  lsp_defaults
)

require'lspconfig'.pyright.setup{
  on_attach=on_attach,
}
require'lspconfig'.tsserver.setup{}
--
-- capabilities.textDocument.completion.completionItem.snippetSupport = true
--
require'lspconfig'.html.setup {
  capabilities = capabilities,
}

--
-- local map = function(mode, lhs, rhs, opts)
--   local options = { noremap = true, silent = true }
--   if opts then
--     options = vim.tbl_extend('force', options, opts)
--   end
--   vim.api.nvim_set_keymap(mode, lhs, rhs, options)
-- end
--
-- vim.g.coq_settings = {
--   auto_start = 'shut-up',
--   completion = { always = false},
-- }
--
-- local custom_on_attach = function(client)
--   map('n','gd','<cmd>lua vim.lsp.buf.definition()<CR>')
--   map('n','K','<cmd>lua vim.lsp.buf.hover()<CR>')
--   map('n','<leader>ar','<cmd>lua vim.lsp.buf.rename()<CR>')
-- end
--
-- -- Enable some language servers with the additional completion capabilities offered by coq_nvim
-- local servers = {'pyright', 'tsserver'}
-- for _, lsp in ipairs(servers) do
--   lspconfig[lsp].setup(require('coq').lsp_ensure_capabilities({
--     on_attach = custom_on_attach,
--   }))
-- end
--
-- local null_ls_status_ok, null_ls = pcall(require, "null-ls")
-- if not null_ls_status_ok then
--   return
-- end
--
-- local formatting = null_ls.builtins.formatting
-- local diagnostics = null_ls.builtins.diagnostics
--
-- null_ls.setup {
--   debug = false,
--   sources = {
--     formatting.black.with { extra_args = { "--fast" } },
--     diagnostics.flake8,
--   },
-- }
--
-- vim.cmd([[ command! Format execute 'lua vim.lsp.buf.formatting()']])
