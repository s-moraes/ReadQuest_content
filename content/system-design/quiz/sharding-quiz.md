## Q1
What is the primary challenge of database sharding?

### Option A [CORRECT]
Cross-shard joins, distributed transactions, and re-sharding data under uneven loads.

### Option B
Higher storage density per disk.

### Option C
Lower database connection limits.

### Option D
Inability to use secondary indexes locally within a shard.

### Explanation
Sharding scales write throughput horizontally but makes multi-table joins and distributed transactions significantly more complex.
===
## Q2
What is a shard key?

### Option A [CORRECT]
The attribute or column used by the routing algorithm to determine which shard stores a record.

### Option B
The encryption key used to encrypt database backups.

### Option C
A primary key index that must be unique across all tables.

### Option D
The TLS certificate key for database replication.

### Explanation
A shard key dictates data distribution across physical database partitions.
===
## Q3
What is a hotspot shard?

### Option A [CORRECT]
A shard receiving a disproportionately high amount of read or write traffic due to a poor shard key choice.

### Option B
A shard that is geographically closest to the primary data center.

### Option C
A shard storing only cached in-memory data.

### Option D
A shard undergoing live schema migration.

### Explanation
Non-uniform key distribution (such as sharding on user creation date or celebrity user IDs) creates hotspots.
===
## Q4
How does consistent hashing alleviate resharding overhead?

### Option A [CORRECT]
Only K/N keys need to be remapped on average when a shard node is added or removed.

### Option B
It avoids all network communication between database shards.

### Option C
It eliminates the need for primary keys.

### Option D
It synchronizes clocks using GPS atomic clocks.

### Explanation
Consistent hashing distributes data around a ring, localizing key movements during topology adjustments.
