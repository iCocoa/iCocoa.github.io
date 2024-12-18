---
title: 应用层数据分布路由算法
date: 2024-11-11 20:15:32+10:00
tags:
- web
- Algorithm
categories:
- web
- Tech
- Algorithm
description: Example article description
sidebar: left
hiddenFromHomePage: false
---
应用层数据分布路由算法主要用于分布式系统中，将数据或请求分配到多个节点（服务器、存储设备或服务实例）上，以实现负载均衡、高可用性和扩展性。常见的有：
哈希取模（Modulo Hashing）、随机路由 (Random Routing)、一致性哈希（Consistent Hashing）等等。

## 随机路由 (Random Routing)
原理：随机选择一个节点处理请求。

特点：
简单直观，但不能保证均匀分布。
不适合高负载系统，因为可能导致数据倾斜。

应用：用于初步负载均衡或测试场景。

## 哈希取模（Modulo Hashing）

原理：使用简单的哈希函数对节点数量取模，将请求分配到相应节点。

公式：节点 = Hash(Key) % N，其中 N 是节点数量。

特点：简单高效，易于实现。

缺点：节点增减时，所有数据都需要重新分配，无法满足动态性要求。

应用：适用于小规模系统或节点数固定的场景。

## 一致性哈希（Consistent Hashing）
原理：将节点和数据映射到一个逻辑环上，数据存储在与其哈希值最接近的节点中。

特点：
高动态性：节点增减时，仅影响邻近的节点，减少数据迁移量。
负载均衡：通过虚拟节点均衡数据分布。

应用：
分布式缓存（如 Memcached、Redis）。
分布式存储（如 Cassandra、Amazon Dynamo）。
微服务负载均衡。

### 一致性哈希算法实现
一致性Hash首先构建一个Hash 环的结构。环的大小是 0 到`2^32-1`，也就是无符号整型的取值范围，0 和最后一个 `2^32-1` 首尾相连，构成一个 Hash 环。将每个缓存服务节点 hash值放到环上。每次一次进行服务器查找路由计算的时候，都是根据key 的hash 值顺时针查找距离它最近的服务器节点。通过这种方式，key 不变的情况下找到的总是相同的服务器。但是，Hash 值是一个随机值，把一个随机值放到一个环上以后，可能是不均衡的，也就是某两个服务器节点在环上的距离可能很近，而和其它的服务器节点距离很远。这会导致有些服务负载压力特别大，有些服务器的负载压力特别小。在实践中，需要使用虚拟节点对方法进行改进，把一个服务节点放到环上时，把它虚拟成200个虚拟节点，然后把 200 个虚拟节点随机放到环上。key 依然是按照顺时针查找距离它最近的虚拟节点，再根据映射关系找到真正的物理节点。

Java 代码实现如下：
```
public class Consistent {
    SortedMap<Long, PhysicalNode> ring;
    int virtualNodeCount;

    public Consistent(int virtualNodeCount) {
        ring = new TreeMap();
        this.virtualNodeCount = virtualNodeCount;
    }

    public void addNode(PhysicalNode node)
    {
        for (long i = 0; i < virtualNodeCount; i++)
        {
            VirtualNode virtualNode = new VirtualNode(node, i);
            ring.put(hash(virtualNode.toString()), node);
        }
    }

    public void removeNode(PhysicalNode node) {
        for (Iterator<Map.Entry<Long, PhysicalNode>> iterator = ring.entrySet().iterator(); iterator.hasNext();) {
            Map.Entry<Long, PhysicalNode> entry = iterator.next();
            if (entry.getValue().equals(node)) {
                iterator.remove();
            }
        }
    }

    public PhysicalNode getNode(String key)
    {
        long hash = hash(key);
        SortedMap<Long, PhysicalNode> tailMap = ring.tailMap(hash);
        Object firstKey = tailMap.isEmpty() ? ring.firstKey() : tailMap.firstKey();
        return ring.get(firstKey);
    }

    private long hash(String key) {
        try {
            MessageDigest md = MessageDigest.getInstance("MD5");
            byte[] digest = md.digest(key.getBytes());
            long hash = ((long) (digest[3] & 0xFF) << 24) |
                    ((long) (digest[2] & 0xFF) << 16) |
                    ((long) (digest[1] & 0xFF) << 8) |
                    ((long) (digest[0] & 0xFF));
            return hash & 0xFFFFFFFFL;
        } catch (NoSuchAlgorithmException e) {
            throw new RuntimeException("MD5 algorithm not found", e);
        }
    }

    public static void main(String[] args) {
        Consistent consistent = new Consistent(100);
        consistent.addNode(new PhysicalNode("node1"));
        consistent.addNode(new PhysicalNode("node2"));
        consistent.addNode(new PhysicalNode("node3"));
        for (String key : Arrays.asList("key1", "key2", "key3", "key4", "key5", "key6", "key7", "key8", "key9", "key10")) {
            PhysicalNode node = consistent.getNode(key);
            System.out.println(key + " is on " + node);
        }
    }
}
```




