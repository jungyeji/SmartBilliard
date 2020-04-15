import pymysql.cursors
from point import find_ball
from collections import deque

arr_row = []
select_flag = 0

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
            #print(rows)
        #commit data
        conn.commit()
    finally:
        conn.close()
    return rows


def cal_ball(yel_x, yel_y, red_x, red_y, white_x, white_y) :
    is_long = 0
    ball_point = 0
    cushion1 = 0


    #1쿠션
    slope1 = (red_y - white_y)/(red_x - white_x)
    slope2 = (yel_y - white_y)/(yel_x - white_x)

    x1 = ((-1) * white_y)/slope1 + white_x
    x2 = ((-1) * white_y)/slope2 + white_x

    if x1 >= 0 and x1 <= 800 :
        if x1 <= 500 :
            cushion1 = x1/10
        else : 
            cushion1 = 50 + (x1-500)/5
        x = (400 - white_y)/slope1 + white_x
        if x >= 0 and x <= 800 :
            ball_point = x/20 + 10
        elif x >= 800 :
            y = slope1 * (800 - white_x) + white_y
            if (400-y) <= 200 :
                ball_point = ((400-y)/10) + 50
            else :
                ball_point = ((400-y)/5) + 30

    elif x2 >= 0 and x2 <= 800 :
        if x2 <= 500 :
            cushion1 = x2/10
        else :
            cushion1 = 50 + (x2-500)/5
        x = (400 - white_y)/slope2 + white_x
        if x >= 0 and x <= 800 :
            ball_point = x/20 + 10
        elif x >= 800 :
            y = slope2 * (800 - white_x) + white_y
            if (400-y) <= 200 :
                ball_point = ((400-y)/10) + 50
            else :
                ball_point = ((400-y)/5) + 30
    else :
        y1 = ((-1) * slope1)/white_x + white_y
        y2 = ((-1) * slope2)/white_x + white_y

        if y1 >= 0 and y1 <= 400 :
            is_long = 1
            cushion1 = y1/10
            
            y = slope1 * (800 - white_x) + white_y
            if y >= 0 and y <= 400 :
                ball_point = (y/20) + 20
            else :
                print("not found route")
        elif y2 >= 0 and y2 <= 400 :
            is_long = 1
            cushion1 = y2/10
            
            y = slope2 * (800 - white_x) + white_y
            if y >= 0 and y <= 400 :
                ball_point = (y/20) + 20
            else :
                print("not found route")
        else :
            print("not found route")
    return ball_point, cushion1, is_long


def select_ball(ball_point, cushion1, is_long) :
    global select_flag
    global arr_row

    sql = """
        select * from route
        where (cushion_1_point between (%s-50) and (%s+50)) and
        (cushion_2_point between (%s-50) and (%s+50)) and
        is_long=%s
        """
    params = (int(ball_point), int(ball_point), int(cushion1), int(cushion1), int(is_long))
    (rows) = db_query('billiworlds', sql, params)
    if select_flag == 0 :
        for x in rows : 
            #print(x)
            # x[4] :cushion_1_point x[5] :cushion_2_point
            temp = int((((x[4]-ball_point) ** 2) + ((x[5] - ball_point) ** 2)) ** 0.5)
            print('{0} : {1}'.format(x[0], temp)) 
            var = (temp, x[0], 0)
            arr_row.append(var)
        arr_row.sort()
    select_flag = 1
    return arr_row

def find_route(data) :
    col = deque()
    sql = """
        select DISTINCT coll_x_loc, coll_y_loc, route_detail_id_self
        from route_detail rd, route r
        where rd.route_detail_id = (select route_detail_id
                                    from route
                                    where route.route_id = %s)
        """
    params = (int(data))
    (route_data) = db_query('billiworlds', sql, params)
    col.append(route_data)
    print(col)
    while(route_data[0][2] is not None) :
        next = route_data[0][2]
        sql = """
            select DISTINCT coll_x_loc, coll_y_loc, route_detail_id_self
            from route_detail rd
            where rd.route_detail_id = %s
        """

        params = (int(next))
        (route_data) = db_query(db='billiworlds', sql=sql, params=params)
        col.append(route_data)
    return col

def find_DB() :
    global arr_row
    (yel_x, yel_y, red_x, red_y, white_x, white_y) = find_ball()
    (ball_point, cushion1, is_long) = cal_ball(yel_x, yel_y, red_x, red_y, white_x, white_y)
    (arr_row) = select_ball(ball_point, cushion1, is_long)
    (data, ball_id, is_pass) = arr_row[-1]
    i = len(arr_row) - 1
    for x in arr_row :
        if x[2] == 0 :
            (data, ball_id, is_pass) = x
            i = arr_row.index(x)
            break
    print(data, ball_id, is_pass)
    temp = (data, ball_id, 1)
    arr_row[i] = temp
    (detail_route) = find_route(arr_row[i][1])
    print('공 좌표 : yellow({0},{1}) red({2},{3}) white({4},{5})'.format(yel_x, yel_y, red_x, red_y, white_x, white_y))
    print('수구포인트 : {0} 1쿠션 포인트 : {1}'.format(int(ball_point), int(cushion1)))
    print(arr_row)
    return detail_route, yel_x, yel_y, red_x, red_y, white_x, white_y

def find_DB_AR() :
    global arr_row
    (yel_x, yel_y, red_x, red_y, white_x, white_y) = find_ball()
    (ball_point, cushion1, is_long) = cal_ball(yel_x, yel_y, red_x, red_y, white_x, white_y)
    (data, ball_id, is_pass) = arr_row[-1]
    i = len(arr_row) - 1
    for x in arr_row :
        if x[2] == 0 :
            (data, ball_id, is_pass) = x
            i = arr_row.index(x) - 1
            break
    # (arr_row) = select_ball(ball_point, cushion1, is_long)
    # i = 0
    # while arr_row[i][2] == 1 :
    #     i = i+1
    # i = i-1
    #(data, ball_id, is_pass) = arr_row[i]
    print(data, ball_id, is_pass)
    (detail_route) = find_route(arr_row[i][1])
    print('공 좌표 : yellow({0},{1}) red({2},{3}) white({4},{5})'.format(yel_x, yel_y, red_x, red_y, white_x, white_y))
    print('수구포인트 : {0} 1쿠션 포인트 : {1}'.format(int(ball_point), int(cushion1)))
    print(arr_row)
    return detail_route, yel_x, yel_y, red_x, red_y, white_x, white_y

#def find_other_DB


if __name__ == "__main__" :
    (yel_x, yel_y, red_x, red_y, white_x, white_y) = find_ball()
    white_x = 606
    white_y = 341
    (ball_point, cushion1, is_long) = cal_ball(yel_x, yel_y, red_x, red_y, white_x, white_y)
    (select_data) = select_ball(ball_point, cushion1, is_long)
    (detail_route) = find_route(select_data)
    #print(yel_x, yel_y, red_x, red_y, white_x, white_y)
    #print()
    #print(ball_point, cushion1, is_long)
    #print(select_data)
    #print(detail_route)

#     ball_point = (white_x + 400 - white_y)/20 + 10
#     if(ball_point > 50) :
#         ball_point = 400 - white_y + white_x
#     slope = (400-white_y)/(ball_point-white_x)
#     cushion_1 = ((white_y) * (-1))/slope + white_x 
#     cushion_3 = ball_point - cushion_1

# def select_ball() :
#     sql='select * from ball'
#     params=()
#     db_query(db='billiworlds', sql=sql, params=params)
