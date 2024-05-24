from theme import *


from PlotCurve import *


DefaultTheme = Theme(
    { 
        "bars1": ColorPalette(
        {
            PALETTE_OBJECT_BAR: { 
                PALETTE_PROPERTY_PLOT_ENABLED: "steelblue",
                PALETTE_PROPERTY_PLOT_DISABLED: "skyblue",
                PALETTE_PROPERTY_LINE_HOVERED: "yellow",
                PALETTE_PROPERTY_LINE_SELECTED: "lawngreen",
                },
        }
        ),
        "bars2": ColorPalette(
        {
            PALETTE_OBJECT_BAR: { 
                PALETTE_PROPERTY_PLOT_ENABLED: "salmon",
                PALETTE_PROPERTY_PLOT_DISABLED: "lightpink",
                PALETTE_PROPERTY_LINE_HOVERED: "yellow",
                PALETTE_PROPERTY_LINE_SELECTED: "magenta",
                },
        }
        ),
        "graph1": ColorPalette(
        {
            PALETTE_OBJECT_GRAPH: { 
                PALETTE_PROPERTY_PLOT_ENABLED: "steelblue",
                PALETTE_PROPERTY_PLOT_DISABLED: "skyblue",
                PALETTE_PROPERTY_PLOT_HOVERED: "lawngreen",
                },
            PALETTE_OBJECT_GRAPH_SELECTION: { 
                PALETTE_PROPERTY_PLOT_ENABLED: "lime",
                PALETTE_PROPERTY_PLOT_DISABLED: "lightseagreen",
                PALETTE_PROPERTY_PLOT_HOVERED: "lightseagreen",
                },
            PALETTE_OBJECT_LINE: { 
                PALETTE_PROPERTY_LINE_ENABLED: "gray",
                PALETTE_PROPERTY_LINE_DISABLED: "lightgrey",
                PALETTE_PROPERTY_LINE_HOVERED: "yellow",
                PALETTE_PROPERTY_LINE_SELECTED: "orange",
                },
        }
        ),
        "graph2": ColorPalette(
        {
            PALETTE_OBJECT_GRAPH: { 
                PALETTE_PROPERTY_PLOT_ENABLED: "salmon",
                PALETTE_PROPERTY_PLOT_DISABLED: "lightpink",
                PALETTE_PROPERTY_PLOT_HOVERED: "magenta",
                },
            PALETTE_OBJECT_GRAPH_SELECTION: { 
                PALETTE_PROPERTY_PLOT_ENABLED: "crimson",
                PALETTE_PROPERTY_PLOT_DISABLED: "tomato",
                PALETTE_PROPERTY_PLOT_HOVERED: "tomato",
                },
            PALETTE_OBJECT_LINE: { 
                PALETTE_PROPERTY_LINE_ENABLED: "gray",
                PALETTE_PROPERTY_LINE_DISABLED: "lightgrey",
                PALETTE_PROPERTY_LINE_HOVERED: "yellow",
                PALETTE_PROPERTY_LINE_SELECTED: "orange",
                },
        }
        )
    }
)