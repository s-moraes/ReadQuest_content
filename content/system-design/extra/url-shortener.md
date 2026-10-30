# Design a URL Shortener

A URL shortener (such as TinyURL or Bitly) maps long web addresses to compact, unique 7-character aliases, redirecting users in milliseconds while handling billions of monthly clicks.

![URL Shortener Architecture](../assets/url-shortener.webp)

---

## 1. Requirements & System Scale

### Functional Requirements
1. **Shortening:** Given a long URL (e.g., `https://example.com/very/long/path?id=42`), return a compact alias (`https://sho.rt/aZ81kQx`).
2. **Redirection:** When visiting the short URL, redirect the browser to the original destination with sub-$10\text{ms}$ latency.
3. **Expiration:** Support optional Time-To-Live (TTL) expiration timestamps.

### Non-Functional Requirements
- **High Availability:** $99.99\%$ uptime; redirection must never fail.
- **Ultra-Low Latency:** Redirection must execute in $<10\text{ms}$.
- **Read-Heavy Ratio:** Anticipate a $100:1$ read-to-write traffic profile.

### Back-of-the-Envelope Estimation
- **Write Volume:** $100\text{ million}$ new URLs/month $\approx 40\text{ writes/sec}$.
- **Read Volume:** $100 \times 40 \approx 4,000\text{ reads/sec}$ (Peak: $8,000\text{ QPS}$).
- **5-Year Storage:** $100\text{M} \times 12 \times 5 = 6\text{ billion records}$.
  - Assuming $500\text{ bytes}$ per record: $6\text{B} \times 500\text{B} \approx 3\text{ TB}$ storage.
- **Cache Sizing (80/20 Rule):** Cache the most active $20\%$ of daily read requests:
  - Daily reads: $100\text{M} \times 100 / 30 \approx 330\text{ million reads/day}$.
  - Daily memory: $330\text{M} \times 0.20 \times 500\text{B} \approx 33\text{ GB RAM}$ (easily fits in a single Redis node).

---

## 2. Encoding Strategy: Base62 vs. Hashing

A short URL key must be compact and URL-safe. Using alphanumeric characters `[0-9a-zA-Z]` provides $10 + 26 + 26 = 62$ symbols (**Base62**).

With a 7-character string:

$$\text{Total Combinations} = 62^7 = 3,521,614,606,208 \quad (\approx 3.52\text{ Trillion URLs})$$

```java
public class Base62Encoder {
    private static final String ALPHABET = 
        "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ";

    public static String encode(long id) {
        StringBuilder sb = new StringBuilder();
        while (id > 0) {
            sb.append(ALPHABET.charAt((int) (id % 62)));
            id /= 62;
        }
        return sb.reverse().toString();
    }
}
```

### Why Hashing (MD5 / SHA-256) is Problematic
Hashing the long URL (`MD5(URL)`) produces a 128-bit hash. Truncating to 7 characters causes **hash collisions**. Resolving collisions requires database lookups and appending salts, adding write latency.

### The Superior Solution: Dedicated Key Generation Service (KGS)
Instead of hashing at runtime, a **Key Generation Service (KGS)** pre-generates unique, random 64-bit integers (using Twitter Snowflake or ZooKeeper range allocations) and encodes them into Base62 in advance. When an application server needs an alias, it claims a pre-generated token in microseconds with zero collision risk.

---

## 3. High-Level Architecture

```text
[ Client ] 
    |
    v
[ CDN / Cloudflare ] ---> (Edge Caching for popular short URLs)
    |
    v
[ Load Balancer ]
    |
    v
[ Shortener Service Fleet ] 
    |                       \
    v                        v
[ Redis Cache ]        [ Distributed DB (NoSQL / PostgreSQL) ]
 (Sub-ms Lookups)       (Indexed on short_key)
```

### HTTP 301 vs. HTTP 302 Redirection

| Status Code | Semantics | Client Behavior | Analytics Impact |
| :--- | :--- | :--- | :--- |
| **HTTP 301** | Moved Permanently | Browser caches redirection indefinitely | Server never sees repeated clicks (Lost analytics)|
| **HTTP 302** | Found (Temporary) | Browser requests redirect from server every time | Every click is tracked for telemetry & billing |

> **Production Choice:** Use **HTTP 302** if analytics, click counts, or fraud detection matter. Use **HTTP 301** if slashing server load is the absolute priority.

---

## 4. Database Schema & Indexing

```sql
CREATE TABLE url_mappings (
    id BIGSERIAL PRIMARY KEY,
    short_key VARCHAR(8) NOT NULL UNIQUE,
    original_url TEXT NOT NULL,
    user_id BIGINT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    expires_at TIMESTAMPTZ
);

CREATE UNIQUE INDEX idx_short_key ON url_mappings (short_key);
```

Because reads query solely by `short_key`, an in-memory B-Tree index on `short_key` delivers sub-millisecond lookups directly from disk or database buffer pools.
