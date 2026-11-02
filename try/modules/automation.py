import time
import configparser
import os
import sys
import base64

try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.chrome.service import Service as ChromeService
    from selenium.webdriver.edge.service import Service as EdgeService
    from selenium.webdriver.common.action_chains import ActionChains
    from selenium.webdriver.common.keys import Keys
    from webdriver_manager.chrome import ChromeDriverManager
    from webdriver_manager.microsoft import EdgeChromiumDriverManager
    from webdriver_manager.core.os_manager import ChromeType
    from bs4 import BeautifulSoup
except ImportError as e:
    print(f"导入模块失败: {e}")
    sys.exit(1)

class AutoClicker:
    def __init__(self):
        self.config = configparser.ConfigParser()
        self.config.read('config.ini')
        self.url = self.config['DEFAULT']['url']
        self.timeout = int(self.config['DEFAULT']['timeout'])
        self.browser = self.config['DEFAULT'].get('browser', 'edge').lower()
        self.report_save_path = self.config['DEFAULT'].get('report_save_path', './reports')
        self.driver = None
        self.tasks = []
        self.log_callback = None
        self.screenshots = []
        self.current_task_info = {}
        
    def set_log_callback(self, callback):
        self.log_callback = callback
        
    def log(self, message):
        timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
        full_message = f"[{timestamp}] {message}"
        print(full_message)
        if self.log_callback:
            self.log_callback(message)
    
    def check_edge_installed(self):
        edge_paths = [
            "C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe",
            "C:\\Program Files\\Microsoft\\Edge\\Application\\msedge.exe",
            "C:\\Users\\%USERNAME%\\AppData\\Local\\Microsoft\\Edge\\Application\\msedge.exe"
        ]
        for path in edge_paths:
            expanded_path = os.path.expandvars(path)
            if os.path.exists(expanded_path):
                self.log(f"找到 Edge 浏览器: {expanded_path}")
                return True
        self.log("警告：未找到 Edge 浏览器")
        return False
    
    def init_driver(self):
        if self.browser == 'edge':
            return self.init_edge_driver()
        else:
            return self.init_chrome_driver()
    
    def init_edge_driver(self):
        if not self.check_edge_installed():
            return False
        
        edge_options = webdriver.EdgeOptions()
        edge_options.add_argument("--start-maximized")
        edge_options.add_argument("--disable-infobars")
        edge_options.add_argument("--disable-extensions")
        edge_options.add_argument("--disable-popup-blocking")
        edge_options.add_argument("--ignore-certificate-errors")
        edge_options.add_argument("--allow-running-insecure-content")
        
        try:
            self.log("正在尝试使用 webdriver-manager 安装 EdgeDriver...")
            driver_path = EdgeChromiumDriverManager().install()
            self.log(f"EdgeDriver 安装路径: {driver_path}")
            
            service = EdgeService(driver_path)
            self.driver = webdriver.Edge(service=service, options=edge_options)
            self.driver.implicitly_wait(self.timeout)
            self.log("Edge 浏览器初始化成功")
            return True
        except Exception as e:
            self.log(f"浏览器初始化失败: {str(e)}")
            return False
    
    def open_url(self):
        try:
            self.log(f"正在打开URL: {self.url}")
            self.driver.get(self.url)
            self.log("页面加载成功")
            time.sleep(5)
            return True
        except Exception as e:
            self.log(f"页面加载失败: {str(e)}")
            return False
    
    def expand_all_chapters(self):
        self.log("=" * 50)
        self.log("开始展开所有章节")
        self.log("=" * 50)
        
        all_clickable_elements = []
        
        expand_selectors = [
            "//button[contains(text(), '展开')]",
            "//button[contains(text(), '展开章节')]",
            "//button[contains(text(), '展开全部')]",
            "//a[contains(text(), '展开')]",
            "//div[contains(@class, 'expand')]",
            "//div[contains(@class, 'toggle')]",
            "//span[contains(@class, 'expand')]",
            "//span[contains(@class, 'toggle')]",
            "//i[contains(@class, 'expand') or contains(@class, 'toggle')]",
            "//*[@data-toggle='expand']",
            "//*[@onclick and contains(text(), '展开')]",
            "//li[@class='chapter']//button",
            "//div[@class='chapter-header']//button",
            "//div[@class='section-header']//button",
            "//button[contains(@class, 'icon-expand')]",
            "//button[contains(@class, 'caret')]"
        ]
        
        found_elements = []
        
        for selector in expand_selectors:
            try:
                elements = self.driver.find_elements(By.XPATH, selector)
                if elements:
                    found_elements.extend([(selector, elem) for elem in elements])
                    self.log(f"使用选择器 '{selector}' 找到 {len(elements)} 个元素")
            except Exception as e:
                self.log(f"选择器 '{selector}' 查询失败: {str(e)}")
        
        self.log(f"共找到 {len(found_elements)} 个可能的展开元素")
        
        clicked_count = 0
        skipped_count = 0
        
        for selector, elem in found_elements:
            try:
                if not elem.is_displayed():
                    skipped_count += 1
                    continue
                
                text = elem.text.strip() if elem.text else "无文本"
                class_name = elem.get_attribute('class') if elem.get_attribute('class') else "无class"
                
                self.log(f"准备点击元素 - 选择器: {selector}, 文本: '{text}', class: {class_name}")
                
                self.driver.execute_script("arguments[0].scrollIntoView(true);", elem)
                time.sleep(0.3)
                
                try:
                    elem.click()
                except:
                    self.driver.execute_script("arguments[0].click();", elem)
                
                clicked_count += 1
                self.log(f"✓ 成功点击第 {clicked_count} 个展开元素")
                time.sleep(0.5)
                
            except Exception as e:
                skipped_count += 1
                self.log(f"✗ 点击元素失败: {str(e)}")
        
        self.log("=" * 50)
        self.log(f"章节展开完成 - 成功点击: {clicked_count} 个, 跳过: {skipped_count} 个")
        self.log("=" * 50)
        
        time.sleep(3)
        
        return clicked_count
    
    def find_unfinished_tasks(self):
        self.log("=" * 50)
        self.log("开始查找未完成任务")
        self.log("=" * 50)
        
        unfinished_tasks = []
        
        continue_selectors = [
            "//button[contains(text(), '继续实验')]",
            "//button[contains(text(), '开始实验')]",
            "//button[contains(text(), '继续学习')]",
            "//button[contains(text(), '开始学习')]",
            "//a[contains(text(), '继续实验')]",
            "//a[contains(text(), '开始实验')]",
            "//div[contains(text(), '继续实验')]",
            "//div[contains(text(), '开始实验')]",
            "//*[@class='continue-btn']",
            "//*[@class='start-btn']",
            "//*[@class='experiment-btn']"
        ]
        
        found_buttons = []
        
        for selector in continue_selectors:
            try:
                buttons = self.driver.find_elements(By.XPATH, selector)
                if buttons:
                    found_buttons.extend([(selector, btn) for btn in buttons])
                    self.log(f"使用选择器 '{selector}' 找到 {len(buttons)} 个按钮")
            except Exception as e:
                self.log(f"选择器 '{selector}' 查询失败: {str(e)}")
        
        self.log(f"共找到 {len(found_buttons)} 个可能的任务按钮")
        
        for idx, (selector, btn) in enumerate(found_buttons):
            try:
                if not btn.is_displayed():
                    self.log(f"跳过不可见按钮 {idx + 1}")
                    continue
                
                btn_text = btn.text.strip() if btn.text else "无文本"
                self.log(f"分析按钮 {idx + 1}: '{btn_text}'")
                
                try:
                    parent = btn.find_element(By.XPATH, "..")
                    title_elems = parent.find_elements(By.XPATH, ".//*[self::h3 or self::h4 or self::div[@class='title'] or self::span[@class='title']]")
                    title = title_elems[0].text.strip() if title_elems else f"任务 {idx + 1}"
                except:
                    title = f"任务 {idx + 1}"
                
                task_info = {
                    'index': idx + 1,
                    'title': title,
                    'button': btn,
                    'button_text': btn_text,
                    'status': '未完成',
                    'selector': selector
                }
                unfinished_tasks.append(task_info)
                self.log(f"✓ 发现未完成任务 {idx + 1}: {title}")
                
            except Exception as e:
                self.log(f"✗ 分析按钮失败: {str(e)}")
        
        self.log("=" * 50)
        self.log(f"任务查找完成 - 共发现 {len(unfinished_tasks)} 个未完成任务")
        self.log("=" * 50)
        
        self.tasks = unfinished_tasks
        return unfinished_tasks
    
    def click_continue_experiment(self, task_info):
        self.log(f"准备执行任务: {task_info['title']}")
        self.log(f"按钮文本: {task_info.get('button_text', '未知')}")
        self.log(f"使用选择器: {task_info.get('selector', '未知')}")
        
        try:
            btn = task_info['button']
            
            if not btn.is_displayed():
                self.log("按钮不可见，尝试滚动到按钮位置")
                self.driver.execute_script("arguments[0].scrollIntoView(true);", btn)
                time.sleep(1)
            
            self.log("正在点击按钮...")
            
            try:
                btn.click()
            except Exception as e1:
                self.log(f"直接点击失败，尝试使用JavaScript: {str(e1)}")
                self.driver.execute_script("arguments[0].click();", btn)
            
            self.log("✓ 按钮点击成功")
            time.sleep(5)
            return True
            
        except Exception as e:
            self.log(f"✗ 点击失败: {str(e)}")
            return False
    
    def get_detailed_reference(self):
        self.log("=" * 50)
        self.log("开始读取详细参考内容")
        self.log("=" * 50)
        
        reference_content = ""
        
        reference_selectors = [
            "//div[contains(@class, 'reference')]",
            "//div[contains(@class, 'detail')]",
            "//div[contains(@class, 'guide')]",
            "//div[contains(@class, 'instructions')]",
            "//div[contains(@class, 'content')]",
            "//div[@id='reference']",
            "//div[@id='detail']",
            "//div[@id='guide']",
            "//div[@class='experiment-detail']",
            "//div[@class='task-detail']",
            "//div[@class='lab-guide']",
            "//pre[@class='code']",
            "//article"
        ]
        
        found_content = []
        
        for selector in reference_selectors:
            try:
                elements = self.driver.find_elements(By.XPATH, selector)
                for elem in elements:
                    text = elem.text.strip()
                    if text and len(text) > 50:
                        found_content.append((selector, text[:50] + "..."))
                        if not reference_content:
                            reference_content = elem.text
            except Exception as e:
                pass
        
        if reference_content:
            self.log(f"✓ 成功读取详细参考内容，长度: {len(reference_content)} 字符")
            self.log(f"内容预览: {reference_content[:200]}...")
        else:
            self.log("✗ 未找到详细参考内容")
        
        self.log("=" * 50)
        self.log("详细参考读取完成")
        self.log("=" * 50)
        
        return reference_content
    
    def take_screenshot(self, step_num):
        try:
            screenshot = self.driver.get_screenshot_as_base64()
            screenshot_info = {
                'step': step_num,
                'timestamp': time.strftime('%Y%m%d_%H%M%S'),
                'image': screenshot
            }
            self.screenshots.append(screenshot_info)
            self.log(f"✓ 截图 {step_num} 已保存")
            return screenshot_info
        except Exception as e:
            self.log(f"✗ 截图 {step_num} 失败: {str(e)}")
            return None
    
    def click_save_environment(self):
        self.log("=" * 50)
        self.log("开始查找保存环境按钮")
        self.log("=" * 50)
        
        save_selectors = [
            "//button[contains(text(), '保存环境')]",
            "//button[contains(text(), '保存')]",
            "//button[contains(text(), '提交')]",
            "//button[contains(text(), '完成实验')]",
            "//button[contains(text(), '结束实验')]",
            "//a[contains(text(), '保存环境')]",
            "//a[contains(text(), '保存')]",
            "//div[contains(text(), '保存环境')]",
            "//*[@class='save-btn']",
            "//*[@class='submit-btn']"
        ]
        
        found_buttons = []
        
        for selector in save_selectors:
            try:
                buttons = self.driver.find_elements(By.XPATH, selector)
                if buttons:
                    found_buttons.extend([(selector, btn) for btn in buttons])
                    self.log(f"使用选择器 '{selector}' 找到 {len(buttons)} 个按钮")
            except Exception as e:
                pass
        
        if not found_buttons:
            self.log("✗ 未找到保存环境按钮")
            return False
        
        for selector, btn in found_buttons:
            try:
                if not btn.is_displayed():
                    continue
                
                btn_text = btn.text.strip() if btn.text else "无文本"
                self.log(f"准备点击保存按钮: '{btn_text}'")
                
                self.driver.execute_script("arguments[0].scrollIntoView(true);", btn)
                time.sleep(0.5)
                
                try:
                    btn.click()
                except:
                    self.driver.execute_script("arguments[0].click();", btn)
                
                self.log("✓ 保存环境按钮点击成功")
                time.sleep(3)
                return True
                
            except Exception as e:
                self.log(f"✗ 点击保存按钮失败: {str(e)}")
        
        self.log("✗ 所有保存按钮点击都失败")
        return False
    
    def refresh_page(self):
        self.log("=" * 50)
        self.log("正在刷新页面...")
        self.log("=" * 50)
        
        try:
            self.driver.refresh()
            time.sleep(5)
            self.log("✓ 页面刷新成功")
        except Exception as e:
            self.log(f"✗ 页面刷新失败: {str(e)}")
    
    def execute_task(self, task_info):
        try:
            self.current_task_info = task_info
            self.screenshots = []
            
            self.log(f"\n{'='*60}")
            self.log(f"开始执行任务: {task_info['title']}")
            self.log(f"{'='*60}")
            
            if not self.click_continue_experiment(task_info):
                self.log("任务执行失败 - 无法点击继续实验按钮")
                return False
            
            detailed_ref = self.get_detailed_reference()
            task_info['description'] = detailed_ref
            
            self.log("等待虚拟机加载...")
            time.sleep(10)
            
            self.log("开始截图记录操作过程...")
            step_num = 1
            max_screenshots = 20
            
            while step_num <= max_screenshots:
                self.log(f"--- 步骤 {step_num}/20 ---")
                self.take_screenshot(step_num)
                
                if step_num == max_screenshots:
                    self.log("已达到最大截图次数")
                    break
                
                save_btn_exists = False
                for selector in ["//button[contains(text(), '保存环境')]", "//button[contains(text(), '保存')]"]:
                    if len(self.driver.find_elements(By.XPATH, selector)) > 0:
                        save_btn_exists = True
                        break
                
                if save_btn_exists:
                    self.log("检测到保存环境按钮，准备结束任务")
                    self.take_screenshot(step_num + 1)
                    break
                
                time.sleep(3)
                step_num += 1
            
            self.click_save_environment()
            
            task_info['screenshots'] = self.screenshots
            self.log(f"\n{'='*60}")
            self.log(f"任务 '{task_info['title']}' 执行完成，共截图 {len(self.screenshots)} 张")
            self.log(f"{'='*60}")
            
            return True
        except Exception as e:
            self.log(f"✗ 执行任务失败: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
    
    def run_all_tasks(self):
        try:
            task_count = 0
            max_tasks = 20
            
            while task_count < max_tasks:
                self.log(f"\n{'='*70}")
                self.log(f"第 {task_count + 1} 轮任务检测")
                self.log(f"{'='*70}")
                
                self.screenshots = []
                
                expand_count = self.expand_all_chapters()
                self.log(f"本轮展开了 {expand_count} 个章节")
                
                tasks = self.find_unfinished_tasks()
                
                if not tasks:
                    self.log("未发现未完成任务，结束执行")
                    break
                
                task = tasks[0]
                self.log(f"\n开始执行任务: {task['title']}")
                
                if self.execute_task(task):
                    task_count += 1
                    self.log(f"任务 {task_count} 执行成功")
                else:
                    self.log(f"任务执行失败")
                
                self.log("等待页面跳转...")
                time.sleep(5)
                
                self.refresh_page()
            
            self.log(f"\n{'='*70}")
            self.log(f"所有任务执行完成，共完成 {task_count} 个任务")
            self.log(f"{'='*70}")
            
            return True
        except Exception as e:
            self.log(f"✗ 执行任务失败: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
    
    def get_current_task_data(self):
        return {
            'task_info': self.current_task_info,
            'screenshots': self.screenshots
        }
    
    def close(self):
        if self.driver:
            self.driver.quit()
            self.log("浏览器已关闭")