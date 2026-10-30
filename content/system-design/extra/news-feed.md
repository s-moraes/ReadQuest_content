# Design a News Feed

Designing a high-scale social news feed (such as Twitter/X, Instagram, or Facebook) requires assembling and ranking personalized, real-time activity timelines for hundreds of millions of users with sub-second latency.

---

## 1. System Requirements & Scale

### Functional Requirements
1. **Post Creation:** Users can publish text, links, and media.
2. **Feed Generation:** Users can view a reverse-chronological or ranked timeline of posts from all accounts they follow.
3. **Feed Pagination:** Infinite scrolling supporting sequential page retrieval.

### Non-Functional Requirements
- **Low Latency:** Feed loading must execute in $<200\text{ms}$.
- **High Availability:** System must tolerate node crashes without dropping feeds.
- **Eventual Consistency:** A few seconds of delay before a newly published post appears in all followers' feeds is acceptable.

---

## 2. Fan-Out Models: Push vs. Pull vs. Hybrid

The central architectural challenge is determining **when** to compute the feed:

```text
FAN-OUT ON WRITE (Push Model)
User posts ---> Fan-Out Service ---> Writes Post ID to 1,000 Follower Caches!
* Read Path is blazing fast O(1), but writing is expensive O(N).

FAN-OUT ON READ (Pull Model)
User opens app ---> Queries posts from all 500 followed accounts ---> Merges & Sorts
* Write Path is instant O(1), but reading is slow and DB-heavy.
```

### 1. Fan-Out on Write (Push Model)
When an author publishes a post, the system queries their follower list and pushes the post ID directly into each follower's pre-computed in-memory feed cache:
- **Pros:** Reading the feed is an instant $O(1)$ memory lookup from Redis.
- **The Celebrity Problem ("The Justin Bieber Flaw"):** When an account with 100 million followers publishes, the system must execute $100\text{ million}$ cache writes, saturating message queues and taking minutes to finish.

### 2. Fan-Out on Read (Pull Model)
When a user opens the app, the feed service fetches the recent posts of everyone they follow, merges the lists, and sorts them by timestamp:
- **Pros:** Publishing is instantaneous with zero wasted writes for inactive users.
- **Cons:** High read latency and severe database strain as follower counts increase.

### 3. The Hybrid Model (Production Standard)
Modern platforms employ a hybrid approach based on author follower counts:

```text
                                [ New Post Created ]
                                         |
                       +-----------------+-----------------+
                       |                                   |
           Author has < 25k Followers          Author is a "Celebrity" (> 25k)
                       v                                   v
             [ Fan-Out on Write ]                 [ Do NOT Fan Out ]
         Pushed to Follower Timelines            Written to Author's Outbox only
                       |                                   |
                       +-----------------+-----------------+
                                         |
                                         v
                         [ Follower Requests Feed ]
                                         |
           Merges Cached Timeline (Push) + Celebrity Posts (Pull)
                                         v
                           [ Sub-100ms Ranked Feed ]
```

---

## 3. High-Level Architecture

```text
[ Author ] ---> [ Post Service ] ---> [ Relational DB (Posts) ]
                      |
              Emits Event to Kafka
                      |
                      v
             [ Fan-Out Workers ]
                      |
       Updates Redis ZSET per Follower
                      |
                      v
[ User ] <--- [ News Feed Service ] <--- [ Redis Timeline Cache ]
```

### Timeline Storage in Redis: Sorted Sets (ZSET)
User feeds are stored in Redis as **Sorted Sets (`ZSET`)**:
- **Key:** `timeline:<user_id>`
- **Score:** Unix timestamp of the post.
- **Value:** `post_id`

```text
ZADD timeline:usr_42 1709210001 "post_901"
ZADD timeline:usr_42 1709210050 "post_902"

// Fetch the 20 most recent posts in sub-millisecond time:
ZREVRANGEBYSCORE timeline:usr_42 +inf -inf LIMIT 0 20
```

### Capping Memory Footprint
Users rarely scroll past 500 posts. To prevent Redis memory exhaustion, background workers truncate each timeline to the latest $800\text{ post IDs}$ (`ZREMRANGEBYRANK timeline:usr_42 0 -801`). If a user scrolls deeper, the system falls back to cold database queries.
