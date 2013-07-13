__author__ = 'tinyms'

import sys
import sqlite3
from utils import connect_db
from PyQt4 import QtCore,QtGui

class CustomTreeView(QtGui.QTreeView):
    def __init__(self):
        QtGui.QTreeView.__init__(self)

    def keyReleaseEvent(self,evt):
        if evt.key()==QtCore.Qt.Key_Delete:
            if not self.currentIndex().isValid():
                return
            self.model().removeRow(self.currentIndex().row())

    def mouseDoubleClickEvent(self,evt):
        index = self.currentIndex()
        if not index.isValid() or index.parent().isValid():
            return
        odds_index = self.model().index(index.row(),8,QtCore.QModelIndex())
        if not odds_index.isValid():
            return
        odds_url = self.model().data(odds_index,QtCore.Qt.DisplayRole)
        QtGui.QDesktopServices.openUrl(QtCore.QUrl(odds_url))
        pass

class QueryUI(QtGui.QWidget):
    def __init__(self):
        super(QueryUI,self).__init__()
        #查询特征
        self.query_factor = "Unknow"
        #UI
        headerWidget = QtGui.QWidget()
        headerLayout = QtGui.QHBoxLayout()
        headerWidget.setLayout(headerLayout)
        #查询条件栏
        self.odds_model = QtGui.QLineEdit()
        self.label3 = QtGui.QLabel("赔率:")
        self.win_radiobox = QtGui.QRadioButton("胜")
        self.win_radiobox.setChecked(True)
        self.draw_radiobox = QtGui.QRadioButton("平")
        self.lost_radiobox = QtGui.QRadioButton("负")
        QtCore.QObject.connect(self.win_radiobox,QtCore.SIGNAL("clicked(bool)"),self.on_310btn_clicked)
        QtCore.QObject.connect(self.draw_radiobox,QtCore.SIGNAL("clicked()"),self.on_310btn_clicked)
        QtCore.QObject.connect(self.lost_radiobox,QtCore.SIGNAL("clicked()"),self.on_310btn_clicked)
        self.after_match_checkbox = QtGui.QCheckBox("后匹配")
        self.before_match_checkbox = QtGui.QCheckBox("前匹配")
        QtCore.QObject.connect(self.after_match_checkbox,QtCore.SIGNAL("stateChanged(int)"),self.on_match_clicked)
        QtCore.QObject.connect(self.before_match_checkbox,QtCore.SIGNAL("stateChanged(int)"),self.on_match_clicked)
        self.before_match_checkbox.setChecked(True)

        self.execute_btn = QtGui.QPushButton("搜索")
        QtCore.QObject.connect(self.execute_btn,QtCore.SIGNAL("clicked()"),self.on_execute_btn_clicked)
        headerLayout.addWidget(self.win_radiobox)
        headerLayout.addWidget(self.draw_radiobox)
        headerLayout.addWidget(self.lost_radiobox)
        headerLayout.addWidget(self.label3)
        headerLayout.addWidget(self.odds_model,True)
        headerLayout.addWidget(self.execute_btn)
        headerLayout.addWidget(self.before_match_checkbox)
        headerLayout.addWidget(self.after_match_checkbox)
        headerLayout.addStretch()
        #End

        self.matchs_grid = CustomTreeView()
        self.data_grid_model = MatchsTreeModel([])
        self.matchs_grid.setModel(self.data_grid_model)
        self.matchs_grid.setRootIsDecorated(False)
        self.matchs_grid.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        self.matchs_grid.setAlternatingRowColors(True)
        self.matchs_grid.header().setStretchLastSection(False)
        self.matchs_grid.header().setResizeMode(0,QtGui.QHeaderView.ResizeToContents)
        self.matchs_grid.header().setResizeMode(1,QtGui.QHeaderView.Stretch)
        self.matchs_grid.header().setResizeMode(2,QtGui.QHeaderView.ResizeToContents)
        self.matchs_grid.header().setResizeMode(3,QtGui.QHeaderView.ResizeToContents)
        self.matchs_grid.header().setResizeMode(4,QtGui.QHeaderView.ResizeToContents)
        self.matchs_grid.header().setResizeMode(5,QtGui.QHeaderView.ResizeToContents)
        self.matchs_grid.header().setResizeMode(6,QtGui.QHeaderView.ResizeToContents)
        self.matchs_grid.header().setResizeMode(7,QtGui.QHeaderView.ResizeToContents)
        self.matchs_grid.header().setResizeMode(8,QtGui.QHeaderView.ResizeToContents)
        self.matchs_grid.header().setResizeMode(9,QtGui.QHeaderView.ResizeToContents)
        self.matchs_grid.header().setResizeMode(10,QtGui.QHeaderView.ResizeToContents)

        self.matchs_grid.setColumnHidden(11,True)

        mainLayout = QtGui.QVBoxLayout()
        mainLayout.addWidget(headerWidget)
        mainLayout.addWidget(self.matchs_grid)
        mainLayout.setMargin(5)
        self.setLayout(mainLayout)

    def on_match_clicked(self,state):
        self.db_query()

    def on_310btn_clicked(self):
        self.db_query()

    def db_query(self):
        if not self.query_factor:
            return
        if not self.odds_model.text():
            return
        wheres = list()
        wheres.append("Factor = '%s'" % self.query_factor)
        if self.win_radiobox.isChecked():
            wheres.append("Result = 3")
        elif self.draw_radiobox.isChecked():
            wheres.append("Result = 1")
        elif self.lost_radiobox.isChecked():
            wheres.append("Result = 0")
        p = "Odds_WL like '%%%s%%'"
        if self.before_match_checkbox.isChecked() and not self.after_match_checkbox.isChecked():
            p = "Odds_WL like '%s%%'"
        elif not self.before_match_checkbox.isChecked() and self.after_match_checkbox.isChecked():
            p = "Odds_WL like '%%%s'"
        word_ = p % self.odds_model.text()
        wheres.append(word_)
        if len(wheres)>0:
            where_str = " AND ".join(wheres)
            sql = "SELECT * FROM Match WHERE %s LIMIT 100" % where_str
            cnn = connect_db()
            cnn.row_factory = sqlite3.Row
            cur = cnn.cursor()
            ds = []
            cur.execute(sql)
            for row in cur:
                if row["Result"]==-1:
                    continue
                ds.append(row)
            self.data_grid_model = MatchsTreeModel(ds)
            self.matchs_grid.setModel(self.data_grid_model)
        pass

    def on_execute_btn_clicked(self):
        self.db_query()

#For Matchs TreeView
class MatchsTreeItem(object):
    def __init__(self, data, parent=None):
        self.parentItem = parent
        self.itemData = data
        self.childItems = []

    def appendChild(self, item):
        self.childItems.append(item)

    def child(self, row):
        return self.childItems[row]

    def childCount(self):
        return len(self.childItems)

    def columnCount(self):
        return len(self.itemData)

    def data(self, column):
        try:
            if column == 0:
                return self.itemData["Result"]
            elif column == 1:
                return self.itemData["TeamNames"]
            elif column == 2:
                return self.itemData["Last10TotalTextStyle"]
            elif column == 3:
                return self.itemData["Last10TextStyle"]
            elif column == 4:
                return self.itemData["Last4TextStyle"]
            elif column == 5:
                return self.itemData["Last4BattleHistoryDesc"]
            elif column == 6:
                return self.itemData["Odds_WL"]
            elif column == 7:
                return self.itemData["Odds_LB"]
            elif column == 8:
                return self.itemData['Odds_AM']
            elif column == 9:
                return self.itemData["Odds_365"]
            elif column == 10:
                return self.itemData["EventName"]
            elif column == 11:
                return self.itemData["BaseFaceUrl"]
            return ""
        except IndexError:
            return None

    def parent(self):
        return self.parentItem

    def row(self):
        if self.parentItem:
            return self.parentItem.childItems.index(self)
        return 0

class MatchsTreeModel(QtCore.QAbstractItemModel):
    def __init__(self, data, parent=None):
        super(MatchsTreeModel, self).__init__(parent)
        titles = dict()
        titles["Result"]="赛果"
        titles["TeamNames"]="对阵球队"
        titles["Last10TotalTextStyle"]="近10场(综合)"
        titles["Last10TextStyle"]="近10场(主客)"
        titles["Last4TextStyle"]="近4场(状态)"
        titles["Last4BattleHistoryDesc"]="近4场(战绩)"
        titles["Odds_WL"] = "威廉"
        titles["Odds_AM"] = "澳门"
        titles["Odds_LB"]="立博"
        titles["Odds_365"]="贝塔"
        titles["EventName"]="赛事"
        titles["BaseFaceUrl"]=""
        self.rootItem = MatchsTreeItem(titles)

        self.setupModelData(data, self.rootItem)

    def columnCount(self, parent):
        if parent.isValid():
            return parent.internalPointer().columnCount()
        else:
            return self.rootItem.columnCount()

    def data(self, index, role):

        if not index.isValid():
            return None

        if role == QtCore.Qt.DisplayRole:
            item = index.internalPointer()
            return item.data(index.column())

        if role == QtCore.Qt.BackgroundRole:
            if 6 == index.column():
                return QtGui.QColor("#FFCCCC")
            if 7 == index.column():
                return QtGui.QColor("#99CCCC")
            if 8 == index.column():
                return QtGui.QColor("#FFCC99")
            if 9 == index.column():
                return QtGui.QColor("#FFCCCC")
            pass

        return None

    def flags(self, index):
        if not index.isValid():
            return QtCore.Qt.NoItemFlags

        return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable

    def headerData(self, section, orientation, role):
        if orientation == QtCore.Qt.Horizontal and role == QtCore.Qt.DisplayRole:
            return self.rootItem.data(section)
        return None

    def index(self, row, column, parent):
        if not self.hasIndex(row, column, parent):
            return QtCore.QModelIndex()

        if not parent.isValid():
            parentItem = self.rootItem
        else:
            parentItem = parent.internalPointer()

        childItem = parentItem.child(row)
        if childItem:
            return self.createIndex(row, column, childItem)
        else:
            return QtCore.QModelIndex()

    def parent(self, index):
        if not index.isValid():
            return QtCore.QModelIndex()

        childItem = index.internalPointer()
        parentItem = childItem.parent()

        if not parentItem:
            return QtCore.QModelIndex()

        if parentItem == self.rootItem:
            return QtCore.QModelIndex()

        return self.createIndex(parentItem.row(), 0, parentItem)

    def rowCount(self, parent):
        if parent.column() > 0:
            return 0

        if not parent.isValid():
            parentItem = self.rootItem
        else:
            parentItem = parent.internalPointer()

        return parentItem.childCount()

    def setupModelData(self, matchs, parent):
        for match in matchs:
            first_child = MatchsTreeItem(match)
            parent.appendChild(first_child)
        pass


if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    window = QueryUI()
    window.show()
    sys.exit(app.exec_())
