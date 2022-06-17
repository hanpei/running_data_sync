# RUNNING_DATA_SYNC

## 介绍

同步garmin_cn数据到strava。**目前仅为个人使用，代码没太多配置参数，只是为了将garmin国内服务器数据同步到strava**

大部分代码都是来自https://github.com/yihong0618/running_page


## 使用说明

Python 3.9.13 运行通过。
```
pip install -r requirements.txt
```

### garmin.py
1. 下载garmin_cn原始数据到download目录
2. 压到activites目录 _（一般为fit文件，也有可能解压出gpx文件，猜测是手动添加的活动）_
``` python
python garmin.py 'your_garmin_cn_email' 'your_garmin_cn_password'
```

### strava.py

1. 上传activites中的fit/gpx数据到strava
2. 将上传的活动id递增排序存储到strava_uploaded.json中
3. strava有rate limit(100/15min, 1000/1day)，目前这里是每次上传50条
4. 再次上传时会比对activites目录中的文件id与strava_uploaded的id，做增量上传
5. strava需要申请api,获取client_id, client_secret, 授权参考[running_page](https://github.com/yihong0618/running_page)中的strava部分


``` python
python strava.py 'strava_client_id' 'strava_client_secret' 'strava_refresh_token'
```

### sync.py

1. github action中使用sync.py做同步
2. github secret中配置好 `STRAVA_CLIENT_ID` , `STRAVA_CLIENT_SECRET` , `STRAVA_CLIENT_REFRESH_TOKEN` , `GRAMIN_EMAIL` , `GARMIN_PASSWORD`
2. 取strava_uploaded.json最后一个活动id的日期作为start_date
3. 从garmin下载start_date到today的活动数据
4. 上传到strava

``` python
python sync.py 'strava_client_id' 'strava_client_secret' 'strava_refresh_token' 'your_garmin_cn_email' 'your_garmin_cn_password'
```

