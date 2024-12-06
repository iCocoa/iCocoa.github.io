---
title: "Kafka 总结"
date: 2022-01-27T20:56:50+10:00
tags: ["Kafka", "中间件"]
categories: ["Java"]
---

### consumer 是推还是拉？
https://kafka.apache.org/documentation/#design_pull
kafka 生产者端生成消息推送（push）到 broker，消费者端从 broker 拉取（pull）消息。

**统一采用 pull 的方式？**
boker 从生产者 pull 消息。在生产者数量庞大的场景下，broker 需要管理维护很多的关系，简直是梦魇。所以采用的是生产者往 broker push 消息。

**统一采用 push 的方式？**
broker 往 consumer push 消息。在 consumer 多样化的场景下，如果生产者的生产速率远远大于消费者，broker 控制不好，push 会造成 consumer 不堪重负。反之，由 consumer 根据自身处理速率来决定何时从 broker 拉取消息，会更好。采用 pull 的弊端在于，如果 broker 没有消息，那么就会空转，这可以通过在调用 poll 接口时传入等待时间阻塞或者传入批次数据包大小来等待阻塞。

### kafka 的 ack 机制
客户端连接到 leader broker 上，发送消息之后，等待或不等待 leader broker 的 ack（是否等待取决于参数`request.required.acks` 配置）。比如：
客户端设置 `acks=0`，客户端不作任何等待，即使消息没有写入 kafka 集群。
客户端设置 `acks=1`，客户端会等待 Leader 副本成功写入后返回的确认，但如果 Leader 副本在消息被同步到其他副本之前崩溃，消息可能会丢失。
客户端设置 `acks=all` 或 `acks=-1`参数，leader 在接收到客户端的消息之后，先写入日志文件，然后往同步副本（ISR）发送数据，等所有的 follower 都确认消息写入成功后，leader 再给客户端发送 ack 确认。

>min.insync.replicas 这个参数定义了在写入消息时，主题（topic）中必须处于“同步”状态的副本数量。同步状态的副本是指那些已经成功写入消息并且与领导者（leader）副本保持同步的副本。如果同步副本的数量少于 min.insync.replicas 指定的值，生产者将无法成功写入消息，从而保证了数据的可靠性。

如果设置了 `min.insync.replicas` 参数，比如设置为 2，结合 acks=all，实际就是需要等 2 个副本都写入才算成功。


### kafka 维护消费状态跟踪的方法

**大部分的消息系统做法**
使用元数据来记录消息的消费状态，粗略分为未消费和已消费状态。那么何时将消息标注为已消费（consumed）状态是一个很关键的决策。
1. 发送消息之后立即将消息标注为 consumed
如果发送消息之后，消费者发生故障，那么消息会丢失
2. 引入确认机制。当消息发送给消费者后，broker 将消息标注为 sent 状态，broker 等待消费者返回确认后才将消息标注为 consumed 状态。
这个策略解决了消息丢失的问题，但引发新的问题。
问题一：消费者处理完消息之后，还没来得及发送确认就出现故障。导致消息一直处于待消费状态，有重发消息重复消费的风险
问题二：性能问题。broker 需要维护消息的状态，在未消费之前需要锁定以防重复发送，消费之后要标注为消费状态。还需要考虑如何处理长时间处于待消费状态没有收到消费者确认的消息。

**Kafka做法**
使用一个偏移量记录消费者的消费进度。消费者可以重置偏移量倒回去消费消息，这个也为消费者提供了一定的容错保障。假设消费者发生故障了，需要重新消费消息。

### 消费者如何不自动提交偏移量
`auto.commit.offset` 参数设置为 false，在处理一批消息后调用提交接口 `commitSync()` or `commitAsync()`

```
ConsumerRecords<> records = consumer.poll();
for (ConsumerRecord<> record: records) {
    // dosomething
}
try {
    consumer.commitSync();
}
```

### 如何设置分区和副本的数量
分区是kafka并行处理的基本单元，为了负载均衡提高吞吐量。
副本是为了做数据冗余备份。
每个分区对应一个或多个副本。
**分区数目设置**：考虑到 broker 的数量，为了负载均衡，一般将分区的数据设置为小于等于 broker 数量。为了提高并行处理能力，更好发挥机器性能，也可以将分区数目设置为大于 broker 到额数目。
**副本数目设置**：为了冗余及高可用性，至少设置大于 1 个并且小于等于 broker 数目，这样副本可以均匀分布在 broker 上。副本数量越多，broker 的存储成本和网络负载也越高。

### kafka 集群中 zookeeper 的作用是什么？
zookeeper 是旧版本（2.8.0 之前） kafka 集群的核心组件之一，负责管理集群的元数据和协调工作。主要包括：
1. 集群协调：broker 注册、leader 选举
2. 元数据管理：topic 和 partition 的配置信息，元数据信息，分区副本的分布、Leader 和 Follower 的位置等
3. 消费者协调：消费者组管理（元数据、消费偏移量）
4. 集群监控：broker 健康状态，分区 Leader 的状态等；通过 Watcher 机制通知集群中其他组件关于集群状态的变化。
kafka新版本（2.8.0）开始引入 KRaft 模式，逐步减少对 zookeeper 的依赖，最终目标是完全移除它。新版本中保留 zookeeper 主要起到升级过度或者混合模式下使用 kafka。

### kafka 生产者负载均衡
生产者发业务消息之前，先往 broker 发送元数据请求（所有的 broker 都可以响应元数据请求）来获得主题分区首领的位置。基于元数据请求的响应结果，生产者直接往分区首领发送数据，中间没有任何路由层。由生产者控制将消息发布到哪个分区，它可以采用随机负载均衡或者定义语义分区函数（用户指定一个键进行哈希并提供接口）。例如，如果将用户 ID 当作 key，那么给定用户的所有数据都会发送到同一个分区。

### kafka 生产者异步发送消息
缓冲批量发送消息，可以配置等待时长或者等待数据累积大小，达到一定大小或者等待时间够了再整批发送，避免频繁 io 

### Unclean leader election: What if they all die?
kafka 对数据丢失的保证是基于至少有一个副本同步，所有复制分区的节点都挂了的情况下无法保证。当这种情况发生时，可以有两种处理策略：
1. 等待 ISR 中的某个副本上线，并选择它作为首领
2. 选择第一个上线的副本作为首领
如果所有 ISR 副本都挂掉了，那么采用第1种策略可能会导致服务长时间不可用；如果采用第2种策略，那么可能上线的副本中的消息不全，丢失部分消息。kafka 从 0.11.0.0 版本开始，默认采用第1种策略，配置参数 `unclean.leader.election.enable` 默认为false。
这是一致性和可用性之前的权衡，不只kafka，所有 quorun-based 方案的系统都有。

### Replicated Logs: Quorums, ISRs, and State Machines (Oh my!)

在核心部分，Kafka 分区是一个复制日志。复制日志是分布式数据系统中最基本的原语之一，有许多实现方法。复制日志可以被其他系统用作实现其他分布式系统的原语，采用状态机风格。


### 主题、分区、key一般怎么定义

主题可以根据业务逻辑来划分比如 `order-processing`、 `user-events` 、`payment-processing`、 `system-logs` 、`iot-data`。key 可以是 `user-id`, `dept-id`, `pay-id`。
kafka 生产者消息分区策略默认提供轮询和随机策略。也可以自定义策略。

### 无消息丢失配置怎么实现？
kafka 只保证已提交的消息不会丢失。

**最佳实践**
不要使用producer.send(msg)，而要使用producer.send(msg, callback)。记住，一定要使用带有回调通知的send方法。

设置acks = all。acks是Producer的一个参数，代表了你对“已提交”消息的定义。如果设置成all，则表明所有副本Broker都要接收到消息，该消息才算是“已提交”。这是最高等级的“已提交”定义。

设置retries为一个较大的值。这里的retries同样是Producer的参数，对应前面提到的Producer自动重试。当出现网络的瞬时抖动时，消息发送可能会失败，此时配置了retries > 0的Producer能够自动重试消息发送，避免消息丢失。

设置unclean.leader.election.enable = false。这是Broker端的参数，它控制的是哪些Broker有资格竞选分区的Leader。如果一个Broker落后原先的Leader太多，那么它一旦成为新的Leader，必然会造成消息的丢失。故一般都要将该参数设置成false，即不允许这种情况的发生。

设置replication.factor >= 3。这也是Broker端的参数。其实这里想表述的是，最好将消息多保存几份，毕竟目前防止消息丢失的主要机制就是冗余。

设置min.insync.replicas > 1。这依然是Broker端参数，控制的是消息至少要被写入到多少个副本才算是“已提交”。设置成大于1可以提升消息持久性。在实际环境中千万不要使用默认值1。

确保replication.factor > min.insync.replicas。如果两者相等，那么只要有一个副本挂机，整个分区就无法正常工作了。我们不仅要改善消息的持久性，防止数据丢失，还要在不降低可用性的基础上完成。推荐设置成replication.factor = min.insync.replicas + 1。

确保消息消费完成再提交。Consumer端有个参数enable.auto.commit，最好把它设置成false，并采用手动提交位移的方式。就像前面说的，这对于单Consumer多线程处理的场景而言是至关重要的。

### Rebalance 及心跳
**Rebalance**：在协调者组件（它专门为消费者组服务）的帮助下，让消费者组内所有的实例就如何消费主题的所有分区达成共识的过程。一般在有消费者数量变化，主题数量变化或者分区数量发生变化时进行 rebalance。Rebalance缺点是，需要所有的消费者停止工作参与进来，耗时，影响 TPS(0.11.0.0版本推出了StickyAssignor，尽量保留先前的分区分配方案)。主题和分区数量的变化一般是运维产生，无法避免，非必要的 rebalance 主要有

下面的参数可以直接使用，可以会话期内发送三次心跳包。max.poll.interval.ms 需要根据下游业务处理所需的时间来确定，比如，消息需要写入数据库，假设写入耗时7 min，那么这个参数应该大于 7min。

```
heartbeat.interval.ms=2000
session.timeout.ms=6000
max.poll.interval.ms=300000
```

session.timeout.ms  和 max.poll.interval.ms 两个时间配置，如果 session 内没有收到心跳包或者两次 poll 时间间隔大于 max.poll.interval.ms， Coordinator就会认为该Consumer已经“死”了，从而将其从Group中移除。

> Kafka为某个Consumer Group确定Coordinator所在的Broker的算法有2个步骤。
第1步：确定由位移主题的哪个分区来保存该Group数据：partitionId=Math.abs(groupId.hashCode() % offsetsTopicPartitionCount)。
第2步：找出该分区Leader副本所在的Broker，该Broker即为对应的Coordinator。

消费者的心跳包通过 poll() api 和后台线程发送，消费者会记录心跳包发送时间戳，两种方式发送心跳包之前需要检查上一次发送的时间戳，kafka 通过同步机制来协调 poll 和后台线程以避免重复发送心跳包。


### kafka 消费者的消费进度监控
对消费者而言，最重要的就是监控消费进度，消费当前的滞后程度（落后于生产者的程度）。
Lag（单位是消息数），值越大说明消费者处理越慢越滞后。

三种监控方法：
1. 使用 kafka 自带的命令行工具 `kafka-consumer-groups`
2. 使用 kafka java consumer api 编程获取
3. 使用kafka 自带的 jmx 监控指标（使用监控框架 Grafana、Zabbix）

`records-lag-max`: 表示消费者组中所有消费者实例的最大滞后记录数。滞后记录数是指消费者当前消费的偏移量与分区中最新消息的偏移量之间的差距。
`records-lead-min`: 表示消费者组中所有消费者实例的最小领先记录数。领先记录数是指消费者当前消费的偏移量与分区中最旧未确认消息的偏移量之间的差距。这个指标帮助你了解消费者是否在处理消息时过于超前。如果 records-lead-min 很小，说明消费者可能在处理消息时过于超前，可能会导致资源浪费或不必要的延迟。

`replica.lag.time.max.ms` 表示副本在多长时间内没有与领导者副本同步数据，就会被认为是不再同步的。如果一个副本在 replica.lag.time.max.ms 时间内没有与领导者副本同步数据，它将被视为“滞后”（lagging），并且可能会被从 ISR（In-Sync Replicas）列表中移除。当副本后面慢慢追赶上 Leader 的速度，那么它是能够重新被加回 ISR的，这是动态调整的集合。

### 实际使用场景中，如何选择
RabbitMQ 或 ActiveMQ 这样的传统消息中间件，它们处理和响应消息的方式是破坏性的（destructive），即一旦消息被成功处理，就会被从 Broker 上删除。
Kafka 是基于日志结构（log-based）的消息引擎，消费者在消费消息时，仅仅是从磁盘上读取数据而已，是读取操作，因此消费者不会删除消息数据。同时，由于位移数据是由消费者控制的，它能够很容易地修改位移的值，实现重复消费历史数据的功能。
那实际场景如何确定使用传统的消息中间件还是使用 Kafka？
传统消息中间件适用场景：消息处理逻辑非常复杂，处理代价很高，不关心消息之间的顺序
kafka 适用场景：需要较高的吞吐量，消息处理时间很短，在意消息的顺序

