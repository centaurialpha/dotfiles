" JEDI CONFIGURATION
autocmd FileType python setlocal completeopt-=previewA
let g:jedi#popup_on_dot = 0
let g:jedi#show_call_signatures = 2
let g:jedi#force_py_version = 3
" PYTHON HIGHLIGHT
let g:python_highlight_all = 1

"ARDUINO
let g:arduino_cmd = '/home/gabox/arduino-1.8.13/arduino'
let g:arduino_dir = '/home/gabox/arduino-1.8.13'

let g:fzf_colors = {'border': ['fg', 'Comment']}

" Configure lightline
let g:lightline = {
  \   'colorscheme': 'dracula',
  \   'active': {
  \     'left':[ [ 'mode', 'paste' ],
  \              [ 'gitbranch', 'readonly', 'filename', 'modified' ]
  \     ]
  \   },
	\   'component': {
	\     'lineinfo': ' %3l:%-2v',
	\   },
  \   'component_function': {
  \     'gitbranch': 'fugitive#head',
  \   }
  \ }
" Configure target lang for translator plugin
let g:translator_target_lang='es'
let g:translator_window_max_height=200
let g:translator_window_max_width=200
" Black Python Formatter
let g:black_linelength = 120
