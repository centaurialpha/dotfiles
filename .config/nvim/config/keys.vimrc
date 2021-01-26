" Make tab got to the matching pair item
nnoremap <Tab> %
" INSERT SPACE IN NORMAL MODE
nnoremap <leader>p li<space><esc>
" Enter normal Mode
inoremap jj <Esc>
" FZF
inoremap <C-f> <Esc><Esc>:BLines!<CR>
nnoremap <silent> <C-p> :FZF -m<CR>
nnoremap <silent> <Leader><Enter> :Buffers<CR>
nnoremap <silent> <Leader>l :Lines<CR>
nnoremap <C-_> :BLines<CR>
" TagBar
nnoremap <silent> <F8> :TagbarToggle<CR>
