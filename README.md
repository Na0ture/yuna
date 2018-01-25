# yuna
目标：用算法来分析标的

支持的数据源
-----------------

- `Wind资讯`
- `阿里云API`


基本使用
----------


数据库更新单一股票特定范围的收盘价
```
>>>import yuna
>>>yuna.update("002614", "20170601", "20180117")
```

数据库更新多只股票特定范围的收盘价
```
>>>yuna.update(["002614", "300550"], "20170601", "20180117")
```

清空数据库里的数据
```
>>>yuna.delete()
```
