# %% 

import pandas as pd
import requests_cache
import requests
import time

from bs4 import BeautifulSoup
from tqdm import tqdm
from requests_cache import NEVER_EXPIRE
from concurrent.futures import ThreadPoolExecutor, as_completed

# %% 

# Obtido do cURL
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:139.0) Gecko/20100101 Firefox/139.0',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'pt-BR,pt;q=0.8,en-US;q=0.5,en;q=0.3',
    'Referer': 'https://na.finalfantasyxiv.com/lodestone/playguide/db/',
    'Sec-GPC': '1',
    'Alt-Used': 'na.finalfantasyxiv.com',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'same-origin',
    'Priority': 'u=0, i',
}

# %%

# Configuração de cache
try:
    requests_cache.install_cache(
        '../ffxiv_cache', # Cria um diretório chamado 'ffxiv_cache'
        backend='filesystem', # Armazena o cache no disco (mais rápido que sqlite)
        expire_after=NEVER_EXPIRE, # Cache setado para não expirar, porém é uma boa prática expirar em 1 hora
        allowable_methods=['GET'], # Métodos permitidos no cache. Estamos somente fazendo GET 
        include_get_headers=True, # Considera os cabeçalhos da requisição como parte da chave do cache. Se True, requisições com cabeçalhos diferentes serão tratadas como diferentes
        fast_save=True,
        serializer='json' 
    )

    print("Cache configurado.")

except Exception as e:
    print(f"Erro: {str(e)}")
    

# %%

def obter_paginas(url_base:str, soup: BeautifulSoup)->list[str]:

    urls = []

    div = soup.find("div", class_="pagination clearfix").find("a", rel="last")
    qtd_paginas = div['href'].split("page=")[-1]
    qtd_paginas = int(qtd_paginas)
        
    for i in range(1, qtd_paginas + 1):
        urls.append(url_base + "&page=" + str(i))

    return list(set(urls))

# %%

def montar_links_itens(soup: BeautifulSoup, url_pagina:str)->list[str]:

    tabela = soup.find("div", class_="db-table__wrapper")
    ancoras = tabela.find_all("a", class_="db_popup db-table__txt--detail_link")

    url_pagina = url_base.split("?")
    urls_itens = []

    for id_item in ancoras:
        urls_itens.append(url_pagina[0] + id_item['href'].split("item/")[-1].strip("/"))
    
    return list(set(urls_itens))

# %%

def extrair_infos_arma(url_item:str, session)->list[dict]:

    try:
        resp = session.get(url_item, timeout=10)
        soup = BeautifulSoup(resp.text, 'html.parser')

        div = soup.find("div", class_="db__l_main db__l_main__view")
        if not div:
            return None
            
        data = {}
        data["Item ID"] = url_item.split("item/")[-1].strip("/")
        data["Weapon Name"] = div.find("h2").get_text(" ", strip=True).encode("ascii", "ignore").decode() if div.find("h2") else "N/A"
        data["Rarity"] = div.find("h2")['class'][-1] if div.find("h2") else "N/A"
        data["Classes"] = div.find("div", class_="db-view__item_equipment__class").text.strip() if div.find("div", class_="db-view__item_equipment__class") else "N/A"
        data["Item Level"] = div.find("div", class_="db-view__item_level").text.split(" ")[-1] if div.find("div", class_="db-view__item_level") else "N/A"
        data["Required Level"] = div.find("div", class_="db-view__item_equipment__level").text.strip() if div.find("div", class_="db-view__item_equipment__level") else "N/A"
        spec_name = [div.text.strip() for div in div.find_all("div", class_="db-view__item_spec__name")]
        spec_stats = [div.text.strip() for div in div.find_all("div", class_="db-view__item_spec__value")]
        for nome, valor in zip(spec_name, spec_stats):
            data[nome] = valor
        bonus_stats = div.find("ul", class_="db-view__basic_bonus")
        if bonus_stats:
            for stat in bonus_stats.find_all("li"):
                if "+" in stat.text:
                    nome, valor = stat.text.split("+")
                    data[nome.strip()] = f"+{valor.strip()}"
        obtained_from = soup.find("table", class_="db-table db-table__item_source")
        data["Obtained From"] = [item.get_text(" ", strip=True) for item in obtained_from.find_all("tr")] if obtained_from is not None else "N/A"  
        div_acquired_from = soup.find_all("div", class_="db-view__data__inner--select_reward")
        data["Acquired From"] = [item.get_text(" ", strip=True) for item in div_acquired_from] if len(div_acquired_from) > 0 else "N/A"
        return data
            
    except Exception as e:
        print(f"Erro ao processar o item {url_item}: {str(e)}")
        return None
    
#%%
def processar_lote_itens(urls_itens: list, session) -> list[dict]:

    with ThreadPoolExecutor(max_workers=10) as executor: 
        futures = []
        for url in urls_itens:
            futures.append(executor.submit(extrair_infos_arma, url, session))
        
        return [future.result() for future in as_completed(futures) if future.result()]
  
# %%

def processar_pagina(url_pagina:str, session)->list[dict]:

    time.sleep(0.05 * (20/max_workers))

    try:
        resp = session.get(url_pagina, timeout=10)

        if resp.status_code != 200:
            print(f"Erro: {resp.status_code} em {url_pagina}")
            return None
                
        soup = BeautifulSoup(resp.text, 'html.parser')
        url_itens = montar_links_itens(soup, url_pagina)

        return processar_lote_itens(url_itens, session)
        
    except Exception as e:
        print(f"Erro ao processar a página {url_pagina}: {str(e)}")
        return []

# %%
    
url_base = "https://na.finalfantasyxiv.com/lodestone/playguide/db/item/?category2=1"
resp = requests.get(url=url_base, headers=headers)
soup = BeautifulSoup(resp.text, 'html.parser')

urls_paginas = obter_paginas(url_base=url_base, soup=soup)
print(f"Total de páginas: {len(urls_paginas)}")

#%%

session = requests_cache.CachedSession()
session.headers.update(headers)

dados_completos = []
max_workers = 7

with ThreadPoolExecutor(max_workers=max_workers) as executor:
    futures = {
        executor.submit(processar_pagina, url_pagina, session)
        for url_pagina in urls_paginas
    }

    for future in tqdm(as_completed(futures), total=len(futures), desc="Processando páginas"):
        try:
            resultado = future.result()
            if resultado:
                dados_completos.extend(resultado)
        except Exception as e:
            print(f"\nErro ao processar página: {e}")

df = pd.DataFrame(dados_completos)

print(f"Finalizado! {len(df)} itens obtidos.")
# %%

df.to_csv("../data/armas_final_fantasy.csv", index = False)
print(f"Itens salvos no arquivo CSV.")

#%%