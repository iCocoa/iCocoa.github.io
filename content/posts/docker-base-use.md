---
title: "Docker 使用"
date: 2020-07-07T22:15:32+10:00
tags: ["Docker","Container","Devops"]
categories: ["Docker"]
---

通过 Docker 命令行工具与 Docker Daemon 进程通讯使用。

## 使用步骤

1. **安装 Docker 到宿主机（物理机）**
2. **到仓库拉取镜像**  
   [https://hub.docker.com](https://hub.docker.com)
3. **运行镜像产生容器（实例，一个镜像可以运行多个）**

## 镜像操作

### 搜索镜像

```bash
docker search imageName
```

### 拉取镜像

```bash
docker pull imageName:tag
```

- `tag` 版本号，如不指定默认是 `latest`

### 查看本地镜像

```bash
docker images
```

### 删除镜像

```bash
docker rmi imageID
docker rmi [repositoryname]:[tag]
```

### 删除所有未加标签的镜像(untagged)

```bash
docker rmi $(docker images | grep "^<none>" | awk "{print $3}")
```

### 重命名镜像

```bash
docker tag imageId imageName:tag
```

### 通过本地 Dockerfile 文件编译镜像文件

```bash
docker build -t mop:latest - < mopDockerfile
```

## 容器操作

### 进入容器

```bash
sudo docker exec -it ubuntu bash
docker exec -it ardupilot bash
```

### 查看容器

```bash
docker ps -a
```

- `-a`：所有容器，包括停止的
- `-q`：查看停止的容器，不加选项默认查看运行中的容器

### 保存容器

```bash
sudo docker save ubuntu > ubuntu_save.tar
```

### 合并多个容器为一个文件

```bash
sudo docker save -o images.tar postgres:9.0 mongo:3.4
```

### 导出容器或镜像

```bash
sudo docker export ubuntu > ubuntu_export.tar
```

### 加载容器

```bash
sudo docker load < ubuntu_save.tar
```

### 导入容器

```bash
cat ubuntu_export.tar | sudo docker import - ubuntu:18.04
```

### 启动或停止容器

```bash
docker start/stop container-name/container-id
```

### 容器日志

```bash
docker logs container-name/container-id
```

```bash
docker logs -f -t --since="2020-10-20" --tail=10 container-name/container-id
```

```bash
docker logs [OPTIONS] CONTAINER

Options:
  --details        显示更多的信息
  -f, --follow     实时输出日志，最后一行为当前时间戳的日志
  --since string   输出日志开始日期，即只输出指定日期之后的日志。
  --tail string    显示最后多少行日志，默认是all
                   （如： -tail=10 : 查看最后的 10 行日志。） 
  -t, --timestamps 显示时间戳
```

### 镜像重命名

- `docker import` 可以
- `docker load` 不可以

### 将多个镜像打包到一个文件中

- `docker export` 不支持
- `docker save` 支持

### 删除容器

```bash
docker rm containerid
```

### 删除所有已停止运行的容器(stopped)

```bash
docker rm $(docker ps -a -q)
```

### 查看容器信息

#### 宿主机上

```bash
docker inspect containerId
```

#### 容器内部

```bash
ps -fe
```

## 运行

### 运行镜像

```bash
docker run --name container-name -d imageName
```

```bash
docker run -itd --name myubuntu ubuntu:latest /bin/bash
```

> 注意查看官方文档推荐的启动实例，指定一些初始化的配置参数，否则可能初始化失败直接退出。例如 MySQL 官方示例，挂载本地配置文件到 Docker 容器内部。
> 
> ```bash
> $ docker run --name -v /config/mysql:/etc/mysql/conf.d -e MYSQL_ROOT_PASSWORD=……...
> $ docker run -p 3307:3306 --name some-mysql -e MYSQL_ROOT_PASSWORD=my-secret-pwd -d mysql:tag --character-set-server=utf8mb4 —collation-server=utf8mb4_unicode_ci 
> ```

如下：`ubuntu_tsn_data` 指定本地 volume，不存会自动创建，可使用命令 `docker volume ls` 查看所有 volume，`/root/code/` 为容器内 volume

```bash
docker run -itd --name ubuntu_tsn -v ubuntu_tsn_data:/root/code/ b79203eae5ef "/bin/sh" "-c" "tail -f /dev/null"
```

### 端口映射

```bash
docker run -d -p 8090:8090 --name myredis docker.io/redis
```

- `-p 8090:8090`：主机端口:容器内部的端口，注意关闭防火墙

### 查看 Docker 系统版本

```bash
cat /etc/issue
```

### 查看宿主机系统

```bash
cat /proc/version
uname -a
```

## Docker GUI

- [https://cntnr.io/running-guis-with-docker-on-mac-os-x-a14df6a76efc](https://cntnr.io/running-guis-with-docker-on-mac-os-x-a14df6a76efc)
  - VNC
  - X11

## 遇到问题

### Got permission denied while trying to connect to the Docker daemon socket

```plaintext
Got permission denied while trying to connect to the Docker daemon socket at unix:///var/run/docker.sock: Get http://%2Fvar%2Frun%2Fdocker.sock/v1.40/containers/json?all=1: dial unix /var/run/docker.sock: connect: permission denied
```

**Fix:**

1. 创建 Docker 组（如果它不存在）

    ```bash
    sudo groupadd docker
    ```

2. 将当前用户添加到 Docker 组

    ```bash
    sudo usermod -aG docker $USER
    ```

3. 运行以下命令或注销并重新登录（如果不起作用，可能需要重启机器）

    ```bash
    newgrp docker
    ```

4. 检查 Docker 是否可以在没有 root 权限的情况下运行

    ```bash
    docker run hello-world
    ```

### Networking features in Docker Desktop for Mac

详见：[https://docs.docker.com/docker-for-mac/networking/](https://docs.docker.com/docker-for-mac/networking/)

### Docker overlay2 占用大量磁盘空间

查看磁盘空间使用情况，发现 overlay2 占用大量磁盘空间

```bash
df -hl
```

**解决方法**

1. 打开配置文件

    ```bash
    vi /etc/docker/daemon.json
    ```

2. 在文件中增加日志参数设置轮转

    ```json
    {
      "log-driver": "json-file",
      "log-opts": {
        "max-size": "10m",    
        "max-file": "3"    
      }
    }
    ```

3. 重启 Docker

    ```bash
    systemctl restart docker
    ```

4. 执行命令 `docker system prune` 默认清除以下资源：
   - 已停止的容器（container）
   - 未被任何容器所使用的卷（volume）
   - 未被任何容器所关联的网络（network）
   - 所有悬空镜像（image）

   也能减少空间占用。

## 让 Docker 容器开机启动

网上有些文章说，要让 Docker 的容器自动在开机启动，是写脚本，比如在 `rc.local` 中写。其实完全没必要这么麻烦，Docker 有相关指令，`docker run` 指令中加入 `--restart=always` 就行。

```bash
sudo docker run --restart=always xxx 
```

如果创建容器时未指定 `--restart=always`，可通过 `update` 命令设置

```bash
docker update --restart=always xxx
```

## Docker Compose

Docker Compose 是一个比较简单轻量的部署工具，适合单机、本地开发测试部署，使用 `docker-compose.yml` 文件定义容器集群拓扑接口。但是，这种方式无法跨主机集群部署，跨主机集群部署需要 Kubernetes（K8s），更复杂、更强大。



