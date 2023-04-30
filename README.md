# Usage

WxBox（wechat版本使用3.6.0.18）里面启用chatgpt以及async_request扩展

## 启动本地服务

```powershell
$env:OPENAI_API_KEY='<your openai api key>'
python .\server.py
```

## wechat使用方法

```
prompt: <问题>
prompt[<指定max_tokens>]: <问题>
```

