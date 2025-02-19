import json
from playwright.sync_api  import sync_playwright
from playwright.async_api  import async_playwright
import nest_asyncio
import asyncio

def scrape_pubchem_Patents(cid, environment='terminal'):
    section_list = ['Depositor-Supplied-Patent-Identifiers','WIPO-PATENTSCOPE','Chemical-Co-Occurrences-in-Patents','Chemical-Disease-Co-Occurrences-in-Patents','Chemical-Gene-Co-Occurrences-in-Patents']
    if environment == 'terminal':
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True) 
            page = browser.new_page() 

            # 导航到目标页面
            page.goto(f'https://pubchem.ncbi.nlm.nih.gov/compound/{cid}#section=Patents') 

            # 核心等待逻辑
            # 步骤1：等待主容器加载
            page.wait_for_selector('section#Patents',  state="attached", timeout=60000)
            # 步骤2：等待子元素稳定（包含动态内容）
            page.wait_for_function('''()  => {
                const section = document.querySelector('section#Patents'); 
                return section && section.querySelectorAll('li').length  > 0;
            }''', timeout=60000)

            # 滚动页面触发懒加载
            page.mouse.wheel(0,  1500)  # 模拟鼠标滚轮滚动
            # 增加额外的等待时间
            page.wait_for_timeout(5000) 

            Patents = page.query_selector('section#Patents') 
            if Patents:
                result = {}
                # 提取每个section的文本内容
                for sec in section_list:
                    section = Patents.query_selector(f"section#{sec}") 
                    if not section:
                        result[sec] = 'None'
                        continue
                    section.wait_for_selector("div",  state="attached", timeout=60000)
                    content = section.inner_html() 
                    result[sec] = content
            else:
                print("No Patents section found.")
                return None
            browser.close() 
            return result
    elif environment == 'jupyter':
        # 允许在嵌套的事件循环中运行异步代码
        nest_asyncio.apply() 
        async def async_scrape():
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True) 
                page = await browser.new_page() 

                # 导航到目标页面
                await page.goto(f'https://pubchem.ncbi.nlm.nih.gov/compound/{cid}#section=Patents') 

                # 核心等待逻辑
                # 步骤1：等待主容器加载
                await page.wait_for_selector('section#Patents',  state="attached", timeout=60000)
                # 步骤2：等待子元素稳定（包含动态内容）
                await page.wait_for_function('''()  => {
                    const section = document.querySelector('section#Patents'); 
                    return section && section.querySelectorAll('li').length  > 0;
                }''', timeout=60000)

                # 滚动页面触发懒加载
                await page.mouse.wheel(0,  1500)  # 模拟鼠标滚轮滚动
                # 增加额外的等待时间
                await page.wait_for_timeout(5000) 

                Patents = await page.query_selector('section#Patents') 
                if Patents:
                    result = {}
                    # 提取每个section的文本内容
                    for sec in section_list:
                        section = await Patents.query_selector(f"section#{sec}") 
                        if not section:
                            result[sec] = 'None'
                            continue
                        await section.wait_for_selector("div",  state="attached", timeout=60000)
                        content = await section.inner_html() 
                        result[sec] = content
                else:
                    print("No Patents section found.")
                    return None
                await browser.close() 
                return result
            
        return asyncio.run(async_scrape()) 