# Reverse Proxies & CDNs

Accelerating content delivery and protecting internal infrastructure from direct public Internet exposure requires placing intermediate caching and routing tiers at the network edge: **Reverse Proxies** and **Content Delivery Networks (CDNs)**.

---

## 1. Forward Proxy vs. Reverse Proxy

While both act as intermediaries, their architectural roles and beneficiaries are fundamentally opposite:

```text
FORWARD PROXY (Protects & Represents Clients)
[ Client A ] \
[ Client B ] ---> [ Forward Proxy ] ---> [ Corporate Firewall ] ---> [ Public Web ]
[ Client C ] /   (Caches out, filters, hides client IP)

REVERSE PROXY (Protects & Represents Servers)
[ Public User ] ---> [ Reverse Proxy ] ---> [ Web Tier A ]
                     (TLS Termination,      [ Web Tier B ]
                      Load Balancing, WAF)  [ Web Tier C ]
```

### Forward Proxy
- Sits in front of internal client devices.
- Evaluates outgoing traffic to enforce corporate compliance, inspect outbound packets, and hide client IP addresses.

### Reverse Proxy
- Sits in front of internal backend servers.
- Evaluates incoming public requests, acting as the public-facing gateway for an organization's internal microservices.

---

## 2. Core Capabilities of Modern Reverse Proxies

Industry-standard reverse proxies (such as NGINX, HAProxy, and Envoy) offload heavy infrastructural duties from application runtimes:

```text
[ Client ] -- HTTPS (TLS Handshake) --> [ Reverse Proxy ] -- Plain HTTP / mTLS --> [ App Pods ]
                                                |
                                        - Terminates TLS
                                        - Compresses Brotli/Gzip
                                        - Buffers slow clients
```

### 1. SSL / TLS Termination
Negotiating cryptographic TLS handshakes (RSA / ECDSA key exchanges) consumes significant CPU cycles. Terminating TLS at the reverse proxy frees application containers (JVM, Node.js, Go) to focus entirely on core business logic.

### 2. Slow Client Buffering
If a mobile client uploads a file or streams a payload over a high-latency 3G connection, a standard application thread would remain blocked for seconds. A reverse proxy buffers the incoming payload in native C/Go memory buffers; once fully received, it flushes the request to the application server in microseconds.

### 3. Static Content Serving & Compression
Reverse proxies serve static files (CSS, JavaScript, images) directly from disk caches or kernel page caches using zero-copy system calls (`sendfile`), applying **Gzip** or **Brotli** compression on the fly.

### 4. Web Application Firewall (WAF) & DDoS Mitigation
Filters malicious traffic (SQL injection, Cross-Site Scripting, volumetric HTTP floods) before requests ever reach internal services.

---

## 3. Content Delivery Networks (CDNs)

While a reverse proxy sits in front of backend servers within a single datacenter, a **Content Delivery Network (CDN)** is a globally distributed network of edge servers (Points of Presence - **PoPs**) designed to serve cached content from the geographic location closest to the user.

```text
[ User in Tokyo ] ------------ (3ms RTT) ------------> [ Tokyo CDN Edge PoP ]
                                                               |
                                                           Cache Miss!
                                                               v
[ User in London ] ---> [ London Edge PoP ] ---> [ US-East Origin Datacenter ]
                           (Cache Hit: 4ms)                  (220ms RTT)
```

### How CDNs Route Users: Anycast Routing
CDNs utilize **BGP Anycast** networking: a single public IP address is announced simultaneously from hundreds of datacenters worldwide. Internet routers automatically direct user packets along the shortest BGP path to the nearest physical PoP.

### The Origin Shield
When hundreds of edge PoPs experience simultaneous cache misses for a popular new file, they all query the origin server at once, triggering an **origin stampede**. 

A **Shielding PoP** sits between edge PoPs and the origin server:

```text
[ Edge Tokyo ]  \
[ Edge Sydney ] --+---> [ Origin Shield (US-Central) ] ---> [ Origin Server ]
[ Edge London ] /       (Consolidates misses to 1 request)
```

---

## 4. HTTP Caching Headers & Invalidation

CDNs rely on standard HTTP/1.1 and HTTP/2 headers to determine caching behavior:

```http
HTTP/1.1 200 OK
Content-Type: application/javascript
Cache-Control: public, max-age=31536000, immutable
ETag: "68b329da9893e34099c7d8ad5cb9c940"
```

### Key Cache-Control Directives
- **`public`:** The response may be cached by any intermediate cache (CDNs, proxies, browser).
- **`private`:** The response is customized for a single user and can only be stored in local browser memory (never in shared CDN caches).
- **`max-age=N`:** Specifies freshness window in seconds for the browser.
- **`s-maxage=N`:** Overrides `max-age` specifically for public shared caches (CDNs).
- **`stale-while-revalidate=N`:** Serves stale cached content immediately while asynchronously fetching the fresh update from the origin in the background.

### Invalidation at the Edge: Purge by Tag
Modern CDNs (Fastly, Cloudflare, Akamai) allow applications to tag cached pages with metadata headers:

```http
Surrogate-Key: product-101 catalog-electronics
```

When product `101` changes price, the application issues an API call to the CDN: `PURGE /tags/product-101`. The CDN purges all matching cached variants across all global PoPs within milliseconds.

---

## 5. Architectural Summary: Reverse Proxy vs. CDN

| Dimension | Reverse Proxy (NGINX / Envoy) | Content Delivery Network (CDN) |
| :--- | :--- | :--- |
| **Physical Location** | Inside origin datacenter / K8s cluster | Hundreds of edge PoPs globally |
| **Primary Goal** | TLS termination, load balancing, security | Slashing geographic network latency |
| **Traffic Handled** | Dynamic APIs, microservice routing | Static assets, media, cached API responses |
| **Routing Protocol** | Internal DNS / Virtual IP | BGP Anycast DNS |
| **Deployment Model** | Self-managed VM / container fleet | Managed SaaS (Cloudflare, CloudFront, Fastly) |
