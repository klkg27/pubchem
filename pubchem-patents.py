from playwright.sync_api  import sync_playwright
import json

def scrape_pubchem_Patents(cid):
    section_list = ['Depositor-Supplied-Patent-Identifiers','WIPO-PATENTSCOPE','Chemical-Co-Occurrences-in-Patents','Chemical-Disease-Co-Occurrences-in-Patents','Chemical-Gene-Co-Occurrences-in-Patents']
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False) 
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

with open("pubchem_Patents.json", "w") as f:
    json.dump(scrape_pubchem_Patents(134611040), f, indent=4)