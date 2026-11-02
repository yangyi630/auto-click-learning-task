from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.core.os_manager import ChromeType
import time

print("测试Chrome浏览器启动...")

try:
    print("尝试使用webdriver-manager安装ChromeDriver...")
    driver_path = ChromeDriverManager(chrome_type=ChromeType.GOOGLE).install()
    print(f"ChromeDriver路径: {driver_path}")
    
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument("--disable-infobars")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--disable-popup-blocking")
    
    service = Service(driver_path)
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
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