
class DailyBatchDelayPipeline:
    
    
    def move_delay_data(self):
        """
        1. Get realtime data from SQLite DB
        2. Calculation delay data
        3. Save delay data to delay table of PostgreSQL
        """
        pass
    
    def manage_delay_data(self):
        """
        1. Check the delay table has recent 7days delay data of weekday and holiday.
            i.e. Total 14days delay data
        2. If table has no data, download from gcs.
        3. If table has data not in recent 7days, remove from delay table
        4. If table has data which aren't in gcs, upload to gcs.
        """
        pass
    
    def save_delay_stat(self):
        """
        1. Calculate delay stat in postgresql and insert to delay_stat table in same db.
        2. Update timetable_with_delay_stat. This timetable is the latest timetable. 
        """
        pass