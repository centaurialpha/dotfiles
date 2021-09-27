from libqtile import widget, bar


class PoweroffWidget(widget.base._TextBox):
    defaults = [
        ("default_text", "", "a text displayed as a button"),
        ("countdown_format", "{}", "this text is showed when counting down."),
        ("timer_interval", 1, "a countdown interval."),
        ("countdown_start", 5, "time to accept the second pushing."),
    ]

    def __init__(self, widget=bar.CALCULATED, **config):
        super().__init__("", widget, **config)
        self.add_defaults(PoweroffWidget.defaults)
        self.is_counting = False
        self.countdown = self.countdown_start
        self.text = self.default_text
        self._call_later_funcs = []

        self.add_callbacks({"Button1": self.shutdown})

    def _reset(self):
        self.is_counting = False
        self.countdown = self.countdown_start
        self.text = self.default_text
        for f in self._call_later_funcs:
            f.cancel()

    def update(self):
        if not self.is_counting:
            return

        self.countdown -= 1
        self.text = self.countdown_format.format(self.countdown)
        func = self.timeout_add(self.timer_interval, self.update)
        self._call_later_funcs.append(func)
        self.draw()

        if self.countdown == 0:
            import subprocess
            subprocess.call("poweroff", shell=True)

    def shutdown(self):
        if not self.is_counting:
            self.is_counting = True
            self.update()
        else:
            self._reset()
            self.draw()


group_box = widget.GroupBox(
    borderwidth=1,
    padding_y=4,
    padding_x=5,
    highlight_method="block",
    urgent_alert_method="block",
    this_current_screen_border="#7e57c2",
    this_screen_border="#bd93f9",
    other_current_screen_border="#7e57c2",
    block_highlight_text_color="#000000",
    urgent_border="#ff5555",
)
prompt = widget.Prompt(prompt="run: ")
window_name = widget.WindowName(
    foreground="#50fa7b", max_chars=40, format="{state}{class}"
)
clock_icon = widget.TextBox(text="", background="#668ee3", foreground="#1e222a")
clock = widget.Clock(
    interval=30,
    foreground="#1e222a",
    background="#7aa2f7",
    format="%B %d [ %H:%M ]",
    margin_y=10,
)
layout_icon = widget.TextBox(text="", foreground="#1e222a", background="#e5c07b")
current_layout = widget.CurrentLayout(foreground="#e5c07b", background="#1e222a")
battery_icon = widget.TextBox(text="", fontsize=16, foreground="#81A1C1")
battery = widget.Battery(
    foreground="#81A1C1",
    format="{char}{percent: 2.0%}",
    charge_char="",
    discharge_char="",
    full_char="",
    empty_char="",
)
thermal = widget.ThermalSensor(foreground="#e06c75", show_tag=True)
cpu = widget.CPU(
    background="#353b45",
    foreground="#abb2bf",
    format="{freq_current}GHz",
    update_interval=5.0,
)
volume_icon = widget.TextBox(text="", foreground="#f1fa8c")
volume = widget.Volume(
    foreground="#f1fa8c",
    get_volume_command=["amixer", "-D", "default", "-M", "sget", "Master"],
)
disk = widget.DF(
    format=" {uf}{m}|{r:.0f}%", foreground="#c678dd", visible_on_warn=False
)
memory = widget.Memory(
    foreground="#7797b7",
    format="{MemUsed: .2f}{mm}",
    update_interval=5.0
)

widgets = [
    layout_icon,
    current_layout,
    group_box,
    prompt,
    window_name,
    clock_icon,
    clock,
    widget.Spacer(length=bar.STRETCH),
    disk,
    memory,
    widget.TextBox(text="CPU", foreground="#3b414d", background="#7ec7a2"),
    cpu,
    thermal,
    battery,
    volume_icon,
    volume,
]
