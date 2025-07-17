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

    - Otimização do script de coleta utilizando threads e paralelização.

---

### A implementar:

- Transformação:
  
  - Limpeza dos dados utilizando Pandas.
  - Inserção em um banco de dados SQLite.

- Análise: 

    - Qual tipo de arma tem maior dano médio?
    - Como o dano físico aumenta conforme o nível do item?
    - Qual classe tem mais opções de armas disponíveis?
    - Quais armas têm os maiores bônus de força ou vitalidade?
    - Qual é a distribuição de raridade entre todas as armas?

- Data-viz: criar gráficos simples como:

    - Gráfico de barras: quantidade de armas por tipo
    - Boxplot: distribuição de dano por raridade
    - Gráfico de dispersão: item level vs. dano
    - Tabela resumo: top 10 armas com maior dano físico
