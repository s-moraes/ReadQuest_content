# Design a Chat System

Designing a real-time messaging platform (such as WhatsApp, Slack, or Discord) requires coordinating bidirectional connections, guaranteeing message ordering, managing user presence, and ensuring zero message loss across millions of concurrent users.

---

## 1. System Requirements

### Functional Requirements
1. **1-on-1 Chat:** Low-latency private messaging between two users.
2. **Group Chat:** Multi-party conversations (up to 500 members).
3. **Presence Status:** Real-time visibility into whether contacts are Online or Offline.
4. **Offline Storage:** Deliver unread messages when offline users reconnect.

### Non-Functional Requirements
- **Ultra-Low Latency:** Sub-$100\text{ms}$ end-to-end delivery when both users are online.
- **Strict Ordering:** Messages must appear in the exact chronological sequence in which they were sent.
- **Zero Loss:** Once accepted by the server, messages must never be dropped.

---

## 2. High-Level Architecture

```text
[ Client A ] === Persistent WebSocket ===> [ Chat Gateway Pod 1 ]
                                                  |
                                           1. Assign Seq ID
                                           2. Persist to DB
                                                  |
                                                  v
                                         [ Message Router ]
                                                  |
                         +------------------------+------------------------+
                         | (User B is Online)                              | (User B is Offline)
                         v                                                 v
             [ Redis Pub/Sub Backplane ]                        [ Push Notification (FCM) ]
                         |
                         v
[ Client B ] <=== WebSocket Push <=== [ Chat Gateway Pod 2 ]
```

### Core Components
1. **WebSocket Gateways:** Stateful servers maintaining persistent TCP sockets with active mobile and desktop clients.
2. **Stateless API Tier:** Standard REST endpoints for authentication, group creation, profile updates, and friend lists.
3. **Presence Service:** Tracks client online/offline states using distributed in-memory heartbeats.
4. **Message Storage:** Wide-column store (Apache Cassandra / ScyllaDB) optimized for massive sequential append operations.

---

## 3. The 1-on-1 Message Delivery Lifecycle

```text
Step 1: User A sends message over WebSocket to Gateway Pod 1.
Step 2: Gateway Pod 1 writes message to Cassandra and obtains a sequential ID.
Step 3: Gateway Pod 1 queries the Presence Service for User B.
Step 4a: If User B is Online on Gateway Pod 2:
         Message Router publishes event to Redis Pub/Sub channel "user:B".
         Gateway Pod 2 receives event and pushes it down User B's WebSocket.
Step 4b: If User B is Offline:
         Message Router enqueues an alert to the Push Notification Service (FCM / APNs).
```

---

## 4. Message Ordering Without Clock Drift

In distributed networks, relying on client wall-clock timestamps causes messages to appear out of order due to NTP clock skew between devices.

### Sequence IDs per Conversation
Instead of global timestamps, every conversation maintains a monotonically increasing **64-bit Sequence ID**:

$$\text{Next ID} = \text{Current Seq ID} + 1$$

- Within a 1-on-1 or group channel, every message receives an incrementing integer.
- The client UI sorts messages strictly by `sequence_id`, guaranteeing that responses never appear before questions, even if packets arrive out of order.

---

## 5. Online Presence & Heartbeat Mechanics

How does the system know when a user loses cellular connectivity or closes their app?

```text
Client ---> Heartbeat Ping every 5s ---> [ Presence Service ] ---> Redis (SET user:online EX 15s)
If no heartbeat received for 15s: Key expires -> User transitions to OFFLINE!
```

- Clients emit an asynchronous ping every 5 seconds.
- The Presence Service writes an ephemeral key to Redis with a **15-second TTL**.
- If a mobile phone drives into a tunnel or runs out of battery, the key expires naturally after 15 seconds, and the presence service broadcasts an `Offline` event to the user's contacts.

---

## 6. Storage Model in Cassandra

Chat messages represent immutable, time-series data. Relational databases degrade under millions of concurrent write inserts, making wide-column stores like **Apache Cassandra** the industry standard:

```sql
CREATE TABLE conversation_messages (
    conversation_id UUID,
    message_seq_id BIGINT,
    sender_id UUID,
    content TEXT,
    created_at TIMESTAMP,
    PRIMARY KEY (conversation_id, message_seq_id)
) WITH CLUSTERING ORDER BY (message_seq_id DESC);
```

- **Partition Key (`conversation_id`):** Clusters all messages for a specific chat on the same physical storage nodes.
- **Clustering Key (`message_seq_id`):** Orders messages sequentially on disk, enabling lightning-fast range queries for chat history (`LIMIT 50`).
