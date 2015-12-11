# mlnx_teuthology
Mellanox Teuthology and ceph latest packages with RDMA enabled

Runner Host  <--- ssh passwordless ---> cluster nodes (1..n)

1. Prerequisites
The runner host and all cluster nodes must be running:
•	Ubuntu 14.04
•	MLNX_OFED_LINUX-3.1-1.0.3
•	Accelio for_next commit 9cea8291787b72a746e42964d5de42d6d48f0e0d

  root@all-host:~# git clone git://github.com/accelio/accelio.git accelio.git
  root@all-host:~# cd accelio.git
  root@all-host:~# git checkout -b rec_commit 9cea8291787b72a746e42964d5de42d6d48f0e0d
  root@all-host:~# ./autogen.sh
  root@all-host:~# ./configure --prefix=/usr/local/
  root@all-host:~# make –j8 && make install

2. Prepare all nodes under test (runner-host and cluster nodes)

2.1 Create new group and user “ubuntu”
  root@all-host:~#  useradd –u 2000 –d /home/ubuntu –m –s /bin/bash ubuntu

2.2 Give root access to the “ubuntu” user
  Add the following line “ALL ALL=(root) NOPASSWD:ALL to /etc/sudoers file

  root@all-host:~# vim /etc/sudoers
  ALL ALL=(root) NOPASSWD:  ALL

2.3 Install openssh-server and setup password-less ssh login between nodes
  Install the openssh-server if needed

  ubuntu@all-host:~# sudo apt-get install openssh-server

  Generate ssh-key if not present. Do not provide any password while generating key
  On runner-host and all cluster nodes, login as “ubuntu” user:

  ubuntu@all-host:~# ssh-keygen
  ubuntu@all-host:~# sudo cp –f ~/.ssh/id_rsa.pub /etc/ssh/ssh_host_rsa_key.pub
  ubuntu@all-host:~# sudo cp –f ~/.ssh/id_rsa /etc/ssh/ssh_host_rsa_key

  On runner-host only:
  ubuntu@runner-host:~# ssh-copy-id <all other cluster nodes>

2.4	Resolve the hostnames across all cluster nodes and runner-host
  For example, add rdma network and rdma hostnames in /etc/hosts
  12.20.1.118     vlab-018-r1
  12.20.1.119     vlab-019-r1
  12.20.1.120     vlab-020-r1

2.5	Install the following dependencies on all node
  ubuntu@all-host:~# sudo apt-get install python-dev python-virtualenv python-pip libevent-dev libmysqlclient-dev python-libvirt python-yaml python-prettytable

  ubuntu@all-host:~# sudo apt-get install binutils libaio1 libboost-system1.54.0 libboost-thread1.54.0 libcrypto++9 libgoogle-perftools4 libjs-jquery libleveldb1 libreadline5 libsnappy1 libtcmalloc-minimal4 libunwind8 python-blinker python-flask python-itsdangerous python-jinja2 python-markupsafe python-pyinotify python-werkzeug xfsprogs libfcgi0ldbl gdebi-core python3-chardet python3-debian python3-six gdisk cryptsetup-bin  cryptsetup syslinux libffi-dev libssl-dev qemu-utils libyaml-dev libev-dev

3.	Install and configure Teuthology
3.1	Install Teuthology on runner-host only
•	Teuthology should be installed on the runner-host
•	Runner-host should have enough storage especially /tmp directory
•	Clone this project to home directory $HOME in runner-host
  ubuntu@runner-host:~# cd $HOME
  ubuntu@runner-host:~# git clone https://github.com/vuhuong/mlnx_teuthology

