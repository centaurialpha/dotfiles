function cam --description 'Control de la cámara EZVIZ'
    set -l serial J50010940
    set -l api env -C ~/projects/ezviz uvx pyezvizapi
    switch "$argv[1]"
        case on
            $api camera --serial $serial switch --switch sleep --enable 0
        case off
            $api camera --serial $serial switch --switch sleep --enable 1
        case status
            $api camera --serial $serial status
        case ver
            mpv $EZVIZ_RTSP
        case '*'
            echo 'uso: cam on|off|status|ver'
            return 1
    end
end
