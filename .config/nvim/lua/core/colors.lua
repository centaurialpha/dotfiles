local status_ok, color_scheme = pcall(require, 'onedark')
if not status_ok then
  return
end


-- OneDark styles: dark, darker, cool, deep, warm, warmer, light
require('onedark').setup {
  style = 'darker',
  colors = {
    bg0 = "#181a1f",
  },
  highlights = {
    -- Dashboard header colors
			StartLogo1 = { fg = "#007adb" },
			StartLogo2 = { fg = "#007adb" },
			StartLogo3 = { fg = "#007adb" },
			StartLogo4 = { fg = "#008edb" },
			StartLogo5 = { fg = "#008edb" },
			StartLogo6 = { fg = "#008edb" },
			StartLogo7 = { fg = "#009bdb" },
			StartLogo8 = { fg = "#009bdb" },
			StartLogo9 = { fg = "#009bdb" },
			StartLogo10 = { fg = "#00a3db" },
			StartLogo11 = { fg = "#00a3db" },
			StartLogo12 = { fg = "#00a3db" },
    }
  -- colors = { fg = '#b2bbcc' }, --default: #a0a8b7
}
require('onedark').load()
