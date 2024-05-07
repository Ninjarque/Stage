class Theme:
    def __init__(self, palettes = {}, error_palette = None):
        self.palettes = palettes
        self.error_palette = error_palette
        if not self.error_palette:
            self.error_palette = ColorPalette({})
        pass

    def set_palette(self, object, palette):
        self.palettes[object] = palette
    
    def get_palette(self, object):
        if object in self.palettes:
            return self.palettes[object]
        print("Theme error, no palette found for '", object, "'!")
        return self.error_palette

class ColorPalette:
    def __init__(self, colors, properties_default_colors = {}, error_color = "darkviolet"):
        self.colors = colors
        self.properties_default_colors = properties_default_colors
        self.error_color = error_color

    def set_color(self, property, state, color):
        self.colors[property][state] = color

    def get_color(self, property, state):
        if property in self.colors:
            if state in self.colors[property]:
                return self.colors[property][state]
            elif property in self.properties_default_colors:
                return self.properties_default_colors[property]
        print("Unknown color arrangement ", property, " for state {", state, "}")
        return self.error_color