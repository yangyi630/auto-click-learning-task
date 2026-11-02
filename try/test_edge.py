from selenium import webdriver
from selenium.webdriver.edge.service import Service
from webdriver_manager.microsoft import EdgeChromiumDriverManager
import time

print("测试Edge浏览器启动...")

try:
    print("尝试使用webdriver-manager安装EdgeDriver...")
    driver_path = EdgeChromiumDriverManager().install()
    print(f"EdgeDriver路径: {driver_path}")
    
    edge_options = webdriver.EdgeOptions()
    edge_options.add_argument("--start-maximized")
    
    service = Service(driver_path)
    driver = webdriver.Edge(service=service, options=edge_options)
    
    print("浏览器启动成功！")
    driver.get("https://www.baidu.com")
    print("页面加载成功:", driver.title)
    
    time.sleep(3)
    driver.quit()
    print("浏览器关闭成功")
    
except Exception as e:
    print(f"错误: {str(e)}")
    import traceback
    traceback.print_exc()