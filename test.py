

mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="prueba"
)

mycursor = mydb.cursor()

sql = "INSERT INTO transcript (video, speaker1,speaker2,message) VALUES (%s, %s,%s, %s)"
val = ("John", "Highway 21","sdsda","dasdsad")
mycursor.execute(sql, val)

mydb.commit()

print(mycursor.rowcount, "record inserted.")