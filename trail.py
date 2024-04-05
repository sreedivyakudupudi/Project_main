import mysql.connector

class CropDiseaseDatabase:
    def __init__(self, host, user, password, database):
        self.conn = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database
        )

    def get_remedies(self, crop, disease):
        select_query = '''SELECT remedies FROM details 
                          WHERE crop=%s AND disease=%s'''
        cursor = self.conn.cursor()
        cursor.execute(select_query, (crop, disease))
        result = cursor.fetchone()
        cursor.close()
        return result[0] if result else None

    def get_precautions(self, crop, disease):
        select_query = '''SELECT precautions FROM details 
                          WHERE crop=%s AND disease=%s'''
        cursor = self.conn.cursor()
        cursor.execute(select_query, (crop, disease))
        result = cursor.fetchone()
        cursor.close()
        return result[0] if result else None

    def get_products(self, crop, disease):
        select_query = '''SELECT fertilisers FROM details 
                          WHERE crop=%s AND disease=%s'''
        cursor = self.conn.cursor()
        cursor.execute(select_query, (crop, disease))
        result = cursor.fetchone()
        cursor.close()
        return result[0] if result else None

    def get_info(self,crop,disease):
        select_query = '''SELECT * FROM details 
                          WHERE crop=%s AND disease=%s'''
        cursor = self.conn.cursor()
        cursor.execute(select_query, (crop, disease))
        result = cursor.fetchone()
        cursor.close()
        return result if result else None
    
    def get_cause(self,crop,disease):
        select_query = '''SELECT cause FROM details 
                          WHERE crop=%s AND disease=%s'''
        cursor = self.conn.cursor()
        cursor.execute(select_query, (crop, disease))
        result = cursor.fetchone()
        cursor.close()
        return result[0] if result else None

# Example usage:

db = CropDiseaseDatabase(host="localhost", user="root", password="system", database="project")
# print("cause :",db.get_cause("Paddy", "Leaf smut"))
    # print(db.get_precautions("Pepper", "Bacterial Spot"))
    # print(db.get_products("Tomato", "Blight"))
