" INSERT SPACE IN NORMAL MODE
nnoremap <leader>p li<space><esc>
" Enter normal Mode
inoremap jj <Esc>
" FZF
inoremap <C-f> <Esc><Esc>:BLines!<CR>
nnoremap <silent> <C-p> :Files<CR>
nnoremap <silent> <Leader><Enter> :Buffers<CR>
nnoremap <silent> <Leader>l :Lines<CR>
nnoremap <C-_> :BLines<CR>

" TagBar
nnoremap <silent> <F8> :TagbarToggle<CR>
