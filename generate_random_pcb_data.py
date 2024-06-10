from datetime import datetime, timedelta

import numpy as np

import pandas as pd

num_of_pcb = 50000  #
num_of_line = 5     # 生产线的数量
defects_scale = [3, 11, 2, 5, 7, 1]  # 各种缺陷的最大数量，可以控制总体上各缺陷的占比
start = '2024-06-01 00:00:00'
end = '2024-07-01 23:59:59'


def random_datetimes(start, end, n=num_of_line):
    start_dt = datetime.strptime(start, '%Y-%m-%d %H:%M:%S')
    end_dt = datetime.strptime(end, '%Y-%m-%d %H:%M:%S')
    delta_seconds = int((end_dt - start_dt).total_seconds())
    random_seconds = np.random.randint(num_of_pcb, delta_seconds, num_of_pcb)
    random_datetime = start_dt + np.array([timedelta(seconds=int(sec)) for sec in random_seconds])
    return random_datetime


def generate_datetime_id(datetime_str):
    dt = datetime.strptime(datetime_str, '%Y-%m-%d %H:%M:%S')
    datetime_id = dt.strftime('%Y%m%d%H%M%S')
    return datetime_id


def create_filename(row):
    """
    根据时间和生产线生成图片文件名，以简单拼接的方式
    """
    datetime_id = generate_datetime_id(str(row['record_time']))
    filename = f"{datetime_id}{row['line_no']}.jpg"
    return filename


if __name__ == '__main__':
    df = pd.DataFrame({
        'record_time': random_datetimes(start, end),
        'line_no': np.random.randint(1, 6, num_of_pcb),
        'has_defect': np.random.randint(0, 2, num_of_pcb),
        # 'file_name':
        'mh': np.random.randint(0, defects_scale[0], num_of_pcb),
        'mb': np.random.randint(0, defects_scale[1], num_of_pcb),
        'oc': np.random.randint(0, defects_scale[2], num_of_pcb),
        'sh': np.random.randint(0, defects_scale[3], num_of_pcb),
        'sp': np.random.randint(0, defects_scale[4], num_of_pcb),
        'spc': np.random.randint(0, defects_scale[5], num_of_pcb),
    })
    df.loc[df['has_defect'] == 0, ['mh', 'mb', 'oc', 'sh', 'sp', 'spc']] = 0
    df['pic_file_name'] = df.apply(create_filename, axis=1)
    print(df.head())
    df.to_csv('./cache/PCB.csv', index=False)
