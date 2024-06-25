import math
from tkinter import *
from tkinter import filedialog
from matplotlib.figure import Figure 
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg,  
NavigationToolbar2Tk)
from matplotlib.gridspec import GridSpec
import subprocess

'''
MAINTAIN THOSE IMPORTS UP TO DATE
'''
from LinkCurvesSpikesDialog import *

import MatchCandidatesGenerator
from FeatureExtractor import *
from Matcher import *
from SpikeLinker import *

from ProjectManager import *

import loader
import saver
from SpikeCluster import *
from PlotCurve import *
from themes import *
from CanvasSpikes import *
from FilterTree import *


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

        self.match_button = Button(master=self.master, command=self.match_regions, height=2, width=20, text="Match selected regions")
        self.match_button.pack()

        self.match_spikes_button = Button(master=self.master, command=self.match_spikes, height=2, width=20, text="Match spikes given regions")
        self.match_spikes_button.pack()

        self.run_blackbox_button = Button(master=self.master, command=self.run_blackbox, height=2, width=20, text="Run black box button")
        self.run_blackbox_button.pack()

        # Menu
        menu = Menu(master)
        self.master.config(menu=menu)
        filemenu = Menu(menu)
        menu.add_cascade(label='File', menu=filemenu)
        filemenu.add_command(label='New project', command=self.new_project)
        filemenu.add_separator()
        filemenu.add_command(label='Open project', command=self.open_project)
        filemenu.add_command(label='Open curve', command=self.open_curve)
        filemenu.add_command(label='Open spikes', command=self.open_spikes)
        filemenu.add_separator()
        filemenu.add_command(label='Link graphs', command=self.link_plots_spikes)
        filemenu.add_separator()
        filemenu.add_command(label='Save project', command=self.save_project)
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

        self.plots = []
        self.bars = []

        self.init_plots()

        ProjectManager.init_project()
        ProjectManager.auto_load(self.graphs_plot, self.bars_plot)

        #self.open_project(self.project)
        self.load_project_data()

        #self.test()

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

    def test(self):
        #large test
        self.plots[1].set_ranges([(1032.110, 1032.125)])
        self.plots[0].set_ranges([(1032.020, 1032.160)])
        
        #second spike small test
        #self.plots[1].set_ranges([(1032.240, 1032.245)])
        #self.plots[0].set_ranges([(1032.265, 1032.280)])

        #third spike large test
        #self.plots[1].set_ranges([(1032.350, 1032.370)])
        #self.plots[0].set_ranges([(1032.265, 1032.550)])

        #fourth spike huge test
        #self.plots[1].set_ranges([(1032.800, 1032.900)])
        #self.plots[0].set_ranges([(1032.550, 1033.150)])

        pass

    def match_regions(self):
        if len(self.plots) > 1:
            target_plot_index = 1
            current_plot_index = 0
            
            target_plot = self.plots[target_plot_index]
            current_plot = self.plots[current_plot_index]

            target_rangex, target_rangey, target_clusters = target_plot.get_ranges()
            current_rangex, current_rangey, current_clusters = current_plot.get_ranges()
            if not target_clusters or not current_clusters:
                print("no target_clusters/current_clusters")
                return
            target_cluster = SpikeCluster.merge(target_clusters)
            target_cluster, new_start_target, new_end_target = SpikeCluster.truncate(target_cluster, 0.2, 0.15)

            current_clusters = SpikeCluster.merge(current_clusters)

            matchRandom = MatchingStep(RandomFeatureExtractor(100, 200), 1.0, 1.0)#0.5, 1.0, 0.5)
            matchDistance = MatchingStep(DistanceFeatureExtractor([0.66, 0.75, 1.0, 1.25, 1.5, 1.66, 1.75], 1.0, 10.0), 0.5, 1.0)
            matchShape = MatchingStep(ShapeFeatureExtractor([0.5, 0.75, 1.0, 1.5, 1.75]), 0.5, 1.0)
            matcher = Matcher(matchDistance)#matchingStep1)#, matchingStep2)
            target_start, target_end, x_start, x_end, target_tree, current_tree = matcher.match(target_cluster, current_clusters, 1)#3)
            
            #target_plot.set_ranges([(target_cluster.spikesX[target_start], target_cluster.spikesX[target_end])])
            target_plot.set_ranges([(target_start, target_end)])
            print("selecting range in current plot of", x_start, ":", x_end)
            current_plot.set_ranges([(x_start, x_end)])
            
        #filterTree = FilterTree.build()
        self.canvas.draw()
        pass
    def match_spikes(self):
        if len(self.plots) > 1 and len(self.bars) > 1:
            target_plot_index = 1
            current_plot_index = 0
            
            target_plot = self.plots[target_plot_index]
            current_plot = self.plots[current_plot_index]

            target_rangex, target_rangey, target_clusters = target_plot.get_ranges()
            current_rangex, current_rangey, current_clusters = current_plot.get_ranges()
            if not target_clusters or not current_clusters:
                print("no target_clusters/current_clusters")
                return
            target_cluster = SpikeCluster.merge(target_clusters)
            current_cluster = SpikeCluster.merge(current_clusters)
    
            target = self.bars[target_plot_index].spikes_data
            current = self.bars[current_plot_index].spikes_data

            target_cluster, _, _ = SpikeCluster.truncate_range_x(target_cluster, target_rangex[0], target_rangex[-1])
            current_cluster, _, _ = SpikeCluster.truncate_range_x(current_cluster, current_rangex[0], current_rangex[-1])

            target_tree = Splitter.generate_tree(target_cluster.spikesX, target_cluster.spikesY)
            current_tree = Splitter.generate_tree(current_cluster.spikesX, current_cluster.spikesY)

            #print("target_rangex[0]", target_rangex[0], ":", target_rangex[-1], "len target_cluster.spikesX", len(target_cluster.spikesX))
            #print("current_rangex[0]", current_rangex[0], ":", current_rangex[-1], "len current_cluster.spikesX", len(current_cluster.spikesX))

            target_splits = target_tree.get_splits()
            current_splits = current_tree.get_splits()
            #print("target_splits", target_splits, "for length", target_tree.length())
            #print("current_splits", current_splits, "for length", current_tree.length())

            target_tree.show(target_cluster.spikesX, target_cluster.spikesY)
            current_tree.show(current_cluster.spikesX, current_cluster.spikesY)
            
            SpikeLinker.link_splits(target_splits, target_cluster.spikesX, target_cluster.spikesY, target, current_splits, current_cluster.spikesX, current_cluster.spikesY, current)
            #SpikeLinker.link(target_x_start, target_x_end, target, current_x_start, current_x_end, current)
        pass

    def run_blackbox(self):
        print("Saving every changes to files...")

        if len(self.plots) > 1 and len(self.bars) > 1:
            target_plot_index = 1
            current_plot_index = 0
            
            target_plot = self.plots[target_plot_index]
            current_plot = self.plots[current_plot_index]

            target_bars = self.bars[target_plot_index]
            current_bars = self.bars[current_plot_index]

            target_compiled = SpikeCluster.compile(target_plot.spikes_clusters, target_bars.spikes_data)
            current_compiled = SpikeCluster.compile(current_plot.spikes_clusters, current_bars.spikes_data)

            saver.write_XY("./result_current.xy", current_compiled.spikesX, current_compiled.spikesY)
            saver.write_ASG("./result_current.asg", current_compiled.bars)

        print("Done saving changes!")
        
        print("Starting to run the black box...")

        try:
            subprocess.call(["./job_xfit_nu3"])
            subprocess.call(["./job_cal_nu3"])
            subprocess.call(["./job_sim_nu3"])
            print("Ran every black box command!")
        except:
            print("Couldn't run the commands, try verifying that the required files are in the correct path and that you are using Mac or Linux!")

        print("Done running the black box!")
        pass

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

    def new_project(self):
        ProjectManager.init_project()
        self.load_project_data()
        ProjectManager.auto_save()

    def open_project(self):
        #root = tk.Tk()
        #root.withdraw()  # Hide the root window
        file_path = filedialog.askopenfilename()
        if not file_path:
            #root.deiconify()
            return
        ProjectManager.load_project(file_path, self.graphs_plot, self.bars_plot)

        ProjectManager.auto_save()

    def save_project(self):
        ProjectManager.auto_save()

    def load_project_data(self):
        print("Loading project...")

        self.plots.clear()
        self.bars.clear()

        window.title(ProjectManager.current_project.name)
        project = ProjectManager.current_project

        self.plots = project.curves
        self.bars = project.spikes

        '''

        paths = ProjectManager.get_curve_paths()
        themes = ProjectManager.get_curve_themes()
        for i in range(len(paths)):
            p = paths[i]
            t = themes[i]
            curve = self.open_curve_file(p, t)
        paths = ProjectManager.get_spikes_paths()
        themes = ProjectManager.get_spikes_themes()
        for i in range(len(paths)):
            p = paths[i]
            t = themes[i]
            bars = self.open_spikes_file(p, t)

        '''
            
        print("Done loading project!")

    def open_curve(self):
        #root = tk.Tk()
        #root.withdraw()  # Hide the root window
        file_path = filedialog.askopenfilename(title="Open spikes (dpt, xy)")
        if not file_path:
            #root.deiconify()
            return
        filename, file_extension = os.path.splitext(file_path)
        
        p = int(np.mod(len(self.plots) - 1, DefaultTheme.get_palettes_count("graph"))) + 1
        theme = "graph" + str(p)
        theme = DefaultTheme.get_palette(theme)

        self.open_curve_file(file_path, theme)

        self.canvas.draw()
        
    def open_curve_file(self, file_path, theme):
        ProjectManager.disable_auto_save()

        clusters = None
        filename, file_extension = os.path.splitext(file_path)
        print("File '", filename, "' is '", file_extension, "' format!")
        if "dpt" in file_extension.lower():
            clusters = loader.parse_DPT(file_path)
        elif "xy" in file_extension.lower():
            clusters = loader.parse_XY(file_path)

        self.plots.append(
        PlotCurve(
            file_path, self.graphs_plot, clusters, 
            theme,
            0.02,
            [],
            RANGE_MODE_CLUSTERS
        )
        )
        plot_i = 0
        for plot in self.plots:
            if plot_i == len(self.plots) - 1:
                plot.enable()
                plot.set_zorder(1)
            else:
                plot.disable()
                plot.set_zorder(0)
            plot_i += 1

        curve = self.plots[-1]

        #curve.set_xoffset(ProjectManager.get_curve_xoffset(curve.name))

        ProjectManager.enable_auto_save()
        return curve

    def open_spikes(self):
        #root = tk.Tk()
        #root.withdraw()  # Hide the root window
        file_path = filedialog.askopenfilename(title="Open spikes (asg, t)")
        if not file_path:
            #root.deiconify()
            return
        filename, file_extension = os.path.splitext(file_path)
        
        p = int(np.mod(len(self.bars) - 1, DefaultTheme.get_palettes_count("bars"))) + 1
        theme = "bars" + str(p)
        theme = DefaultTheme.get_palette(theme)

        self.open_spikes_file(file_path, theme)
        
        self.canvas.draw()

    def open_spikes_file(self, file_path, theme):
        ProjectManager.disable_auto_save()

        bars = None
        filename, file_extension = os.path.splitext(file_path)
        print("File '", filename, "' is '", file_extension, "' format!")
        if "t" in file_extension.lower():
            bars = loader.parse_T(file_path)
            xdata = [b.x for b in bars]
        if "asg" in file_extension.lower():
            bars = loader.parse_ASG(file_path)
            xdata = [b.x for b in bars]

        self.bars.append(
        CanvasSpikes(file_path, self.bars_plot, bars, xdata, theme)
        )
        plot_i = 0
        for plot in self.plots:
            if plot_i == len(self.plots) - 1:
                plot.enable()
                plot.set_zorder(1)
            else:
                plot.disable()
                plot.set_zorder(0)
            plot_i += 1
        
        ProjectManager.enable_auto_save()
        return self.bars[-1]

    def link_plots_spikes(self):
        app = LinkCurvesSpikesDialog(self.plots, self.bars)
        app.run()


    '''
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
    '''

    def init_plots(self):
        # the figure that will contain the plot
        fig = Figure(figsize=(10, 8), dpi=100)

        gs = GridSpec(3, 1, figure=fig)  # Divide figure into 3 rows, 1 column

        self.bars_plot = fig.add_subplot(gs[0, 0])  # Top small subplot for bars
        self.graphs_plot = fig.add_subplot(gs[1:, 0])  # Larger subplot for graphs

        # creating the Tkinter canvas containing the Matplotlib figure
        self.canvas = FigureCanvasTkAgg(fig, master=self.master)
        self.canvas.draw()

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