import dracula.draw

config.load_autoconfig(False)

# Default home page
c.url.default_page = 'https://google.com.ar'
c.confirm_quit = ['multiple-tabs']

dracula.draw.blood(c, {
    'spacing': {
        'vertical': 6,
        'horizontal': 8
    }
})
