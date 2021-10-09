import gender_guesser.detector as gender
from selenium import webdriver
import pandas as pd
import numpy as np
import feather

class Curia:
    def __init__(self, i, d, t, ti, c, a, g, ):
        self.id = i
        self.date = d
        self.type = t
        self.title = ti
        self.categories = c
        self.author = a
        self.gender = g

    def __str__(self):
        return "Number: {}\nDate: {}\nType: {}\nTitle: {}\nCategories: {}\nAuthor: {}\nGender: {}" \
            .format(self.id, self.date, self.type, self.title, self.categories, self.author, self.gender)

    def to_dict(self):
        return {
            'number': self.id,
            'date': self.date,
            'type': self.type,
            'title': self.title,
            'categories': np.array(self.categories),
            'author': self.author,
            'gender': self.gender,
        }


if __name__ == '__main__':
    driver = webdriver.Chrome("./chromedriver")
    d = gender.Detector()

    startId = 20214313
    endId = 20214113
    curiaList = []

    for affairId in range(startId, endId, -1):
        # Fetch
        url = "https://www.parlament.ch/de/ratsbetrieb/suche-curia-vista/geschaeft?AffairId=" + str(affairId)
        driver.get(url)
        driver.implicitly_wait(50)

        try:
            # Extract
            id = driver.find_element_by_xpath(
                "/html/body/form/div[4]/div/div/div[5]/div[1]/div[1]/div[2]/div/div/div/div[2]/div[1]/article/div[1]/header/span[1]"
            ).text

            date = driver.find_element_by_xpath(
                "/html/body/form/div[4]/div/div/div[5]/div[1]/div[1]/div[2]/div/div/div/div[2]/div[1]/article/div[2]/div[3]/div"
            ).text

            type = driver.find_element_by_xpath(
                "/html/body/form/div[4]/div/div/div[5]/div[1]/div[1]/div[2]/div/div/div/div[2]/div[1]/article/div[1]/header/span[2]"
            ).text

            title = driver.find_element_by_xpath(
                "/html/body/form/div[4]/div/div/div[5]/div[1]/div[1]/div[2]/div/div/div/div[2]/div[1]/article/div[1]/header/h2"
            ).text

            personFullName = driver.find_element_by_xpath(
                "/html/body/form/div[4]/div/div/div[5]/div[1]/div[1]/div[2]/div/div/div/div[2]/div[1]/article/div[2]/div[1]/div/a[2]"
            ).text

            categoryElements = driver.find_element_by_xpath(
                "/html/body/form/div[4]/div/div/div[5]/div[1]/div[1]/div[2]/div/div/div/div[2]/div[5]/div/div[2]/div[2]/div/div[5]/p"
            ).find_elements_by_tag_name("span")
            categories = [c.text for c in categoryElements]

            # Identify
            author = personFullName.title()
            nameSplit = author.split()
            firstName = nameSplit[len(nameSplit) - 1]
            gender = d.get_gender(firstName)

            # Store
            curiaList.append(Curia(id, date, type, title, categories, author, gender))
        except:
            print("Error on: " + url)

    driver.close()

    curiaDataFrame = pd.DataFrame.from_records([c.to_dict() for c in curiaList])
    feather.write_dataframe(curiaDataFrame, "./curia.feather")
