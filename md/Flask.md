# Flask基础框架
1. 创建Flask应用实例
```Flask
app=Flask(__name__)
```
2.定义路由和视图函数
```angular2html
@app.route('/')
def index:
    return 'Hello World!'
```
3. 运行Flask应用
```angular2html
if __name__=='__main__':
    app.run()
```