-- Pull in the wezterm API
local wezterm = require 'wezterm'

-- This will hold the configuration.
local config = wezterm.config_builder()

-- Tabbar toggle isn't supported as an action yet
-- See https://github.com/wez/wezterm/issues/4625
wezterm.on("toggle-tabbar", function(window, _)
	local overrides = window:get_config_overrides() or {}
	if overrides.enable_tab_bar == false then
		overrides.enable_tab_bar = true
	else
		overrides.enable_tab_bar = false
	end
	window:set_config_overrides(overrides)
end)

-- Font Config

-- Old man eyes
config.font_size = 13.0

-- Set the default font
config.font = wezterm.font { family = 'Fira Code' }

-- By default, wezterm uses 'DemiBold' for 'Bold' fonts, we want the real deal
config.font_rules = {
    {
        intensity = 'Bold',
        italic = false,
        font = wezterm.font {
            family = 'Fira Code',
            weight = 'Bold',
        },
    },
}


-- Color Schemes
-- config.color_scheme = 'Monokai Soda'
-- config.color_scheme = 'Monokai Remastered'
config.color_scheme = 'Molokai'
config.inactive_pane_hsb = {
  saturation = 0.6,
  brightness = 0.2,
}

-- Key Bindings
--
-- enable for keyboard debugging
config.debug_key_events = false


config.keys = {
    -- iTerm split pane compat
    {
        key = 'd',
        mods = 'SUPER|SHIFT',
        action = wezterm.action.SplitVertical { domain = 'CurrentPaneDomain' },
    },
    {
        key = 'd',
        mods = 'SUPER',
        action = wezterm.action.SplitHorizontal { domain = 'CurrentPaneDomain' },
    },
    -- sane 'cmd w'
    {
        key = 'w',
        mods = 'SUPER',
        action = wezterm.action.CloseCurrentPane { confirm = false },
    },
    {
        key = 't',
        mods = 'SUPER|SHIFT',
        action = wezterm.action.EmitEvent("toggle-tabbar"),
    },
    {
        key = 't',
        mods = 'SUPER|SHIFT|ALT',
        action = wezterm.action.PaneSelect,
    },
}

-- and finally, return the configuration to wezterm
return config
