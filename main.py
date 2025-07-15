import pandas as pd
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

def aceitar_cookies(driver, wait):
    """
    Aceita os cookies na página principal.
    Args:
        driver (webdriver): Instância do WebDriver.
        wait (WebDriverWait): Instância do WebDriverWait para aguardar elementos.
    """
    try:
        aceitar_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Entendi')]")))
        aceitar_btn.click()
        print("Botão de cookies clicado.")
    except Exception:
        print("Botão de cookies não encontrado ou já fechado.")

def extrair_lojas(driver, wait):
    """
    Extrai as lojas da página principal.

    Args:
        driver (webdriver): Instância do WebDriver.
        wait (WebDriverWait): Instância do WebDriverWait para aguardar elementos.

    Returns:
        list: Lista de elementos <li> que contêm as informações das lojas.
    """
    return wait.until(EC.presence_of_all_elements_located(
        (By.CSS_SELECTOR, "li.col-md-4.col-ms-12.col-6.mb-4.pl-0.pl-sm-3")
    ))


def extrair_nome_e_url(loja):
    """
    Extrai o nome e a URL de uma loja.
    Args:
        loja (WebElement): Elemento Web que representa a loja.
    """
    a_tag = loja.find_element(By.TAG_NAME, "a")
    return a_tag.text, a_tag.get_attribute("href")


def extrair_telefones(driver, wait, nome):
    """
    Extrai os números de telefone de uma loja.
    Args:
        driver (webdriver): Instância do WebDriver.
        wait (WebDriverWait): Instância do WebDriverWait para aguardar elementos.
        nome (str): Nome da loja, usado para mensagens de erro.
    """
    try:
        botao_telefone = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'telefone')]"))
        )
        botao_telefone.click()
    except Exception:
        print(f"Botão 'Ver telefone' não encontrado para {nome}")
        return "Não encontrado"

    try:
        ver_telefone_div = wait.until(EC.visibility_of_element_located((By.ID, "verTelefone")))
        telefones = [
            li.find_element(By.TAG_NAME, "span").text
            for li in ver_telefone_div.find_elements(By.CSS_SELECTOR, "ul.exibindo-fone li")
        ]
        return " / ".join(telefones) if telefones else "Não encontrado"
    except Exception:
        print(f"Telefones não encontrados para {nome}")
        return "Não encontrado"

def main():
    """
    Main function to scrape car dealerships from carrosp.com.br
    This function initializes the WebDriver, navigates to the target URL,
    accepts cookies, extracts dealership names, URLs, and phone numbers,
    and saves the data to a CSV file.
    """
    # Início do contador
    inicio = datetime.now()
    print("Início:", inicio.strftime("%Y-%m-%d %H:%M:%S"))

    chrome_options = Options()
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument("--disable-infobars")
    chrome_options.add_argument("--disable-extensions")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    wait = WebDriverWait(driver, 5)

    url = "https://carrosp.com.br/revendas/"
    driver.get(url)
    aceitar_cookies(driver, wait)

    nomes_lojas = []
    urls_lojas = []
    telefones_lojas = []

    lojas = extrair_lojas(driver, wait)
    total_lojas = len(lojas)
    print(f"Total de lojas: {len(lojas)}")

    for i in range(total_lojas):
        # Sempre recarrega a lista de lojas para evitar elementos "stale"
        lojas = extrair_lojas(driver, wait)
        loja = lojas[i]
        nome, link = extrair_nome_e_url(loja)
        nomes_lojas.append(nome)
        urls_lojas.append(link)

        driver.get(link)
        telefone = extrair_telefones(driver, wait, nome)
        telefones_lojas.append(telefone)

        driver.back()

    data = {
        "loja": nomes_lojas,
        "url": urls_lojas,
        "telefone": telefones_lojas
    }

    df = pd.DataFrame(data)
    print(f"O Dataframe possui {df.shape[0]} linhas e {df.shape[1]} colunas.")

    df.to_csv("telefones_anuciantes_carros_sp.csv", index=False, encoding="utf-8")
    print("Arquivo CSV criado com sucesso.")

    driver.quit()

    # Fim do contador
    fim = datetime.now()
    print("Fim:", fim.strftime("%Y-%m-%d %H:%M:%S"))
    print("Duração:", str(fim - inicio))

if __name__ == "__main__":
    main()
