import json 
import logging 
from playwright.sync_api  import sync_playwright 
from playwright.async_api  import async_playwright 
import nest_asyncio 
import asyncio 
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
    before_sleep_log 
)
 
# 配置日志格式 
logging.basicConfig( 
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO 
)
logger = logging.getLogger(__name__) 
 
# 通用重试策略配置 
COMMON_RETRY = retry(
    stop=stop_after_attempt(5),  # 最多5次重试 
    wait=wait_exponential(multiplier=1, max=2000),  # 指数退避，最大2秒 
    retry=retry_if_exception_type(Exception),  # 捕获所有异常 
    before_sleep=before_sleep_log(logger, logging.WARNING)  # 重试前日志 
)
 
section_dict = {'Literature':['Consolidated-References', 'Thieme-References',
                                'Chemical-Co-Occurrences-in-Literature',
                                'Chemical-Gene-Co-Occurrences-in-Literature',
                                'Chemical-Disease-Co-Occurrences-in-Literature'],
                'Patents':['Depositor-Supplied-Patent-Identifiers','WIPO-PATENTSCOPE',
                                'Chemical-Co-Occurrences-in-Patents',
                                'Chemical-Disease-Co-Occurrences-in-Patents',
                                'Chemical-Gene-Co-Occurrences-in-Patents']}
 
def scrape_pubchem(cid, environment='terminal',section_type='Literature'):
    """
    通用爬取函数，支持Literature和Patents切换 
    :param section_type: 可选 Literature 或 Patents 
    :param cid: 化合物CID 
    :param environment: 运行环境（terminal/jupyter）
    """
    @COMMON_RETRY 
    def _sync_scrape():
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True) 
            page = browser.new_page() 

            # 导航到目标页面
            page.goto(f'https://pubchem.ncbi.nlm.nih.gov/compound/{cid}#section={section_type}', timeout=5000) 

            # 核心等待逻辑，缩短单次等待时间
            # 步骤1：等待主容器加载
            page.wait_for_selector(f'section#{section_type}',  state="attached", timeout=2000)
            # 步骤2：等待子元素稳定（包含动态内容）
            page.wait_for_function(f'''()  => {{
                const section = document.querySelector('section#{section_type}'); 
                return section && section.querySelectorAll('li').length  > 0;
            }}''', timeout=2000)

            # 滚动页面触发懒加载
            page.mouse.wheel(0,  1500)  # 模拟鼠标滚轮滚动
            # 增加额外的等待时间，缩短单次等待时间
            page.wait_for_timeout(2000) 

            target_section = page.query_selector(f'section#{section_type}') 
            if target_section:
                section_list = section_dict[section_type]
                result = {}
                # 提取每个section的文本内容
                for sec in section_list:
                    section = target_section.query_selector(f"section#{sec}") 
                    if not section:
                        result[sec] = 'None'
                        continue
                    section.wait_for_selector("div",  state="attached", timeout=2000)
                    content = section.inner_html() 
                    result[sec] = content
            else:
                print(f"No {section_type} section found.")
                return None
            browser.close() 
            return result 
 
    @COMMON_RETRY 
    async def _async_scrape():
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True) 
            page = await browser.new_page() 

            # 导航到目标页面
            await page.goto(f'https://pubchem.ncbi.nlm.nih.gov/compound/{cid}#section={section_type}', timeout=5000) 

            # 核心等待逻辑，缩短单次等待时间
            # 步骤1：等待主容器加载
            await page.wait_for_selector(f'section#{section_type}',  state="attached", timeout=2000)
            # 步骤2：等待子元素稳定（包含动态内容）
            await page.wait_for_function(f'''()  => {{
                const section = document.querySelector('section#{section_type}'); 
                return section && section.querySelectorAll('li').length  > 0;
            }}''', timeout=2000)

            # 滚动页面触发懒加载
            await page.mouse.wheel(0,  1500)  # 模拟鼠标滚轮滚动
            # 增加额外的等待时间，缩短单次等待时间
            await page.wait_for_timeout(2000) 

            target_section = await page.query_selector(f'section#{section_type}') 
            if target_section:
                section_list = section_dict[section_type]
                result = {}
                # 提取每个section的文本内容
                for sec in section_list:
                    section = await target_section.query_selector(f"section#{sec}") 
                    if not section:
                        result[sec] = 'None'
                        continue
                    await section.wait_for_selector("div",  state="attached", timeout=2000)
                    content = await section.inner_html() 
                    result[sec] = content
            else:
                print(f"No {section_type} section found.")
                return None
            await browser.close() 
            return result 
 
    if environment == 'terminal':
        return _sync_scrape()
    elif environment == 'jupyter':
        nest_asyncio.apply() 
        return asyncio.run(_async_scrape()) 

