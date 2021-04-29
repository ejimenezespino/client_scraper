from requests import Session
from bs4 import BeautifulSoup
import mysql.connector
import os


headers = {"User-Agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Safari/537.36"}
URL = "https://www.gotrendier.mx/profile/transactions/mis/ventas"
login_url = "https://www.gotrendier.mx/login"

db = mysql.connector.connect(
        host="localhost",
        user=os.environ['DB_USER'],
        password=os.environ['DB_PASSWORD'],
        db="gotrendier_scrapper",
        auth_plugin='mysql_native_password'
        ) #always include auth_plugin
print(db) #prints the Mysqlconnection object to confirm that the mySQL.connector works

cursor = db.cursor()
reset = "TRUNCATE TABLE gotrendier_scrapper.gt_clients"
cursor.execute(reset)

with Session() as s:
    login_url = "https://www.gotrendier.mx/login"
    login_response = s.get(login_url, headers=headers)
    bs_content = BeautifulSoup(login_response.text, "html.parser")
    token = bs_content.find("input", {"name": "csrf_for_security"})["value"]
    login_data = {"login[username]": "ejimenezespinosa@hotmail.com", "login[password]": "Adanyeva1",
                  "csrf_for_security": token}
    s.post(login_url, login_data)
    response = s.get(URL, headers=headers)
    # print(response.text) #we print response to make sure that the login/user-agent work

    bs_container = BeautifulSoup(response.content, "html.parser")
    container = bs_container.find_all('div', class_="tab-content mb-3")

    products = bs_container.find_all('div', class_="col order-2")
    for product in products:
        title = product.find('a', class_="text-neutral01").text
        price = product.find('span', class_="text-neutral01").text
        # convert every element of a list according to the lambda, in this case: item -> item.text
        order = list(map(lambda item: item.text, product.find_all('p', class_="mb-0 fs-14")))[0] #map applies the instruction of every element of the list..
        date = list(map(lambda item: item.text, product.find_all('p', class_="mb-0 fs-14")))[1] #list prints resulrt.. if yo just print date, it print map object
        buyer = list(map(lambda item: item.text, product.find_all('p', class_="mb-0 fs-14")))[2]
        profit = list(map(lambda item: item.text, product.find_all('p', class_="mb-0 fs-14")))[3]
        tracking_number = list(map(lambda item: item.text, product.find_all('p', class_="mb-0 fs-14")))[5]
        # print(title)
        # print(price)
        # print(order.split()[2])
        # print(date.split()[1])
        # print(buyer.split()[1])
        # print(profit.split()[1])
        # print(tracking_number.split()[1])
        # print()
        db = mysql.connector.connect(
            host="localhost",
            user=os.environ['DB_USER'],
            password=os.environ['DB_PASSWORD'],
            db="gotrendier_scrapper",
            auth_plugin='mysql_native_password'
        )

        # you must create a Cursor object. It will let
        #  you execute all the queries you need
        cursor = db.cursor()
        query = "INSERT INTO gotrendier_scrapper.gt_clients (articulo, precio_venta, pedido, fecha, compradora, ganancia, guia_estafeta) VALUES (%s, %s, %s, %s, %s, %s, %s)"

        # storing values in a variable
        values = (title, price, order.split()[2], date.split()[1], buyer.split()[1], profit.split()[1], tracking_number.split()[1])
        # executing the query with values
        cursor.execute(query, values)

        # to make final output we have to run the 'commit()' method of the database object
        db.commit()
        cursor.close()
        db.close()

        print(cursor.rowcount, "record inserted")