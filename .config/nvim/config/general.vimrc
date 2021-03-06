" EXPLORER
let g:netrw_banner = 0
let g:netrw_liststyle = 3
let g:netrw_browse_split = 4
let g:netrw_winsize = 20

set noswapfile
set clipboard+=unnamedplus
set number
set relativenumber
set diffopt+=vertical
" COLOR SCHEME
" For true colors in tmux and vim without issues
if (empty($TMUX))
  if (has("nvim"))
  "For Neovim 0.1.3 and 0.1.4 < https://github.com/neovim/neovim/pull/2198 >
  let $NVIM_TUI_ENABLE_TRUE_COLOR=1
  endif
endif
if (has("termguicolors"))
  set termguicolors
endif
colorscheme one

" colorscheme dracula
hi Normal guibg=#1e2127
hi SignColumn guibg=#1e2127

" REMOVE SPACES AFTER SAVE
autocmd BufWritePre * :%s/\s\+$//e
" YAML
autocmd FileType yaml setlocal ts=2 sts=2 sw=2 expandtab
autocmd FileType c,cpp,json,qs setlocal ts=4 sts=4 sw=4 expandtab
autocmd BufRead,BufNewFile *.htm,*.html setlocal tabstop=2 shiftwidth=2 softtabstop=2
