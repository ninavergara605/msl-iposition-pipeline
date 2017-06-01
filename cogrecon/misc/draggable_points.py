import matplotlib.pyplot as plt
import matplotlib.patches as patches


class DraggablePoint:
    lock = None  # only one can be animated at a time

    def __init__(self, point, move_callback=None):
        self.move_callback = move_callback
        self.cidmotion = self.point.figure.canvas.mpl_connect('motion_notify_event', self.on_motion)
        self.cidrelease = self.point.figure.canvas.mpl_connect('button_release_event', self.on_release)
        self.cidpress = self.point.figure.canvas.mpl_connect('button_press_event', self.on_press)
        self.point = point
        self.press = None
        self.background = None

    def connect(self, move_callback=None):
        # connect to all the events we need
        pass

    def on_press(self, event):
        if event.inaxes != self.point.axes:
            return
        if DraggablePoint.lock is not None:
            return
        contains, attrd = self.point.contains(event)
        if not contains:
            return
        self.press = self.point.center, event.xdata, event.ydata
        DraggablePoint.lock = self

        # draw everything but the selected rectangle and store the pixel buffer
        canvas = self.point.figure.canvas
        axes = self.point.axes
        self.point.set_animated(True)
        canvas.draw()
        self.background = canvas.copy_from_bbox(self.point.axes.bbox)

        # now redraw just the rectangle
        axes.draw_artist(self.point)

        # and blit just the redrawn area
        canvas.blit(axes.bbox)

    def on_motion(self, event):
        if self.move_callback:
            self.move_callback()

        if DraggablePoint.lock is not self:
            return
        if event.inaxes != self.point.axes:
            return
        self.point.center, xpress, ypress = self.press
        dx = event.xdata - xpress
        dy = event.ydata - ypress
        self.point.center = (self.point.center[0]+dx, self.point.center[1]+dy)

        canvas = self.point.figure.canvas
        axes = self.point.axes

        # restore the background region
        canvas.restore_region(self.background)

        # redraw just the current rectangle
        axes.draw_artist(self.point)

        # blit just the redrawn area
        canvas.blit(axes.bbox)

    def on_release(self):
        # on release we reset the press data
        if DraggablePoint.lock is not self:
            return

        self.press = None
        DraggablePoint.lock = None

        # turn off the rect animation property and reset the background
        self.point.set_animated(False)
        self.background = None

        # redraw the full figure
        self.point.figure.canvas.draw()

    def disconnect(self):
        # disconnect all the stored connection ids
        self.point.figure.canvas.mpl_disconnect(self.cidpress)
        self.point.figure.canvas.mpl_disconnect(self.cidrelease)
        self.point.figure.canvas.mpl_disconnect(self.cidmotion)

if __name__ == "__main__":
    fig = plt.figure()
    ax = fig.add_subplot(111)
    drs = []
    circles = [patches.Circle((0.32, 0.3), 0.03, fc='r', alpha=0.5),
               patches.Circle((0.3, 0.3), 0.03, fc='g', alpha=0.5)]

    for circ in circles:
        ax.add_patch(circ)
        dr = DraggablePoint(circ)
        dr.connect()
        drs.append(dr)

    plt.show()