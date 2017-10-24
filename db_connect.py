import MySQLdb

def connection():
    conn = MySQLdb.connect(host="localhost",
                           user="root",
                           passwd = "cookies", #put your password here
                           db = "demopyth")
    
    c = conn.cursor()
    
    return c, conn
                           
    