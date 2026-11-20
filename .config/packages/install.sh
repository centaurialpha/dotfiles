#!/usr/bin/env bash
# Install packages for this machine: base, desktop, dev plus <machine>.txt
# Usage: install.sh [machine]   (machine autodetected from DMI when omitted)
set -euo pipefail

dir=$(dirname "$(readlink -f "$0")")

detect_machine() {
    local vendor product
    vendor=$(cat /sys/class/dmi/id/sys_vendor)
    product=$(cat /sys/class/dmi/id/product_version /sys/class/dmi/id/product_name)
    case "$vendor $product" in
        *ASUSTeK*) echo asus ;;
        *ThinkPad*) echo thinkpad ;;
        *Micro-Star*) echo msi ;;
        *) echo unknown ;;
    esac
}

install_paru() {
    command -v paru >/dev/null && return
    sudo pacman -S --needed --noconfirm base-devel git
    local tmp
    tmp=$(mktemp -d)
    git clone https://aur.archlinux.org/paru-bin.git "$tmp/paru-bin"
    (cd "$tmp/paru-bin" && makepkg -si --noconfirm)
    rm -rf "$tmp"
}

add_pritunl_repo() {
    grep -q '^\[pritunl\]' /etc/pacman.conf && return
    local key=7568D9BB55FF9E5287D586017AE645C0CF8E292A
    sudo pacman-key --keyserver hkp://keyserver.ubuntu.com -r "$key"
    sudo pacman-key --lsign-key "$key"
    printf '\n[pritunl]\nServer = https://repo.pritunl.com/unstable/pacman\n' | sudo tee -a /etc/pacman.conf >/dev/null
}

machine=${1:-$(detect_machine)}
echo "machine: $machine"

lists=("$dir/base.txt" "$dir/desktop.txt" "$dir/dev.txt")
[[ -f "$dir/$machine.txt" ]] && lists+=("$dir/$machine.txt")

[[ "$machine" == asus ]] && add_pritunl_repo
install_paru

grep -hvE '^\s*(#|$)' "${lists[@]}" | paru -Syu --needed -

sudo systemctl enable dhcpcd iwd power-profiles-daemon sshd systemd-timesyncd tailscaled paccache.timer

fish_path=$(command -v fish)
[[ "$(getent passwd "$USER" | cut -d: -f7)" == "$fish_path" ]] || chsh -s "$fish_path"
