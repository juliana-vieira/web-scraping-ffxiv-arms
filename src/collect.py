# %% 

import pandas as pd
import requests_cache
import requests_cache
import time
import requests

from bs4 import BeautifulSoup
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed
from joblib import Parallel, delayed
from requests_cache import NEVER_EXPIRE
from random import uniform

# %%

# Configurações obtidas do cURL

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:139.0) Gecko/20100101 Firefox/139.0',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'pt-BR,pt;q=0.8,en-US;q=0.5,en;q=0.3',
    # 'Accept-Encoding': 'gzip, deflate, br, zstd',
    'Referer': 'https://na.finalfantasyxiv.com/lodestone/playguide/db/',
    'Sec-GPC': '1',
    'Alt-Used': 'na.finalfantasyxiv.com',
    'Connection': 'keep-alive',
    # 'Cookie': 'ldst_touchstone=1; ldst_is_support_browser=1; ldst_sess=f3deaaa430e08c76e55c80c1814bd69ac11892c3',
    'Upgrade-Insecure-Requests': '1',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'same-origin',
    'Priority': 'u=0, i',
    # Requests doesn't support trailers
    # 'TE': 'trailers',
}
# %% 

# Configuração de cache thread-safe
try:
    requests_cache.install_cache(
        '../ffxiv_cache', # Cria um diretório chamado 'ffxiv_cache'
        backend='filesystem', # Armazena o cache no disco (mais rápido que sqlite)
        expire_after=NEVER_EXPIRE, # Cache setado para não expirar, porém é uma boa prática expirar em 1 hora
        allowable_methods=['GET'], # Métodos permitidos no cache. Estamos somente fazendo GET 
        include_get_headers=True # Considera os cabeçalhos da requisição como parte da chave do cache. Se True, requisições com cabeçalhos diferentes serão tratadas como diferentes
    )

    print("Cache configurado.")

except Exception as e:
    print(f"Erro: {str(e)}")
    
#%%

try:
    with requests_cache.CachedSession() as session: 
        session.headers.update(headers)
    print("Sessão configurada.")

except Exception as e:
    print(f"Erro: {str(e)}")

# %%

def obter_paginas(url_base, soup):

    urls = []

    div = soup.find("div", class_="pagination clearfix").find("a", rel="last")
    qtd_paginas = div['href'].split("page=")[-1]
        
    for i in range(1, int(qtd_paginas) + 1):
        urls.append(url_base + "&page=" + str(i))

    return urls

# %%

def montar_links(soup, url):
    tabela = soup.find("div", class_="db-table__wrapper")
    ancoras = tabela.find_all("a", class_="db_popup db-table__txt--detail_link")

    url = url.split("?")
    urls = []

    for id_item in ancoras:
        urls.append(url[0] + id_item['href'].split("item/")[1])
    
    return urls

# %%

def extrair_infos_arma(url):
    try:
        with requests_cache.CachedSession() as session:
            session.headers.update(headers)

            time.sleep(uniform(0.5, 1.5))
            resp = session.get(url, timeout=10)
            soup = BeautifulSoup(resp.text, 'html.parser')

            div = soup.find("div", class_="db__l_main db__l_main__view")
            if not div:
                return None

            data = {}

            data["Item ID"] = url.split("/")[-2]
            data["Weapon Name"] = div.find("h2").get_text(strip=True) if div.find("h2") else "N/A"
            data["Rarity"] = div.find("h2")['class'][1] if div.find("h2") else "N/A"
            data["Classes"] = div.find("div", class_="db-view__item_equipment__class").text.strip() if div.find("div", class_="db-view__item_equipment__class") else "N/A"
            data["Item Level"] = div.find("div", class_="db-view__item_level").text.split(" ")[2] if div.find("div", class_="db-view__item_level") else "N/A"

            spec_name = [div.get_text(strip=True) for div in div.find_all("div", class_="db-view__item_spec__name")]
            spec_stats = [div.get_text(strip=True) for div in div.find_all("div", class_="db-view__item_spec__value")]
            for nome, valor in zip(spec_name, spec_stats):
                data[nome] = valor

            data["Required Level"] = div.find("div", class_="db-view__item_equipment__level").text.strip() if div.find("div", class_="db-view__item_equipment__level") else "N/A"

            bonus_stats = div.find("ul", class_="db-view__basic_bonus")
            if bonus_stats:
                for stat in bonus_stats.find_all("li"):
                    if "+" in stat.text:
                        nome, valor = stat.text.split("+")
                        data[nome.strip()] = f"+{valor.strip()}"

            obtained_from_table = soup.find("table", class_="db-table db-table__item_source")
            if obtained_from_table:
                headers_table = [th.get_text(strip=True) for th in obtained_from_table.find('thead').find_all('th')]
                extracted_table_data = []
                for row in obtained_from_table.find('tbody').find_all('tr'):
                    values = [' '.join(cell.get_text(separator=' ').split()) for cell in row.find_all('td')]
                    row_data = dict(zip(headers_table, values))
                    extracted_table_data.append(row_data)
            
                data["Obtained From"] = extracted_table_data
            else:
                data["Obtained From"] = "N/A"
                
            div_acquired_from = soup.find_all("div", class_="db-view__data__inner--select_reward")
            data["Acquired From"] = [item.get_text(strip=True) for item in div_acquired_from] if len(div_acquired_from) > 0 else "N/A"

            return data
            
    except Exception as e:
        print(f"Erro ao processar {url}: {e}")
        return None

#%%

def processar_armas(urls_itens):

    urls_itens = list(set(urls_itens))
    resultados = Parallel(n_jobs=8)(delayed(extrair_infos_arma)(url) for url in urls_itens)
    return [r for r in resultados if r is not None]

# %%

def processar_pagina(url):

        resp = session.get(url, timeout=10)
        if resp.status_code != 200:
            print(f"Erro: {resp.status_code} em {url}")
            return None
            
        soup = BeautifulSoup(resp.text, 'html.parser')
        url_itens = montar_links(soup, url)

        return processar_armas(url_itens)

# %%
    
url_base = "https://na.finalfantasyxiv.com/lodestone/playguide/db/item/?category2=1"
resp = requests.get(url_base, headers=headers, timeout = 10)
soup = BeautifulSoup(resp.text, 'html.parser')

urls_paginas = obter_paginas(url_base, soup)
print(f"Total de páginas: {len(urls_paginas)}")

dados_completos = []

with ThreadPoolExecutor(max_workers=10) as executor:
    futures = [executor.submit(processar_pagina, url) for url in urls_paginas]
                
    for future in tqdm(as_completed(futures), total=len(futures)):
        resultado = future.result()
        if resultado:
            dados_completos.extend(resultado)              


df = pd.DataFrame(dados_completos)
print(f"Finalizado! {len(df)} itens obtidos.")

# %%

df.to_csv("../data/armas_final_fantasy.csv", index = False)
print("Dados Salvos!")

# %%