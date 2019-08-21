#!/usr/bin/python3
import time
import pickle
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains


class PSASpider:
    """ PSASpider 类，爬取国家知识产权局专利检索库数据
        网址是： http://www.pss-system.gov.cn/
        由于该网站必须登录后才能查询，因此这个程序是半自动化的，需要用户先登录。
    Attributes:
        driver   用于设置爬取的浏览器自动化程序，我这里用 chromedriver
    """

    def __init__(self):
        self.driver = webdriver.Chrome()

    def login(self):
        """ 访问登录页面，让用户手动登录，并保存 cookie
        """
        self.driver.get(
            "http://pss-system.cnipa.gov.cn/sipopublicsearch/portal/uilogin-forwardLogin.shtml"
        )
        time.sleep(30)
        pickle.dump(self.driver.get_cookies(), open("cookies.pkl", "wb"))

    def make_query(self, keyword, wait_time):
        """ 输入关键字，爬取查询结果
        Args:
            keyword    字符串类型，表示查询关键字
        Raises:
            NoSuchElementException    selenium没有找到相应的元素
            TimeoutException          等待超时异常
        Return:
            results    列表类型，其中每个元素都是一个dict，包含相应信息
        """
        self.driver.get(
            "http://pss-system.cnipa.gov.cn/sipopublicsearch/patentsearch/searchHomeIndex-searchHomeIndex.shtml"
        )
        # 装载之前登录后获取的 cookie
        cookies = pickle.load(open("cookies.pkl", "rb"))
        for cookie in cookies:
            cookie_dict = {
                "domain": cookie.get('domain'),
                'name': cookie.get('name'),
                'value': cookie.get('value'),
                "expires": "",
                'path': cookie.get('path'),
                'httpOnly': cookie.get('httpOnly'),
                'HostOnly': False,
                'Secure': cookie.get('Secure')
            }
            self.driver.add_cookie(cookie_dict)
        # 输入查询关键字，并等待查询结果
        input = self.driver.find_element_by_id('search_input')
        input.send_keys(keyword)
        input.send_keys(Keys.ENTER)
        WebDriverWait(self.driver, 80).until(
            EC.visibility_of_element_located((By.ID, 'search_result_former')))
        results = []
        try:
            patents = self.driver.find_elements_by_css_selector('li.patent')
        except NoSuchElementException:
            return []
        while True:
            for p in patents:
                result = {}
                result['专利名称'] = p.find_element_by_css_selector(
                    'div.item-header h1').text
                info_items = p.find_elements_by_css_selector(
                    'div.item-content-body p')
                check_reference = p.find_element_by_partial_link_text(
                    '引证：')
                check_cite = p.find_element_by_partial_link_text(
                    '被引：')
                for item in info_items:
                    info = item.text.split(':', 1)
                    item_name = re.sub(r'\s+', '', info[0])
                    item_value = re.sub(r'\s+', '', info[1])
                    result[item_name] = item_value
                results.append(result)
                if check_reference.text != '引证：0':
                    reference_dict = {}
                    reference_list = []
                    reference_dict['引证'] = " "
                    print(check_reference.text)
                    actionchains = ActionChains(self.driver)
                    actionchains.move_to_element(check_reference).perform()
                    p.find_element_by_link_text(check_reference.text).click()
                    time.sleep(5)
                    m = self.driver.find_element_by_class_name('m-pagination-info')
                    number = m.text.split(" ")
                    print(number)
                    for i in range(int(number[-2])//5 + 1):
                        reference = self.driver.find_element_by_xpath('//*[@id="tableContentLeftId"]')
                        all_rows = reference.find_elements_by_tag_name("tr")
                        q = self.driver.find_element_by_class_name('ui-dialog-body')
                        for row in all_rows:
                            cells = row.find_elements_by_tag_name("td")
                            references = []
                            for n in cells:
                                references.append(n.text)
                            reference_dict[row.text] = references
                            print(references)
                        try:
                            q.find_element_by_link_text(str(i+2))
                            WebDriverWait(q, 10).until(
                                EC.element_to_be_clickable(
                                (By.LINK_TEXT, str(i+2)))).click()
                        except (NoSuchElementException, TimeoutException): break
                        time.sleep(5)
                    self.driver.find_element_by_class_name('ui-dialog-close').click()
                    reference_list.append(reference_dict)
                    results.append(reference_list)
                if check_cite.text != '被引：0':
                    cite_dict = {}
                    cite_list = []
                    cite_dict["被引"] = " "
                    print(check_cite.text)
                    actionchains = ActionChains(self.driver)
                    actionchains.move_to_element(check_cite).perform()
                    p.find_element_by_link_text(check_cite.text).click()
                    time.sleep(5)
                    m = self.driver.find_element_by_class_name('m-pagination-info')
                    number = m.text.split(" ")
                    print(number)
                    for i in range(int(number[-2])//5 + 1):
                        reference = self.driver.find_element_by_id('tableContentId')
                        all_rows = reference.find_elements_by_tag_name("tr")
                        q = self.driver.find_element_by_class_name('ui-dialog-body')
                        for row in all_rows:
                            cells = row.find_elements_by_tag_name("td")
                            cites = []
                            for n in cells:
                                cites.append(n.text)
                            cite_dict[row.text] = cites
                            print(cites)
                        try:
                            q.find_element_by_link_text(str(i+2))
                            WebDriverWait(q, 10).until(
                                EC.element_to_be_clickable(
                                (By.LINK_TEXT, str(i+2)))).click()
                        except (NoSuchElementException, TimeoutException): break
                        time.sleep(5)
                    self.driver.find_element_by_class_name('ui-dialog-close').click()
                    cite_list.append(cite_dict)
                    results.append(cite_list)
            # 将滚动条滚动到窗口最下方
            self.driver.execute_script(
                "window.scrollTo(0, document.body.scrollHeight)")
            time.sleep(wait_time)
            try:
                self.driver.find_element_by_link_text(u'下一页')
                WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable(
                        (By.LINK_TEXT, u'下一页'))).click()
                time.sleep(3)  #等待页面更新
                self.driver.execute_script(
                    "window.scrollTo(0, 0)")
                WebDriverWait(self.driver, 80).until(
                    EC.visibility_of_element_located(
                        (By.ID, 'search_result_former')))
                time.sleep(1)
                patents = self.driver.find_elements_by_css_selector(
                    'li.patent')
            except (NoSuchElementException, TimeoutException):
                return results

    def exit(self):
        """ 关闭浏览器窗口
        """
        self.driver.close()