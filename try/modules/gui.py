import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.automation import AutoClicker
from modules.report_generator import ReportGenerator

from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QPushButton, QTextEdit, QLabel, 
                            QProgressBar, QMessageBox, QListWidget, QListWidgetItem,
                            QGroupBox, QSplitter, QCheckBox)
from PyQt5.QtCore import QThread, pyqtSignal, Qt
from PyQt5.QtGui import QFont, QIcon

class WorkerThread(QThread):
    log_signal = pyqtSignal(str)
    progress_signal = pyqtSignal(int)
    task_signal = pyqtSignal(list)
    finished_signal = pyqtSignal(bool)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.auto_clicker = AutoClicker()
        self.report_generator = ReportGenerator()
    
    def run(self):
        try:
            self.auto_clicker.set_log_callback(self.log_signal.emit)
            
            self.log_signal.emit("正在初始化浏览器...")
            if not self.auto_clicker.init_driver():
                self.log_signal.emit("浏览器初始化失败")
                self.finished_signal.emit(False)
                return
            
            self.log_signal.emit("浏览器初始化成功")
            self.log_signal.emit("正在打开学习页面...")
            
            if not self.auto_clicker.open_url():
                self.log_signal.emit("页面打开失败，请检查网络连接")
                self.auto_clicker.close()
                self.finished_signal.emit(False)
                return
            
            self.log_signal.emit("页面加载成功")
            
            task_count = 0
            max_tasks = 20
            
            while task_count < max_tasks:
                self.log_signal.emit("\n=== 开始新一轮任务检测 ===")
                
                self.auto_clicker.expand_all_chapters()
                tasks = self.auto_clicker.find_unfinished_tasks()
                
                if not tasks:
                    self.log_signal.emit("未发现未完成任务，结束执行")
                    break
                
                task = tasks[0]
                self.log_signal.emit(f"发现未完成任务: {task['title']}")
                
                if self.auto_clicker.execute_task(task):
                    task_count += 1
                    self.log_signal.emit(f"\n任务 {task_count} 执行完成")
                    
                    self.log_signal.emit("正在生成实验报告...")
                    report_path = self.report_generator.create_report(task)
                    if report_path:
                        self.log_signal.emit(f"实验报告已生成: {report_path}")
                    else:
                        self.log_signal.emit("实验报告生成失败")
                else:
                    self.log_signal.emit(f"任务执行失败")
                
                self.log_signal.emit("等待页面跳转...")
                time.sleep(5)
                
                self.auto_clicker.refresh_page()
            
            self.auto_clicker.close()
            self.log_signal.emit(f"\n=== 所有任务执行完成，共完成 {task_count} 个任务 ===")
            self.finished_signal.emit(True)
            
        except Exception as e:
            self.log_signal.emit(f"运行过程中发生错误: {str(e)}")
            import traceback
            traceback.print_exc()
            if self.auto_clicker.driver:
                self.auto_clicker.close()
            self.finished_signal.emit(False)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("学习任务自动完成工具")
        self.setGeometry(100, 100, 900, 600)
        
        self.worker_thread = None
        self.report_generator = ReportGenerator()
        
        self.init_ui()
    
    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QHBoxLayout(central_widget)
        splitter = QSplitter(Qt.Horizontal)
        main_layout.addWidget(splitter)
        
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        
        title_label = QLabel("学习任务自动完成工具")
        title_font = QFont("Microsoft YaHei", 16, QFont.Bold)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignCenter)
        left_layout.addWidget(title_label)
        
        url_label = QLabel("目标地址:")
        url_font = QFont("Microsoft YaHei", 10)
        url_label.setFont(url_font)
        left_layout.addWidget(url_label)
        
        url_value = QLabel("https://spc.gsupl.edu.cn/student/studentCourse/tpl?...")
        url_value.setFont(url_font)
        url_value.setWordWrap(True)
        left_layout.addWidget(url_value)
        
        start_button = QPushButton("一键运行")
        start_button.setFont(QFont("Microsoft YaHei", 12))
        start_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border-radius: 8px;
                padding: 15px 30px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:disabled {
                background-color: #cccccc;
            }
        """)
        start_button.clicked.connect(self.start_automation)
        left_layout.addWidget(start_button)
        self.start_button = start_button
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid #bbb;
                border-radius: 5px;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: #4CAF50;
            }
        """)
        left_layout.addWidget(self.progress_bar)
        
        task_group = QGroupBox("任务列表")
        task_layout = QVBoxLayout(task_group)
        
        self.task_list = QListWidget()
        task_layout.addWidget(self.task_list)
        left_layout.addWidget(task_group)
        
        report_group = QGroupBox("生成的报告")
        report_layout = QVBoxLayout(report_group)
        
        self.report_list = QListWidget()
        report_layout.addWidget(self.report_list)
        left_layout.addWidget(report_group)
        
        refresh_button = QPushButton("刷新报告列表")
        refresh_button.clicked.connect(self.refresh_reports)
        left_layout.addWidget(refresh_button)
        
        splitter.addWidget(left_panel)
        splitter.setSizes([300, 600])
        
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        
        log_group = QGroupBox("运行日志")
        log_layout = QVBoxLayout(log_group)
        
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setFont(QFont("Consolas", 10))
        self.log_text.setStyleSheet("background-color: #f5f5f5;")
        log_layout.addWidget(self.log_text)
        
        right_layout.addWidget(log_group)
        splitter.addWidget(right_panel)
        
        self.refresh_reports()
    
    def log(self, message):
        self.log_text.append(message)
        self.log_text.verticalScrollBar().setValue(self.log_text.verticalScrollBar().maximum())
    
    def start_automation(self):
        if self.worker_thread and self.worker_thread.isRunning():
            QMessageBox.warning(self, "提示", "任务正在运行中，请等待完成")
            return
        
        self.start_button.setEnabled(False)
        self.progress_bar.setValue(0)
        self.log_text.clear()
        self.task_list.clear()
        
        self.log("=== 开始执行自动化任务 ===")
        self.log("步骤说明：")
        self.log("1. 展开所有章节")
        self.log("2. 查找未完成任务（继续实验按钮）")
        self.log("3. 点击继续实验，跳转虚拟机")
        self.log("4. 读取详细参考说明")
        self.log("5. 每3秒截图一次")
        self.log("6. 点击保存环境按钮")
        self.log("7. 生成实验报告（含截图和说明）")
        self.log("8. 刷新页面，重复以上步骤")
        
        self.worker_thread = WorkerThread()
        self.worker_thread.log_signal.connect(self.log)
        self.worker_thread.progress_signal.connect(self.update_progress)
        self.worker_thread.task_signal.connect(self.update_task_list)
        self.worker_thread.finished_signal.connect(self.on_finished)
        self.worker_thread.start()
    
    def update_progress(self, value):
        self.progress_bar.setValue(value)
    
    def update_task_list(self, tasks):
        self.task_list.clear()
        for task in tasks:
            status_icon = "✓" if task['status'] == '已完成' else "○"
            item = QListWidgetItem(f"{status_icon} {task['title']}")
            if task['status'] == '已完成':
                item.setForeground(Qt.gray)
            self.task_list.addItem(item)
    
    def on_finished(self, success):
        self.start_button.setEnabled(True)
        self.progress_bar.setValue(100)
        
        if success:
            self.log("=== 任务执行完成 ===")
            QMessageBox.information(self, "完成", "自动化任务执行完成！")
        else:
            self.log("=== 任务执行失败 ===")
            QMessageBox.warning(self, "失败", "自动化任务执行失败，请查看日志")
        
        self.refresh_reports()
    
    def refresh_reports(self):
        self.report_list.clear()
        reports = self.report_generator.get_report_list()
        for report in reports:
            item = QListWidgetItem(report['name'])
            self.report_list.addItem(item)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())