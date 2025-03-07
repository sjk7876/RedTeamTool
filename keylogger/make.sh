# Spencer Kurtz
# sjk7876@rit.edu
# Team Foxtrot - 2245

#!/bin/bash
NETWORK="spencer-test"
ANS="attacker"
HOST="victim"

printf "** Recreating Network and Containers **\n\n"
incus rm ${HOST} --force > /dev/null
incus rm ${ANS} --force > /dev/null

incus network rm ${NETWORK}
incus network create ${NETWORK} network=UPLINK ipv4.address=192.168.4.1/24 ipv4.nat=true ipv6.address=none ipv6.nat=false

incus init images:ubuntu/noble/cloud ${ANS} --network ${NETWORK} -t c2-m6 -d eth0,ipv4.address=192.168.4.2 -d root,size=100GiB
incus init images:ubuntu/noble/cloud ${HOST} --network ${NETWORK} -t c2-m6 -d eth0,ipv4.address=192.168.4.3 -d root,size=100GiB

printf "\n** Starting Containers **\n"
incus start ${ANS}
incus start ${HOST}

printf "\n** Set Up Ansible - ${ANS} **\n\n"
incus exec ${ANS} -- bash -c 'apt update' > /dev/null
incus exec ${ANS} -- bash -c 'DEBIAN_FRONTEND=noninteractive apt-get install -y ansible net-tools python3 python3-flask nano ssh curl ' #> /dev/null
incus exec ${ANS} -- bash -c 'ln -s /usr/bin/python3 /usr/bin/python'

incus exec ${ANS} -- bash -c 'useradd -m -s /bin/bash "ansible"'
incus exec ${ANS} -- usermod -aG sudo ansible
incus exec ${ANS} -- bash -c 'echo ansible:ansible | chpasswd'
incus exec ${ANS} -- bash -c 'su ansible -c "mkdir --mode=750 /home/ansible/.ssh"'
incus exec ${ANS} -- bash -c 'su ansible -c "ssh-keygen -t rsa -b 4096 -f /home/ansible/.ssh/id_rsa -P \"\""' #> /dev/null

printf "\n** Move SSH Key **\n\n"
incus file pull ${ANS}/home/ansible/.ssh/id_rsa.pub .
incus file push id_rsa.pub ${HOST}/tmp/id_rsa.pub

printf "\n** Set Up Minecraft Host - ${HOST} **\n\n"
incus exec ${HOST} -- bash -c 'apt update' > /dev/null
incus exec ${HOST} -- bash -c 'useradd -m -s /bin/bash "ansible"'
incus exec ${HOST} -- usermod -aG sudo ansible
incus exec ${HOST} -- bash -c 'echo ansible:ansible | chpasswd'

incus exec ${HOST} -- bash -c 'su ansible -c "mkdir --mode=750 /home/ansible/.ssh"'
incus exec ${HOST} -- bash -c 'cat /tmp/id_rsa.pub >> /home/ansible/.ssh/authorized_keys'
incus exec ${HOST} -- bash -c 'rm /tmp/id_rsa.pub'

incus exec ${HOST} -- bash -c 'echo "ansible ALL=(ALL) NOPASSWD:ALL" > /etc/sudoers.d/ansible'
incus exec ${HOST} -- bash -c 'chmod 440 /etc/sudoers.d/ansible'
incus exec ${HOST} -- bash -c 'chown ansible:ansible -R /home/ansible'

incus exec ${HOST} -- bash -c 'DEBIAN_FRONTEND=noninteractive apt-get install -y openssh-server python3 acct nano curl ' #> /dev/null

printf "\n** Enable SSH **\n\n"
incus exec ${ANS} -- bash -c 'systemctl restart ssh' > /dev/null
incus exec ${ANS} -- bash -c 'systemctl enable --now ssh' > /dev/null
incus exec ${HOST} -- bash -c 'systemctl restart ssh' > /dev/null
incus exec ${HOST} -- bash -c 'systemctl enable --now ssh' > /dev/null

printf "\n** Push Ansible Files to Ansible **\n"
incus file push -r ansible ${ANS}/home/ansible/

incus exec ${ANS} -- bash -c 'echo "reset; echo YOU ARE LOGGED IN AS ROOT IN ansible, USE su ansible TO SWITCH USERS" >> /root/.bashrc'
incus exec ${HOST} -- bash -c 'echo "reset; echo YOU ARE LOGGED IN AS ROOT IN mchost, USE su ansible TO SWITCH USERS" >> /root/.bashrc'

printf "\n** Ready to Start - Use the Following to Connect **\n\n"
printf "incus shell ${ANS}\n"
printf "incus shell ${HOST}\n"
