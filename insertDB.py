import pymysql.cursors
from point import find_ball
from collections import deque

max_ball_num = 0

def db_query(db, sql, params):
    #connect to MySQL
    conn = pymysql.connect(host='localhost',
    user='root',
    password='1234',
    charset='utf8mb4',
    db=db)
    try:
        #create Dictionary Cursor
        with conn.cursor() as cursor:
            sql_query = sql
            #excute SQL
            cursor.execute(sql_query, params)
            rows = cursor.fetchall()
            print(rows)
        #commit data
        conn.commit()
    finally:
        conn.close()
    return rows
def insert_route_detail(route_detail) :
    null_flag = 0
    sql = """
        select max(route_detail_id)
        from ball
        """
    params=()
    (max_route_detail) = db_query(db='billiworlds', sql=sql, params=params)
    route_detail.reverse()
    final_max_route_detail_num = max_route_detail[0][0] + len(route_detail)
    for x in range(len(route_detail)) :
        sql = 'insert into route_detail(route_detail_id, coll_x_loc, coll_y_loc, route_detail_id_self) values(%s, %s, %s, %s)'
        if null_flag == 0 :
            params = (final_max_route_detail_num, x.coll_x_loc, x.coll_y_loc, 'NULL')
            null_flag = 1
        else :
            params = (final_max_route_detail_num, x.coll_x_loc, x.coll_y_loc, final_max_route_detail_num + 1)
        
        db_query(db='billiworlds', sql=sql, params=params)
        final_max_route_detail_num = final_max_route_detail_num - 1

def insert_ball(white_x,white_y,red_x,red_y,yel_x,yel_y) :
    sql = """
        select max(ball_id)
        from ball
        """
    params=()
    (max_ball) = db_query(db='billiworlds', sql=sql, params=params)
    max_ball_num = max_ball[0][0]+1
    sql='insert into ball(ball_id, whiteball_x, whiteball_y, redball_x, redball_y, yellowball_x, yellowball_y) values(%s, %s, %s, %s, %s, %s, %s)'
    params=(max_ball_num, white_x, white_y, red_x, red_y, yel_x, yel_y)
    db_query(db='billiworlds', sql=sql, params=params)

def insert_route(is_success, cushion1, cushion2, is_long, route_detail) :
    sql = """
        select max(route_id)
        from route
        """
    params=()
    (max_route) = db_query(db='billiworlds', sql=sql, params=params)
    sql = """
        select max(ball_id)
        from ball
        """
    (max_ball) = db_query(db='billiworlds', sql=sql, params=params)
    sql = """
        select max(route_detail_id)
        from route_detail
        """
    (max_route_detail) = db_query(db='billiworlds', sql=sql, params=params)
    max_route_detail=max_route_detail - len(route_detail[0]) + 1
    max_route = max_route[0][0]+1
    sql='insert into route(route_id, ball_id, route_detail_id, is_success, cushion_1_point, cushion_2_point, is_long) values(%s, %s, %s, %s, %s, %s, %s)'
    params=(max_route, max_ball, max_route_detail, is_success, cushion1, cushion2, is_long)
    db_query(db='billiworlds', sql=sql, params=params)



if __name__ == "__main__" :
    insert_ball(1, 2, 3, 4, 5, 6)