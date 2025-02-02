import sqlite3
from sqlite3 import Error
from datetime import date, timedelta
from setup import get_full_path

class DB:

    def realdate(self, dt):
        if not isinstance(dt, date):
            d = list(map(int, dt.split('-')))
            dt = date(d[0], d[1], d[2])
        return dt.toordinal() + 1721424.5
    # def update_date_format(self):
    #     sql = "SELECT * from water"
    #     cur = self.conn.cursor()
    #     cur.execute(sql)
    #     rows = cur.fetchall()
    #     for row in rows:
    #         dt = row[0]
    #         if "/" in dt:
    #             dt = list(map(int, dt.split('/')))
    #             dt = date(dt[2],dt[0], dt[1])
    #             sql = f"UPDATE water SET date='{str(dt)}' where date='{row[0]}' and reservoir='{row[1]}'"
    #             cur.execute(sql)
    #     self.conn.commit()

    def create_connection(self, db_file):
        """ create a database connection to the SQLite database
            specified by db_file
        :param db_file: database file
        :return: Connection object or None
        """
        conn = None
        try:
            conn = sqlite3.connect(db_file)
            return conn
        except Error as e:
            print(e)

        return conn

    def create_table(self, create_table_sql):
        """ create a table from the create_table_sql statement
        :param conn: Connection object
        :param create_table_sql: a CREATE TABLE statement
        :return:
        """
        try:
            c = self.conn.cursor()
            c.execute(create_table_sql)
        except Error as e:
            print(e)

    # Note in cretion we can postpone commit to after all
    # data is inserted, else it takes longer
    # hence there is a separate commit method
    # if you want to commit immediately pass True here.
    def create_water_record(self, data, commit = False):
        """
        Create a new data into the water table
        :param data: (date, reservoir, level_ft, storage_tmc, inflow_cusecs, outflow_cusecs)
        :return: data id
        """

        sql = f'''INSERT INTO water(realdate, date, reservoir, level_ft, storage_tmc, inflow_cusecs, outflow_cusecs)
                VALUES({self.realdate(data[0])},?,?,?,?,?,?)'''
        cur = self.conn.cursor()
        cur.execute(sql, data)
        if commit:
            self.conn.commit()
        return cur.lastrowid

    def predict_risk(self, num_days):
        return f"risk prediction called for {num_days} days"

    def storage_stats(self, from_date, to_date):
        return f"storage_stats called for {from_date} to {to_date}"

    def compare_forecasts(self, reservoir, model1, model2, show=False):
        sql = f"SELECT m1.date, m1.storage_tmc, m2.storage_tmc FROM water_forecast m1 INNER JOIN water_forecast m2 ON m1.date==m2.date and m1.reservoir==m2.reservoir WHERE m1.reservoir='{reservoir}' and m1.model={model1} and m2.model={model2}"
        cur = self.conn.cursor()
        cur.execute(sql)
        rows = cur.fetchall()
        if show:
            for row in rows:
                print(row)

        s = rows[0][1]-rows[0][2]
        a = b = s
        l = [s]
        for row in rows[1:]:
            x = row[1]-row[2]
            l.append(x)
            a = min(a, x)
            b = max(b, x)
            s += x
        mean = s/len(rows)
        v = sum([(x-mean)**2 for x in l])/len(l)
        from math import sqrt
        
        print(f"mean = {mean:0.2f}, min = {a:0.2f}, max = {b:0.2f}, variance = {v:0.2f}, stdev = {sqrt(v):0.2f}")


    # find variance between actual and forecast values for various models
    def find_variance(self, reservoir, model, show=False):
        sql = f"SELECT water.date, water.storage_tmc, water_forecast.storage_tmc, water_forecast.model FROM water INNER JOIN water_forecast ON water.date==water_forecast.date and water.reservoir==water_forecast.reservoir WHERE water.reservoir='{reservoir}' and water_forecast.model={model}"
        cur = self.conn.cursor()
        cur.execute(sql)
        rows = cur.fetchall()
        if show:
            for row in rows:
                print(row)

        s = rows[0][1]-rows[0][2]
        a = b = s
        l = [s]
        for row in rows[1:]:
            x = row[1]-row[2]
            l.append(x)
            a = min(a, x)
            b = max(b, x)
            s += x
        mean = s/len(rows)
        v = sum([(x-mean)**2 for x in l])/len(l)
        from math import sqrt
        
        print(f"mean = {mean:0.2f}, min = {a:0.2f}, max = {b:0.2f}, variance = {v:0.2f}, stdev = {sqrt(v):0.2f}")

    def display_all_water_data(self, reservoir):
        sql = f"SELECT * FROM water WHERE reservoir='{reservoir}'"
        cur = self.conn.cursor()
        cur.execute(sql)
        rows = cur.fetchall()
        for row in rows:
            print(row)
        #return rows

    def display_all_water_forecast_data(self, reservoir='krs'):
        sql = f"SELECT * FROM water_forecast WHERE reservoir='{reservoir}'"
        cur = self.conn.cursor()
        cur.execute(sql)
        rows = cur.fetchall()
        for row in rows:
            print(row)
        #return rows

    def get_water_record(self, day, reservoir):
        sql = f"SELECT * FROM water WHERE date='{day}' and reservoir='{reservoir}'"
        #print(sql)
        cur = self.conn.cursor()
        cur.execute(sql)
        rows = cur.fetchall()
        return rows[0]

    def upsert_water_record(self, data, commit=False):
        """
        Create a new data into the water table
        :param data: (date, reservoir, level_ft, storage_tmc, inflow_cusecs, outflow_cusecs)
        :return: data id
        """
        cur = self.conn.cursor()
        sql = f"SELECT * FROM water WHERE date='{data[0]}' and reservoir='{data[1]}'"
        
        cur.execute(sql)
        rows = cur.fetchall()
        if len(rows) > 0:
            # update
            sql = f'''UPDATE water SET realdate={self.realdate(data[0])}, date=?, reservoir=?, level_ft=?, storage_tmc=?, 
                     inflow_cusecs=?, outflow_cusecs=?
                     WHERE date='{data[0]}' and reservoir='{data[1]}' '''
            cur.execute(sql, data)
            if commit:
                self.conn.commit()
            print("UPDATING...", data[0], data[1])
            return cur.lastrowid
        else:
            # insert
            print("INSERTING...", data[0], data[1])
            return self.create_water_record(data, commit)

    def create_weather_record(self, data, commit=False):
        """
        Create a new data into the weather table
        :param data: (date, location, max_temp, min_temp, temp, precip, wind, wind_dir, visibility, cloudcover, humidity, forecast)
        :return: data id
        """
        sql = f'''INSERT INTO weather(realdate, date, location, max_temp, min_temp, temp, precip, wind, wind_dir, visibility, cloudcover, humidity, forecast)
                VALUES({self.realdate(data[0])}, ?,?,?,?,?,?,?,?,?,?,?,?)'''
        cur = self.conn.cursor()
        cur.execute(sql, data)
        if commit:
            self.conn.commit()
        return cur.lastrowid

    def upsert_weather_record(self, data, commit=False):
        """
        Create a new data into the weather table
        :param data: (date, location, max_temp, min_temp, temp, precip, wind, wind_dir, visibility, cloudcover, humidity, forecast)
        :return: data id
        """
        cur = self.conn.cursor()
        sql = f"SELECT * FROM weather WHERE date='{data[0]}' and location='{data[1]}'"
        
        cur.execute(sql)
        rows = cur.fetchall()
        if len(rows) > 0:
            # update
            sql = f'''UPDATE weather SET realdate={self.realdate(data[0])}, date=?, location=?, max_temp=?, min_temp=?, temp=?, precip=?, wind=?, 
                     wind_dir=?, visibility=?, cloudcover=?, humidity=?, forecast=?
                     WHERE date='{data[0]}' and location='{data[1]}' '''
            cur.execute(sql, data)
            if commit:
                self.conn.commit()
            print("UPDATING...", data[0], data[1])
            return cur.lastrowid
        else:
            # insert
            print("INSERTING...", data[0], data[1])
            return self.create_weather_record(data, commit)
        

    def get_data_for_prediction(self, todate, window):
        start = self.realdate(todate + timedelta(-window))
        end = self.realdate(todate)
        sql = f''' SELECT water.date, water.storage_tmc, water.inflow_cusecs, water.outflow_cusecs, 
                         weather.max_temp, weather.visibility, weather.wind, weather.humidity, weather.cloudcover 
                  FROM water INNER JOIN weather 
                  ON  water.reservoir='krs' AND weather.location='karnataka' AND water.date = weather.date
                      AND water.realdate > {start} AND water.realdate <= {end} 
                  '''
        cur = self.conn.cursor()
        cur.execute(sql)
        return cur.fetchall()

    def get_data_for_training(self):
        sql = f''' SELECT water.date, water.storage_tmc, water.inflow_cusecs, water.outflow_cusecs, 
                         weather.max_temp, weather.visibility, weather.wind, weather.humidity, weather.cloudcover 
                  FROM water INNER JOIN weather 
                  ON  water.reservoir='krs' AND weather.location='karnataka' AND water.realdate = weather.realdate
                  '''
        cur = self.conn.cursor()
        cur.execute(sql)
        return cur.fetchall()

    def get_water_data_for_prediction(self, todate, window):
        start = self.realdate(todate + timedelta(-window))
        end = self.realdate(todate)
        sql = f''' SELECT date, water.storage_tmc
                  FROM water WHERE reservoir='krs' AND realdate > {start} AND realdate <= {end} 
                  '''
        cur = self.conn.cursor()
        cur.execute(sql)
        return cur.fetchall()

    def get_weather_data_for_prediction(self, todate, window):
        start = self.realdate(todate + timedelta(-window))
        end = self.realdate(todate +  timedelta(90))
        sql = f''' SELECT date, max_temp, visibility, wind, humidity, cloudcover 
                  FROM weather 
                  WHERE location='karnataka' AND realdate > {start} AND realdate <= {end} 
                  '''
        cur = self.conn.cursor()
        cur.execute(sql)
        return cur.fetchall()

    def upsert_forecast_record(self, data, commit=False):
        """
        Create a new data into the water_forecast table
        :param data: (date, reservoir, level_ft, storage_tmc, inflow_cusecs, outflow_cusecs, model)
        :return: data id
        """
        cur = self.conn.cursor()
        sql = f"SELECT * FROM water_forecast WHERE date='{data[0]}' and reservoir='{data[1]}' and model={data[-1]}"
        
        cur.execute(sql)
        rows = cur.fetchall()
        if len(rows) > 0:
            # update
            sql = f'''UPDATE water_forecast SET realdate={self.realdate(data[0])}, date=?, reservoir=?, storage_tmc=?, model=?
                     WHERE date='{data[0]}' and reservoir='{data[1]}' and model={data[-1]}'''
            cur.execute(sql, data)
            if commit:
                self.conn.commit()
            print("UPDATING...", data)
            return cur.lastrowid
        else:
            # insert
            print("INSERTING...", data)
            sql = f'''INSERT INTO water_forecast(realdate, date, reservoir, storage_tmc, model)
                VALUES({self.realdate(data[0])},?,?,?,?)'''
            cur = self.conn.cursor()
            cur.execute(sql, data)
            if commit:
                self.conn.commit()
            return cur.lastrowid


    def display_all_weather(self):
        """
        Query all rows in the weather table
        :return:
        """
        cur = self.conn.cursor()
        cur.execute("SELECT * FROM weather")

        rows = cur.fetchall()

        for row in rows:
            print(row)

    def commit(self):
        self.conn.commit()
            
    def delete_all_weather(self):
        """
        Delete all rows in the weather table
        :return:
        """
        sql = 'DELETE FROM weather'
        cur = self.conn.cursor()
        cur.execute(sql)
        self.conn.commit()

    def delete_all_forecast(self):
        """
        Delete all rows in the weather table
        :return:
        """
        sql = 'DELETE FROM water_forecast'
        cur = self.conn.cursor()
        cur.execute(sql)
        self.conn.commit()

    def __init__(self, db_file):
        sql_create_weather_table = """ CREATE TABLE IF NOT EXISTS weather (
                                        date text NOT NULL,
                                        location text NOT NULL,
                                        max_temp real,
                                        min_temp real,
                                        temp real,
                                        precip real,
                                        wind real,
                                        wind_dir real,
                                        visibility real,
                                        cloudcover real,
                                        humidity real,
                                        forecast integer,
                                        realdate real
                                    ); """

        sql_create_water_table = """ CREATE TABLE IF NOT EXISTS water (
                                        date text NOT NULL,
                                        reservoir text NOT NULL,
                                        level_ft real,
                                        storage_tmc real,
                                        inflow_cusecs real,
                                        outflow_cusecs real,
                                        realdate real
                                    ); """

        sql_create_forecast_table = """ CREATE TABLE IF NOT EXISTS water_forecast (
                                        date text NOT NULL,
                                        reservoir text NOT NULL,
                                        level_ft real,
                                        storage_tmc real,
                                        inflow_cusecs real,
                                        outflow_cusecs real,
                                        model integer,
                                        realdate real
                                    ); """


        # create a database connection
        self.conn = self.create_connection(database)

        # create tables
        if self.conn is not None:
            # create weather table
            self.create_table(sql_create_weather_table)

            # create water table
            self.create_table(sql_create_water_table)

            # create water forecast table
            self.create_table(sql_create_forecast_table)

            self.initialized = True
        else:
            print("Error! cannot create the database connection.")

 
try:
    print(appdb.initialized)
except:
    database = get_full_path('data', "pythonsqlite.db")
    print(database)
    appdb = DB(database)