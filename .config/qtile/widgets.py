from libqtile import widget


group_box = widget.GroupBox(
    borderwidth=1,
    padding_y=4,
    padding_x=5,
    highlight_method='block',
    urgent_alert_method='block',
    this_current_screen_border='#7e57c2',
    this_screen_border='#bd93f9',
    other_current_screen_border='#7e57c2',
    block_highlight_text_color='#000000',
    urgent_border='#ff5555',
)
prompt = widget.Prompt(prompt='run: ')
window_name = widget.WindowName(
    foreground='#50fa7b',
    max_chars=40,
    format='{state}{class}'
)
clock_icon = widget.TextBox(
    text='', background="#668ee3", foreground='#1e222a')
clock = widget.Clock(
    interval=30,
    foreground='#1e222a',
    background="#7aa2f7",
    format="%B %d [ %H:%M ]",
    margin_y=10
)
layout_icon = widget.TextBox(text='', foreground='#1e222a', background="#e5c07b")
current_layout = widget.CurrentLayout(foreground='#e5c07b', background="#1e222a")
battery_icon = widget.TextBox(text='', fontsize=16, foreground='#81A1C1')
battery = widget.Battery(
    foreground='#81A1C1',
    format='{char}{percent: 2.0%}',
    charge_char='',
    discharge_char='',
    full_char='',
    empty_char=""
)
thermal_icon = widget.TextBox(text='', foreground='#e06c75')
thermal = widget.ThermalSensor(foreground='#e06c75')
cpu = widget.CPU(
    background="#353b45",
    foreground='#abb2bf',
    format="{freq_current}GHz",
    update_interval=5.0
)
volume_icon = widget.TextBox(text='', foreground='#f1fa8c')
volume = widget.Volume(
    foreground='#f1fa8c',
    get_volume_command=['amixer', '-D', 'default', '-M', 'sget', 'Master'],
)
disk = widget.DF(format=" {uf}{m}|{r:.0f}%", foreground='#c678dd', visible_on_warn=False)
memory = widget.Memory(foreground="#7797b7", format="{MemUsed: .0f}", update_interval=5.0)

widgets = [
    layout_icon,
    current_layout,
    prompt,
    window_name,
    widget.Spacer(),
    group_box,
    widget.Spacer(300),
    disk,
    memory,
    widget.TextBox(
        text="CPU",
        foreground="#3b414d",
        background="#7ec7a2"
    ),
    cpu,
    thermal_icon,
    thermal,
    battery,
    clock_icon,
    clock,
    volume_icon,
    volume,
]
