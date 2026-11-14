function scrot --wraps scrot --description 'scrot que guarda en ~/Pictures/screenshots si no se pasa -F'
    if contains -- -F $argv; or contains -- --file $argv
        command scrot $argv
        return
    end
    mkdir -p ~/Pictures/screenshots
    command scrot $argv -F ~/Pictures/screenshots/'%Y-%m-%d-%H%M%S_$wx$h_scrot.png'
end
