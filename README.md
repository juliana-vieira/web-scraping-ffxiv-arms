# Web Scraping Eorzea Database

Repositório do projeto de análise de armas do Final Fantasy XIV.

Passos concluídos:

- Coleta: Extrair os dados de armas do Final Fanatsy XIV do [Eorzea Database](https://na.finalfantasyxiv.com/lodestone/playguide/db/item/?category2=1) com as seguintes informações:

    - Nome da arma

    - Nível do item (item level)

    - Nível mínimo para uso (required level)

    - Classe(s) que pode(m) usar

    - Tipo da arma (espada, cajado, lança...)

    - Atributos principais (Strength, Vitality, Mind...)

    - Dano físico / Auto-ataque / Delay

    - Raridade (com base na cor do contorno do ícone)
      
    - Extrair a Fonte do item (ex: vendido por NPC, obtido por coffer, comprado com tomestones...)

---

### A implementar:
  
- Coleta:
  
    - Otimização do script de coleta utilizando threads e paralelização.

- Transformação:
  
  - Limpeza dos dados utilizando Pandas.
