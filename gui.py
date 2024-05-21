import math
from tkinter import *
from matplotlib.figure import Figure 
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg,  
NavigationToolbar2Tk)
from matplotlib.gridspec import GridSpec


'''
MAINTAIN THOSE IMPORTS UP TO DATE PLS
'''
import loader
from PlotCurve import *
from themes import *
from CanvasSpikes import *


class Spectre:
    def __init__(self):
        pass

class Spikes:
    def __init__(self):
        pass



class NavigationToolbar(NavigationToolbar2Tk):

    def enable(self):
        self.enabled = True
        
    def disable(self):
        self.enabled = False

    #Only pass on events when enabled and delay requests to Navbar so that the graphics overlays can handle them first
    def _zoom_pan_handler(self, event):
        event.requeued = False if not hasattr(event, 'requeued') else True
        if not hasattr(self, 'enabled'):
            self.enabled = True
        if not self.enabled:
            return
        if event.name == 'button_press_event' and not event.requeued:
            event.requeued = True
            self.after(100, self._zoom_pan_handler, event)
        else:
            super()._zoom_pan_handler(event)



class GUI:
    def __init__(self, master):
        self.master = master
        self.master.title('Main Window')
        self.master.geometry("1000x800")

        self.plots = []

        # Button to display the plot
        self.plot_button = Button(master=self.master, command=self.toggle_curves, height=2, width=20, text="Toggle curve selection")
        self.plot_button.pack()


        # Menu
        menu = Menu(master)
        self.master.config(menu=menu)
        filemenu = Menu(menu)
        menu.add_cascade(label='File', menu=filemenu)
        filemenu.add_command(label='New')
        filemenu.add_command(label='Open...')
        filemenu.add_separator()
        filemenu.add_command(label='Exit', command=master.quit)
        helpmenu = Menu(menu)
        menu.add_cascade(label='Help', menu=helpmenu)
        helpmenu.add_command(label='About')

        # Utility
        self.start_click_pos = None
        self.moved_too_much = False

        # Limits
        self.x_range = 0.0
        self.y_range = 0.0

        self.plot()

    def toggle_curves(self):
        if len(self.plots) == 0:
            return
        plot_i = 0
        i = 0
        for plot in self.plots:
            if plot.enabled:
                plot_i = i
                break
            i += 1
        plot_i = (plot_i + 1) % len(self.plots)
        self.select(self.plots[plot_i])

    def select(self, plot):
        for p in self.plots:
            p.disable()
            p.set_zorder(0)
        plot.enable()
        plot.set_zorder(1)
        bar_i = 0
        for bars in self.bars:
            plot = self.plots[bar_i]
            if plot.enabled:
                bars.enable()
            else:
                bars.disable()
            bar_i += 1
        self.canvas.draw()

    def plot(self):
        # the figure that will contain the plot
        fig = Figure(figsize=(10, 8), dpi=100)

        gs = GridSpec(3, 1, figure=fig)  # Divide figure into 3 rows, 1 column

        self.bars_plot = fig.add_subplot(gs[0, 0])  # Top small subplot for bars
        self.graphs_plot = fig.add_subplot(gs[1:, 0])  # Larger subplot for graphs

        # Assuming you have already defined these somewhere
        data1_x, data1_y = self.get_data1()
        data2_x, data2_y = self.get_data2()

        spikes_data1, spikes_xdata1 = self.get_spikes_data1()
        spikes_data2, spikes_xdata2 = self.get_spikes_data2()

        # creating the Tkinter canvas containing the Matplotlib figure
        self.canvas = FigureCanvasTkAgg(fig, master=self.master)
        self.canvas.draw()

        self.bars = [
        CanvasSpikes(self.bars_plot, spikes_data1, spikes_xdata1, DefaultTheme.get_palette("bars1")),
        CanvasSpikes(self.bars_plot, spikes_data2, spikes_xdata2, DefaultTheme.get_palette("bars2")),
        ]

        self.plots = [
        PlotCurve(
            self.graphs_plot, self.graph1_spikes_clusters, 
            0.02,
            DefaultTheme.get_palette("graph1"),
            RANGE_MODE_CLUSTERS
        ),
        PlotCurve(
            self.graphs_plot, self.graph2_spikes_clusters, 
            0.02,
            DefaultTheme.get_palette("graph2"),
            RANGE_MODE_CLUSTERS
        )
        ]
        plot_i = 0
        for plot in self.plots:
            if plot_i == 1:
                plot.enable()
                plot.set_xoffset(0.5)
                plot.set_zorder(1)
            else:
                plot.disable()
                plot.set_zorder(0)
            plot_i += 1
        bar_i = 0
        #check linking name or something
        for bars in self.bars:
            plot = self.plots[bar_i]
            if plot.enabled:
                bars.enable()
            else:
                bars.disable()
            plot.link_plotbar(bars)
            bar_i += 1

        #graphs_plot.callbacks.connect('xlim_changed', self.on_xlims_change_graph)
        self.graphs_plot.callbacks.connect('ylim_changed', self.on_ylims_change)
        
        # Connect xlim changes
        self.bars_plot.callbacks.connect('xlim_changed', lambda ax: self.on_xlims_change(ax, self.graphs_plot))
        self.graphs_plot.callbacks.connect('xlim_changed', lambda ax: self.on_xlims_change(ax, self.bars_plot))

        #bars_plot.callbacks.connect('xlim_changed', self.on_xlims_change_bars)
        #bars_plot.callbacks.connect('ylim_changed', self.on_ylims_change_bars)
  
        # Connect the mouse movement event to the canvas
        self.canvas.mpl_connect('motion_notify_event', self.mouse_move)
        self.canvas.mpl_connect('button_press_event', self.on_click)
        self.canvas.mpl_connect('button_release_event', self.on_release)

        self.canvas.mpl_connect('key_press_event', self.on_key_press)
        self.canvas.mpl_connect('key_press_event', self.on_key_release)
        
        # placing the canvas on the Tkinter window
        self.canvas.get_tk_widget().pack()

        # creating the Matplotlib toolbar
        self.toolbar = NavigationToolbar(self.canvas, self.master)
        self.toolbar.zoom()
        self.toolbar.pan()
        self.toolbar.update()
        self.canvas.get_tk_widget().pack()

        x_lims = self.graphs_plot.get_xlim()
        print(x_lims)
        print(self.bars_plot.get_xlim())
        self.bars_plot.set_xlim(x_lims)

        self.canvas.draw()


    def mouse_move(self, event):
        if event.inaxes and self.start_click_pos:
            x_start, _ = self.start_click_pos
            if x_start and event.xdata and abs(x_start - event.xdata) >= 0.01 * self.x_range:  # Threshold of 0.1 units
                self.moved_too_much = True
        need_redraw = False
        for plot in self.plots:
            rcode = plot.update_mouse(event.inaxes, event.xdata, event.ydata, self.moved_too_much, 
                                False, False)
            if rcode != CODE_NONE:
                need_redraw = True
        
        for bar in self.bars:
            r = bar.update_mouse(event.inaxes, event.xdata, event.ydata, self.moved_too_much, 
                            False, False)
            if r != CODE_NONE:
                rcode = r
            if rcode != CODE_NONE:
                need_redraw = True
        if need_redraw:
            self.canvas.draw()


    def on_click(self, event):
        correctClick = event.button == 1
        self.start_click_pos = (event.xdata, event.ydata)
        self.moved_too_much = False
        dont_need_update = False
        for plot in self.plots:
            if not dont_need_update and event.inaxes and event.button == 1:
                rcode = plot.update_mouse(event.inaxes, event.xdata, event.ydata, self.moved_too_much, 
                                    correctClick, False)
                if rcode == CODE_SELECTED_LINE:
                    self.disable_navigation()
                    dont_need_update = True
                if rcode == CODE_SELECTED_PLOT:
                    self.disable_navigation()
                    dont_need_update = True
                    self.select(plot)
            plot.draw()
        for bar in self.bars:
            bar.update_mouse(event.inaxes, event.xdata, event.ydata, self.moved_too_much, 
                                    correctClick, False)
            bar.draw()
        
        self.canvas.draw()
    
    def on_release(self, event):
        correctClick = event.button == 1
        for plot in self.plots:
            if event.inaxes and event.button == 1:
                rcode = plot.update_mouse(event.inaxes, event.xdata, event.ydata, self.moved_too_much, 
                                False, correctClick)
                if rcode == CODE_UNSELECTED_LINE or rcode == CODE_NONE:
                    self.enable_navigation()
            plot.draw()
        for bar in self.bars:
            if event.inaxes and event.button == 1:
                rcode = bar.update_mouse(event.inaxes, event.xdata, event.ydata, self.moved_too_much, 
                                False, correctClick)
                if rcode == CODE_UNSELECTED_LINE or rcode == CODE_NONE:
                    self.enable_navigation()
            plot.draw()
        self.moved_too_much = False

        self.canvas.draw()
    

    def on_key_press(self, event):
        for plot in self.plots:
            plot.update_key(event.key, True, False)
            plot.draw()
        for bar in self.bars:
            bar.update_key(event.key, True, False)
            bar.draw()

        self.canvas.draw()
    def on_key_release(self, event):
        for plot in self.plots:
            plot.update_key(event.key, False, True)
            plot.draw()
        for bar in self.bars:
            bar.update_key(event.key, False, True)
            bar.draw()

        self.canvas.draw()

    def on_ylims_change(self, event_ax):
        minx = event_ax.get_xlim()[0];
        maxx = event_ax.get_xlim()[1];
        miny = event_ax.get_ylim()[0];
        maxy = event_ax.get_ylim()[1];
        for plot in self.plots:
            plot.update_limits(minx, maxx, miny, maxy)

        self.canvas.draw()

    def on_xlims_change(self, source_ax, target_ax):
        """Update target plot's x-limits to match source plot's x-limits, with a check to prevent unnecessary changes."""
        # Get current limits from both axes
        source_xlim = source_ax.get_xlim()
        target_xlim = target_ax.get_xlim()

        # Only update if the limits are differentprint("set_xlim type:", type(target_ax.set_xlim))
        if source_xlim != target_xlim:
            target_ax.set_xlim(source_xlim)
            target_ax.set_xlim(source_xlim)

        if source_ax == self.graphs_plot:
            minx = source_ax.get_xlim()[0];
            maxx = source_ax.get_xlim()[1];
            miny = source_ax.get_ylim()[0];
            maxy = source_ax.get_ylim()[1];
            for plot in self.plots:
                plot.update_limits(minx, maxx, miny, maxy)
        if source_ax == self.bars_plot:
            minx = source_ax.get_xlim()[0];
            maxx = source_ax.get_xlim()[1];
            miny = source_ax.get_ylim()[0];
            maxy = source_ax.get_ylim()[1];
            for bar in self.bars:
                bar.update_limits(minx, maxx, miny, maxy)
                bar.draw()

        self.canvas.draw()

    def get_data1(self):
        self.graph1_spikes_clusters = loader.parse_DPT("")
        self.total_data = loader.graph_DPT(self.graph1_spikes_clusters)
        return self.total_data
    def get_data2(self):
        self.graph2_spikes_clusters = loader.parse_XY("")
        self.total_data = loader.graph_DPT(self.graph2_spikes_clusters)
        return self.total_data
    
    def get_spikes_data1(self):
        bars = loader.parse_ASG("")
        values = [b.x for b in bars]
        return bars, values
    def get_spikes_data2(self):
        bars = loader.parse_T("")
        values = [b.x for b in bars]
        return bars, values

    
    def disable_navigation(self):
        self.toolbar.disable()
        self.canvas.draw()

    def enable_navigation(self):
        self.toolbar.enable()
        self.canvas.draw()

# Main Tkinter window
window = Tk()
app = GUI(window)
window.mainloop()