



#client_max_body_size 1G;
#client_body_buffer_size 128k;
#proxy_buffer_size 16k;
#proxy_buffers 4 32k;
#proxy_read_timeout 300s;
#proxy_send_timeout 300s;
#proxy_request_buffering off

#/etc/nginx/nginx.conf

#update lines
import logging
logging.basicConfig(level=logging.INFO)
with open('/etc/nginx/nginx.conf', 'r') as file:
    lines = file.readlines()
    for i, line in enumerate(lines):
        if 'client_max_body_size' in line:
            lines[i] = 'client_max_body_size 1G;\n'
            logging.info('Updated client_max_body_size')
        if 'client_body_buffer_size' in line:
            lines[i] = 'client_body_buffer_size 128k;\n'
            logging.info('Updated client_body_buffer_size')
        if 'proxy_buffer_size' in line:
            lines[i] = 'proxy_buffer_size 16k;\n'
            logging.info('Updated proxy_buffer_size')
        if 'proxy_buffers' in line:
            lines[i] = 'proxy_buffers 4 32k;\n'
            logging.info('Updated proxy_buffers')
        if 'proxy_read_timeout' in line:
            lines[i] = 'proxy_read_timeout 300s;\n'
            logging.info('Updated proxy_read_timeout')
        if 'proxy_send_timeout' in line:
            lines[i] = 'proxy_send_timeout 300s;\n'
            logging.info('Updated proxy_send_timeout')
        if 'proxy_request_buffering' in line:
            lines[i] = 'proxy_request_buffering off\n'
            logging.info('Updated proxy_request_buffering')

with open('/etc/nginx/nginx.conf', 'w') as file:
    file.writelines(lines)

