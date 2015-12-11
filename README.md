# mlnx_teuthology
    Mellanox Teuthology and ceph latest packages with RDMA enabled

Configuration
=============

  Runner Host <--- ssh passwordless ---> cluster nodes (1..n)

Prerequisites
=============
  The runner host and all cluster nodes must be running:
  - Ubuntu 14.04
  - MLNX_OFED_LINUX-3.1-1.0.3
  - Accelio for_next commit 9cea8291787b72a746e42964d5de42d6d48f0e0d

    root@all-host:~# git clone git://github.com/accelio/accelio.git accelio.git
    root@all-host:~# cd accelio.git
    root@all-host:~# git checkout -b rec_commit 9cea8291787b72a746e42964d5de42d6d48f0e0d
    root@all-host:~# ./autogen.sh
    root@all-host:~# ./configure --prefix=/usr/local/ root@all-host:~# make j8 && make install

Prepare all nodes under test (runner-host and cluster nodes)
===========================================================

o Create new group and user ubuntu

    root@all-host:~# useradd u 2000 d /home/ubuntu m s /bin/bash ubuntu

o Give root access to the ubuntu user. Add the following line
  "ALL ALL=(root) NOPASSWD:ALL" to /etc/sudoers file

    root@all-host:~# vim /etc/sudoers ALL ALL=(root) NOPASSWD: ALL

o Install openssh-server and setup password-less ssh login between nodes

    ubuntu@all-host:~# sudo apt-get install openssh-server

  - Generate ssh-key if not present.
  - Do not provide any password while generating key
  - On runner-host and all cluster nodes, login as ubuntu user:

    ubuntu@all-host:~# ssh-keygen
    ubuntu@all-host:~# sudo cp f ~/.ssh/id_rsa.pub /etc/ssh/ssh_host_rsa_key.pub
    ubuntu@all-host:~# sudo cp f ~/.ssh/id_rsa /etc/ssh/ssh_host_rsa_key

  - On runner-host only:

    ubuntu@runner-host:~# ssh-copy-id

o Resolve the hostnames across all cluster nodes and runner-host

  For example, add rdma network and rdma hostnames in /etc/hosts
  12.20.1.118 vlab-018-r1
  12.20.1.119 vlab-019-r1
  12.20.1.120 vlab-020-r1

o Install the following dependencies on all node

    ubuntu@all-host:~# sudo apt-get install python-dev python-virtualenv python-pip libevent-dev libmysqlclient-dev python-libvirt python-yaml python-prettytable

    ubuntu@all-host:~# sudo apt-get install binutils libaio1 libboost-system1.54.0 libboost-thread1.54.0 libcrypto++9 libgoogle-perftools4 libjs-jquery libleveldb1 libreadline5 libsnappy1 libtcmalloc-minimal4 libunwind8 python-blinker python-flask python-itsdangerous python-jinja2 python-markupsafe python-pyinotify python-werkzeug xfsprogs libfcgi0ldbl gdebi-core python3-chardet python3-debian python3-six gdisk cryptsetup-bin cryptsetup syslinux libffi-dev libssl-dev qemu-utils libyaml-dev libev-dev


Install and configure Teuthology
================================

o Install teuthology and ceph-qa-suite on runner-host only

  - Teuthology should be installed on the runner-host
  - Runner-host should have enough storage especially /tmp directory
  - Clone this project to home directory $HOME in runner-host

    ubuntu@runner-host:~# cd ~
    ubuntu@runner-host:~# git clone https://github.com/vuhuong/mlnx_teuthology
    ubuntu@runner-host:~# cd mlnx_teuthology

  - Clone "teuthology" project

    ubuntu@runner-host:~# cd ~/mlnx_teuthology
    ubuntu@runner-host:~# git clone https://github.com/vuhuong/teuthology

  - Change the permission of "teuthology" directory to 777 and bootstrap to install

    ubuntu@runner-host:~# cd ~/mlnx_teuthology
    ubuntu@runner-host:~# sudo chmod -R 777 teuthology
    ubuntu@runner-host:~# cd teuthology
    ubuntu@runner-host:~# ./bootstrap

  - Clone "ceph-qa-suite" project

    ubuntu@runner-host:~# cd ~/mlnx_teuthology
    ubuntu@runner-host:~# git clone https://github.com/vuhuong/ceph-qa-suite

o Provide disks/partitions infomation on each OSD node

  - "sudo lsblk" to find all disks/partitions available
  - In the root "/" directory, create a file "/scratch/devs" and add/append available
    disks/partitions used in test. Teuthology will use these disks/partitions as OSD(s)
    in the test.
    The content of "/scratch_devs" file should look like this:

        /dev/sdc2
        /dev/sdd1
        /dev/sdf

  - Change the permission of "/scratch_dev" file to 777

    ubuntu@osd-host:~# sudo chmod -R 777 /scratch_devs

o Create target file on runner-host

  Target file(s) is test configuration file(s) which contains the information about:
  - Test setup and cleanup
  - Path to test suite(s)
  - Path to all built packages
  - Role of each node in cluster
  - Target (key details to connect to cluster nodes)
  - Ceph configuration and test environment setup steps

  The file(s) will have .yaml extension

  Ideally one .yaml file has to be created for each test suite (bvt, fvt, etc...).
  This file will be one of the input parameters to run the test automation suite.

  "~/mlnx_teuthology/target_bvt_sample_xio.yaml" is an example.

