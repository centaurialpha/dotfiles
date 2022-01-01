" INSERT SPACE IN NORMAL MODE
nnoremap <leader>p li<space><esc>
" Enter normal Mode
inoremap jj <Esc>
" FZF
nnoremap <silent> <C-p> :Files<CR>
nnoremap <C-j> :Buffers<CR>
nnoremap <silent> <Leader>l :Lines<CR>
nnoremap <C-_> :BLines<CR>
nnoremap <C-k> :BTags<CR>

" TagBar
nnoremap <silent> <F8> :TagbarToggle<CR>

" NERDTree
nnoremap <leader>n :NERDTreeFocus<CR>
nnoremap <C-t> :NERDTreeToggle<CR>
