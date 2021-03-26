import dracula.draw

config.load_autoconfig(False)

# Default home page
c.url.default_page = 'https://google.com.ar'

dracula.draw.blood(c, {
    'spacing': {
        'vertical': 6,
        'horizontal': 8
    }
})
