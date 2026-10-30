# RESTful Architecture Patterns & Modern APIs

Microservice architectures depend on well-defined network APIs to exchange data and execute business capabilities across process boundaries. Selecting the appropriate API paradigm—**REST**, **gRPC**, or **GraphQL**—fundamentally impacts network throughput, payload efficiency, and developer productivity.

---

## 1. RESTful Architecture (Representational State Transfer)

Defined by Roy Fielding in his 2000 doctoral dissertation, REST is an architectural style based on standard web standards:

```text
[ Client ] --- HTTP/1.1 GET /api/v1/orders/101 ---> [ RESTful API Server ]
           <-- 200 OK (JSON Payload) -------------
```

### Core REST Constraints
1. **Stateless Operations:** Every HTTP request contains all necessary credentials and parameters. The server stores no conversational session context.
2. **Resource-Oriented URIs:** URIs represent nouns (`/users`, `/orders/42/items`), while standard HTTP verbs represent actions.
3. **Uniform Interface:** Consistent error codes (HTTP 4xx/5xx), content negotiation (`Accept: application/json`), and standard semantics.

### HTTP Verb Semantics: Safety & Idempotency

| Verb | Semantics | Safe? (No side effects) | Idempotent? ($f(f(x)) = f(x)$) |
| :--- | :--- | :--- | :--- |
| **`GET`** | Retrieve resource | Yes | Yes |
| **`POST`** | Create child resource / Trigger action | No | No |
| **`PUT`** | Completely replace resource | No | Yes |
| **`PATCH`** | Partially update fields of resource | No | No (unless specifically designed) |
| **`DELETE`**| Remove resource | No | Yes |

### Drawbacks of REST in High-Scale Microservices
- **Over-Fetching:** A mobile screen needing only a user's name receives a 2KB JSON blob containing addresses, order history, and preferences.
- **Under-Fetching & Waterfall Latency:** Loading a dashboard requires multiple sequential HTTP round-trips (`GET /user`, then `GET /orders`, then `GET /items`).
- **Text Serialization Overhead:** Parsing JSON strings, serializing floats, and handling whitespace consumes significant CPU cycles at millions of QPS.

---

## 2. gRPC & Protocol Buffers (Protobuf)

Developed by Google, **gRPC** is an open-source, high-performance Remote Procedure Call (RPC) framework built on **HTTP/2** and **Protocol Buffers**.

```text
[ Microservice A ] --- Binary Protobuf Payload (HTTP/2) ---> [ Microservice B ]
 (Generates Stub)                                             (Implements Server)
```

### Protocol Buffers: Strongly-Typed Binary Contracts

APIs are authored in language-neutral `.proto` schema files:

```protobuf
syntax = "proto3";

package readquest.order;

service OrderService {
  rpc GetOrder (OrderRequest) returns (OrderResponse);
  rpc StreamTelemetry (TelemetryRequest) returns (stream TelemetryChunk);
}

message OrderRequest {
  string order_id = 1;
}

message OrderResponse {
  string order_id = 1;
  double total_amount = 2;
  enum Status { PENDING = 0; PAID = 1; SHIPPED = 2; }
  Status status = 3;
}
```

### Why gRPC Outperforms REST
1. **Binary Wire Format:** Protobuf encodes field tags as integers instead of textual string keys. Payloads are $70\%$ to $80\%$ smaller than equivalent JSON.
2. **HTTP/2 Transport:** Multiplexes dozens of concurrent RPCs over a single persistent TCP socket, eliminating head-of-line blocking and TCP handshake overhead.
3. **Code Generation:** Protobuf compilers automatically generate type-safe client stubs and server interfaces across Java, Go, Python, and C++.
4. **Streaming Modes:** Supports four communication styles:
   - **Unary:** Standard single request, single response.
   - **Server Streaming:** Client sends one request, server streams multiple chunks.
   - **Client Streaming:** Client streams data chunks, server sends one response.
   - **Bidirectional Streaming:** Both sides read and write streams concurrently.

---

## 3. GraphQL: Client-Driven Declarative Data Fetching

Created by Meta in 2012, **GraphQL** turns the REST model upside down: instead of the server defining the response structure, **the client requests the exact shape of the data it requires**.

```graphql
# Single client request to /graphql endpoint
query GetUserProfile {
  user(id: "usr_99") {
    name
    email
    recentOrders(limit: 2) {
      orderId
      totalAmount
    }
  }
}
```

The server returns an exact JSON mirror of the query shape:

```json
{
  "data": {
    "user": {
      "name": "Alice Smith",
      "email": "alice@example.com",
      "recentOrders": [
        { "orderId": "ord_101", "totalAmount": 49.99 },
        { "orderId": "ord_102", "totalAmount": 12.50 }
      ]
    }
  }
}
```

### The $N+1$ Query Problem in GraphQL
If 10 user records each fetch their associated order list, naive GraphQL resolvers execute 1 query for the users and 10 individual SQL queries for each user's orders ($N+1$ total queries).

```text
Naive: 1 (SELECT * FROM users) + 10 (SELECT * FROM orders WHERE user_id = ?)
DataLoader: 1 (SELECT * FROM users) + 1 (SELECT * FROM orders WHERE user_id IN (...))
```

Production GraphQL servers solve this using the **DataLoader pattern**, which batches and deduplicates field resolution into a single combined SQL `IN` query.

---

## 4. Architectural Selection Matrix

| Dimension | RESTful APIs | gRPC | GraphQL |
| :--- | :--- | :--- | :--- |
| **Transport** | HTTP/1.1 or HTTP/2 | HTTP/2 (Strict) | HTTP/1.1 or HTTP/2 |
| **Payload Format** | Textual JSON / XML | Binary Protocol Buffers | Textual JSON |
| **Schema Contract** | OpenAPI / Swagger (Optional)| `.proto` file (Mandatory) | GraphQL Schema (Mandatory) |
| **Streaming** | Limited (SSE) | Full Native Duplex | Subscriptions (WebSockets) |
| **Client Control** | Low (Fixed endpoints) | Low (Fixed RPC procedures)| High (Declarative queries) |
| **Browser Support** | Universal | Requires gRPC-Web proxy | Universal |
| **Best Used For** | Public APIs, mobile backends| Internal microservice RPC | Aggregation hubs, BFFs |
