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
    
    def to_dict(self):
        return {
            "palettes": {k: v.to_dict() for k, v in self.palettes.items()},
            "error_palette": self.error_palette.to_dict()
        }

    @classmethod
    def from_dict(cls, data):
        palettes = {k: ColorPalette.from_dict(v) for k, v in data.get("palettes", {}).items()}
        error_palette = ColorPalette.from_dict(data.get("error_palette", {}))
        return cls(palettes=palettes, error_palette=error_palette)

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
    
    def to_dict(self):
        return {
            "colors": self.colors,
            "properties_default_colors": self.properties_default_colors,
            "error_color": self.error_color
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            colors=data.get("colors", {}),
            properties_default_colors=data.get("properties_default_colors", {}),
            error_color=data.get("error_color", "darkviolet")
        )