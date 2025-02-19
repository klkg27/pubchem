import requests 
from urllib.parse  import quote 
import json 
 
def get_cid_from_smiles(smiles: str) -> int:
    """
    通过PubChem API根据SMILES获取CID 
    :param smiles: SMILES字符串 
    :return: 化学物质CID 
    :raises: Exception 包含API错误信息 
    """
    # URL编码处理特殊字符（如#）
    encoded_smiles = quote(smiles, safe='')
    
    # 构建API请求URL()
    url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/smiles/{encoded_smiles}/cids/txt" 
    
    try:
        # 发送带自定义Header的请求()
        response = requests.get( 
            url,
            headers={
                "User-Agent": "Python PubChem Client/1.0",
                "Accept": "application/txt"
            },
            timeout=10 
        )
        response.raise_for_status() 
        
        # 返回结果
        return int(response.text.strip())
        
    except requests.exceptions.HTTPError  as e:
        raise Exception(f"API请求失败: HTTP {e.response.status_code}")  from e 
    except (KeyError, json.JSONDecodeError) as e:
        raise Exception("无效的API响应格式") from e 
