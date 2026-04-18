import requests
from bs4 import BeautifulSoup

# 🛒 Mercado Livre
def buscar_mercado_livre():
    url = "https://lista.mercadolivre.com.br/ofertas"
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")

    ofertas = []
    produtos = soup.select(".ui-search-result__content")

    for produto in produtos[:5]:
        titulo = produto.select_one(".ui-search-item__title")
        preco = produto.select_one(".ui-search-price__second-line .andes-money-amount__fraction")
        link = produto.select_one("a.ui-search-link")

        if titulo and preco and link:
            texto = f"🛒 Mercado Livre:\n{titulo.text.strip()} — R$ {preco.text.strip()}\n🔗 {link['href']}"
            ofertas.append(texto)

    return ofertas


# 🛍️ Amazon Brasil
def buscar_amazon():
    url = "https://www.amazon.com.br/s?i=black-friday"
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")

    ofertas = []
    produtos = soup.select("div.s-main-slot div[data-component-type='s-search-result']")

    for produto in produtos[:5]:
        titulo = produto.select_one("h2 a span")
        preco = produto.select_one(".a-price .a-offscreen")
        link = produto.select_one("h2 a")

        if titulo and preco and link:
            texto = f"🛍️ Amazon:\n{titulo.text.strip()} — {preco.text.strip()}\n🔗 https://www.amazon.com.br{link['href']}"
            ofertas.append(texto)

    return ofertas


# ⚡ Kabum
def buscar_kabum():
    url = "https://www.kabum.com.br/promocao"
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")

    ofertas = []
    produtos = soup.select(".productCard")

    for produto in produtos[:5]:
        titulo = produto.select_one(".productCardName")
        preco = produto.select_one(".priceCard")
        link = produto.select_one("a")

        if titulo and preco and link:
            texto = f"⚡ Kabum:\n{titulo.text.strip()} — {preco.text.strip()}\n🔗 https://www.kabum.com.br{link['href']}"
            ofertas.append(texto)

    return ofertas


# 🧨 Magazine Luiza
def buscar_magalu():
    url = "https://www.magazineluiza.com.br/ofertas"
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")

    ofertas = []
    produtos = soup.select("li[data-testid='product-card']")

    for produto in produtos[:5]:
        titulo = produto.select_one("h2")
        preco = produto.select_one("p[data-testid='price-value']")
        link = produto.select_one("a")

        if titulo and preco and link:
            texto = f"🧨 Magalu:\n{titulo.text.strip()} — {preco.text.strip()}\n🔗 https://www.magazineluiza.com.br{link['href']}"
            ofertas.append(texto)

    return ofertas


# 🔗 Função agregadora
def buscar_todas_as_ofertas():
    todas = []

    for funcao in [buscar_mercado_livre, buscar_amazon, buscar_kabum, buscar_magalu]:
        try:
            ofertas = funcao()
            if ofertas:
                todas.extend(ofertas)
        except Exception as e:
            todas.append(f"⚠️ Erro em {funcao.__name__}: {str(e)}")

    return todas
