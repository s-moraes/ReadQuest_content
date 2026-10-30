# WebSockets & Server-Sent Events

Traditional web protocols operate on a request-response model initiated exclusively by the client. However, modern applications—such as real-time messaging, financial tickers, collaborative document editing, and live sports updates—require instant data delivery from server to client with sub-millisecond latency.

---

## 1. The Evolution of Real-Time Web Communication

```text
1. SHORT POLLING (Inefficient)
[ Client ] --- Every 2s: Any new data? ---> [ Server ]
           <-- No (Empty 200 OK) ----------

2. LONG POLLING (Moderate)
[ Client ] --- Any new data? -------------> [ Server ]
           ... Server HOLDS connection open until event occurs ...
           <-- Event occurred! (Data) -----
           --- Reconnects immediately ---->

3. WEBSOCKETS / SSE (True Streaming)
[ Client ] === Persistent Full-Duplex or Push Stream ===> [ Server ]
           <================ Immediate Events ===========
```

### The Limitations of Polling
- **Short Polling:** Overwhelms backend servers with millions of redundant HTTP requests, consuming network bandwidth and database connections for empty answers.
- **Long Polling:** Reduces wasted requests by holding connections open, but incurs full HTTP handshake and header re-transmission overhead every time an event is delivered.

---

## 2. WebSockets (Full-Duplex Bidirectional)

Standardized in RFC 6455, **WebSockets** establish a persistent, bidirectional, full-duplex TCP communication channel between browser and server over a single socket connection.

```text
[ Client ] -- 1. HTTP GET (Upgrade: websocket) --> [ Gateway ]
           <- 2. HTTP 101 Switching Protocols ---
           ===========================================
           <== Bidirectional Binary / Text Frames ===>
```

### The WebSocket Handshake

The connection initiates as a standard HTTP/1.1 request:

```http
GET /chat/v1 HTTP/1.1
Host: api.readquest.com
Upgrade: websocket
Connection: Upgrade
Sec-WebSocket-Key: dGhlIHNhbXBsZSBub25jZQ==
Sec-WebSocket-Version: 13
```

If the server supports WebSockets, it responds with **HTTP 101 Switching Protocols**:

```http
HTTP/1.1 101 Switching Protocols
Upgrade: websocket
Connection: Upgrade
Sec-WebSocket-Accept: s3pPLMBiTxaQ9kYGzzhZRbK+xOo=
```

Once upgraded, the HTTP protocol is completely abandoned. Data transfers in lightweight binary or text **frames** with minimal framing overhead (just 2 to 10 bytes per frame, compared to thousands of bytes in standard HTTP request headers).

### Scaling WebSocket Gateways in Cloud Clusters
Because WebSocket connections are stateful and persistent, they introduce distinct operational challenges:
- **Socket Memory Footprint:** 100,000 idle TCP connections consume significant operating system memory buffers. Non-blocking I/O frameworks (Netty, Vert.x) are required to avoid thread-per-socket exhaustion.
- **Load Balancing Affinity:** Once established, a socket is pinned to a specific server pod. If Pod A receives a message intended for User B (connected to Pod C), an external **Pub/Sub Backplane** (such as Redis Pub/Sub or Kafka) must bridge the pods.

---

## 3. Server-Sent Events (SSE)

**Server-Sent Events (SSE)** is a W3C standard providing lightweight, unidirectional, real-time push streaming from server to client over standard HTTP.

```text
[ Client ] --- HTTP GET /events/prices (Accept: text/event-stream) ---> [ Server ]
           <-- HTTP 200 OK (Keep-Alive) --------------------------------
           <-- event: price_tick\ndata: {"ticker":"AAPL","val":182.4}\n\n
           <-- event: price_tick\ndata: {"ticker":"GOOG","val":140.2}\n\n
```

### Native Browser Capabilities
Unlike WebSockets, SSE is built directly into standard web browsers via the native `EventSource` JavaScript API:
- **Built-in Auto-Reconnection:** If the connection drops due to mobile network handoffs, the browser automatically reconnects after a configurable retry interval.
- **Message IDs & Replay:** Every message carries an optional `id: 1042`. Upon reconnection, the browser sends a `Last-Event-ID: 1042` header, allowing the server to replay missed events.
- **HTTP/2 Multiplexing:** Multiple SSE streams share a single underlying TCP connection over HTTP/2, bypassing browser connection limits.

---

## 4. Architectural Selection Matrix

| Dimension | Short Polling | Long Polling | WebSockets | Server-Sent Events (SSE) |
| :--- | :--- | :--- | :--- | :--- |
| **Directionality** | Client pull | Client pull | Full Duplex (Both ways) | Unidirectional (Server to client)|
| **Protocol** | HTTP | HTTP | WebSocket (RFC 6455) | Standard HTTP/1.1 or HTTP/2 |
| **Header Overhead** | Extreme (Per request) | High (Per event) | Minimal (2–10 bytes/frame) | Minimal (No request headers) |
| **Auto-Reconnect** | Manual app code | Manual app code | Manual app code | Native browser built-in |
| **Firewall / Proxy**| Friendly | Friendly | May require WSS (Port 443)| Standard HTTP friendly |
| **Best Used For** | Low-frequency checks | Legacy fallback | Real-time chat, gaming | Stock feeds, live dashboards |
