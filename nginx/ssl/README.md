# SSL证书目录

此目录用于存放SSL/TLS证书文件。

## 证书文件

- `cert.pem` - SSL证书文件
- `key.pem` - 私钥文件

## 生成自签名证书（开发环境使用）

```bash
# 生成私钥
openssl genrsa -out key.pem 2048

# 生成证书签名请求
openssl req -new -key key.pem -out cert.csr

# 生成自签名证书（有效期365天）
openssl x509 -req -days 365 -in cert.csr -signkey key.pem -out cert.pem

# 清理临时文件
rm cert.csr
```

## 使用Let's Encrypt（生产环境推荐）

```bash
# 安装certbot
sudo apt-get update
sudo apt-get install certbot python3-certbot-nginx

# 获取证书
sudo certbot --nginx -d yourdomain.com

# 复制证书到此目录
sudo cp /etc/letsencrypt/live/yourdomain.com/fullchain.pem ./cert.pem
sudo cp /etc/letsencrypt/live/yourdomain.com/privkey.pem ./key.pem
```

## 注意事项

1. 生产环境请使用有效的SSL证书
2. 私钥文件权限应设置为600：`chmod 600 key.pem`
3. 证书定期更新，Let's Encrypt证书有效期为90天
4. 自签名证书会产生浏览器安全警告，仅用于开发测试