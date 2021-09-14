from libqtile import widget


group_box = widget.GroupBox(
    borderwidth=1,
    fontsize=12,
    padding_y=1,
    font="Hermit",
    padding_x=10,
    highlight_method='block',
    urgent_alert_method='block',
    this_current_screen_border='#7e57c2',
    this_screen_border='#ffb86c',
    other_current_screen_border='#7e57c2',
    block_highlight_text_color='#000000',
    urgent_border='#ff5555',
)
prompt = widget.Prompt(prompt='run: ')
window_name = widget.WindowName(
    background='#181818',
    foreground='#50fa7b',
    max_chars=40,
    format='{state}{class}'
)
clock_icon = widget.TextBox(text=' ', foreground='#42a5f5')
clock = widget.Clock(
    interval=30,
    foreground='#dddddd',
    format='%I:%M %p'
)
layout_icon = widget.TextBox(text=' ', foreground='#fbc02d')
current_layout = widget.CurrentLayout(foreground='#dddddd')
baterry_icon = widget.TextBox(text=' ', foreground='#c1c766')
baterry = widget.Battery(
    foreground='#dddddd',
    format='{char} {percent: 2.0%}',
    charge_char='C',
    discharge_char='D',
    full_char='F',
)
thermal_icon = widget.TextBox(text=' ', foreground='#ba68c8')
thermal = widget.ThermalSensor(foreground='#dddddd')
cpu_icon = widget.TextBox(text=' ', foreground='#ec407a')
cpu = widget.CPU(foreground='#dddddd', update_interval=5.0)
volume_icon = widget.TextBox(text=' ', foreground='#ec7875')
volume = widget.Volume(
    foreground='#dddddd',
    get_volume_command=['amixer', '-D', 'default', '-M', 'sget', 'Master'],
)
disk_icon = widget.TextBox(text=' ', foreground='#7cb342')
disk = widget.DF(foreground='#dddddd', visible_on_warn=False)
memory_icon = widget.TextBox(text=' ', foreground='#7e57c2')
memory = widget.Memory(foreground='#dddddd', update_interval=5.0)
backlight = widget.Backlight()

widgets = [
    group_box,
    prompt,
    window_name,
    layout_icon,
    current_layout,
    disk_icon,
    disk,
    memory_icon,
    memory,
    cpu_icon,
    cpu,
    thermal_icon,
    thermal,
    baterry_icon,
    baterry,
    volume_icon,
    volume,
    clock_icon,
    clock,
]
