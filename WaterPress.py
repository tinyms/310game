'''
Created on 2013-2-28

@author: tinyms
'''
import images_rc
import os
from except_filter import ExceptFilter
from odds_statistics import Odds_Statistics
from utils import send_msg,md5
from utils import MessageService
from utils import mkdirs,get_date_text
from utils import get_last_access_urls,create_history_db
from utils import cache_last_access_urls
from utils import url_with_params
from utils import MatchsTreeModel,get_cache_web_file_name
from parse import HtmlParseThread,DownloadHistoryMatch
from PyQt5 import QtCore,QtGui,QtWidgets,QtWebKitWidgets
from postgres import wl_lb_match_history_cache

class CustomTreeView(QtWidgets.QTreeView):
    #signal_row_clicked = QtCore.pyqtSignal(int)
    def __init__(self):
        QtWidgets.QTreeView.__init__(self)

    # def keyReleaseEvent(self,evt):
    #     if evt.key()==QtCore.Qt.Key_Delete:
    #         if not self.currentIndex().isValid():
    #             return
    #         self.model().removeRow(self.currentIndex().row())

class CustomComboBox(QtWidgets.QComboBox):
    def __init__(self):
        QtWidgets.QComboBox.__init__(self)
    def keyReleaseEvent(self,evt):
        if evt.key()==QtCore.Qt.Key_Enter or evt.key()==QtCore.Qt.Key_Return:
            send_msg("trigger_matchs_analyze")
        
class Workbench(QtWidgets.QWidget):
    MATCHS = []
    message_loop_task = MessageService()
    def __init__(self):
        super(Workbench,self).__init__()

        self.resize(800,600)
        self.setWindowIcon(QtGui.QIcon(':/images/football.png'))
        self.setWindowTitle("WaterPress 4.2 - http://t.qq.com/tinyms")
        self.current_matchgrid_selected_rowindex = -1

        headerWidget = QtWidgets.QWidget()
        headerLayout = QtWidgets.QHBoxLayout()
        headerWidget.setLayout(headerLayout)

        self.select_all_checkbox = QtWidgets.QCheckBox("过滤")
        self.select_all_checkbox.stateChanged.connect(self.on_select_all_310_clicked)
        self.example_checkbox = QtWidgets.QCheckBox("练习")
        self.rq_checkbox = QtWidgets.QCheckBox("让球")
        self.rq_checkbox.setChecked(True)
        self.rq_checkbox.stateChanged.connect(self.on_rq_clicked)
        self.win_checkbox = QtWidgets.QCheckBox("胜")
        self.draw_checkbox = QtWidgets.QCheckBox("平")
        self.lost_checkbox = QtWidgets.QCheckBox("负")
        self.win_checkbox.stateChanged.connect(self.win_draw_lost_checkbox_clicked)
        self.draw_checkbox.stateChanged.connect(self.win_draw_lost_checkbox_clicked)
        self.lost_checkbox.stateChanged.connect(self.win_draw_lost_checkbox_clicked)
        self.urlComboBox = CustomComboBox()
        self.urlComboBox.setEditable(True)
        self.example_checkbox.stateChanged.connect(self.exampleCheckBoxEvent)
        self.execute_button = QtWidgets.QPushButton("赛事分析")#Execute
        self.execute_button.clicked.connect(self.on_execute_btn_clicked)
        self.clear_button = QtWidgets.QPushButton("刷新变赔")
        self.clear_button.clicked.connect(self.on_clear_history_data_clicked)

        headerLayout.addWidget(self.select_all_checkbox)
        headerLayout.addWidget(self.win_checkbox)
        headerLayout.addWidget(self.draw_checkbox)
        headerLayout.addWidget(self.lost_checkbox)
        headerLayout.addWidget(self.example_checkbox)
        headerLayout.addWidget(self.rq_checkbox)
        headerLayout.addWidget(self.urlComboBox,True)
        headerLayout.addWidget(self.execute_button)
        headerLayout.addWidget(self.clear_button)
        
        #Matchs TreeView
        self.matchs_grid = CustomTreeView()
        self.matchs_grid.clicked.connect(self.row_clicked_callback)
        self.data_grid_model = MatchsTreeModel([])
        self.matchs_grid.setModel(self.data_grid_model)
        self.matchs_grid.setRootIsDecorated(False)
        self.matchs_grid.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        self.matchs_grid.setAlternatingRowColors(True)
        self.matchs_grid.header().setStretchLastSection(False)
        self.matchs_grid.header().setSectionResizeMode(0,QtWidgets.QHeaderView.ResizeToContents)
        self.matchs_grid.header().setSectionResizeMode(1,QtWidgets.QHeaderView.ResizeToContents)
        self.matchs_grid.header().setSectionResizeMode(2,QtWidgets.QHeaderView.ResizeToContents)
        self.matchs_grid.header().setSectionResizeMode(3,QtWidgets.QHeaderView.ResizeToContents)
        self.matchs_grid.header().setSectionResizeMode(4,QtWidgets.QHeaderView.ResizeToContents)
        self.matchs_grid.header().setSectionResizeMode(5,QtWidgets.QHeaderView.Stretch)
        self.matchs_grid.header().setSectionResizeMode(6,QtWidgets.QHeaderView.ResizeToContents)
        self.matchs_grid.header().setSectionResizeMode(7,QtWidgets.QHeaderView.ResizeToContents)
        self.matchs_grid.header().setSectionResizeMode(8,QtWidgets.QHeaderView.ResizeToContents)
        
        #Message Bar
        self.msg_bar = QtWidgets.QLabel("就绪.")
        #history query grid panel
        self.first_odds_web_browser = QtWebKitWidgets.QWebView()
        self.web_browser_for_odds_change = QtWebKitWidgets.QWebView()
        self.web_browser_for_base_face = QtWebKitWidgets.QWebView()
        self.tab_panel = QtWidgets.QTabWidget()
        self.tab_panel.setFixedHeight(230)
        self.tab_panel.addTab(self.first_odds_web_browser,"初赔")
        self.tab_panel.addTab(self.web_browser_for_odds_change,"变赔")
        self.tab_panel.addTab(self.web_browser_for_base_face,"基本面")
        # self.tab_panel.addTab(self.query_history,"历史")
        
        mainLayout = QtWidgets.QVBoxLayout()
        mainLayout.addWidget(headerWidget)
        mainLayout.addWidget(self.matchs_grid)
        mainLayout.addWidget(self.tab_panel)
        mainLayout.addWidget(self.msg_bar)
        self.setLayout(mainLayout)
        
        #Init
        self.download_history_thread = DownloadHistoryMatch()
        self.message_loop_task.signal_message_arrival.connect(self.message_service_callback)
    
    def closeEvent(self,evt):
        send_msg("close_message_loop")
        if self.message_loop_task:
            self.message_loop_task.exit()
        
    def showEvent(self,evt):
        self.first_run = True
        mkdirs("data")
        create_history_db()

        self.message_loop_task.start()
        self.urlComboBox.addItem("http://zc.trade.500.com/sfc/index.php")
        urls = get_last_access_urls()
        for url in urls:
            self.urlComboBox.addItem(url)

    def webbrowserLinkEvent(self,url):
        print(url)

    def exampleCheckBoxEvent(self,state):
        if state:
            self.matchs_grid.setColumnHidden(1,True)
            MatchsTreeModel.HIDE_SCORE = True
        else:
            self.matchs_grid.setColumnHidden(1,False)
            MatchsTreeModel.HIDE_SCORE = False
        pass

    def on_select_all_310_clicked(self,state):
        filter_ = ExceptFilter()
        self.analyze_thread.dataset = filter_.check(self.analyze_thread.dataset)
        self.data_grid_model = MatchsTreeModel(self.analyze_thread.dataset)
        self.matchs_grid.setModel(self.data_grid_model)
        # if state:
        #     for m in self.analyze_thread.dataset:
        #         if not m["actual_result"]:
        #             m["actual_result"] = "310"
        #     self.data_grid_model = MatchsTreeModel(self.analyze_thread.dataset)
        #     self.matchs_grid.setModel(self.data_grid_model)
        # pass

    def win_draw_lost_checkbox_clicked(self,state):
        if self.current_matchgrid_selected_rowindex != -1:
            arr = []
            if self.win_checkbox.isChecked():
                arr.append("3")
            if self.draw_checkbox.isChecked():
                arr.append("1")
            if self.lost_checkbox.isChecked():
                arr.append("0")
            r = "".join(arr)
            if len(self.analyze_thread.dataset)>=self.current_matchgrid_selected_rowindex+1:
                self.analyze_thread.dataset[self.current_matchgrid_selected_rowindex]["actual_result"]=r
                self.data_grid_model = MatchsTreeModel(self.analyze_thread.dataset)
                self.matchs_grid.setModel(self.data_grid_model)
                sel = self.matchs_grid.selectionModel()
                sel.select(QtCore.QItemSelection(self.data_grid_model.index(self.current_matchgrid_selected_rowindex,0,QtCore.QModelIndex()),
                                                self.data_grid_model.index(self.current_matchgrid_selected_rowindex,self.data_grid_model.columnCount(QtCore.QModelIndex())-1,QtCore.QModelIndex())),
                           QtCore.QItemSelectionModel.Select)

    def trigger_matchs_analyze(self):
        url = self.urlComboBox.currentText()
        purl = str(url).strip()
        if purl.find("@history")!=-1:
            start_date = get_date_text(purl)
            if start_date!="":
                DownloadHistoryMatch.START_DATE = start_date
            self.execute_button.setEnabled(False)
            self.urlComboBox.setEnabled(False)
            self.download_history_thread.start()
            return
        if purl.find("500.com/")==-1:
            return
        cache_last_access_urls(purl)
        # if url_with_params(url):
        #     file_path = "data/"+md5(url)
        #     if os.path.exists(file_path):
        #         # dataset = read_file(file_path)
        #         # self.data_grid_model = MatchsTreeModel(json.loads(dataset))
        #         # self.matchs_grid.setModel(self.data_grid_model)
        #         return
        self.clear_button.setEnabled(False)
        self.urlComboBox.setEnabled(False)
        self.execute_button.setEnabled(False)
        self.analyze_matchs()

    def on_rq_clicked(self,state):
        if state:
            HtmlParseThread.RQ = True
        else:
            HtmlParseThread.RQ = False
        pass

    def on_execute_btn_clicked(self):
        self.trigger_matchs_analyze()

    def on_clear_history_data_clicked(self):
        if len(self.analyze_thread.dataset)>0:
            self.clear_button.setEnabled(False)
            for  row in self.analyze_thread.dataset:
                f_name = get_cache_web_file_name(row["odds_url"])
                os.remove(f_name)
            pass
            self.trigger_matchs_analyze()
        # import shutil
        # if os.path.exists("cache_web_pages/"):
        #     self.clear_button.setEnabled(False)
        #     shutil.rmtree("cache_web_pages/")
        #     self.clear_button.setEnabled(True)

    def row_clicked_callback(self,rowIndexer):
        row_id = rowIndexer.row()
        self.current_matchgrid_selected_rowindex = -1
        #Example
        self.win_checkbox.setChecked(False)
        self.draw_checkbox.setChecked(False)
        self.lost_checkbox.setChecked(False)

        result_index = self.data_grid_model.index(row_id,1,QtCore.QModelIndex())
        result_value = self.data_grid_model.data(result_index,QtCore.Qt.DisplayRole)
        if result_value:
            words = [i for i in result_value]
            if words.count("3")>0:
                self.win_checkbox.setChecked(True)
            if words.count("1")>0:
                self.draw_checkbox.setChecked(True)
            if words.count("0")>0:
                self.lost_checkbox.setChecked(True)
        self.current_matchgrid_selected_rowindex = row_id
        #first odds
        if len(self.analyze_thread.dataset)>row_id:
            row = self.analyze_thread.dataset[row_id]
            stats = Odds_Statistics()
            wl_stats = stats.single_company(row["Odds_WL"],row["Odds_WL_Change"])
            am_stats = stats.single_company(row["Odds_AM"],row["Odds_AM_Change"])
            lb_stats = stats.single_company(row["Odds_LB"],row["Odds_LB_Change"])
            beta_stats = stats.single_company(row["Odds_365"],row["Odds_365_Change"])
            ysb_stats = stats.single_company(row["Odds_YSB"],row["Odds_YSB_Change"])

            html = "<!DOCTYPE html>"
            html += "<html><head><meta charset='gb2312'/></head><body>"
            html += "<div style='color:#000000;font-size:14px;font-family:simsun,tahoma;'>"
            html += "<div>"
            html += "近10场: "+row["last_10_text_style"]+"<br/>"
            html += "近06场: "+row["last_6_text_style"]+"<br/>"
            html += "近04场: "+row["last_4_text_style"]+"<br/>"
            html += "</div>"
            html += "<div style='margin-top:10px;'>"
            html += "实力: <font color='red'>"+row["asia_avg_balls"]+"</font>" + " 状态: <font color='#336633'>"+row["last_4_status_text_style"]+"</font><br/>"
            html += "</div>"
            html += "<div style='margin-top:5px;'>";
            html += "威廉: "+row["Odds_WL"]+" ~ "+row["Odds_WL_Change"]+" ~ "+wl_stats["odds_diff"]+" ~ "+wl_stats["model_diff"]+"<br/>"
            html += "立博: "+row["Odds_LB"]+" ~ "+row["Odds_LB_Change"]+" ~ "+lb_stats["odds_diff"]+" ~ "+lb_stats["model_diff"]+"<br/><br/>"
            html += "贝塔: "+row["Odds_365"]+" ~ "+row["Odds_365_Change"]+" ~ "+beta_stats["odds_diff"]+" ~ "+beta_stats["model_diff"]+"<br/>"
            html += "澳门: "+row["Odds_AM"]+" ~ "+row["Odds_AM_Change"]+" ~ "+am_stats["odds_diff"]+" ~ "+am_stats["model_diff"]+"<br/>"
            html += "易博: "+row["Odds_YSB"]+" ~ "+row["Odds_YSB_Change"]+" ~ "+ysb_stats["odds_diff"]+" ~ "+ysb_stats["model_diff"]+"<br/>"

            html += "</div>"
            html += "</div></body></html>"
            self.first_odds_web_browser.setHtml(html)
            self.web_browser_for_odds_change.load(QtCore.QUrl(row["odds_url"]+"#datatb"))
            self.web_browser_for_base_face.load(QtCore.QUrl(row["base_face_url"]+"#team_zhanji2_1"))

    def message_service_callback(self,msg):
        if msg=="refresh_match_grid":
            self.data_grid_model = MatchsTreeModel(self.analyze_thread.dataset)
            self.matchs_grid.setModel(self.data_grid_model)
            if url_with_params(self.urlComboBox.currentText()):
                file_path = "data/"+md5(self.urlComboBox.currentText())
                if not os.path.exists(file_path):
                    # for row in self.analyze_thread.dataset:
                    #     row.pop("formula_total")
                    #     row.pop("formula_last10")
                    #     row.pop("formula_last4")
                    # write_file(file_path,json.dumps(self.analyze_thread.dataset))
                    pass
            self.execute_button.setEnabled(True)
            self.clear_button.setEnabled(True)
            self.urlComboBox.setEnabled(True)
        elif msg == "cache_history_data":
            #batch_save_history_matchs(self.download_history_thread.dataset)
            wl_lb_match_history_cache(self.download_history_thread.dataset)
            pass
        elif msg == "completed":
            self.execute_button.setEnabled(True)
            self.urlComboBox.setEnabled(True)
        elif msg == "trigger_matchs_analyze":
            self.trigger_matchs_analyze()
        else:
            self.msg_bar.setText(msg)
    
    def analyze_matchs(self):
        self.analyze_thread = HtmlParseThread()
        self.analyze_thread.targetUrl = self.urlComboBox.currentText()
        self.analyze_thread.start()
