import MySQLdb

def connection():
    conn = MySQLdb.connect(host="localhost",
                           user="root",
                           passwd = "trogdor144", #put your password here
                           db = "demo")
    
    c = conn.cursor()
    
    return c, conn
                           
    