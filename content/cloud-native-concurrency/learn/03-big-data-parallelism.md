# Parallelism in Big Data & Stream Processing

When datasets scale into terabytes or petabytes, single-machine concurrency primitives (such as thread pools, executors, or local locks) saturate CPU cores, exhaust physical memory, and bottleneck on local disk I/O. Analyzing massive data volumes requires **parallel processing distributed across computing clusters**. Java provides the core runtime foundation and native APIs for the industry's leading big data engines.

---

## 1. Concurrency vs. Parallelism at Scale

While the terms are often used interchangeably, they represent distinct physical execution characteristics:

```text
[ CONCURRENCY ] (1 Core, Interleaved)
Core 0: [ Task A ] -> [ Task B ] -> [ Task A ] -> [ Task C ]

[ PARALLELISM ] (Multiple Physical Cores / Clustered Nodes)
Node 1 (Core 0): [ Task A (Partition 1) ] ======================>
Node 2 (Core 1): [ Task A (Partition 2) ] ======================>
Node 3 (Core 2): [ Task A (Partition 3) ] ======================>
```

- **Concurrency:** Managing multiple tasks simultaneously by interleaving execution timelines (e.g., event loops, non-blocking I/O).
- **Parallelism:** Executing computational tasks literally at the same physical instant across separate hardware cores or distributed cluster nodes.

### The Mathematics of Scaling: Amdahl vs. Gustafson

How much speedup can a cluster achieve by adding more worker nodes?

#### 1. Amdahl's Law (Fixed Workload)
Amdahl's Law dictates that the maximum speedup is strictly limited by the sequential (non-parallelizable) portion of the algorithm:

$$\text{Speedup} \le \frac{1}{(1 - P) + \frac{P}{N}}$$

Where $P$ is the parallel fraction of the program and $N$ is the number of processor nodes. If $5\%$ of a batch job must execute sequentially (e.g., initial coordinator setup or final merge), a cluster of 1,000 nodes can **never** exceed a $20\times$ speedup, regardless of hardware expenditure!

#### 2. Gustafson's Law (Scaled Workload)
In big data architectures, the dataset size grows with the cluster capacity. Gustafson's Law recognizes that parallel workloads scale problem size with compute resources:

$$\text{Speedup} = N - (1 - P)(N - 1)$$

Big data engines exploit Gustafson's Law: by partitioning massive datasets into smaller chunks, thousands of worker nodes achieve near-linear processing throughput.

### The Data Skew Bottleneck (The Curse of the Straggler)
Even with 100 worker nodes running in parallel, overall job duration is determined by the slowest worker:

```text
Worker 1: [================] (Completed in 10s)
Worker 2: [================] (Completed in 11s)
Worker 3: [===================================================>] (120s! Data Skew)
Total Job Latency = 120s!
```

If partitioning keys are skewed (e.g., millions of records sharing a `null` key or popular customer ID), a single worker receives disproportionate load. Solving data skew requires **salting keys** (appending random suffixes) or using adaptive query partitioners.

---

## 2. Apache Hadoop & The MapReduce Paradigm

Apache Hadoop pioneered petabyte-scale distributed computing by pairing the **Hadoop Distributed File System (HDFS)** with the **MapReduce** programming model.

```text
+-----------------------------------------------------------------+
|                         HDFS ARCHITECTURE                       |
|                 [ NameNode (Metadata & Master) ]                |
|                    /           |            \                   |
|                   v            v             v                  |
|            [ DataNode 1 ] [ DataNode 2 ] [ DataNode 3 ]         |
|             (Block A, B)   (Block B, C)   (Block A, C)          |
|                 <--- 3x Rack-Aware Replication --->             |
+-----------------------------------------------------------------+
```

### The MapReduce Execution Pipeline

MapReduce processes data in structured, distributed phases:

```text
[ HDFS Input Splits ] 
       |
       v
[ Map Phase ] ---------> (Process splits in parallel on local DataNodes)
       |
       v
[ Combiner (Local) ] --> (Optional local aggregation to save network bandwidth)
       |
       v
[ Shuffle & Sort ] ----> (High network transfer: routes identical keys to same Reducer)
       |
       v
[ Reduce Phase ] ------> (Aggregate values per key across partitions)
       |
       v
[ HDFS Output ]
```

### Java Implementation of MapReduce

```java
// Word Count Mapper in native Hadoop Java API
public class WordCountMapper 
    extends Mapper<LongWritable, Text, Text, IntWritable> {

    private static final IntWritable ONE = new IntWritable(1);
    private final Text wordText = new Text();

    @Override
    protected void map(LongWritable key, Text value, Context context) 
            throws IOException, InterruptedException {
        String line = value.toString();
        StringTokenizer tokenizer = new StringTokenizer(line);
        while (tokenizer.hasMoreTokens()) {
            wordText.set(tokenizer.nextToken().toLowerCase());
            context.write(wordText, ONE);
        }
    }
}

// Word Count Reducer in native Hadoop Java API
public class WordCountReducer 
    extends Reducer<Text, IntWritable, Text, IntWritable> {

    private final IntWritable result = new IntWritable();

    @Override
    protected void reduce(Text key, Iterable<IntWritable> values, Context context) 
            throws IOException, InterruptedException {
        int sum = 0;
        for (IntWritable val : values) {
            sum += val.get();
        }
        result.set(sum);
        context.write(key, result);
    }
}
```

### Why MapReduce Reached Its Limits
1. **Persistent Disk I/O:** Every Map stage flushes intermediate results to physical disks. The subsequent Shuffle reads from disk and writes to the network.
2. **High Latency:** Initializing JVM tasks across nodes takes seconds, making MapReduce unsuitable for interactive queries or streaming pipelines.

---

## 3. In-Memory Parallelism with Apache Spark

**Apache Spark** revolutionized distributed computing by replacing MapReduce's disk-bound stages with in-memory execution graphs.

```text
[ Spark Driver ] 
       |
       +---> [ Cluster Manager (K8s / YARN) ]
       |                  |
       v                  v
+----------------+ +----------------+
| Executor Pod 1 | | Executor Pod 2 |
|  [ Task Slot ] | |  [ Task Slot ] |
|  [ In-Memory ] | |  [ In-Memory ] |
|  [ RDD Block ] | |  [ RDD Block ] |
+----------------+ +----------------+
```

### Core Abstractions: RDDs and Lineage Graphs

A **Resilient Distributed Dataset (RDD)** is an immutable, lazily evaluated, partitioned collection of records distributed across cluster memory.

Instead of writing data to disk after each transformation, Spark builds a **Directed Acyclic Graph (DAG)** of execution. If a worker node crashes mid-job, Spark consults the lineage graph and recomputes only the lost partition:

```text
[ textFile ] ---> [ filter ] ---> [ map ] ---> [ reduceByKey ]
 (Partition 2 Lost!) ===> Recomputes ONLY Partition 2 from source!
```

### Narrow vs. Wide Dependencies

Understanding dependencies is critical for Spark performance:

```text
NARROW DEPENDENCY (No Shuffle - Fast)
Partition 1 [ Map ] ----> Partition 1
Partition 2 [ Map ] ----> Partition 2

WIDE DEPENDENCY (Network Shuffle - Expensive)
Partition 1 \          /----> Partition A (Aggregated)
             [ Shuffle ]
Partition 2 /          \----> Partition B (Aggregated)
```

- **Narrow Dependencies (`map`, `filter`, `flatMap`):** Each partition of the parent RDD is used by at most one partition of the child RDD. Can be pipelined in memory within the same worker task.
- **Wide Dependencies (`reduceByKey`, `groupByKey`, `join`):** Multiple child partitions depend on data distributed across all parent partitions, forcing an expensive **cluster network shuffle**.

### Java Spark Code Example

```java
SparkConf conf = new SparkConf()
    .setAppName("LogMetricAggregator")
    .setMaster("local[*]");

try (JavaSparkContext sc = new JavaSparkContext(conf)) {
    JavaRDD<String> logLines = sc.textFile("hdfs://cluster/logs/app.log");

    // reduceByKey performs map-side combine before shuffle!
    JavaPairRDD<String, Integer> statusCounts = logLines
        .filter(line -> line.contains("HTTP/1.1"))
        .mapToPair(line -> {
            String statusCode = extractStatus(line);
            return new Tuple2<>(statusCode, 1);
        })
        .reduceByKey(Integer::sum);

    statusCounts.saveAsTextFile("hdfs://cluster/output/status_summary");
}
```

> **Performance Tip:** Always prefer `reduceByKey` over `groupByKey`. `reduceByKey` aggregates data locally on each executor prior to the shuffle, reducing network traffic by over $90\%$.

---

## 4. Real-Time Stream Processing & Continuous Parallelism

Batch architectures process static, bounded datasets at rest. Modern cloud architectures require continuous processing of unbounded event streams as data arrives.

```text
[ IoT / Microservices ] ---> [ Kafka Broker ] ---> [ Flink / Kafka Streams ] ---> [ Real-time DB ]
                                (Partitions)          (Parallel Workers)
```

### Time Semantics in Stream Processing

Stream engines must reason about time when ordering concurrent events:

1. **Event Time:** The instant the event was generated on the client device (embedded in the payload timestamp).
2. **Ingestion Time:** The timestamp when the message broker (e.g., Kafka) received the record.
3. **Processing Time:** The local wall-clock time of the cluster worker executing the operator.

```text
Device Event Created (12:00:01) ---> Network Lag (30s) ---> Flink Processing (12:00:31)
     [ Event Time ]                                              [ Processing Time ]
```

### Watermarks: Managing Out-of-Order Events
Network jitter causes events to arrive out of order. A **Watermark** is a control signal injected into the data stream that asserts: *"All events with Event Time $\le T$ have arrived."*

When a watermark for timestamp $T$ passes through a window operator, the window closes and emits its aggregated result, even if late events arrive later.

### Windowing Strategies

```text
TUMBLING WINDOW (Fixed size, Non-overlapping: [0-5s], [5-10s])
|--- 5s ---|--- 5s ---|--- 5s ---|

SLIDING WINDOW (Fixed size, Overlapping: 10s window every 2s)
|===== 10s =====|
  |===== 10s =====|
    |===== 10s =====|

SESSION WINDOW (Dynamic, Bound by inactivity gap)
[ Event 1 ][ Event 2 ] -- Gap > 15m -- [ Event 3 ]
|--- Session A ------|                 |-- Session B --|
```

---

## 5. Apache Flink: Stateful Exactly-Once Streaming

**Apache Flink** is a true streaming-first engine (treating batch processing as a special case of streaming with bounded inputs).

```java
StreamExecutionEnvironment env = 
    StreamExecutionEnvironment.getExecutionEnvironment();

DataStream<SensorReading> stream = env.addSource(new KafkaConsumerSource())
    .assignTimestampsAndWatermarks(
        WatermarkStrategy.<SensorReading>forBoundedOutOfOrderness(Duration.ofSeconds(5))
            .withTimestampAssigner((event, timestamp) -> event.getTimestamp())
    );

DataStream<Alert> alerts = stream
    .keyBy(SensorReading::getDeviceId)
    .window(TumblingEventTimeWindows.of(Time.seconds(60)))
    .aggregate(new TemperatureAnomalyAggregator());

alerts.addSink(new KafkaAlertSink());
env.execute("Sensor Anomaly Detector");
```

### Flink's Chandy-Lamport Checkpointing Algorithm

Flink achieves **End-to-End Exactly-Once Processing** using the **Chandy-Lamport distributed snapshotting algorithm**:

```text
[ Data Stream ] ---> [ Record 1 ] -> [ Record 2 ] -> [ BARRIER ] -> [ Record 3 ]
                                                         |
                                    Worker catches Barrier:
                                    1. Pauses processing
                                    2. Flushes RocksDB state to S3
                                    3. Acknowledges JobManager
                                    4. Resumes processing Record 3
```

- Special **Checkpoint Barriers** flow through the stream alongside data records without stopping stream flow.
- When an operator receives a barrier, it takes an asynchronous snapshot of its local state (stored in **RocksDB**) and persists it to durable cloud storage.
- If any node crashes, the entire stream restarts from the latest coordinated checkpoint barrier, and transactions commit via a **Two-Phase Commit Sink**.

---

## 6. Big Data & Streaming Processing Matrix

| Dimension | Apache Hadoop MapReduce | Apache Spark | Apache Flink | Kafka Streams |
| :--- | :--- | :--- | :--- | :--- |
| **Execution Model** | Batch (Disk-bound) | Micro-batch / In-memory | True Native Streaming | Lightweight Streaming Library |
| **Latency** | Tens of minutes | Sub-second to minutes | Milliseconds (Event-by-event)| Milliseconds |
| **State Storage** | HDFS / Disk | Memory (Tungsten Off-heap)| RocksDB / Managed Heap | Embedded RocksDB |
| **Fault Recovery**| Task restart from disk | RDD Lineage Recompute | Barrier Checkpointing | Changelog topics in Kafka |
| **Deployment** | YARN / Heavy Cluster | YARN / Kubernetes | Standalone / Kubernetes | Embedded in Java App / Pod |
| **Best Used For** | Archival batch transforms | ML, Data Warehousing, ETL | Complex Event Processing (CEP)| Microservice stream joins |
