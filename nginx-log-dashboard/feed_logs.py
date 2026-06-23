import sys, os, time
fpath = r'I:\codex\projects\logsview\nginx-log-dashboard\sample_access.log'
with open(fpath, 'a', encoding='utf-8') as f:
    for i in range(20):
        h = time.localtime().tm_hour
        m = time.localtime().tm_min
        s = time.localtime().tm_sec + i
        date_str = f'10/Jun/2026:{h:02d}:{m:02d}:{s:02d} +0800'
        url = ['/api/users','/api/orders','/api/products','/api/search','/api/auth'][i % 5]
        method = ['GET','GET','POST','PUT','DELETE'][i % 5]
        status = [200,200,200,200,201,204,301,401,500,500][i % 10]
        rt = round((i % 10 + 1) * 0.05 + (i * 0.01), 3)
        f.write(f'192.168.1.{i+1} - - [{date_str}] \"{method} {url} HTTP/1.1\" {status} {100+i*50} \"-\" \"Mozilla/5.0\" {rt}\n')
        print(f'Wrote line {i+1}: {url} {rt}s status={status}')
