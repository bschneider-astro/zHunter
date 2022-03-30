import pyqtgraph as pg
from PyQt5 import QtGui
from PyQt5 import QtCore
import pandas as pd
import logging
from pathlib import Path


log = logging.getLogger(__name__)
ROOT_DIR = Path(__file__).parent.resolve()


class SpecSystem():
    """
        A class to represent a spectroscopic system, either in emission
        or in absorption.
    """
    def __init__(self, z, PlotItem, sys_type,
                 color=QtGui.QColor('blue'),
                 fname=ROOT_DIR/'line_lists/basic_line_list.csv',
                 lines=None):
        self.redshift = z
        self.color = color
        self.sys_type = sys_type
        if lines is None:
            self.lines = pd.read_csv(fname, sep=',', names=['name','wvlg'], comment='#')
        else:
            self.lines = lines
        self.plotted_lines = []
        self.pi = PlotItem

    def draw(self, xmin=None, xmax=None):
        pen = pg.mkPen(self.color, width=3)
        # Make background for the rectangle on which to print line names
        black = QtGui.QColor('k')
        black.setAlpha(200)
        brush = pg.mkBrush(color=black)
        # Add lines to plot
        log.debug('Drawing %s System at redshift : %.5lf', self.sys_type, self.redshift)
        for w, n in zip(self.lines['wvlg'], self.lines['name']):
            gt_min = (xmin is None) or (w * (1+self.redshift) >= xmin)
            lt_max = (xmax is None) or (w * (1+self.redshift) <= xmax)
            if gt_min and lt_max:
                if self.sys_type == 'abs':
                    line = pg.InfiniteLine(w * (1+self.redshift),
                                           span=(0.,0.8),
                                           pen=pen,
                                           name='z={:.5f}'.format(self.redshift),
                                           label=n,
                                           labelOpts={'color':self.color,
                                                      'fill':brush,
                                                      'angle':45,
                                                      'position':1})#,movable=True)
                elif self.sys_type == 'em':
                    line = pg.InfiniteLine(w * (1+self.redshift),
                                           span=(0.2, 1.),
                                           pen=pen,
                                           name='z={:.5f}'.format(self.redshift),
                                           label=n,
                                           labelOpts={'color':self.color,
                                                      'fill':brush,
                                                      'angle':-45,
                                                      'position':0})#,movable=True)
                self.pi.addItem(line)
                self.plotted_lines.append(line)

    def remove(self):
        for line in self.plotted_lines:
            self.pi.removeItem(line)
        log.info("Deleted %s System at redshift %.5lf", self.sys_type, self.redshift)


class SpecSystemModel(QtCore.QAbstractListModel):
    def __init__(self, *args, specsystems=None, **kwargs):
        super(SpecSystemModel, self).__init__(*args, **kwargs)
        self.specsystems = specsystems or []

    def data(self, index, role):
        if role == QtCore.Qt.DisplayRole:
            # See below for the data structure.
            status, specsys = self.specsystems[index.row()]
            return "z = {:.5f} ({:s})".format(specsys.redshift,
                                              specsys.sys_type)

        if role == QtCore.Qt.ForegroundRole:
            status, specsys = self.specsystems[index.row()]
            return QtGui.QBrush(QtGui.QColor(specsys.color))

        if role == QtCore.Qt.DecorationRole:
            status, specsys = self.specsystems[index.row()]
            return QtGui.QColor(specsys.color)

    def rowCount(self, index):
        return len(self.specsystems)

    def delete(self, index):
        # Remove the item and refresh.
        _, _sys = self.specsystems[index.row()]
        log.debug("Received request to delete system at redshift %.5lf", _sys.redshift)
        _sys.remove()
        del self.specsystems[index.row()]
        self.layoutChanged.emit()
        self.sort(0)

    def clear(self):
        for _, specsys in self.specsystems:
            specsys.remove()
        self.specsystems = []
