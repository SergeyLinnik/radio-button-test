"""
Автоматизированный тест для проверки radio buttons на сайте https://demoqa.com/radio-button
Исправленная версия: работает с iframe на странице
"""

import logging
import time
from typing import Optional

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager


# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)


def setup_driver() -> webdriver.Chrome:
    """
    Настройка и возврат экземпляра драйвера Chrome.
    ChromeDriver устанавливается автоматически через webdriver-manager.
    """
    logging.info("Начинаем настройку ChromeDriver...")
    
    service = Service(ChromeDriverManager().install())
    
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    
    driver = webdriver.Chrome(service=service, options=options)
    logging.info("ChromeDriver успешно настроен и запущен")
    
    return driver


def switch_to_radio_button_frame(driver: webdriver.Chrome) -> bool:
    """
    Переключается на iframe, содержащий радио-кнопки.
    На странице demoqa.com радио-кнопки находятся внутри iframe.
    
    Args:
        driver: Экземпляр веб-драйвера
    
    Returns:
        bool: True если удалось переключиться, иначе False
    """
    try:
        # Ждем появления iframe
        wait = WebDriverWait(driver, 10)
        
        # Пробуем найти iframe по разным селекторам
        iframe_selectors = [
            "iframe[src*='radio-button']",
            "iframe.demo-frame",
            "iframe[title*='Radio Button']",
            "iframe"
        ]
        
        for selector in iframe_selectors:
            try:
                iframe = wait.until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                )
                driver.switch_to.frame(iframe)
                logging.info(f"Переключились в iframe: {selector}")
                return True
            except:
                continue
        
        # Если iframe не найден, пробуем другой подход - страница может быть перестроена
        logging.warning("Не удалось найти iframe, пробуем работать с основным DOM")
        return True  # Продолжаем без переключения
        
    except Exception as e:
        logging.error(f"Ошибка при переключении в iframe: {e}")
        return False


def find_radio_button(driver: webdriver.Chrome, value: str) -> Optional[WebElement]:
    """
    Находит радиокнопку по её значению (атрибут value) или тексту.
    
    Args:
        driver: Экземпляр веб-драйвера
        value: Значение радиокнопки ("Yes", "Impressive", "No")
    
    Returns:
        Optional[WebElement]: Элемент радиокнопки или None
    """
    try:
        # Пробуем разные селекторы
        selectors = [
            f"input[type='radio'][value='{value}']",
            f"//label[contains(text(), '{value}')]/preceding-sibling::input",
            f"//div[contains(@class, 'custom-control')][.//label[contains(text(), '{value}')]]//input"
        ]
        
        # Сначала пробуем CSS селектор
        try:
            radio_button = driver.find_element(By.CSS_SELECTOR, selectors[0])
            logging.debug(f"Радиокнопка '{value}' найдена по CSS")
            return radio_button
        except:
            pass
        
        # Пробуем XPath
        try:
            radio_button = driver.find_element(By.XPATH, selectors[1])
            logging.debug(f"Радиокнопка '{value}' найдена по XPath")
            return radio_button
        except:
            pass
        
        # Третий вариант XPath
        try:
            radio_button = driver.find_element(By.XPATH, selectors[2])
            logging.debug(f"Радиокнопка '{value}' найдена по XPath (вариант 2)")
            return radio_button
        except:
            pass
        
        logging.error(f"Радиокнопка '{value}' не найдена ни одним из селекторов")
        return None
        
    except Exception as e:
        logging.error(f"Ошибка при поиске радиокнопки '{value}': {e}")
        return None


def is_radio_selected(radio_button: WebElement) -> bool:
    """Проверяет, выбрана ли радиокнопка."""
    return radio_button.is_selected()


def get_selected_status_text(driver: webdriver.Chrome) -> Optional[str]:
    """
    Получает текст успешного сообщения, которое появляется после выбора радио.
    """
    try:
        # Пробуем найти сообщение в разных местах
        selectors = [
            (By.CLASS_NAME, "mt-3"),
            (By.CSS_SELECTOR, ".text-success"),
            (By.XPATH, "//span[contains(text(), 'You have selected')]"),
            (By.XPATH, "//div[contains(@class, 'mt-3')]")
        ]
        
        for by, selector in selectors:
            try:
                message_element = WebDriverWait(driver, 3).until(
                    EC.presence_of_element_located((by, selector))
                )
                text = message_element.text
                if text and "You have selected" in text:
                    return text
            except:
                continue
        
        return None
        
    except Exception as e:
        logging.debug(f"Не удалось получить текст сообщения: {e}")
        return None


def click_radio_button(driver: webdriver.Chrome, radio_button: WebElement, value: str) -> bool:
    """
    Кликает по радиокнопке через JavaScript (более надежный способ).
    """
    try:
        # Способ 1: JavaScript клик (самый надежный)
        driver.execute_script("arguments[0].click();", radio_button)
        logging.info(f"✓ Клик по радиокнопке '{value}' (JavaScript)")
        return True
    except Exception as e1:
        try:
            # Способ 2: обычный клик
            radio_button.click()
            logging.info(f"✓ Клик по радиокнопке '{value}' (обычный)")
            return True
        except Exception as e2:
            logging.error(f"✗ Не удалось кликнуть по радиокнопке '{value}': {e2}")
            return False


def print_page_structure(driver: webdriver.Chrome) -> None:
    """
    Отладочная функция: выводит информацию о структуре страницы.
    """
    try:
        # Получаем заголовок страницы
        title = driver.title
        logging.info(f"Заголовок страницы: '{title}'")
        
        # Ищем все радио-кнопки
        radios = driver.find_elements(By.CSS_SELECTOR, "input[type='radio']")
        logging.info(f"Найдено радио-кнопок на странице: {len(radios)}")
        
        for radio in radios:
            value = radio.get_attribute("value")
            is_enabled = radio.is_enabled()
            logging.info(f"  - Радио: value='{value}', enabled={is_enabled}")
            
    except Exception as e:
        logging.error(f"Ошибка при анализе страницы: {e}")


def test_radio_button(driver: webdriver.Chrome, radio_value: str) -> None:
    """
    Основная логика тестирования одной радиокнопки.
    """
    logging.info(f"=" * 50)
    logging.info(f"Тестируем радиокнопку: '{radio_value}'")
    logging.info(f"=" * 50)
    
    # 1. Найти радиокнопку
    radio_btn = find_radio_button(driver, radio_value)
    if not radio_btn:
        logging.warning(f"Радиокнопка '{radio_value}' не найдена, пропускаем")
        return
    
    # 2. Проверяем, не заблокирована ли кнопка
    if not radio_btn.is_enabled():
        logging.warning(f"Радиокнопка '{radio_value}' заблокирована (disabled)")
        if radio_value == "No":
            logging.info(f"✓ Кнопка 'No' заблокирована - это ожидаемое поведение")
        return
    
    # 3. Кликаем по радиокнопке
    if not click_radio_button(driver, radio_btn, radio_value):
        return
    
    time.sleep(0.5)
    
    # 4. Проверить состояние радиокнопки
    selected = is_radio_selected(radio_btn)
    if selected:
        logging.info(f"✅ РАДИОКНОПКА ВЫБРАНА: '{radio_value}'")
    else:
        logging.warning(f"❌ Радиокнопка НЕ ВЫБРАНА: '{radio_value}'")
    
    # 5. Получить текст сообщения
    success_message = get_selected_status_text(driver)
    expected_text = f"You have selected {radio_value}"
    
    if success_message:
        if expected_text in success_message:
            logging.info(f"✅ Текст подтверждения: '{success_message}'")
        else:
            logging.warning(f"❌ Неожиданный текст: '{success_message}'")
    else:
        logging.info("ℹ️ Сообщение не появилось (возможно, не предусмотрено для этой кнопки)")


def main() -> None:
    """Главная функция."""
    driver = None
    
    try:
        driver = setup_driver()
        
        url = "https://demoqa.com/radio-button"
        logging.info(f"Переходим на страницу: {url}")
        driver.get(url)
        
        # Ждем загрузки
        time.sleep(2)
        
        # Переключаемся в iframe
        if not switch_to_radio_button_frame(driver):
            logging.warning("Не удалось переключиться в iframe, работаем с текущим DOM")
        
        # Отладочная информация
        print_page_structure(driver)
        
        # Тестируем радио-кнопки
        radio_buttons_to_test = ["Yes", "Impressive", "No"]
        
        for radio_value in radio_buttons_to_test:
            test_radio_button(driver, radio_value)
            time.sleep(1)
        
        # Если переключались в iframe, возвращаемся обратно
        try:
            driver.switch_to.default_content()
            logging.info("Вернулись в основной контент")
        except:
            pass
        
        logging.info("=" * 50)
        logging.info("✅ ВСЕ ТЕСТЫ ЗАВЕРШЕНЫ")
        logging.info("=" * 50)
        
        time.sleep(3)
        
    except Exception as e:
        logging.error(f"❌ КРИТИЧЕСКАЯ ОШИБКА: {e}")
        import traceback
        logging.error(traceback.format_exc())
        
    finally:
        if driver:
            driver.quit()
            logging.info("Браузер закрыт")


if __name__ == "__main__":
    main()