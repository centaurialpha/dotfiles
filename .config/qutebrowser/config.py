# import dracula.draw
# 
config.load_autoconfig()
# 
# # Default home page
c.url.default_page = 'https://google.com.ar'
c.confirm_quit = ['multiple-tabs']
# 
# dracula.draw.blood(c, {
#     'spacing': {
#         'vertical': 6,
#         'horizontal': 8
#     }
# })

c.auto_save.session = True

# Fonts
c.fonts.completion.category = '12pt Hermit'
c.fonts.completion.entry = '10pt Hermit'
c.fonts.statusbar = '10pt Hermit'
c.fonts.tabs.selected = '10pt Hermit'
c.fonts.tabs.unselected = '10pt Hermit'
c.fonts.prompts = '10pt Hermit'
c.fonts.messages.error = '10pt Hermit'
c.fonts.messages.info = '10pt Hermit'
c.fonts.messages.warning = '10pt Hermit'
c.fonts.hints = '12pt Hermit'
